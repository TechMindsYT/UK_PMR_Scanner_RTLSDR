import sys
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui

from gnuradio import gr, analog, audio, filter, blocks
from gnuradio.fft import logpwrfft
import osmosdr

# ==========================================================
# PMR CHANNELS
# ==========================================================
PMR_CHANNELS = [
    446.00625e6, 446.01875e6, 446.03125e6, 446.04375e6,
    446.05625e6, 446.06875e6, 446.08125e6, 446.09375e6,
    446.10625e6, 446.11875e6, 446.13125e6, 446.14375e6,
    446.15625e6, 446.16875e6, 446.18125e6, 446.19375e6,
]
NUM_CHANNELS = len(PMR_CHANNELS)

# ==========================================================
# COLOUR MAP
# ==========================================================
def colormap_fire(db, lo=-95, hi=-30):
    x = np.clip((db - lo) / (hi - lo), 0.0, 1.0)
    r = np.clip(3*x - 1, 0, 1)
    g = np.clip(3*x, 0, 1)
    b = np.clip(1 - 3*x, 0, 1)
    return (np.stack([r, g, b], axis=1) * 255).astype(np.uint8)

# ==========================================================
# WATERFALL WIDGET (OVERLAY SAFE)
# ==========================================================
class WaterfallWidget(QtWidgets.QWidget):
    def __init__(self, fft_size, height=140, channels=16):
        super().__init__()
        self.fft_size = fft_size
        self.channels = channels
        self.setFixedHeight(height)

        self.img = QtGui.QImage(
            fft_size, height, QtGui.QImage.Format_RGB888
        )
        self.img.fill(QtGui.QColor(0, 0, 0))

        self._row_bytes = b""

    def push_row(self, spectrum):
        if spectrum is None or len(spectrum) != self.fft_size:
            return

        rgb = colormap_fire(spectrum)
        self._row_bytes = rgb.tobytes()

        p = QtGui.QPainter(self.img)
        p.drawImage(
            0, 1,
            self.img.copy(0, 0, self.fft_size, self.img.height() - 1)
        )

        row_img = QtGui.QImage(
            self._row_bytes,
            self.fft_size,
            1,
            3 * self.fft_size,
            QtGui.QImage.Format_RGB888
        )
        p.drawImage(0, 0, row_img)
        p.end()
        self.update()

    def paintEvent(self, e):
        p = QtGui.QPainter(self)

        # draw waterfall
        p.drawImage(self.rect(), self.img)

        w = self.width()
        h = self.height()
        ch_w = w / self.channels

        # vertical channel lines
        p.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 100), 1))
        for ch in range(1, self.channels):
            x = int(ch * ch_w)
            p.drawLine(x, 0, x, h)

        # # channel labels (BOLD BLACK, centered)
        # font = QtGui.QFont("Segoe UI", 10, QtGui.QFont.Bold)
        # p.setFont(font)

        # for ch in range(self.channels):
        #     rect = QtCore.QRectF(
        #         ch * ch_w,
        #         2,
        #         ch_w,
        #         18
        #     )

        #     # subtle shadow for readability
        #     p.setPen(QtGui.QColor(255, 255, 255, 140))
        #     p.drawText(rect.translated(1, 1),
        #                QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop,
        #                f"CH{ch+1}")

        #     p.setPen(QtGui.QColor(0, 0, 0))
        #     p.drawText(rect,
        #                QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop,
        #                f"CH{ch+1}")

        p.end()

# ==========================================================
# SDR CHANNEL
# ==========================================================
class PMRChannel:
    def __init__(self, tb, src, center, freq):
        self.freq = freq
        self._vol = 0.25
        self.muted = False

        offset = freq - center

        self.xlating = filter.freq_xlating_fir_filter_ccf(
            int(tb.samp_rate / tb.quad_rate),
            filter.firdes.low_pass(1.0, tb.samp_rate, 5800, 900),
            offset,
            tb.samp_rate
        )

        self.squelch = analog.simple_squelch_cc(-48, 0.02)

        self.nfm = analog.nbfm_rx(
            audio_rate=tb.audio_rate,
            quad_rate=tb.quad_rate,
            tau=35e-6
        )

        self.lpf = filter.fir_filter_fff(
            1, filter.firdes.low_pass(1.0, tb.audio_rate, 3000, 800)
        )

        self.vol = blocks.multiply_const_ff(self._vol)
        self.mute = blocks.multiply_const_ff(1.0)
        self.audio = audio.sink(tb.audio_rate, "", True)

        self.mag2 = blocks.complex_to_mag_squared()
        self.avg = blocks.moving_average_ff(512, 1/512, 4000)
        self.probe = blocks.probe_signal_f()

        tb.connect(src, self.xlating)
        tb.connect(self.xlating, self.mag2, self.avg, self.probe)
        tb.connect(self.xlating, self.squelch, self.nfm)
        tb.connect(self.nfm, self.lpf, self.vol, self.mute, self.audio)

    def rf_level(self):
        return float(self.probe.level())

    def set_volume(self, v):
        self._vol = v
        if not self.muted:
            self.vol.set_k(v)

    def set_squelch(self, v):
        self.squelch.set_threshold(v)

    def set_muted(self, m):
        self.muted = m
        self.mute.set_k(0.0 if m else 1.0)
        if not m:
            self.vol.set_k(self._vol)

# ==========================================================
# SCANNER
# ==========================================================
class PMRScanner(gr.top_block):
    def __init__(self):
        super().__init__()

        self.samp_rate = 2_000_000
        self.quad_rate = 240_000
        self.audio_rate = 48_000

        self.center = sum(PMR_CHANNELS) / NUM_CHANNELS

        self.src = osmosdr.source("numchan=1")
        self.src.set_sample_rate(self.samp_rate)
        self.src.set_center_freq(self.center)
        self.src.set_gain(35)

        self.channels = [
            PMRChannel(self, self.src, self.center, f)
            for f in PMR_CHANNELS
        ]

        self.decim = 8
        self.wf_rate = self.samp_rate // self.decim

        self.wf_lpf = filter.fir_filter_ccf(
            self.decim,
            filter.firdes.low_pass(1.0, self.samp_rate, 120_000, 20_000)
        )

        self.fft_size = 1024
        self.fft = logpwrfft.logpwrfft_c(
            self.wf_rate, self.fft_size,
            2.0, 10, True, 0.25
        )

        self.sink = blocks.vector_sink_f(self.fft_size)
        self.connect(self.src, self.wf_lpf, self.fft, self.sink)

    def get_spectrum(self):
        data = self.sink.data()
        if len(data) < self.fft_size:
            return None
        row = np.array(data[-self.fft_size:], dtype=np.float32)
        self.sink.reset()
        return np.roll(row, self.fft_size // 2)

    def set_gain(self, g):
        self.src.set_gain(int(g))

# ==========================================================
# UI
# ==========================================================
class ChannelWidget(QtWidgets.QFrame):
    def __init__(self, scanner, idx):
        super().__init__()
        self.scanner = scanner
        self.ch = scanner.channels[idx]

        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setLineWidth(2)

        v = QtWidgets.QVBoxLayout(self)

        title = QtWidgets.QLabel(
            f"CH {idx+1}\n{self.ch.freq/1e6:.5f} MHz"
        )
        title.setAlignment(QtCore.Qt.AlignCenter)
        v.addWidget(title)

        self.rf = QtWidgets.QProgressBar()
        self.rf.setRange(0, 100)
        self.rf.setTextVisible(False)
        self.rf.setStyleSheet("""
        QProgressBar {
            background: #111;
            border: 1px solid #444;
        }
        QProgressBar::chunk {
            background: qlineargradient(
                x1:0,y1:0,x2:1,y2:0,
                stop:0 #2ecc71,
                stop:0.7 #f1c40f,
                stop:1 #e74c3c
            );
        }""")
        v.addWidget(self.rf)

        self.rf_lbl = QtWidgets.QLabel("RF: 0")
        self.rf_lbl.setAlignment(QtCore.Qt.AlignCenter)
        v.addWidget(self.rf_lbl)

        sliders = QtWidgets.QHBoxLayout()

        sql_box = QtWidgets.QVBoxLayout()
        self.sql = QtWidgets.QSlider(QtCore.Qt.Vertical)
        self.sql.setRange(-70, -30)
        self.sql.setValue(-48)
        self.sql.valueChanged.connect(self.ch.set_squelch)
        sql_box.addWidget(self.sql)
        sql_box.addWidget(QtWidgets.QLabel("SQL", alignment=QtCore.Qt.AlignCenter))

        vol_box = QtWidgets.QVBoxLayout()
        self.vol = QtWidgets.QSlider(QtCore.Qt.Vertical)
        self.vol.setRange(0, 100)
        self.vol.setValue(25)
        self.vol.valueChanged.connect(lambda v: self.ch.set_volume(v/100))
        vol_box.addWidget(self.vol)
        vol_box.addWidget(QtWidgets.QLabel("VOL", alignment=QtCore.Qt.AlignCenter))

        sliders.addLayout(sql_box)
        sliders.addLayout(vol_box)
        v.addLayout(sliders)

        self.mute = QtWidgets.QPushButton("Mute")
        self.mute.setCheckable(True)
        self.mute.toggled.connect(self.ch.set_muted)
        v.addWidget(self.mute)

        self.solo = QtWidgets.QPushButton("Solo")
        self.solo.setCheckable(True)
        self.solo.toggled.connect(self.on_solo)
        v.addWidget(self.solo)

    def on_solo(self, s):
        if s:
            for c in self.scanner.channels:
                c.set_muted(True)
            self.ch.set_muted(False)
        else:
            for c in self.scanner.channels:
                c.set_muted(False)

    def update_ui(self):
        rf = min(100, int(self.ch.rf_level() * 3e6))
        self.rf.setValue(rf)
        self.rf_lbl.setText(f"RF: {rf}")

class MainWindow(QtWidgets.QWidget):
    def __init__(self, scanner):
        super().__init__()
        self.scanner = scanner
        self.setWindowTitle("PMR446 Scanner by M0DQW Tech Minds")

        main = QtWidgets.QVBoxLayout(self)

        gain_row = QtWidgets.QHBoxLayout()
        gain_row.addWidget(QtWidgets.QLabel("RF Gain"))
        self.gain_val = QtWidgets.QLabel("35 dB")

        gain = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        gain.setRange(10, 49)
        gain.setValue(35)
        gain.valueChanged.connect(self.on_gain)

        gain_row.addWidget(gain)
        gain_row.addWidget(self.gain_val)
        main.addLayout(gain_row)

        self.waterfall = WaterfallWidget(scanner.fft_size, 140, NUM_CHANNELS)
        main.addWidget(self.waterfall)

        grid = QtWidgets.QGridLayout()
        self.widgets = []
        for i in range(NUM_CHANNELS):
            w = ChannelWidget(scanner, i)
            self.widgets.append(w)
            grid.addWidget(w, i // 8, i % 8)
        main.addLayout(grid)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(100)

    def on_gain(self, v):
        self.scanner.set_gain(v)
        self.gain_val.setText(f"{v} dB")

    def update_ui(self):
        for w in self.widgets:
            w.update_ui()

        row = self.scanner.get_spectrum()
        if row is not None:
            self.waterfall.push_row(row)

# ==========================================================
# MAIN
# ==========================================================
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    scanner = PMRScanner()
    scanner.start()

    win = MainWindow(scanner)
    win.show()

    app.exec_()
