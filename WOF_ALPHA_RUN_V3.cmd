@echo off
setlocal EnableExtensions EnableDelayedExpansion
title WOF_ALPHA_STANDALONE_V3

echo.
echo ================================================
echo WOF_ALPHA_STANDALONE_V3
echo ================================================
echo.

set "REPO="
set "ENTRY="
set "GITEXE="
set "TMPPS=%TEMP%\WOF_ALPHA_BOOT_V3_%RANDOM%_%RANDOM%.ps1"

rem Fast common locations first.
if exist "%~dp0.git" if exist "%~dp0parallel\PYLAUNCH\render_authority_measurement_entry.py" set "REPO=%~dp0"
if not defined REPO if exist "%USERPROFILE%\Documents\GitHub\wof-ai-private\.git" set "REPO=%USERPROFILE%\Documents\GitHub\wof-ai-private"
if not defined REPO if exist "%USERPROFILE%\Desktop\wof-ai-private\.git" set "REPO=%USERPROFILE%\Desktop\wof-ai-private"
if not defined REPO if exist "%USERPROFILE%\Downloads\wof-ai-private\.git" set "REPO=%USERPROFILE%\Downloads\wof-ai-private"
if not defined REPO if exist "%USERPROFILE%\source\repos\wof-ai-private\.git" set "REPO=%USERPROFILE%\source\repos\wof-ai-private"
if not defined REPO if exist "D:\GitHub\wof-ai-private\.git" set "REPO=D:\GitHub\wof-ai-private"
if not defined REPO if exist "E:\GitHub\wof-ai-private\.git" set "REPO=E:\GitHub\wof-ai-private"
if not defined REPO if exist "D:\wof-ai-private\.git" set "REPO=D:\wof-ai-private"
if not defined REPO if exist "E:\wof-ai-private\.git" set "REPO=E:\wof-ai-private"

if defined REPO goto :repo_found

echo Searching for local wof-ai-private checkout using Windows WHERE...
call :search_root "%USERPROFILE%"
if defined REPO goto :repo_found
if exist "D:\" call :search_root "D:\"
if defined REPO goto :repo_found
if exist "E:\" call :search_root "E:\"
if defined REPO goto :repo_found
if exist "F:\" call :search_root "F:\"
if defined REPO goto :repo_found
if exist "G:\" call :search_root "G:\"
if defined REPO goto :repo_found
if exist "C:\" call :search_root "C:\"
if defined REPO goto :repo_found

echo.
echo ERROR: Could not find the local wof-ai-private Git checkout.
echo Open GitHub Desktop and select wof-ai-private once, then run this file again.
echo.
pause
exit /b 90

:search_root
set "SEARCHROOT=%~1"
for /f "delims=" %%F in ('where /r "%SEARCHROOT%" render_authority_measurement_entry.py 2^>nul') do (
  for %%D in ("%%F") do set "ENTRYDIR=%%~dpD"
  for %%R in ("!ENTRYDIR!..\..") do set "CAND=%%~fR"
  if exist "!CAND!\.git" if exist "!CAND!\parallel\PYLAUNCH\render_authority_measurement_entry.py" (
    set "REPO=!CAND!"
    exit /b 0
  )
)
exit /b 0

:repo_found
echo Repo:
echo %REPO%
echo.

rem Find Git without PowerShell.
for /f "delims=" %%G in ('where git.exe 2^>nul') do if not defined GITEXE set "GITEXE=%%G"
if defined GITEXE goto :git_found
if exist "%LOCALAPPDATA%\GitHubDesktop" (
  for /f "delims=" %%G in ('where /r "%LOCALAPPDATA%\GitHubDesktop" git.exe 2^>nul') do if not defined GITEXE set "GITEXE=%%G"
)

:git_found
if not defined GITEXE (
  echo ERROR: Git was not found. Open GitHub Desktop first.
  echo.
  pause
  exit /b 91
)

echo Git:
echo %GITEXE%
echo.

echo Fetching latest main from origin...
"%GITEXE%" -C "%REPO%" fetch --quiet origin +refs/heads/main:refs/remotes/wof-alpha-authority/main
if errorlevel 1 (
  echo.
  echo ERROR: Could not fetch latest main from origin.
  echo Open GitHub Desktop and click Fetch origin, then run this file again.
  echo.
  pause
  exit /b 92
)

"%GITEXE%" -C "%REPO%" show refs/remotes/wof-alpha-authority/main:parallel/PYLAUNCH/start_alpha_current_main.ps1 > "%TMPPS%"
if errorlevel 1 (
  echo.
  echo ERROR: Could not extract the Alpha launcher from latest main.
  echo.
  pause
  exit /b 93
)
if not exist "%TMPPS%" (
  echo.
  echo ERROR: Temporary Alpha launcher was not created.
  echo.
  pause
  exit /b 94
)

echo Starting current-main Alpha...
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%TMPPS%" -Repo "%REPO%"
set "RC=%ERRORLEVEL%"
del /q "%TMPPS%" >nul 2>&1

echo.
echo WOF Alpha launcher exit code: %RC%
echo.
pause
exit /b %RC%
