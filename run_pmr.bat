@echo off
SETLOCAL

SET ENV_NAME=pmr
SET PROJECT_DIR=%~dp0
SET ACTIVATE_BAT=%USERPROFILE%\radioconda\Scripts\activate.bat

IF NOT EXIST "%ACTIVATE_BAT%" (
  echo ERROR: Could not find Radioconda activate.bat at:
  echo   %ACTIVATE_BAT%
  echo.
  echo Install Radioconda to: %USERPROFILE%\radioconda  (default)
  pause
  exit /b 1
)

REM Activate environment (this runs conda.bat internally)
CALL "%ACTIVATE_BAT%" %ENV_NAME%
IF ERRORLEVEL 1 (
  echo ERROR: Failed to activate environment "%ENV_NAME%".
  echo If you haven't created it yet, run:
  echo   conda create -n %ENV_NAME% python=3.11
  pause
  exit /b 1
)

REM Run from the repo folder
cd /d "%PROJECT_DIR%"
python pmr_monitor.py

pause
ENDLOCAL
