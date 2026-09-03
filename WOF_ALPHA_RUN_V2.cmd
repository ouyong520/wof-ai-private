@echo off
setlocal EnableExtensions DisableDelayedExpansion
title WOF_ALPHA_STANDALONE_V2

echo.
echo ================================================
echo WOF_ALPHA_STANDALONE_V2
echo ================================================
echo.

set "REPO="
set "GITEXE="
set "TMPPS=%TEMP%\WOF_ALPHA_BOOT_%RANDOM%_%RANDOM%.ps1"

if exist "%~dp0.git" if exist "%~dp0parallel\PYLAUNCH\render_authority_measurement_entry.py" set "REPO=%~dp0"
if not defined REPO if exist "%USERPROFILE%\Documents\GitHub\wof-ai-private\.git" set "REPO=%USERPROFILE%\Documents\GitHub\wof-ai-private"
if not defined REPO if exist "%USERPROFILE%\Desktop\wof-ai-private\.git" set "REPO=%USERPROFILE%\Desktop\wof-ai-private"
if not defined REPO if exist "%USERPROFILE%\Downloads\wof-ai-private\.git" set "REPO=%USERPROFILE%\Downloads\wof-ai-private"
if not defined REPO if exist "%USERPROFILE%\source\repos\wof-ai-private\.git" set "REPO=%USERPROFILE%\source\repos\wof-ai-private"
if not defined REPO if exist "D:\GitHub\wof-ai-private\.git" set "REPO=D:\GitHub\wof-ai-private"
if not defined REPO if exist "E:\GitHub\wof-ai-private\.git" set "REPO=E:\GitHub\wof-ai-private"
if not defined REPO if exist "D:\wof-ai-private\.git" set "REPO=D:\wof-ai-private"
if not defined REPO if exist "E:\wof-ai-private\.git" set "REPO=E:\wof-ai-private"

if not defined REPO (
  echo Searching for local wof-ai-private checkout...
  for /f "usebackq delims=" %%P in (`powershell.exe -NoProfile -Command "$ErrorActionPreference='SilentlyContinue'; $roots=@($env:USERPROFILE,'D:\','E:\','F:\','G:\') ^| Where-Object { $_ -and (Test-Path $_) }; foreach($r in $roots){ $hit=Get-ChildItem -LiteralPath $r -Directory -Filter 'wof-ai-private' -Recurse -ErrorAction SilentlyContinue ^| Where-Object { Test-Path (Join-Path $_.FullName '.git') } ^| Select-Object -First 1; if($hit){ Write-Output $hit.FullName; break } }"`) do (
    set "REPO=%%P"
    goto :repo_found
  )
)

:repo_found
if not defined REPO (
  echo.
  echo ERROR: Could not find the local wof-ai-private Git checkout.
  echo Open GitHub Desktop and select wof-ai-private once, then run this file again.
  echo.
  pause
  exit /b 90
)

echo Repo:
echo %REPO%
echo.

for /f "delims=" %%G in ('where git.exe 2^>nul') do if not defined GITEXE set "GITEXE=%%G"
if not defined GITEXE (
  for /f "usebackq delims=" %%G in (`powershell.exe -NoProfile -Command "$r=Join-Path $env:LOCALAPPDATA 'GitHubDesktop'; if(Test-Path $r){ $g=Get-ChildItem -LiteralPath $r -Filter git.exe -Recurse -ErrorAction SilentlyContinue ^| Where-Object { $_.FullName -match '\\resources\\app\\git\\cmd\\git\.exe$' } ^| Select-Object -First 1; if($g){Write-Output $g.FullName} }"`) do (
    set "GITEXE=%%G"
    goto :git_found
  )
)

:git_found
if not defined GITEXE (
  echo.
  echo ERROR: Git was not found. Open GitHub Desktop first.
  echo.
  pause
  exit /b 91
)

echo Git:
echo %GITEXE%
echo.
echo Fetching latest main...
"%GITEXE%" -C "%REPO%" fetch --quiet https://github.com/ouyong520/wof-ai-private.git +refs/heads/main:refs/remotes/wof-alpha-authority/main
if errorlevel 1 (
  echo.
  echo ERROR: Could not fetch latest main.
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
