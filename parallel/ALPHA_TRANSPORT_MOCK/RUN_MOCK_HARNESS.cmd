@echo off
setlocal
cd /d "%~dp0"
where node >nul 2>nul
if errorlevel 1 (
  echo [FAIL] Node.js was not found. Install Node.js and run again.
  exit /b 1
)
node harness.mjs
if errorlevel 1 (
  echo [FAIL] Alpha transport mock harness failed. See result.json.
  exit /b 1
)
echo [PASS] Alpha transport mock harness: 67/67.
exit /b 0
