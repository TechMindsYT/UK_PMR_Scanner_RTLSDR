@echo off
SETLOCAL

SET ENV_NAME=base
SET PROJECT_DIR=%~dp0
SET RADIO_SCRIPTS=%USERPROFILE%\radioconda\Scripts

IF NOT EXIST "%RADIO_SCRIPTS%\activate.bat" (
  echo ERROR: Radioconda Scripts not found:
  echo   %RADIO_SCRIPTS%
  pause
  exit /b 1
)

cd /d "%RADIO_SCRIPTS%"
CALL activate.bat %ENV_NAME%
IF ERRORLEVEL 1 (
  echo ERROR: Failed to activate "%ENV_NAME%".
  pause
  exit /b 1
)

cd /d "%PROJECT_DIR%"
python pmr_monitor.py

pause
ENDLOCAL
