
@echo off
REM =================================================
REM UK PMR446 Scanner launcher (portable, Windows)
REM Requires Conda (Anaconda / Miniconda / Radioconda)
REM =================================================

SET ENV_NAME=pmr

REM Locate conda.bat
where conda >nul 2>nul
IF ERRORLEVEL 1 (
    echo ERROR: Conda not found in PATH.
    echo Please install Anaconda / Miniconda and ensure it is added to PATH.
    pause
    exit /b 1
)

REM Get conda base path
FOR /F "delims=" %%i IN ('conda info --base') DO SET CONDA_BASE=%%i

REM Activate environment using conda.bat (THIS IS THE KEY)
CALL "%CONDA_BASE%\Scripts\activate.bat" %ENV_NAME%
IF ERRORLEVEL 1 (
    echo ERROR: Failed to activate Conda environment "%ENV_NAME%".
    echo Make sure it exists by running:
    echo   conda create -n %ENV_NAME% python=3.11
    pause
    exit /b 1
)

REM Run application using env python
python "%~dp0pmr_monitor.py"

pause
