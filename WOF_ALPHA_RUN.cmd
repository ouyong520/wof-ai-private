@echo off
setlocal EnableExtensions DisableDelayedExpansion
title WOF Alpha Current Main

set "REPO=%~dp0"
set "SCRIPT=%REPO%parallel\PYLAUNCH\start_alpha_current_main.ps1"

if not exist "%SCRIPT%" (
  echo.
  echo ERROR: Alpha launcher script is missing.
  echo Run this file from the root of the wof-ai-private Git checkout.
  echo.
  pause
  exit /b 90
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT%" -Repo "%REPO%"
set "RC=%ERRORLEVEL%"

echo.
echo WOF Alpha launcher exit code: %RC%
echo.
pause
exit /b %RC%
