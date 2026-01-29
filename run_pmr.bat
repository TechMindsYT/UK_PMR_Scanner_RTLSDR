@echo off
REM =============================================
REM UK PMR446 Scanner launcher for Windows
REM =============================================

SET ENV_NAME=pmr

CALL "%USERPROFILE%\anaconda3\Scripts\activate.bat" %ENV_NAME%
IF ERRORLEVEL 1 (
    echo Failed to activate Conda environment: %ENV_NAME%
    pause
    exit /b 1
)

python "%~dp0pmr_monitor.py"
pause
