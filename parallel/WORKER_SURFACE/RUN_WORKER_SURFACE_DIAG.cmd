@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"
title WOF Worker Surface 一键诊断

echo.
echo ============================================================
echo WOF Chrome Worker Surface 一键只读诊断
echo ============================================================
echo 不需要 DevTools，不需要选择 Worker，不需要粘贴 JS。
echo 诊断不会写游戏 RAM，不会注入游戏输入，不会替换 Worker。
echo.

set "PYBOOT="
where py >nul 2>nul
if not errorlevel 1 set "PYBOOT=py -3"
if defined PYBOOT goto :python_ok
where python >nul 2>nul
if not errorlevel 1 set "PYBOOT=python"
if defined PYBOOT goto :python_ok

echo [失败] 未找到 Python 3。
echo 请先安装 64 位 Python 3.11+，然后重新双击本文件。
pause
exit /b 1

:python_ok
if not exist ".venv\Scripts\python.exe" (
  echo [首次运行] 正在创建诊断环境……
  %PYBOOT% -m venv ".venv"
  if errorlevel 1 goto :setup_fail
)

".venv\Scripts\python.exe" -c "import websocket" >nul 2>nul
if errorlevel 1 (
  echo [首次运行] 正在安装最小诊断依赖……
  ".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
  if errorlevel 1 goto :setup_fail
)

del /q "WORKER_SURFACE_DIAG.json" >nul 2>nul
echo.
echo 如果自动打开浏览器，请正常进入 WOF 房间。
echo 进入后不用做额外操作，工具会自动完成采集。
echo.

".venv\Scripts\python.exe" worker_surface_diag.py --output "%CD%\WORKER_SURFACE_DIAG.json"
set "RC=%ERRORLEVEL%"

echo.
if exist "WORKER_SURFACE_DIAG.json" (
  echo ============================================================
  echo 诊断文件已经生成：
  echo %CD%\WORKER_SURFACE_DIAG.json
  echo.
  echo 只需要把这个 JSON 文件发回即可。
  echo ============================================================
) else (
  echo [失败] 没有生成诊断 JSON。
)
pause
exit /b %RC%

:setup_fail
echo.
echo [失败] 诊断环境准备失败。
echo 游戏和浏览器没有被修改。
pause
exit /b 2
