@echo off
setlocal
cd /d "%~dp0"
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY (
  echo [错误] 未找到 Python。请先使用 WOF Toolkit 安装/准备 Python 环境。
  pause
  exit /b 2
)
if "%~1"=="" (
  echo 用法：把候选 manifest JSON 拖到本文件上，或执行：
  echo RUN_PROSPECTIVE_VALIDATOR.cmd candidate.json
  pause
  exit /b 2
)
%PY% live_validator.py "%~1"
set "RC=%ERRORLEVEL%"
echo.
if "%RC%"=="0" (
  echo 前瞻验证流程已结束，结果保存在 parallel\PROSPECTIVE_VALIDATOR\results\
) else (
  echo 前瞻验证未完成，错误码 %RC%。上方信息不会影响游戏运行。
)
pause
exit /b %RC%
