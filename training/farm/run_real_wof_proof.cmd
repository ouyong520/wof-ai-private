@echo off
setlocal
cd /d "%~dp0\..\.."
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  py -3 -m training.farm.real_wof_proof_owner_runner %*
  exit /b %ERRORLEVEL%
)
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  python -m training.farm.real_wof_proof_owner_runner %*
  exit /b %ERRORLEVEL%
)
echo WAITING_PREREQUISITE - Python launcher not found.
exit /b 2
