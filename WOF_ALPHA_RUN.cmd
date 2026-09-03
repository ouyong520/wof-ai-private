@echo off
setlocal EnableExtensions DisableDelayedExpansion
title WOF_ALPHA_ASCII_LAUNCHER_V2

echo.
echo ================================================
echo WOF_ALPHA_ASCII_LAUNCHER_V2
echo ================================================
echo.

set "SCRIPT="

if exist "%~dp0parallel\PYLAUNCH\start_alpha_current_main.ps1" set "SCRIPT=%~dp0parallel\PYLAUNCH\start_alpha_current_main.ps1"
if not defined SCRIPT if exist "%USERPROFILE%\Documents\GitHub\wof-ai-private\parallel\PYLAUNCH\start_alpha_current_main.ps1" set "SCRIPT=%USERPROFILE%\Documents\GitHub\wof-ai-private\parallel\PYLAUNCH\start_alpha_current_main.ps1"
if not defined SCRIPT if exist "%USERPROFILE%\Desktop\wof-ai-private\parallel\PYLAUNCH\start_alpha_current_main.ps1" set "SCRIPT=%USERPROFILE%\Desktop\wof-ai-private\parallel\PYLAUNCH\start_alpha_current_main.ps1"
if not defined SCRIPT if exist "%USERPROFILE%\Downloads\wof-ai-private\parallel\PYLAUNCH\start_alpha_current_main.ps1" set "SCRIPT=%USERPROFILE%\Downloads\wof-ai-private\parallel\PYLAUNCH\start_alpha_current_main.ps1"
if not defined SCRIPT if exist "%USERPROFILE%\source\repos\wof-ai-private\parallel\PYLAUNCH\start_alpha_current_main.ps1" set "SCRIPT=%USERPROFILE%\source\repos\wof-ai-private\parallel\PYLAUNCH\start_alpha_current_main.ps1"
if not defined SCRIPT if exist "D:\GitHub\wof-ai-private\parallel\PYLAUNCH\start_alpha_current_main.ps1" set "SCRIPT=D:\GitHub\wof-ai-private\parallel\PYLAUNCH\start_alpha_current_main.ps1"
if not defined SCRIPT if exist "E:\GitHub\wof-ai-private\parallel\PYLAUNCH\start_alpha_current_main.ps1" set "SCRIPT=E:\GitHub\wof-ai-private\parallel\PYLAUNCH\start_alpha_current_main.ps1"
if not defined SCRIPT if exist "D:\wof-ai-private\parallel\PYLAUNCH\start_alpha_current_main.ps1" set "SCRIPT=D:\wof-ai-private\parallel\PYLAUNCH\start_alpha_current_main.ps1"
if not defined SCRIPT if exist "E:\wof-ai-private\parallel\PYLAUNCH\start_alpha_current_main.ps1" set "SCRIPT=E:\wof-ai-private\parallel\PYLAUNCH\start_alpha_current_main.ps1"

if not defined SCRIPT (
  echo Searching for the local wof-ai-private checkout...
  for /f "usebackq delims=" %%P in (`powershell.exe -NoProfile -Command "$ErrorActionPreference='SilentlyContinue'; $roots=@($env:USERPROFILE,'D:\','E:\','F:\','G:\') ^| Where-Object { $_ -and (Test-Path $_) }; foreach($r in $roots){ $hit=Get-ChildItem -LiteralPath $r -Filter start_alpha_current_main.ps1 -File -Recurse -ErrorAction SilentlyContinue ^| Where-Object { $_.FullName -like '*\wof-ai-private\parallel\PYLAUNCH\start_alpha_current_main.ps1' } ^| Select-Object -First 1; if($hit){ Write-Output $hit.FullName; break } }"`) do (
    set "SCRIPT=%%P"
    goto :found
  )
)

:found
if not defined SCRIPT (
  echo.
  echo ERROR: Could not find the local wof-ai-private Git checkout.
  echo Open GitHub Desktop once and select wof-ai-private, then run this file again.
  echo.
  pause
  exit /b 90
)

echo Found launcher:
echo %SCRIPT%
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT%"
set "RC=%ERRORLEVEL%"

echo.
echo WOF Alpha launcher exit code: %RC%
echo.
pause
exit /b %RC%
