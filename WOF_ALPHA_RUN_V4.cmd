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

if defined LOCALAPPDATA (
  set "BASE=%LOCALAPPDATA%\WOF_ALPHA_CURRENT_MAIN"
) else (
  set "BASE=%USERPROFILE%\WOF_ALPHA_CURRENT_MAIN"
)
set "REPO=%BASE%\repo"
set "REMOTE=https://github.com/ouyong520/wof-ai-private.git"

if not exist "%BASE%" mkdir "%BASE%" >nul 2>&1

echo Git:
echo %GITEXE%
echo Managed repo:
echo %REPO%
echo.

if not exist "%REPO%\.git" goto :first_clone
goto :update_repo

:first_clone
echo First run: downloading the Alpha source...
echo A GitHub sign-in window may appear once.
echo.
"%GITEXE%" clone --origin origin --branch main --single-branch "%REMOTE%" "%REPO%"
if errorlevel 1 (
  echo.
  echo ERROR: Could not download the private GitHub repository.
  echo If a GitHub sign-in window appeared, sign in and run this file again.
  echo.
  pause
  exit /b 92
)
goto :repo_ready

:update_repo
echo Updating managed Alpha source to latest main...
"%GITEXE%" -C "%REPO%" remote set-url origin "%REMOTE%" >nul 2>&1
"%GITEXE%" -C "%REPO%" fetch --quiet origin main
if errorlevel 1 (
  echo.
  echo ERROR: Could not fetch latest main from GitHub.
  echo Check the network or GitHub sign-in and run again.
  echo.
  pause
  exit /b 93
)
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
  echo ERROR: Current main does not contain the Alpha launcher script.
  echo.
  pause
  exit /b 95
)
if not exist "%REPO%\parallel\PYLAUNCH\render_authority_measurement_entry.py" (
  echo.
  echo ERROR: Current main does not contain the Alpha runtime entry.
  echo.
  pause
  exit /b 96
)

echo Exact main:
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
