@echo off
setlocal
chcp 65001 >nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "HERE=%~dp0"
if "%~1"=="" (
  echo ERROR: exact 40-hex source commit is required.
  exit /b 2
)
py "%HERE%post_repair_final_candidate_rebuild.py" --root "%HERE%..\.." build-verify --source "%~1"
set "RC=%ERRORLEVEL%"
exit /b %RC%
