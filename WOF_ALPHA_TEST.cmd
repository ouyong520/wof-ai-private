@echo off
setlocal EnableExtensions DisableDelayedExpansion
title WOF_ALPHA_TEST

set "REPO=%LOCALAPPDATA%\WOF_ALPHA_CURRENT_MAIN\repo"
set "LOOP=%REPO%\parallel\PYLAUNCH\owner_live_retest_loop.ps1"

if not exist "%LOOP%" (
  echo ERROR: The permanent WOF Alpha controller is not installed.
  echo Run WOF_ALPHA_SETUP_ONCE.cmd once. After that, keep using this same Desktop path forever.
  pause
  exit /b 20
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%LOOP%"
exit /b %ERRORLEVEL%
