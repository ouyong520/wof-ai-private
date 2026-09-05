@echo off
setlocal EnableExtensions
set "HERE=%~dp0"
set "INPUT=%~1"
if not defined INPUT set "INPUT=%WOF_ALPHA_P22_INPUT%"
set "OUTPUT=%~2"
if not defined OUTPUT set "OUTPUT=%USERPROFILE%\Documents\WOF_RESULTS"

if not defined INPUT (
  echo P22_FAIL_CLOSED: same-session canonical evidence bundle was not supplied by P21/P17.
  echo This wrapper does not ask the Owner to create coordinates, edit JSON, or classify HIT/DOWN/JUMP/DEATH.
  exit /b 2
)

where py >nul 2>nul
if not errorlevel 1 (
  py -3 "%HERE%dynamic_actor_state_coverage.py" --input "%INPUT%" --output-dir "%OUTPUT%"
  exit /b %ERRORLEVEL%
)

where python >nul 2>nul
if errorlevel 1 (
  echo P22_FAIL_CLOSED: Python 3 was not found.
  exit /b 2
)
python "%HERE%dynamic_actor_state_coverage.py" --input "%INPUT%" --output-dir "%OUTPUT%"
exit /b %ERRORLEVEL%
