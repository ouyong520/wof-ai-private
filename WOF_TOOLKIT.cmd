@echo off
setlocal EnableExtensions
title WOF Windows Operator Toolkit

for %%I in ("%~dp0.") do set "ROOT=%%~fI"

:find_root
if exist "%ROOT%\parallel\PYLAUNCH\launcher.py" if exist "%ROOT%\product\alpha" goto :root_ok
for %%I in ("%ROOT%\..") do set "PARENT=%%~fI"
if /I "%PARENT%"=="%ROOT%" goto :bad_root
set "ROOT=%PARENT%"
goto :find_root

:root_ok
if defined LOCALAPPDATA (
  set "VENV=%LOCALAPPDATA%\WOF Toolkit\venv"
) else (
  set "VENV=%TEMP%\WOF_TOOLKIT\venv"
)
set "PYBOOT="

if exist "%VENV%\Scripts\python.exe" goto :deps

where py >nul 2>&1
if not errorlevel 1 set "PYBOOT=py -3"
if defined PYBOOT goto :mkvenv

where python >nul 2>&1
if not errorlevel 1 set "PYBOOT=python"
if defined PYBOOT goto :mkvenv

echo.
echo WOF Toolkit could not find Python 3.
echo Install Python 3, then double-click WOF_TOOLKIT.cmd again.
echo Nothing in the game or project was changed.
pause
exit /b 1

:mkvenv
echo Preparing WOF Toolkit Python environment...
%PYBOOT% -m venv "%VENV%"
if errorlevel 1 goto :venv_fail

:deps
"%VENV%\Scripts\python.exe" -m pip install --disable-pip-version-check -r "%ROOT%\parallel\PYLAUNCH\requirements.txt"
if errorlevel 1 goto :deps_fail
if exist "%ROOT%\parallel\WOF052L_RECORDER\requirements.txt" (
  "%VENV%\Scripts\python.exe" -m pip install --disable-pip-version-check -r "%ROOT%\parallel\WOF052L_RECORDER\requirements.txt"
  if errorlevel 1 goto :deps_fail
)

cd /d "%ROOT%"
"%VENV%\Scripts\python.exe" "%ROOT%\parallel\OPTOOLKIT\toolkit.py" --root "%ROOT%"
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo.
  echo WOF Toolkit exited with code %RC%.
  echo No game RAM write or gameplay input was attempted by Toolkit.
  pause
)
exit /b %RC%

:bad_root
echo.
echo WOF Toolkit could not locate the WOF project folder.
echo Keep WOF_TOOLKIT.cmd inside the project checkout and try again.
pause
exit /b 2

:venv_fail
echo.
echo Python was found, but Toolkit could not create its environment.
echo Your game and project files were not changed.
pause
exit /b 3

:deps_fail
echo.
echo Toolkit could not install/update the existing WOF Python dependencies.
echo Check Internet access and Python/pip, then run WOF_TOOLKIT.cmd again.
echo Your game and project files were not changed.
pause
exit /b 4
