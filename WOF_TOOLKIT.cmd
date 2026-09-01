@echo off
setlocal EnableExtensions
chcp 65001 >nul 2>&1
title WOF 中文工具箱

for %%I in ("%~dp0.") do set "ROOT=%%~fI"

:find_root
if exist "%ROOT%\parallel\PYLAUNCH\launcher.py" if exist "%ROOT%\parallel\OPTOOLKIT\toolkit.py" goto :root_ok
for %%I in ("%ROOT%\..") do set "PARENT=%%~fI"
if /I "%PARENT%"=="%ROOT%" goto :bad_root
set "ROOT=%PARENT%"
goto :find_root

:root_ok
if exist "%ROOT%\PACKAGE_MANIFEST.json" set "WOF_PACKAGED_MODE=1"
if defined WOF_TOOLKIT_PYTHON if exist "%WOF_TOOLKIT_PYTHON%" set "VENV_PY=%WOF_TOOLKIT_PYTHON%"
if defined VENV_PY goto :deps

if defined LOCALAPPDATA (
  if "%WOF_PACKAGED_MODE%"=="1" (
    set "VENV=%LOCALAPPDATA%\WOF Future Danger\OwnerTools\venv"
  ) else (
    set "VENV=%LOCALAPPDATA%\WOF Toolkit\venv"
  )
) else (
  set "VENV=%TEMP%\WOF_TOOLKIT\venv"
)
set "VENV_PY=%VENV%\Scripts\python.exe"
set "PYBOOT="

if exist "%VENV_PY%" goto :deps
where py >nul 2>&1
if not errorlevel 1 set "PYBOOT=py -3"
if defined PYBOOT goto :mkvenv
where python >nul 2>&1
if not errorlevel 1 set "PYBOOT=python"
if defined PYBOOT goto :mkvenv

echo.
echo 未找到 Python 3。
echo 如果你是从 WOF_一键工具.cmd 进入，请退出后重新双击一键工具，它会尝试自动准备 Python。
echo 游戏本身没有受到影响。
pause
exit /b 1

:mkvenv
echo 正在准备 WOF Python 环境...
%PYBOOT% -m venv "%VENV%"
if errorlevel 1 goto :venv_fail

:deps
"%VENV_PY%" -m pip install --disable-pip-version-check -q -r "%ROOT%\parallel\PYLAUNCH\requirements.txt"
if errorlevel 1 goto :deps_fail
if exist "%ROOT%\parallel\WOF052L_RECORDER\requirements.txt" (
  "%VENV_PY%" -m pip install --disable-pip-version-check -q -r "%ROOT%\parallel\WOF052L_RECORDER\requirements.txt"
  if errorlevel 1 goto :deps_fail
)

cd /d "%ROOT%"
"%VENV_PY%" "%ROOT%\parallel\OPTOOLKIT\toolkit.py" --root "%ROOT%"
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo.
  echo WOF 工具箱已退出，错误代码：%RC%
  echo 游戏本身没有受到影响。
  pause
)
exit /b %RC%

:bad_root
echo.
echo 没有找到完整的 WOF 工具文件。
echo 请重新双击 WOF_一键工具.cmd，它会自动修复或更新工具。
pause
exit /b 2

:venv_fail
echo.
echo 已找到 Python，但创建 WOF Python 环境失败。
echo 游戏本身没有受到影响。
pause
exit /b 3

:deps_fail
echo.
echo Python 依赖准备失败，请检查网络后重新双击 WOF_一键工具.cmd。
echo 旧版本工具和游戏本身没有受到影响。
pause
exit /b 4
