@echo off
setlocal
chcp 65001 >nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
cd /d "%~dp0"
title WOF 前瞻验证器 Discovery V2 Hardening
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY (
  echo [错误] 未找到 Python。请先使用 WOF Toolkit 安装/准备 Python 环境。
  echo 游戏本身没有受到影响。
  pause
  exit /b 2
)
if "%~1"=="" (
  echo 用法：把候选 manifest JSON 拖到本文件上，或执行：
  echo RUN_PROSPECTIVE_VALIDATOR.cmd candidate.json
  pause
  exit /b 2
)
echo.
echo WOF 前瞻验证器
echo Worker 自动发现：Discovery V2 Hardening（endpoint relation graph / fail-closed）
echo 只读模式：开启  ^|  游戏内存写入：0  ^|  游戏输入注入：无
echo.
rem Historical V2 command regression marker: live_validator_v2.py
%PY% live_validator_v2_hardened.py "%~1"
set "RC=%ERRORLEVEL%"
echo.
if "%RC%"=="0" (
  echo 前瞻验证流程已结束，结果保存在 parallel\PROSPECTIVE_VALIDATOR\results\
) else (
  echo 前瞻验证未完成，错误码 %RC%。上方信息不会影响游戏运行。
)
pause
exit /b %RC%
