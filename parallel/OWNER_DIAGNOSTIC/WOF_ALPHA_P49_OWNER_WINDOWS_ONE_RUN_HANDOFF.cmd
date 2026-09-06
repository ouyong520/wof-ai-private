@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul
if "%~4"=="" (
  echo Usage: %~nx0 ^<metadata-repo-root^> ^<source-checkout^> ^<browser-websocket-url^> ^<output-directory^>
  echo Example: %~nx0 "D:\wof-ai-private" "D:\WOF Alpha Source" "ws://127.0.0.1:9222/devtools/browser/EXACT-ID" "D:\WOF-P49-Output"
  exit /b 64
)
set "META=%~1"
set "SOURCE=%~2"
set "BROWSER_WS=%~3"
set "OUTPUT=%~4"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0p49_owner_windows_one_run_handoff.ps1" -MetadataRepoRoot "%META%" -SourceCheckout "%SOURCE%" -BrowserWebSocketUrl "%BROWSER_WS%" -OutputDirectory "%OUTPUT%"
exit /b %ERRORLEVEL%
