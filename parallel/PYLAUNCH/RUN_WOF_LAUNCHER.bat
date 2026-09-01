@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
title WOF Python Launcher

if not exist ".venv\Scripts\python.exe" (
  echo 正在创建 WOF Launcher Python 环境...
  py -3 -m venv .venv
  if errorlevel 1 goto :fail
)

echo 正在检查 Launcher 依赖...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :fail

".venv\Scripts\python.exe" launcher.py
exit /b %errorlevel%

:fail
echo.
echo WOF Launcher 准备或启动失败。
echo 游戏和浏览器本身没有受到影响。
pause
exit /b 1
