@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul 2>&1
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
title WOF Alpha Current Main 实机验收

for %%I in ("%~dp0.") do set "ROOT=%%~fI"

if not exist "%ROOT%\.git" goto :not_checkout
if not exist "%ROOT%\parallel\PYLAUNCH\render_authority_measurement_entry.py" goto :missing_alpha
if not exist "%ROOT%\parallel\RENDER_AUTHORITY_V3\measurement_runner.py" goto :missing_alpha
if not exist "%ROOT%\parallel\PYLAUNCH\wof_launcher\head_visual_tracker.py" goto :missing_alpha
if not exist "%ROOT%\parallel\PYLAUNCH\wof_launcher\production_p1_overlay.py" goto :missing_alpha
if not exist "%ROOT%\parallel\PYLAUNCH\wof_launcher\render_authority_capture.py" goto :missing_alpha
if not exist "%ROOT%\product\alpha\wof_alpha_hud.js" goto :missing_alpha
if not exist "%ROOT%\product\alpha\wof_alpha_relative_head_anchor.js" goto :missing_alpha
if not exist "%ROOT%\product\alpha\wof_alpha_relative_enemy_overlay.js" goto :missing_alpha
if not exist "%ROOT%\parallel\PYLAUNCH\requirements.txt" goto :missing_alpha

where git >nul 2>&1
if errorlevel 1 goto :no_git

set "DIRTY="
for /f "delims=" %%H in ('git -C "%ROOT%" status --porcelain --untracked-files=all') do set "DIRTY=1"
if defined DIRTY goto :dirty

echo 正在确认 GitHub main exact SHA……
git -C "%ROOT%" fetch --quiet https://github.com/ouyong520/wof-ai-private.git +refs/heads/main:refs/remotes/wof-alpha-authority/main
if errorlevel 1 goto :fetch_fail
for /f "delims=" %%H in ('git -C "%ROOT%" rev-parse HEAD') do set "HEAD_SHA=%%H"
for /f "delims=" %%H in ('git -C "%ROOT%" rev-parse refs/remotes/wof-alpha-authority/main') do set "MAIN_SHA=%%H"
if not defined HEAD_SHA goto :sha_fail
if not defined MAIN_SHA goto :sha_fail
if /I not "%HEAD_SHA%"=="%MAIN_SHA%" goto :not_current_main

echo.
echo Alpha current main exact SHA: %HEAD_SHA%
echo 此入口仅用于实机验收当前 main，不发布、不更新 immutable Owner package。
echo 它直接启动菜单 6 最终调用的同一个 Alpha production runtime entry。
echo P1 production draw 建立后不会自动退出，会继续保持实时 actor feed 供怪物头顶验收。
echo 只运行 Alpha PYLAUNCH / production overlay 路径，不运行其他项目。
echo.

if defined LOCALAPPDATA (
  set "VENV=%LOCALAPPDATA%\WOF Alpha Current Main\venv"
) else (
  set "VENV=%TEMP%\WOF_ALPHA_CURRENT_MAIN\venv"
)
set "VENV_PY=%VENV%\Scripts\python.exe"
if exist "%VENV_PY%" goto :deps

set "PYBOOT="
where py >nul 2>&1
if not errorlevel 1 set "PYBOOT=py -3"
if defined PYBOOT goto :mkvenv
where python >nul 2>&1
if not errorlevel 1 set "PYBOOT=python"
if not defined PYBOOT goto :no_python

:mkvenv
echo 正在准备 Alpha-only Python 环境……
%PYBOOT% -m venv "%VENV%"
if errorlevel 1 goto :venv_fail

:deps
echo 正在检查 Alpha PYLAUNCH 依赖……
"%VENV_PY%" -m pip install --disable-pip-version-check -q -r "%ROOT%\parallel\PYLAUNCH\requirements.txt"
if errorlevel 1 goto :deps_fail

if defined USERPROFILE (
  set "RESULTS=%USERPROFILE%\Documents\WOF_RESULTS\alpha_current_main_acceptance"
) else (
  set "RESULTS=%TEMP%\WOF_RESULTS\alpha_current_main_acceptance"
)
if not exist "%RESULTS%" mkdir "%RESULTS%" >nul 2>&1
>"%RESULTS%\CURRENT_MAIN_ACCEPTANCE.json" echo {"schema":"wof-alpha-current-main-live-acceptance-v1","sourceCommit":"%HEAD_SHA%","mode":"production-runtime-live-acceptance-only","menu6RuntimeEntry":"parallel/PYLAUNCH/render_authority_measurement_entry.py","liveAcceptanceHoldAfterP1":true,"immutablePackagePublished":false,"readOnly":true,"ramWrites":0,"inputInjection":false}
set "WOF_ALPHA_ACCEPTANCE_COMMIT=%HEAD_SHA%"
set "WOF_ALPHA_LIVE_ACCEPTANCE_HOLD=1"

cd /d "%ROOT%\parallel\PYLAUNCH"
"%VENV_PY%" "%ROOT%\parallel\PYLAUNCH\render_authority_measurement_entry.py" --root "%ROOT%" --output-root "%RESULTS%"
set "RC=%ERRORLEVEL%"
echo.
echo Alpha current-main 实机验收已结束，exit=%RC%
echo Exact SHA: %HEAD_SHA%
echo 结果目录: %RESULTS%
exit /b %RC%

:not_checkout
echo BLOCKED：此验收入口必须从 GitHub 仓库 checkout 运行，不能从旧 immutable package 目录运行。
exit /b 20

:missing_alpha
echo BLOCKED：Alpha current-main production runtime 文件不完整。
exit /b 21

:no_git
echo BLOCKED：未找到 Git，无法证明本地代码就是 GitHub current main exact SHA。
exit /b 22

:dirty
echo BLOCKED：仓库有本地修改。为保证 exact-SHA 验收，本次不会启动 Alpha。
git -C "%ROOT%" status --short
exit /b 23

:fetch_fail
echo BLOCKED：无法直接获取 ouyong520/wof-ai-private GitHub main，不能证明 current-main authority。
exit /b 24

:sha_fail
echo BLOCKED：无法解析 HEAD / GitHub main exact SHA。
exit /b 25

:not_current_main
echo BLOCKED：本地 HEAD 不是 GitHub current main。
echo Local HEAD : %HEAD_SHA%
echo GitHub main: %MAIN_SHA%
echo 请先用 GitHub Desktop 更新到 main 后再运行本文件。
exit /b 26

:no_python
echo BLOCKED：未找到 Python 3。
exit /b 27

:venv_fail
echo BLOCKED：Alpha-only Python 环境创建失败。
exit /b 28

:deps_fail
echo BLOCKED：Alpha PYLAUNCH 依赖安装失败。
exit /b 29
