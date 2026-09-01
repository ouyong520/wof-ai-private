@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"

echo WOF-052L 自动分析器
echo 只读分析 / 游戏内存写入 0 / 不注入输入 / 不自动晋级生产规则
echo.

where py >nul 2>nul
if not errorlevel 1 (
  set "PY=py -3"
) else (
  where python >nul 2>nul
  if not errorlevel 1 (
    set "PY=python"
  ) else (
    echo 错误：没有找到 Python 3。请先安装 Python 3，或从 WOF Toolkit 启动已配置环境。
    pause
    exit /b 1
  )
)

if "%~1"=="" (
  echo 正在自动读取 WOF-052L Recorder 已保存的目录，并持续监控新的 JSON。
  echo 结束时按 Ctrl+C。
  echo.
  %PY% "%~dp0analyzer.py" --watch
) else (
  %PY% "%~dp0analyzer.py" %*
)

if errorlevel 1 (
  echo.
  echo 分析器异常结束。请查看上面的中文错误说明。
  pause
)
endlocal
