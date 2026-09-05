@echo off
setlocal EnableExtensions DisableDelayedExpansion
title WOF_ALPHA_SETUP_ONCE

echo.
echo ================================================
echo WOF Alpha - ONE TIME PERMANENT SETUP
echo ================================================
echo This bootstraps from an empty managed directory.
echo After this, use only Desktop\WOF_ALPHA_TEST.cmd.
echo.

set "BASE=%LOCALAPPDATA%\WOF_ALPHA_CURRENT_MAIN"
set "REPO=%BASE%\repo"
set "REMOTE=git@github.com:ouyong520/wof-ai-private.git"
set "LIVE_BRANCH=alpha-live"
set "KEYDIR=%USERPROFILE%\.ssh"
set "KEY=%KEYDIR%\wof_alpha_github_ed25519"
set "STAGING=%BASE%\repo.bootstrap.%RANDOM%.%RANDOM%"

set "GITEXE="
for /f "delims=" %%G in ('where git.exe 2^>nul') do if not defined GITEXE set "GITEXE=%%G"
if not defined GITEXE (
  echo ERROR: Git for Windows was not found.
  echo Install Git for Windows once, then run this same setup again.
  pause
  exit /b 20
)

set "KEYGEN="
for /f "delims=" %%K in ('where ssh-keygen.exe 2^>nul') do if not defined KEYGEN set "KEYGEN=%%K"
if not defined KEYGEN if exist "C:\Windows\System32\OpenSSH\ssh-keygen.exe" set "KEYGEN=C:\Windows\System32\OpenSSH\ssh-keygen.exe"
if not defined KEYGEN if exist "C:\Program Files\Git\usr\bin\ssh-keygen.exe" set "KEYGEN=C:\Program Files\Git\usr\bin\ssh-keygen.exe"
if not defined KEYGEN (
  echo ERROR: ssh-keygen.exe was not found.
  echo Enable Windows OpenSSH Client or reinstall Git for Windows, then rerun this same setup.
  pause
  exit /b 21
)

if not exist "%KEYDIR%" mkdir "%KEYDIR%" >nul 2>&1
if not exist "%KEY%" (
  echo Creating only the dedicated WOF Alpha GitHub key...
  "%KEYGEN%" -q -t ed25519 -N "" -C WOF_ALPHA_UPDATER -f "%KEY%"
  if errorlevel 1 (
    echo ERROR: Could not create %KEY%.
    pause
    exit /b 22
  )
)

if not exist "%KEY%.pub" (
  echo Rebuilding the public half of the existing dedicated Alpha key...
  "%KEYGEN%" -y -f "%KEY%" > "%KEY%.pub.tmp" 2>nul
  if errorlevel 1 (
    if exist "%KEY%.pub.tmp" del /q "%KEY%.pub.tmp" >nul 2>&1
    echo ERROR: The dedicated Alpha private key exists but is not readable.
    echo It was NOT overwritten. Fix or replace only %KEY% and rerun this same setup.
    pause
    exit /b 23
  )
  move /y "%KEY%.pub.tmp" "%KEY%.pub" >nul
)

set "KEYSSH=%KEY:\=/%"
set "GIT_SSH_COMMAND=ssh -i '%KEYSSH%' -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=8 -p 22"

echo [1/4] Checking GitHub SSH port 22 authorization...
"%GITEXE%" ls-remote "%REMOTE%" HEAD >nul 2>&1
if not errorlevel 1 goto ALPHA_SSH_READY

echo.
echo ONE-TIME GitHub authorization is required.
powershell.exe -NoProfile -Command "try { Get-Content -LiteralPath '%KEY%.pub' -Raw ^| Set-Clipboard } catch {}" >nul 2>&1
echo The dedicated Alpha public key was copied to the clipboard.
echo On GitHub, add it as an Authentication Key with title:
echo   WOF Alpha updater
echo.
start "" "https://github.com/settings/ssh/new" >nul 2>&1
echo This setup will detect authorization automatically.
echo.
set /a WOF_WAIT=0

:WAIT_FOR_ALPHA_SSH
timeout /t 3 /nobreak >nul
"%GITEXE%" ls-remote "%REMOTE%" HEAD >nul 2>&1
if not errorlevel 1 goto ALPHA_SSH_READY
set /a WOF_WAIT+=1
if %WOF_WAIT% GEQ 200 goto ALPHA_SSH_FAILED
<nul set /p "=."
goto WAIT_FOR_ALPHA_SSH

:ALPHA_SSH_READY
echo.
echo SSH22_AUTO_UPDATE_READY

echo [2/4] Bootstrapping the managed Alpha repo...
if not exist "%BASE%" mkdir "%BASE%" >nul 2>&1
if exist "%REPO%" if not exist "%REPO%\.git" (
  echo Removing only the incomplete managed Alpha repo directory...
  rmdir /s /q "%REPO%" >nul 2>&1
)
if not exist "%REPO%\.git" (
  if exist "%STAGING%" rmdir /s /q "%STAGING%" >nul 2>&1
  "%GITEXE%" clone --quiet --no-tags --single-branch --branch "%LIVE_BRANCH%" "%REMOTE%" "%STAGING%"
  if errorlevel 1 (
    if exist "%STAGING%" rmdir /s /q "%STAGING%" >nul 2>&1
    echo ERROR: Could not clone controlled Alpha live release over GitHub SSH port 22.
    echo Confirm outbound TCP/22 to github.com is allowed, then rerun this same setup.
    pause
    exit /b 24
  )
  move /y "%STAGING%" "%REPO%" >nul
  if errorlevel 1 (
    echo ERROR: Could not install the managed Alpha repo at:
    echo   %REPO%
    pause
    exit /b 25
  )
)

"%GITEXE%" -C "%REPO%" fetch --quiet "%REMOTE%" "+refs/heads/%LIVE_BRANCH%:refs/remotes/origin/%LIVE_BRANCH%"
if errorlevel 1 (
  echo ERROR: Could not refresh the controlled Alpha live release over SSH port 22.
  pause
  exit /b 28
)
"%GITEXE%" -C "%REPO%" reset --hard "refs/remotes/origin/%LIVE_BRANCH%" >nul
if errorlevel 1 (
  echo ERROR: Could not apply the controlled Alpha live release.
  pause
  exit /b 27
)

echo [3/4] Installing the permanent controller...
set "INSTALLER=%REPO%\parallel\PYLAUNCH\install_live_retest_once.ps1"
if not exist "%INSTALLER%" (
  echo ERROR: The controlled Alpha live release is missing its installer.
  echo No fallback download is required; the release pointer must be repaired.
  pause
  exit /b 26
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%INSTALLER%"
if errorlevel 1 exit /b %ERRORLEVEL%

echo [4/4] Setup complete.
echo From now on, always use Desktop\WOF_ALPHA_TEST.cmd.
exit /b 0

:ALPHA_SSH_FAILED
echo.
echo ERROR: GitHub SSH port 22 authorization was not detected.
echo The dedicated key was preserved and no other .ssh or VPS key was changed.
echo Add %KEY%.pub to GitHub and ensure outbound TCP/22 to github.com is allowed.
echo Then run this SAME WOF_ALPHA_SETUP_ONCE.cmd again.
pause
exit /b 27
