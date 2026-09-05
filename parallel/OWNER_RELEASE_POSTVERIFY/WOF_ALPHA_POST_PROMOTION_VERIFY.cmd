@echo off
setlocal EnableExtensions DisableDelayedExpansion
title WOF Alpha - Post Promotion Verify

set "HERE=%~dp0"
for %%I in ("%HERE%..\..") do set "ROOT=%%~fI"
set "RESULTS=%USERPROFILE%\Documents\WOF_RESULTS"
set "SCRIPT=%HERE%post_promotion_verify.py"

if not exist "%SCRIPT%" (
  echo P23 verifier missing: %SCRIPT%
  exit /b 20
)

set "PY="
for /f "delims=" %%P in ('where py.exe 2^>nul') do if not defined PY set "PY=%%P"
if defined PY (
  "%PY%" -3 "%SCRIPT%" --repo-root "%ROOT%" --results-dir "%RESULTS%" --output-dir "%RESULTS%"
  exit /b %ERRORLEVEL%
)
for /f "delims=" %%P in ('where python.exe 2^>nul') do if not defined PY set "PY=%%P"
if not defined PY (
  echo Python 3 was not found. No release state was changed.
  exit /b 21
)
"%PY%" "%SCRIPT%" --repo-root "%ROOT%" --results-dir "%RESULTS%" --output-dir "%RESULTS%"
exit /b %ERRORLEVEL%
