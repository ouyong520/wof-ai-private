@echo off
setlocal EnableExtensions DisableDelayedExpansion
title WOF_ALPHA_SETUP_ONCE

echo.
echo ================================================
echo WOF Alpha - FINAL ONE TIME SETUP
echo ================================================
echo After this, use only Desktop\WOF_ALPHA_TEST.cmd
echo.

set "REPO=%LOCALAPPDATA%\WOF_ALPHA_CURRENT_MAIN\repo"
if not exist "%REPO%\.git" (
  echo ERROR: Managed Alpha repo was not found:
  echo %REPO%
  pause
  exit /b 20
)

set "KEYDIR=%USERPROFILE%\.ssh"
set "KEY=%KEYDIR%\wof_alpha_github_ed25519"
if not exist "%KEYDIR%" mkdir "%KEYDIR%" >nul 2>&1

set "KEYGEN="
for /f "delims=" %%K in ('where ssh-keygen.exe 2^>nul') do if not defined KEYGEN set "KEYGEN=%%K"
if not defined KEYGEN if exist "C:\Windows\System32\OpenSSH\ssh-keygen.exe" set "KEYGEN=C:\Windows\System32\OpenSSH\ssh-keygen.exe"
if not defined KEYGEN if exist "C:\Program Files\Git\usr\bin\ssh-keygen.exe" set "KEYGEN=C:\Program Files\Git\usr\bin\ssh-keygen.exe"

if not defined KEYGEN (
  echo ERROR: ssh-keygen.exe was not found.
  pause
  exit /b 21
)

if not exist "%KEY%" (
  echo Creating the dedicated WOF Alpha update key once...
  "%KEYGEN%" -q -t ed25519 -N "" -C WOF_ALPHA_UPDATER -f "%KEY%"
  if errorlevel 1 (
    echo ERROR: Could not create the SSH key.
    pause
    exit /b 22
  )
)

if not exist "%KEY%.pub" (
  echo ERROR: SSH public key is missing.
  pause
  exit /b 23
)

set "INSTALLER=%REPO%\parallel\PYLAUNCH\install_live_retest_once.ps1"
if not exist "%INSTALLER%" (
  echo ERROR: The cached repo does not contain the final installer yet.
  echo Run the supplied final setup package once to install it locally.
  pause
  exit /b 24
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%INSTALLER%"
exit /b %ERRORLEVEL%
