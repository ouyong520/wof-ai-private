@echo off
setlocal
cd /d "%~dp0"
where node >nul 2>nul
if errorlevel 1 (
  echo [FAIL] 未找到 Node.js，无法运行 Alpha Transport Reference acceptance。
  exit /b 1
)
node run_all.mjs
if errorlevel 1 exit /b 1
echo [PASS] Alpha Transport Reference: selftest PASS, 67/67 contract PASS.
exit /b 0
