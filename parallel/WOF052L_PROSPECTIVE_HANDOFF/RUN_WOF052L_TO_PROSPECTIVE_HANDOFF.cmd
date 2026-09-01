@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY (
  echo [错误] 未找到 Python。请先使用 WOF Toolkit 安装/准备 Python 环境。
  pause
  exit /b 2
)

echo WOF-052L 自动 Discovery -^> Prospective Handoff
echo 只读模式：开启 ^| 游戏内存写入：0 ^| 游戏输入注入：无 ^| Production 自动晋级：禁止
echo.
%PY% handoff.py --watch
set "RC=%ERRORLEVEL%"
echo.
if "%RC%"=="0" (
  echo Handoff 已正常结束。
) else (
  echo Handoff 异常结束，错误码 %RC%。不会影响游戏或其他 Browser Fleet 房间。
)
pause
exit /b %RC%
