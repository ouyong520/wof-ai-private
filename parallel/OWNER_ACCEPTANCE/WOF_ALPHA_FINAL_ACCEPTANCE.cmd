@echo off
setlocal
chcp 65001 >nul 2>nul
set "SCRIPT_DIR=%~dp0"
set "ORCHESTRATOR=%SCRIPT_DIR%final_acceptance_orchestrator.py"

echo [Alpha 最终验收]
echo 1. 请启动或保持 WOF 正常运行。
echo 2. 接下来只需正常游玩，不需要打开开发者工具、不需要校准、不需要选择坐标。
echo 3. 自动采样完成后，请看屏幕确认提示是否稳定跟随正确人物。
echo.

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 "%ORCHESTRATOR%" --invoke-w3
) else (
  python "%ORCHESTRATOR%" --invoke-w3
)
set "RC=%ERRORLEVEL%"
echo.
if not "%RC%"=="0" echo 验收编排未正常完成，请保留输出给维护者诊断。
pause
exit /b %RC%
