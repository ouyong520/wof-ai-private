@echo off
setlocal
chcp 65001 >nul 2>nul
cd /d "%~dp0\..\.."

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  py -3 -m training.farm.beginner_real_wof_launcher %*
  set "WOF_BEGINNER_RC=%ERRORLEVEL%"
  goto :done
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  python -m training.farm.beginner_real_wof_launcher %*
  set "WOF_BEGINNER_RC=%ERRORLEVEL%"
  goto :done
)

echo ========================================================================
echo Training Farm R0.4 小白实机证明 / Beginner Real-WOF Proof
echo ========================================================================
echo WAITING_PREREQUISITE - 未找到 Python / Python launcher not found.
echo 请先安装当前 Training Farm 支持的 Python 3.10..3.14，然后重新双击本文件。
echo 本 launcher 不会自动下载 ROM、BIOS 或专有游戏资源。
set "WOF_BEGINNER_RC=2"

:done
echo.
if not defined WOF_BEGINNER_NO_PAUSE pause
exit /b %WOF_BEGINNER_RC%
