@echo off
setlocal EnableExtensions DisableDelayedExpansion
title WOF_ALPHA_TEST

set "REPO=%LOCALAPPDATA%\WOF_ALPHA_CURRENT_MAIN\repo"
set "LOOP=%REPO%\parallel\PYLAUNCH\owner_live_retest_loop.ps1"

if not exist "%LOOP%" (
  echo ERROR: WOF Alpha live retest loop is not installed yet.
  echo Run the one-time setup once, then use this file forever.
  pause
  exit /b 20
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%LOOP%"
exit /b %ERRORLEVEL%
