@echo off
setlocal
set "ROOT=%~dp0\..\.."
for %%I in ("%ROOT%") do set "ROOT=%%~fI"
set "OUT=%USERPROFILE%\Documents\WOF_RESULTS\ALPHA_P25_COMPOSITE_ACCEPTANCE"
if not exist "%OUT%" mkdir "%OUT%"
py "%~dp0composite_acceptance.py" --repo-root "%ROOT%" --output-root "%OUT%"
exit /b %ERRORLEVEL%
