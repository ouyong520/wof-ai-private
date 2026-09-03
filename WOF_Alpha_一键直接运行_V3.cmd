@echo off
setlocal EnableExtensions
chcp 65001 >nul 2>&1
title WOF Alpha 一键直接运行 V3

set "PS1=%~dp0parallel\PYLAUNCH\start_alpha_current_main.ps1"
if not exist "%PS1%" (
  echo.
  echo 启动脚本缺失：
  echo %PS1%
  echo.
  echo 请先在 GitHub Desktop 点 Pull origin 更新项目。
  echo 然后再双击本文件。
  echo.
  pause
  exit /b 90
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%PS1%"
set "RC=%ERRORLEVEL%"

echo.
if not "%RC%"=="0" (
  echo WOF Alpha 返回错误代码：%RC%
  echo 请把这个窗口截图发给 ChatGPT。
)
echo.
pause
exit /b %RC%
