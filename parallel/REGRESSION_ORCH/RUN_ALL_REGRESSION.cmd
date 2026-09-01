@echo off
setlocal EnableExtensions
chcp 65001 >nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
title WOF 全仓库回归编排器

set "HERE=%~dp0"
set "PYEXE="

where py >nul 2>nul
if not errorlevel 1 set "PYEXE=py -3"

if not defined PYEXE (
  where python >nul 2>nul
  if not errorlevel 1 set "PYEXE=python"
)

if not defined PYEXE (
  echo [受阻] 未找到 Python 3。
  echo 请先通过 WOF Toolkit 准备 Python 环境，然后重新双击本文件。
  exit /b 2
)

echo ============================================================
echo WOF 全仓库离线回归
echo ============================================================
echo 将运行已批准的离线测试；不会自动进入游戏，不会执行真人 Browser proof。
echo.

%PYEXE% "%HERE%orchestrator.py" --repo-root "%HERE%..\.."
set "RC=%ERRORLEVEL%"

echo.
echo ============================================================
if "%RC%"=="0" (
  echo [完成] 仓库侧离线回归已完成。
) else (
  echo [需要查看] 存在失败或受阻项目，请打开中文结果与对应日志。
)
echo JSON：%HERE%REGRESSION_SUMMARY.json
echo 中文结果：%HERE%回归结果.txt
echo ============================================================

exit /b %RC%
