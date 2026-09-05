@echo off
setlocal
set "HERE=%~dp0"
where py >nul 2>nul
if %ERRORLEVEL%==0 (
  py -3 "%HERE%provenance_chain.py" %*
) else (
  python "%HERE%provenance_chain.py" %*
)
exit /b %ERRORLEVEL%
