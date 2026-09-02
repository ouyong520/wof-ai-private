@echo off
setlocal EnableExtensions
chcp 65001 >nul 2>&1
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
title WOF 一键工具

for %%I in ("%~dp0.") do set "LAUNCH_DIR=%%~fI"
set "PORTABLE_ROOT=%LAUNCH_DIR%\WOF_Portable"
set "CURRENT_FILE=%PORTABLE_ROOT%\current.txt"

rem Normal second-and-later launch is intentionally local/offline: no manifest,
rem bootstrap, pip or update request is made here. Menu 1 / --update-only is the
rem only normal path that performs an update/repair check.
if /I "%~1"=="--update-only" goto :bootstrap
if exist "%CURRENT_FILE%" (
  set "CURRENT_VERSION="
  set /p CURRENT_VERSION=<"%CURRENT_FILE%"
  if defined CURRENT_VERSION (
    set "CURRENT_RELEASE=%PORTABLE_ROOT%\releases\%CURRENT_VERSION%"
    set "CURRENT_PY=%PORTABLE_ROOT%\venv\Scripts\python.exe"
    if exist "%PORTABLE_ROOT%\releases\%CURRENT_VERSION%\installed.ok" if exist "%PORTABLE_ROOT%\releases\%CURRENT_VERSION%\PACKAGE_MANIFEST.json" if exist "%PORTABLE_ROOT%\releases\%CURRENT_VERSION%\parallel\OPTOOLKIT\owner_zh_cn.py" if exist "%PORTABLE_ROOT%\venv\Scripts\python.exe" goto :direct
  )
)

goto :bootstrap

:direct
set "WOF_PACKAGED_MODE=1"
set "WOF_PACKAGE_VERSION=%CURRENT_VERSION%"
set "WOF_TOOLKIT_PYTHON=%CURRENT_PY%"
set "WOF_BOOTSTRAP_PATH=%~f0"
echo.
echo ================================================
echo              WOF 一键工具
echo ================================================
echo 已找到本地 portable 工具 %CURRENT_VERSION%，直接打开中文工具箱。
"%CURRENT_PY%" "%CURRENT_RELEASE%\parallel\OPTOOLKIT\owner_zh_cn.py" --root "%CURRENT_RELEASE%"
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" goto :run_fail
exit /b 0

:bootstrap
rem The bootstrap implementation itself is immutable-pinned. It may consult the
rem official package manifest only on first install or explicit menu-1 repair/update.
if defined WOF_BOOTSTRAP_URL (
  set "BOOT_URL=%WOF_BOOTSTRAP_URL%"
) else (
  set "BOOT_URL=https://raw.githubusercontent.com/ouyong520/wof-ai-private/e2aea5058a60c2229175c98c35623ebc66a0ad23/parallel/OWNER_ONECLICK/bootstrap_v2.ps1"
)
set "BOOT_PS1=%TEMP%\WOF_owner_bootstrap_%RANDOM%_%RANDOM%.ps1"
echo.
echo ================================================
echo              WOF 一键工具
echo ================================================
echo 正在进行首次安装或显式更新/修复检查...
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; $r=Invoke-WebRequest -UseBasicParsing -Uri '%BOOT_URL%' -TimeoutSec 45; $enc=New-Object System.Text.UTF8Encoding($true); [System.IO.File]::WriteAllText('%BOOT_PS1%', [string]$r.Content, $enc)"
if errorlevel 1 goto :download_fail
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%BOOT_PS1%" -InstallRoot "%PORTABLE_ROOT%" -LauncherPath "%~f0" %*
set "RC=%ERRORLEVEL%"
del /q "%BOOT_PS1%" >nul 2>&1
if not "%RC%"=="0" goto :run_fail
exit /b 0

:download_fail
echo.
echo 无法下载固定版本的 WOF 安装/更新程序，请检查网络后重试。
echo 已安装的 portable 旧版本不会被删除，游戏本身没有受到影响。
echo 下载地址：%BOOT_URL%
pause
exit /b 10

:run_fail
echo.
echo WOF 一键工具没有完成，错误代码：%RC%
echo 已安装版本和游戏本身没有被删除或写入。
echo 日志位置：%PORTABLE_ROOT%\logs\bootstrap.log
pause
exit /b %RC%
