@echo off
setlocal EnableExtensions DisableDelayedExpansion
set "ROOT=%~dp0..\.."
where py.exe >nul 2>&1
if not errorlevel 1 (
  py -3 "%~dp0owner_release_gate.py" run --repo-root "%ROOT%"
) else (
  python "%~dp0owner_release_gate.py" run --repo-root "%ROOT%"
)
set "RC=%ERRORLEVEL%"
echo.
if "%RC%"=="0" echo Final visual receipt and promotion plan are ready. alpha-live was NOT moved.
if not "%RC%"=="0" echo Final release gate stopped fail-closed. alpha-live was NOT moved.
exit /b %RC%
