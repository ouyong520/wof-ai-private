@echo off
setlocal
chcp 65001 >nul 2>nul
title WOF 项目状态扫描器

set "HERE=%~dp0"
set "PYEXE="

where py >nul 2>nul
if not errorlevel 1 set "PYEXE=py -3"

if not defined PYEXE (
  where python >nul 2>nul
  if not errorlevel 1 set "PYEXE=python"
)

if not defined PYEXE (
  echo.
  echo [错误] 未检测到 Python 3。
  echo 请先安装 Python 3，或从 WOF Toolkit 的“更新/准备环境”入口完成环境准备。
  echo 扫描器不会修改游戏、不会写游戏内存。
  echo.
  pause
  exit /b 2
)

echo.
echo WOF 项目状态扫描器
echo 正在只读扫描仓库状态、结果文件和最近提交……
echo.

%PYEXE% "%HERE%scan_project_status.py"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo 扫描完成。
  echo 中文摘要：%HERE%项目状态.txt
  echo 机器状态：%HERE%PROJECT_STATUS.json
) else (
  echo 扫描失败，错误码：%RC%
)
echo.
pause
exit /b %RC%
