@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"

title WOF 一键真人验证
set "VENV=.venv"
set "PYBOOT="

echo.
echo ========================================
echo   WOF Python Launcher 一键真人验证
echo ========================================
echo 只读模式：开启
echo 游戏内存写入：0
echo 输入注入：关闭
echo.

if exist "%VENV%\Scripts\python.exe" goto :deps
where py >nul 2>&1
if not errorlevel 1 set "PYBOOT=py -3"
if defined PYBOOT goto :mkvenv
where python >nul 2>&1
if not errorlevel 1 set "PYBOOT=python"
if defined PYBOOT goto :mkvenv

echo 未找到 Python 3，无法启动 WOF Launcher。
echo 游戏和浏览器本身没有受到影响。
echo 请先安装 Python 3，然后重新双击本文件。
pause
exit /b 1

:mkvenv
echo 正在准备 WOF Launcher 运行环境...
%PYBOOT% -m venv "%VENV%"
if errorlevel 1 goto :fail

:deps
"%VENV%\Scripts\python.exe" -c "import websocket, pystray, PIL" >nul 2>&1
if errorlevel 1 (
  echo 正在安装 Launcher 必需组件...
  "%VENV%\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
  if errorlevel 1 goto :fail
)

del /q "WINDOWS_PROOF_STATUS.json" >nul 2>&1
start "" "%VENV%\Scripts\pythonw.exe" launcher.py --proof-json "%CD%\WINDOWS_PROOF_STATUS.json"
timeout /t 2 /nobreak >nul
if not exist "WINDOWS_PROOF_STATUS.json" goto :fail

echo.
echo Launcher 已启动。
echo 请在自动打开的专用 Chrome/Edge 中正常进入 WOF 房间。
echo 不需要打开 DevTools，不需要选择 Worker Console，也不需要粘贴 JavaScript。
echo.
echo 右下角 WOF 托盘图标会自动显示：
echo   浏览器 / WOF 页面 / Worker / WASM 内存 / World 921031
echo.
echo 这个窗口现在可以关闭。
exit /b 0

:fail
echo.
echo WOF Launcher 准备或启动失败。
echo 游戏和浏览器本身没有被修改或关闭。
echo 如果目录中已经生成 WINDOWS_PROOF_STATUS.json，只需要把这个文件发回来。
pause
exit /b 1
