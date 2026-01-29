@echo off
REM =================================================
REM UK PMR446 Scanner launcher (Radioconda)
REM Portable for any Windows user
REM =================================================

SET ENV_NAME=pmr
SET PROJECT_DIR=%~dp0
SET RADIOCONDA_SCRIPTS=%USERPROFILE%\radioconda\Scripts

REM Check Radioconda exists
IF NOT EXIST "%RADIOCONDA_SCRIPTS%\activate.bat" (
    echo ERROR: Radioconda not found at:
    echo %RADIOCONDA_SCRIPTS%
    echo.
    echo Please install Radioconda or adjust your PATH.
    pause
    exit /b 1
)

REM Go to Radioconda Scripts
cd /d "%RADIOCONDA_SCRIPTS%"

REM Activate environment
CALL activate.bat %ENV_NAME%
IF ERRORLEVEL 1 (
    echo ERROR: Failed to activate Conda environment "%ENV_NAME%"
    echo Make sure it exists:
    echo   conda create -n %ENV_NAME% python=3.11
    pause
    exit /b 1
)

REM Return to project directory
cd /d "%PROJECT_DIR%"

REM Run application
python pmr_monitor.py

pause
