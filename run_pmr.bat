@echo off
REM =================================================
REM UK PMR446 Scanner launcher (portable)
REM Requires Conda (Anaconda / Miniconda / Radioconda)
REM =================================================

SET ENV_NAME=pmr

REM Check conda is available
where conda >nul 2>nul
IF ERRORLEVEL 1 (
    echo ERROR: Conda not found in PATH.
    echo Please install Anaconda / Miniconda and ensure it is added to PATH.
    pause
    exit /b 1
)

REM Activate environment
CALL conda activate %ENV_NAME%
IF ERRORLEVEL 1 (
    echo ERROR: Failed to activate Conda environment "%ENV_NAME%".
    echo Make sure it exists by running:
    echo   conda create -n %ENV_NAME% python=3.11
    pause
    exit /b 1
)

REM Run application
python "%~dp0pmr_monitor.py"

pause
