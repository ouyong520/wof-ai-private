@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "VENV=.venv"
set "PYBOOT="

if exist "%VENV%\Scripts\python.exe" goto :deps

where py >nul 2>&1
if not errorlevel 1 set "PYBOOT=py -3"
if defined PYBOOT goto :mkvenv

where python >nul 2>&1
if not errorlevel 1 set "PYBOOT=python"
if defined PYBOOT goto :mkvenv

echo.
echo WOF Windows proof could not find Python 3.
echo Nothing was changed in the game or browser.
pause
exit /b 1

:mkvenv
%PYBOOT% -m venv "%VENV%"
if errorlevel 1 goto :fail

:deps
"%VENV%\Scripts\python.exe" -c "import websocket, pystray, PIL" >nul 2>&1
if errorlevel 1 (
  "%VENV%\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
  if errorlevel 1 goto :fail
)

del /q "WINDOWS_PROOF_STATUS.json" >nul 2>&1
start "" "%VENV%\Scripts\pythonw.exe" launcher.py --proof-json "%CD%\WINDOWS_PROOF_STATUS.json"

timeout /t 2 /nobreak >nul
if not exist "WINDOWS_PROOF_STATUS.json" goto :fail

exit /b 0

:fail
echo.
echo WOF Windows proof launcher setup/start failed.
echo The base game/browser was not modified or closed.
echo If WINDOWS_PROOF_STATUS.json exists, return that one file.
pause
exit /b 1
