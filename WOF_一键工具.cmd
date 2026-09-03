@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul 2>&1
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
title WOF 一键工具

for %%I in ("%~dp0.") do set "LAUNCH_DIR=%%~fI"
set "PORTABLE_ROOT=%LAUNCH_DIR%\WOF_Portable"
set "CURRENT_FILE=%PORTABLE_ROOT%\current.txt"

rem Owner always enters through the original Chinese toolbox.
rem Alpha is started only after Owner chooses menu 6 inside that toolbox.
if /I "%~1"=="--update-only" goto :bootstrap
if exist "%LAUNCH_DIR%\.git" goto :source_checkout

rem Normal packaged second-and-later launch is intentionally local/offline: no manifest,
rem bootstrap, pip or update request is made here. Menu 1 / --update-only is the
rem only normal path that performs an update/repair check.
if exist "%CURRENT_FILE%" (
  set "CURRENT_VERSION="
  set /p CURRENT_VERSION=<"%CURRENT_FILE%"
  if defined CURRENT_VERSION (
    set "CURRENT_RELEASE=%PORTABLE_ROOT%\releases\!CURRENT_VERSION!"
    set "CURRENT_PY=%PORTABLE_ROOT%\venv\Scripts\python.exe"
    if exist "!CURRENT_RELEASE!\installed.ok" if exist "!CURRENT_RELEASE!\PACKAGE_MANIFEST.json" if exist "!CURRENT_RELEASE!\parallel\OPTOOLKIT\owner_zh_cn.py" if exist "!CURRENT_PY!" goto :direct
  )
)

goto :bootstrap

:source_checkout
if not exist "%LAUNCH_DIR%\parallel\OPTOOLKIT\current_main_owner_entry.py" goto :source_missing
if not exist "%LAUNCH_DIR%\parallel\PYLAUNCH\requirements.txt" goto :source_missing
where git >nul 2>&1
if errorlevel 1 goto :source_no_git
set "DIRTY="
for /f "delims=" %%H in ('git -C "%LAUNCH_DIR%" status --porcelain --untracked-files=all') do set "DIRTY=1"
if defined DIRTY goto :source_dirty

echo.
echo ================================================
echo              WOF 一键工具
echo ================================================
echo 正在确认 GitHub current main……
git -C "%LAUNCH_DIR%" fetch --quiet https://github.com/ouyong520/wof-ai-private.git +refs/heads/main:refs/remotes/wof-alpha-authority/main
if errorlevel 1 goto :source_fetch_fail
for /f "delims=" %%H in ('git -C "%LAUNCH_DIR%" rev-parse HEAD') do set "HEAD_SHA=%%H"
for /f "delims=" %%H in ('git -C "%LAUNCH_DIR%" rev-parse refs/remotes/wof-alpha-authority/main') do set "MAIN_SHA=%%H"
if not defined HEAD_SHA goto :source_sha_fail
if not defined MAIN_SHA goto :source_sha_fail
if /I not "!HEAD_SHA!"=="!MAIN_SHA!" goto :source_not_current

echo Current main exact SHA: !HEAD_SHA!
echo 将打开原中文工具箱；只有选择菜单 6 才启动 Alpha。
echo 当前 Git checkout 的菜单 6 使用 current-main production runtime，不读取旧 package runtime。
echo.

if defined LOCALAPPDATA (
  set "SOURCE_VENV=%LOCALAPPDATA%\WOF Alpha Current Main\venv"
) else (
  set "SOURCE_VENV=%TEMP%\WOF_ALPHA_CURRENT_MAIN\venv"
)
set "SOURCE_PY=!SOURCE_VENV!\Scripts\python.exe"
if exist "!SOURCE_PY!" goto :source_deps
set "PYBOOT="
where py >nul 2>&1
if not errorlevel 1 set "PYBOOT=py -3"
if defined PYBOOT goto :source_mkvenv
where python >nul 2>&1
if not errorlevel 1 set "PYBOOT=python"
if not defined PYBOOT goto :source_no_python

:source_mkvenv
echo 正在准备 current-main Alpha Python 环境……
%PYBOOT% -m venv "!SOURCE_VENV!"
if errorlevel 1 goto :source_venv_fail

:source_deps
echo 正在检查 Alpha 运行依赖……
"!SOURCE_PY!" -m pip install --disable-pip-version-check -q -r "%LAUNCH_DIR%\parallel\PYLAUNCH\requirements.txt"
if errorlevel 1 goto :source_deps_fail
set "WOF_ALPHA_CURRENT_MAIN_SOURCE=1"
set "WOF_ALPHA_ACCEPTANCE_COMMIT=!HEAD_SHA!"
set "WOF_ALPHA_LIVE_ACCEPTANCE_HOLD=1"
set "WOF_PACKAGED_MODE=0"
set "WOF_TOOLKIT_PYTHON=!SOURCE_PY!"
set "WOF_BOOTSTRAP_PATH=%~f0"
cd /d "%LAUNCH_DIR%\parallel\OPTOOLKIT"
"!SOURCE_PY!" "%LAUNCH_DIR%\parallel\OPTOOLKIT\current_main_owner_entry.py" --root "%LAUNCH_DIR%"
set "RC=!ERRORLEVEL!"
if not "!RC!"=="0" goto :run_fail
exit /b 0

:direct
set "WOF_PACKAGED_MODE=1"
set "WOF_PACKAGE_VERSION=!CURRENT_VERSION!"
set "WOF_TOOLKIT_PYTHON=!CURRENT_PY!"
set "WOF_BOOTSTRAP_PATH=%~f0"
echo.
echo ================================================
echo              WOF 一键工具
echo ================================================
echo 已找到本地 portable 工具 !CURRENT_VERSION!，直接打开中文工具箱。
"!CURRENT_PY!" "!CURRENT_RELEASE!\parallel\OPTOOLKIT\owner_zh_cn.py" --root "!CURRENT_RELEASE!"
set "RC=!ERRORLEVEL!"
if not "!RC!"=="0" goto :run_fail
exit /b 0

:bootstrap
rem The bootstrap implementation itself is immutable-pinned. It may consult the
rem official package manifest only on first install or explicit menu-1 repair/update.
if defined WOF_BOOTSTRAP_URL (
  set "BOOT_URL=%WOF_BOOTSTRAP_URL%"
) else (
  set "BOOT_URL=https://raw.githubusercontent.com/ouyong520/wof-ai-private/e4bada0109dadff96e1847199b334aa718f5d7be/parallel/OWNER_ONECLICK/bootstrap_v2.ps1"
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

:source_missing
echo BLOCKED：current-main Owner 工具入口或 Alpha 依赖清单缺失。
pause
exit /b 21

:source_no_git
echo BLOCKED：未找到 Git，无法证明本地代码是 GitHub current main。
pause
exit /b 22

:source_dirty
echo BLOCKED：仓库存在本地修改。请先在 GitHub Desktop 处理本地修改后再运行。
git -C "%LAUNCH_DIR%" status --short
pause
exit /b 23

:source_fetch_fail
echo BLOCKED：无法获取 GitHub current main，未启动 Alpha。
pause
exit /b 24

:source_sha_fail
echo BLOCKED：无法解析本地 HEAD / GitHub main exact SHA。
pause
exit /b 25

:source_not_current
echo BLOCKED：本地仓库还不是 GitHub current main。
echo Local HEAD : !HEAD_SHA!
echo GitHub main: !MAIN_SHA!
echo 请在 GitHub Desktop 更新后，再双击同一个 WOF_一键工具.cmd。
pause
exit /b 26

:source_no_python
echo BLOCKED：未找到 Python 3。
pause
exit /b 27

:source_venv_fail
echo BLOCKED：current-main Alpha Python 环境创建失败。
pause
exit /b 28

:source_deps_fail
echo BLOCKED：Alpha 运行依赖安装失败。
pause
exit /b 29

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
