@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "HERE=%~dp0"

if "%~8"=="" (
  echo Usage: %~nx0 ^<metadata-repo-root^> ^<source-checkout^> ^<sourceCommit^> ^<metadataCommit^> ^<pointer-rel^> ^<provenance-rel^> ^<browser-websocket-url^> ^<output-root^> [extra python args]
  exit /b 64
)

if not defined LOCALAPPDATA (
  echo P43_ERROR: LOCALAPPDATA is not set; existing WOF dedicated venv cannot be resolved.
  exit /b 65
)
set "PY=%LOCALAPPDATA%\WOF Alpha Current Main\venv\Scripts\python.exe"
if not exist "%PY%" (
  echo P43_ERROR: existing WOF dedicated venv Python missing: "%PY%"
  echo P43_ERROR: no install and no Python fallback are permitted.
  exit /b 66
)

set "REPO=%~1"
set "SOURCE_CHECKOUT=%~2"
set "SOURCE_COMMIT=%~3"
set "METADATA_COMMIT=%~4"
set "POINTER=%~5"
set "PROVENANCE=%~6"
set "BROWSER_WS=%~7"
set "OUTPUT=%~8"
shift
shift
shift
shift
shift
shift
shift
shift

"%PY%" "%HERE%p43_bounded_zero_click_live_diagnostic.py" ^
  --repo-root "%REPO%" ^
  --source-checkout "%SOURCE_CHECKOUT%" ^
  --source-commit "%SOURCE_COMMIT%" ^
  --metadata-commit "%METADATA_COMMIT%" ^
  --pointer "%POINTER%" ^
  --provenance "%PROVENANCE%" ^
  --browser-websocket-url "%BROWSER_WS%" ^
  --output-root "%OUTPUT%" %*
exit /b %ERRORLEVEL%
