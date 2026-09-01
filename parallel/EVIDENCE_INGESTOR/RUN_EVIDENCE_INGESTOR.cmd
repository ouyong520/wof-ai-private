@echo off
setlocal EnableExtensions
chcp 65001 >nul 2>&1
title WOF 自动结果整理器

for %%I in ("%~dp0.") do set "HERE=%%~fI"
set "PY="
where py >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if defined PY goto :run
where python >nul 2>&1
if not errorlevel 1 set "PY=python"
if defined PY goto :run

echo.
echo 未找到 Python 3。
echo 请先安装 Python 3，然后重新双击本文件。
echo 原始结果和游戏都没有被修改。
pause
exit /b 2

:run
echo.
echo WOF 自动结果整理器
echo ================================================
echo 扫描目录：%%USERPROFILE%%\Documents\WOF_RESULTS
echo 将自动检查 JSON、版本、安全字段、World 921031、重复文件和损坏文件。
echo 原始证据不会被删除、移动或修改。
echo.
%PY% "%HERE%\run.py" --package
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo 整理完成，没有发现阻断级安全/身份异常。
) else if "%RC%"=="1" (
  echo 整理完成，但发现严重安全或身份异常。请查看生成的“结果汇总.txt”。
) else (
  echo 本次整理没有正常完成。请查看上方中文错误说明。
)
echo.
echo 输出目录：%%USERPROFILE%%\Documents\WOF_RESULTS\_自动整理
pause
exit /b %RC%
