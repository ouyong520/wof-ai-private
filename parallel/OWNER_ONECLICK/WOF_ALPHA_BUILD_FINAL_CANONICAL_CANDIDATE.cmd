@echo off
setlocal
chcp 65001 >nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "HERE=%~dp0"
py "%HERE%final_canonical_candidate.py" --root "%HERE%..\.." build-verify --source HEAD
set "RC=%ERRORLEVEL%"
if "%RC%"=="4" echo P19 final candidate is waiting for terminal P18 evidence. No candidate or latest pointer was changed.
exit /b %RC%
