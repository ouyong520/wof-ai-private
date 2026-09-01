@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv
  if errorlevel 1 goto :fail
)

".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :fail

".venv\Scripts\python.exe" launcher.py
exit /b %errorlevel%

:fail
echo.
echo WOF Launcher setup/start failed. The game/browser was not modified.
pause
exit /b 1
