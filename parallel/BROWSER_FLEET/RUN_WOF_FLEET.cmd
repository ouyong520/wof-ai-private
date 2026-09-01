@echo off
setlocal EnableExtensions
chcp 65001 >nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
cd /d "%~dp0"
title WOF 多房间浏览器管理器

set "PYTHON_CMD="
where py >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=py -3"
if not defined PYTHON_CMD (
  where python >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=python"
)
if not defined PYTHON_CMD (
  echo.
  echo 未找到 Python 3，暂时无法启动 WOF 多房间浏览器管理器。
  echo 游戏本身没有受到影响。
  echo 请安装 64 位 Python 3.11 或更高版本，然后重新双击本文件。
  pause
  exit /b 2
)

echo.
echo WOF 多房间浏览器管理器
echo 每个房间使用独立配置和本机 CDP 端口，一个崩溃不会影响其他房间。
echo.
set "COUNT="
set /p COUNT=请输入要打开的浏览器房间数量 [1/5/10，默认 10]：
if "%COUNT%"=="" set "COUNT=10"

echo.
%PYTHON_CMD% fleet_owner_zh_cn.py start %COUNT% --interactive
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo.
  echo 浏览器管理器没有正常完成，退出代码：%RC%。
  echo 游戏本身没有受到影响，也没有进行游戏内存写入或输入注入。
  pause
)
exit /b %RC%
