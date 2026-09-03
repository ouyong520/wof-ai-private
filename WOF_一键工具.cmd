@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul 2>&1
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
title WOF 一键工具

for %%I in ("%~dp0.") do set "LAUNCH_DIR=%%~fI"
set "PORTABLE_ROOT=%LAUNCH_DIR%\WOF_Portable"
set "CURRENT_FILE=%PORTABLE_ROOT%\current.txt"

rem Owner always uses this original entry name.
rem In a Git checkout, normal double-click runs exact-current-main Alpha live acceptance.
rem Outside a checkout, the historical immutable portable flow remains unchanged.
if /I "%~1"=="--update-only" goto :bootstrap
if exist "%LAUNCH_DIR%\.git" goto :alpha_checkout

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

:alpha_checkout
set "ROOT=%LAUNCH_DIR%"
if not exist "%ROOT%\parallel\PYLAUNCH\render_authority_measurement_entry.py" goto :alpha_missing
if not exist "%ROOT%\parallel\RENDER_AUTHORITY_V3\measurement_runner.py" goto :alpha_missing
if not exist "%ROOT%\parallel\PYLAUNCH\wof_launcher\head_visual_tracker.py" goto :alpha_missing
if not exist "%ROOT%\parallel\PYLAUNCH\wof_launcher\production_p1_overlay.py" goto :alpha_missing
if not exist "%ROOT%\parallel\PYLAUNCH\wof_launcher\render_authority_capture.py" goto :alpha_missing
if not exist "%ROOT%\product\alpha\wof_alpha_hud.js" goto :alpha_missing
if not exist "%ROOT%\product\alpha\wof_alpha_relative_head_anchor.js" goto :alpha_missing
if not exist "%ROOT%\product\alpha\wof_alpha_relative_enemy_overlay.js" goto :alpha_missing
if not exist "%ROOT%\parallel\PYLAUNCH\requirements.txt" goto :alpha_missing

where git >nul 2>&1
if errorlevel 1 goto :alpha_no_git
set "DIRTY="
for /f "delims=" %%H in ('git -C "%ROOT%" status --porcelain --untracked-files=all') do set "DIRTY=1"
if defined DIRTY goto :alpha_dirty

echo.
echo ================================================
echo              WOF 一键工具
echo ================================================
echo 正在确认 GitHub main exact SHA……
git -C "%ROOT%" fetch --quiet https://github.com/ouyong520/wof-ai-private.git +refs/heads/main:refs/remotes/wof-alpha-authority/main
if errorlevel 1 goto :alpha_fetch_fail
for /f "delims=" %%H in ('git -C "%ROOT%" rev-parse HEAD') do set "HEAD_SHA=%%H"
for /f "delims=" %%H in ('git -C "%ROOT%" rev-parse refs/remotes/wof-alpha-authority/main') do set "MAIN_SHA=%%H"
if not defined HEAD_SHA goto :alpha_sha_fail
if not defined MAIN_SHA goto :alpha_sha_fail
if /I not "%HEAD_SHA%"=="%MAIN_SHA%" goto :alpha_not_current_main

echo Alpha current main exact SHA: %HEAD_SHA%
echo 当前为 Alpha 实机验收：不发布、不更新 immutable Owner package。
echo 直接进入菜单 6 使用的同一 production runtime。
echo P1 production draw 建立后继续保持实时 actor feed，用于怪物头顶验收。
echo.

if defined LOCALAPPDATA (
  set "ALPHA_VENV=%LOCALAPPDATA%\WOF Alpha Current Main\venv"
) else (
  set "ALPHA_VENV=%TEMP%\WOF_ALPHA_CURRENT_MAIN\venv"
)
set "ALPHA_PY=%ALPHA_VENV%\Scripts\python.exe"
if exist "%ALPHA_PY%" goto :alpha_deps

set "PYBOOT="
where py >nul 2>&1
if not errorlevel 1 set "PYBOOT=py -3"
if defined PYBOOT goto :alpha_mkvenv
where python >nul 2>&1
if not errorlevel 1 set "PYBOOT=python"
if not defined PYBOOT goto :alpha_no_python

:alpha_mkvenv
echo 正在准备 Alpha Python 环境……
%PYBOOT% -m venv "%ALPHA_VENV%"
if errorlevel 1 goto :alpha_venv_fail

:alpha_deps
echo 正在检查 Alpha PYLAUNCH 依赖……
"%ALPHA_PY%" -m pip install --disable-pip-version-check -q -r "%ROOT%\parallel\PYLAUNCH\requirements.txt"
if errorlevel 1 goto :alpha_deps_fail

if defined USERPROFILE (
  set "RESULTS=%USERPROFILE%\Documents\WOF_RESULTS\alpha_current_main_acceptance"
) else (
  set "RESULTS=%TEMP%\WOF_RESULTS\alpha_current_main_acceptance"
)
if not exist "%RESULTS%" mkdir "%RESULTS%" >nul 2>&1
>"%RESULTS%\CURRENT_MAIN_ACCEPTANCE.json" echo {"schema":"wof-alpha-current-main-live-acceptance-v1","sourceCommit":"%HEAD_SHA%","ownerEntry":"WOF_一键工具.cmd","mode":"production-runtime-live-acceptance-only","menu6RuntimeEntry":"parallel/PYLAUNCH/render_authority_measurement_entry.py","liveAcceptanceHoldAfterP1":true,"immutablePackagePublished":false,"readOnly":true,"ramWrites":0,"inputInjection":false}
set "WOF_ALPHA_ACCEPTANCE_COMMIT=%HEAD_SHA%"
set "WOF_ALPHA_LIVE_ACCEPTANCE_HOLD=1"

cd /d "%ROOT%\parallel\PYLAUNCH"
"%ALPHA_PY%" "%ROOT%\parallel\PYLAUNCH\render_authority_measurement_entry.py" --root "%ROOT%" --output-root "%RESULTS%"
set "RC=%ERRORLEVEL%"
echo.
echo Alpha current-main 实机验收已结束，exit=%RC%
echo Exact SHA: %HEAD_SHA%
echo 结果目录: %RESULTS%
exit /b %RC%

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

:alpha_missing
echo BLOCKED：当前 Git checkout 缺少 Alpha production runtime 文件。
pause
exit /b 21

:alpha_no_git
echo BLOCKED：未找到 Git，无法证明本地代码就是 GitHub current main exact SHA。
pause
exit /b 22

:alpha_dirty
echo BLOCKED：仓库有本地修改。为保证 exact-SHA 实机验收，本次不会启动 Alpha。
git -C "%ROOT%" status --short
pause
exit /b 23

:alpha_fetch_fail
echo BLOCKED：无法直接获取 GitHub main，不能证明 current-main authority。
pause
exit /b 24

:alpha_sha_fail
echo BLOCKED：无法解析本地 HEAD / GitHub main exact SHA。
pause
exit /b 25

:alpha_not_current_main
echo BLOCKED：本地 HEAD 不是 GitHub current main。
echo Local HEAD : %HEAD_SHA%
echo GitHub main: %MAIN_SHA%
echo 请先用 GitHub Desktop 更新 main，再双击同一个 WOF_一键工具.cmd。
pause
exit /b 26

:alpha_no_python
echo BLOCKED：未找到 Python 3。
pause
exit /b 27

:alpha_venv_fail
echo BLOCKED：Alpha Python 环境创建失败。
pause
exit /b 28

:alpha_deps_fail
echo BLOCKED：Alpha PYLAUNCH 依赖安装失败。
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
