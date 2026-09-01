@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo WOF HUDANCHOR 一键 Browser Proof
echo 只读模式 / RAM 写入 0 / 不注入输入
echo ========================================
where py >nul 2>nul && (set "PY=py -3") || (set "PY=python")
%PY% --version >nul 2>nul || (
  echo [失败] 未找到 Python。请先运行现有 WOF Toolkit / PYLAUNCH 环境准备。
  pause
  exit /b 2
)
%PY% hudanchor_proof_safe.py
set "RC=%ERRORLEVEL%"
echo.
if "%RC%"=="0" (
  echo [PASS] 自动 proof 已通过。
) else (
  echo [未通过/待闭合] 已 fail-closed，不会伪造 PASS。
)
echo 结果文件: %~dp0results\HUDANCHOR_PROOF.json
pause
exit /b %RC%
