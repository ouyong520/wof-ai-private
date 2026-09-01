@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"

set "PYEXE="
where py >nul 2>nul && set "PYEXE=py -3"
if not defined PYEXE (
  where python >nul 2>nul && set "PYEXE=python"
)
if not defined PYEXE (
  echo [WOF-052L] Python 3 was not found.
  echo Install Python 3.11+ and run this CMD again.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo [WOF-052L] First run: creating local Python environment...
  %PYEXE% -m venv ".venv"
  if errorlevel 1 goto :fail
)

".venv\Scripts\python.exe" -c "import websocket" >nul 2>nul
if errorlevel 1 (
  echo [WOF-052L] First run: installing websocket-client...
  ".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
  if errorlevel 1 goto :fail
)

".venv\Scripts\python.exe" fleet_recorder.py %*
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo.
  echo [WOF-052L] Recorder exited with code %RC%.
  pause
)
exit /b %RC%

:fail
echo.
echo [WOF-052L] Setup failed. Game/browser was not modified.
pause
exit /b 1
