@echo off
setlocal EnableExtensions
chcp 65001 >nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
cd /d "%~dp0"
title WOF-052L 自动多房间采集器

set "PYEXE="
set "PIPLOG=.venv\pip_install.log"
where py >nul 2>nul && set "PYEXE=py -3"
if not defined PYEXE (
  where python >nul 2>nul && set "PYEXE=python"
)
if not defined PYEXE (
  echo.
  echo 未找到 Python 3，暂时无法启动 WOF-052L 采集器。
  echo 游戏本身没有受到影响。
  echo 请安装 Python 3.11 或更高版本，然后重新双击本文件。
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo 首次使用：正在创建 WOF-052L 专用 Python 环境……
  %PYEXE% -m venv ".venv"
  if errorlevel 1 goto :fail
)

".venv\Scripts\python.exe" -c "import websocket" >nul 2>nul
if errorlevel 1 (
  echo 首次使用：正在安装浏览器连接依赖 websocket-client……
  ".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r requirements.txt >"%PIPLOG%" 2>&1
  if errorlevel 1 goto :fail
)

echo.
echo WOF-052L 自动多房间采集器
echo 只读模式：开启  ^|  游戏内存写入：0  ^|  游戏输入注入：无
echo.
".venv\Scripts\python.exe" owner_zh_cn.py %*
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo.
  echo WOF-052L 采集器没有正常完成，退出代码：%RC%。
  echo 游戏本身没有受到影响，也没有进行游戏内存写入或输入注入。
  pause
)
exit /b %RC%

:fail
echo.
echo WOF-052L 初始环境准备失败。
echo 游戏和浏览器没有被修改。
echo 请检查 Python/pip 和网络连接后重新双击本文件。
if exist "%PIPLOG%" echo 技术详情已保存：%CD%\%PIPLOG%
pause
exit /b 1
