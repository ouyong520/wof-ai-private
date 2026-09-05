@echo off
setlocal
set "HERE=%~dp0"
where py >nul 2>nul
if %ERRORLEVEL%==0 (
  py -3 "%HERE%durable_session.py" %*
) else (
  python "%HERE%durable_session.py" %*
)
exit /b %ERRORLEVEL%
