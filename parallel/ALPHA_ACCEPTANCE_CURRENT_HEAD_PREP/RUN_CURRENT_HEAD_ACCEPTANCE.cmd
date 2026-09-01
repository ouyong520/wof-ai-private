@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0\..\.."

echo WOF Alpha Current-HEAD 有界验收
echo.
python "parallel\ALPHA_ACCEPTANCE_CURRENT_HEAD_PREP\acceptance_orchestrator.py" --output "parallel\ALPHA_ACCEPTANCE_CURRENT_HEAD_PREP\acceptance_result.json"
set "RC=%ERRORLEVEL%"
echo.
if "%RC%"=="0" (
  echo 验收命令完成。请保留 acceptance_result.json。
) else if "%RC%"=="3" (
  echo 当前被 release gate 或 Browser attestation 阻断；不要绕过门槛。
) else (
  echo 验收未通过或证据不完整。请保留第一次有效结果，不要反复重试碰运气。
)
echo.
pause
exit /b %RC%
