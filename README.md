
# UK PMR446 Multi-Channel Scanner (RTL-SDR)

A Python + GNU Radio application for monitoring **all 16 UK PMR446 channels simultaneously** using an **RTL-SDR Blog V3** on **Windows 11**.

---

## ⚠️ Important Notes (Please Read First)

- This application **requires GNU Radio** and **cannot be bundled into a single EXE on Windows**
- It runs from **Python inside a Conda environment**
- This is normal and expected for SDR applications on Windows
- Tested with:
  - **Windows 11**
  - **RTL-SDR Blog V3**
  - **Python 3.11**
  - **GNU Radio (conda-forge)**

---

## 📦 Hardware Requirements

- RTL-SDR Blog **V3**
- PMR446-capable antenna (UHF ~446 MHz)
- USB 2.0 / 3.0 port

---

## 🧰 Software Prerequisites

### 1️⃣ Install RTL-SDR USB Driver (Zadig)

1. Plug in your RTL-SDR
2. Download **Zadig**  
   https://zadig.akeo.ie
3. Open Zadig
4. Select:
   - Device: `RTL2832U` (or similar)
   - Driver: **WinUSB**
5. Click **Install Driver**

✅ This step is mandatory.

---

### 2️⃣ Install Anaconda (Python Environment Manager)

Download and install **Anaconda (64-bit)**:

https://www.anaconda.com/products/distribution

During install:
- ✔ Add Anaconda to PATH (recommended)
- ✔ Use default options

Restart your PC after installation.

---

## 🧪 Environment Setup (One-Time)

### 3️⃣ Open **Anaconda Prompt**

From Start Menu:
```
Anaconda Prompt
```

---

### 4️⃣ Create a dedicated environment (Python 3.11)

```
conda create -n pmr python=3.11
conda activate pmr
```

You should now see:
```
(pmr)
```

---

### 5️⃣ Enable conda-forge (required)

```
conda config --add channels conda-forge
conda config --set channel_priority strict
```

---

### 6️⃣ Install GNU Radio

```
conda install gnuradio
```

⏳ This can take several minutes — this is normal.

---

### 7️⃣ Install Python dependencies

```
pip install numpy pyqt5
```

---

## 📂 Application Setup

### 8️⃣ Clone this repository

```
git clone https://github.com/TechMindsYT/UK_PMR_Scanner_RTLSDR.git
cd UK_PMR_Scanner_RTLSDR
```

Or download the ZIP from GitHub and extract it.

---

## ▶️ Running the Application

### Option A — Using the batch file (recommended)

A helper script is included to make running the app easier.

1. Double-click:
```
run_pmr.bat
```

The script will:
- Activate the `pmr` Conda environment
- Launch `pmr_monitor.py`

---

### Option B — Manual start

```
conda activate pmr
python pmr_monitor.py
```

---

## ✅ What You Should See

- Main window opens
- RF Gain slider at the top
- Wide waterfall showing **446.0–446.2 MHz**
- 16 channel panels:
  - Channels 1–8 (top row)
  - Channels 9–16 (bottom row)
- Each channel has:
  - RF level meter
  - Squelch control
  - Volume control
  - Mute / Solo buttons
- Audio plays automatically when a channel opens squelch

---

## 🔧 Troubleshooting

### ❌ “No module named gnuradio”
Make sure:
- You are using **Anaconda Prompt**
- `(pmr)` is visible in the prompt
- GNU Radio was installed successfully

Check with:
```
python -c "from gnuradio import gr; print('OK')"
```

---

### ❌ RTL-SDR not detected
- Re-run Zadig
- Confirm **WinUSB** driver is installed
- Unplug / replug the dongle
- Close SDR# or any other SDR apps

---

### ❌ Audio distorted or bleeding between channels
- Reduce **RF Gain** (30–35 is usually ideal)
- Adjust squelch per channel
- Ensure a good antenna and avoid overload

---

## 📝 Notes on Windows & SDR

- GNU Radio on Windows **cannot be packaged into a single EXE**
- This project intentionally runs from source for stability
- This is the same approach used by many SDR research tools

---

## 📜 License

MIT License

---

## 🙌 Acknowledgements

- GNU Radio Project
- RTL-SDR Blog
- Conda-Forge community
