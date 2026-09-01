@echo off
setlocal
cd /d "%~dp0"
title WOF Browser Fleet Manager

set "PYTHON_CMD="
where py >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=py -3"
if not defined PYTHON_CMD (
  where python >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=python"
)
if not defined PYTHON_CMD (
  echo Python 3 was not found.
  echo Install 64-bit Python 3.11+ or use the Python already prepared for PYLAUNCH.
  pause
  exit /b 2
)

set "FLEET_SETTINGS=%LOCALAPPDATA%\WOF Future Danger\Fleet\settings.json"
if not exist "%FLEET_SETTINGS%" (
  echo.
  echo First run only: configure Browser and optional WOF URL.
  %PYTHON_CMD% fleet_manager.py configure
  if errorlevel 1 (
    echo Fleet configuration failed.
    pause
    exit /b 2
  )
)

echo.
set "COUNT="
set /p COUNT=How many WOF Browser windows? [1/5/10, default 10]: 
if "%COUNT%"=="" set "COUNT=10"

echo.
%PYTHON_CMD% fleet_manager.py start %COUNT% --interactive
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo.
  echo Fleet Manager exited with code %RC%.
  pause
)
exit /b %RC%
