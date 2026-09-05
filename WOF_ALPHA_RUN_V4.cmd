@echo off
setlocal EnableExtensions DisableDelayedExpansion
title WOF_ALPHA_STANDALONE_V4

echo.
echo ================================================
echo WOF_ALPHA_STANDALONE_V4
echo ================================================
echo.

set "GITEXE="
for /f "delims=" %%G in ('where git.exe 2^>nul') do if not defined GITEXE set "GITEXE=%%G"
if not defined GITEXE (
  echo ERROR: Git was not found.
  echo Install or open GitHub Desktop, then run this file again.
  echo.
  pause
  exit /b 91
)

set "SSHEXE="
for /f "delims=" %%S in ('where ssh.exe 2^>nul') do if not defined SSHEXE set "SSHEXE=%%S"
if not defined SSHEXE if exist "C:\Program Files\Git\usr\bin\ssh.exe" set "SSHEXE=C:\Program Files\Git\usr\bin\ssh.exe"
if not defined SSHEXE if exist "C:\Program Files\Git\bin\ssh.exe" set "SSHEXE=C:\Program Files\Git\bin\ssh.exe"

if defined LOCALAPPDATA (
  set "BASE=%LOCALAPPDATA%\WOF_ALPHA_CURRENT_MAIN"
) else (
  set "BASE=%USERPROFILE%\WOF_ALPHA_CURRENT_MAIN"
)
set "REPO=%BASE%\repo"
set "REMOTE_SSH=git@github.com:ouyong520/wof-ai-private.git"
set "REMOTE_HTTPS=https://github.com/ouyong520/wof-ai-private.git"

if not exist "%BASE%" mkdir "%BASE%" >nul 2>&1

echo Git:
echo %GITEXE%
echo Managed repo:
echo %REPO%
if defined SSHEXE (
  echo Update transport: SSH port 22 preferred
) else (
  echo Update transport: SSH client not found; cached source will be used if HTTPS is unavailable
)
echo.

if not exist "%REPO%\.git" goto :first_clone
goto :update_repo

:first_clone
echo First run: downloading the Alpha source...
set "CLONE_OK="
if defined SSHEXE (
  echo Trying GitHub SSH on port 22...
  set "GIT_SSH_COMMAND=%SSHEXE% -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=accept-new"
  "%GITEXE%" clone --origin origin --branch main --single-branch "%REMOTE_SSH%" "%REPO%"
  if not errorlevel 1 set "CLONE_OK=1"
  set "GIT_SSH_COMMAND="
)
if not defined CLONE_OK (
  echo SSH clone did not succeed. Trying HTTPS once...
  "%GITEXE%" -c http.version=HTTP/1.1 clone --origin origin --branch main --single-branch "%REMOTE_HTTPS%" "%REPO%"
  if not errorlevel 1 set "CLONE_OK=1"
)
if not defined CLONE_OK (
  echo.
  echo ERROR: First download could not complete over SSH 22 or HTTPS.
  echo The first install needs one working GitHub transport.
  echo.
  pause
  exit /b 92
)
goto :repo_ready

:update_repo
echo Updating managed Alpha source to latest main...
set "FETCH_OK="
set "FETCH_TRANSPORT="

if defined SSHEXE (
  echo Trying GitHub SSH on port 22...
  set "GIT_SSH_COMMAND=%SSHEXE% -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=accept-new"
  "%GITEXE%" -C "%REPO%" fetch --quiet "%REMOTE_SSH%" "+refs/heads/main:refs/remotes/origin/main"
  if not errorlevel 1 (
    set "FETCH_OK=1"
    set "FETCH_TRANSPORT=SSH22"
    "%GITEXE%" -C "%REPO%" remote set-url origin "%REMOTE_SSH%" >nul 2>&1
  )
  set "GIT_SSH_COMMAND="
)

if not defined FETCH_OK (
  echo SSH 22 update did not succeed.
  echo Trying HTTPS 443 once as fallback...
  "%GITEXE%" -c http.version=HTTP/1.1 -C "%REPO%" fetch --quiet "%REMOTE_HTTPS%" "+refs/heads/main:refs/remotes/origin/main"
  if not errorlevel 1 (
    set "FETCH_OK=1"
    set "FETCH_TRANSPORT=HTTPS443"
    "%GITEXE%" -C "%REPO%" remote set-url origin "%REMOTE_HTTPS%" >nul 2>&1
  )
)

if not defined FETCH_OK (
  echo.
  echo WARNING: GitHub update is unavailable on both SSH 22 and HTTPS 443.
  echo Using the last cached Alpha source so testing can continue.
  echo No redownload is required.
  echo.
  goto :repo_ready
)

echo Update transport used: %FETCH_TRANSPORT%
"%GITEXE%" -C "%REPO%" reset --hard origin/main >nul
if errorlevel 1 (
  echo.
  echo ERROR: Could not update the managed Alpha source.
  echo.
  pause
  exit /b 94
)

:repo_ready
if not exist "%REPO%\parallel\PYLAUNCH\start_alpha_current_main.ps1" (
  echo.
  echo ERROR: Current cached source does not contain the Alpha launcher script.
  echo.
  pause
  exit /b 95
)
if not exist "%REPO%\parallel\PYLAUNCH\render_authority_measurement_entry.py" (
  echo.
  echo ERROR: Current cached source does not contain the Alpha runtime entry.
  echo.
  pause
  exit /b 96
)

echo Running commit:
"%GITEXE%" -C "%REPO%" rev-parse --verify HEAD
if errorlevel 1 (
  echo ERROR: Could not read managed repo HEAD.
  pause
  exit /b 97
)
echo.
echo Starting WOF Alpha...
echo Keep the game open.
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%REPO%\parallel\PYLAUNCH\start_alpha_current_main.ps1" -Repo "%REPO%"
set "RC=%ERRORLEVEL%"

echo.
echo WOF Alpha launcher exit code: %RC%
echo.
pause
exit /b %RC%
