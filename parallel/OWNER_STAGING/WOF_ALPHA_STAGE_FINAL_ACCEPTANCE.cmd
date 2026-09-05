@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "HERE=%~dp0"
py "%HERE%exact_candidate_staging_acceptance.py" --repo-root "%HERE%..\.."
exit /b %ERRORLEVEL%
