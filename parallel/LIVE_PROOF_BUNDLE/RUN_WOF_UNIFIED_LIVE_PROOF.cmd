@echo off
chcp 65001 >nul
setlocal EnableExtensions

title WOF 统一 Windows 真人短验证

if /I "%~1"=="--local" goto :local_run
if defined WOF_UNIFIED_BOOTSTRAPPED goto :local_run

set "WOF_ROOT=%LOCALAPPDATA%\WOF Future Danger\UnifiedLiveProof"
if not defined LOCALAPPDATA set "WOF_ROOT=%TEMP%\WOF_Future_Danger\UnifiedLiveProof"
set "WOF_STAGE=%WOF_ROOT%\stage_%RANDOM%_%RANDOM%"
set "WOF_ZIP=%TEMP%\wof-ai-private-main-%RANDOM%_%RANDOM%.zip"

echo.
echo ============================================================
echo   WOF 统一 Windows 真人短验证
echo ============================================================
echo.
echo 只读模式：开启
echo 游戏内存写入：0
echo 游戏输入注入：无
echo.
echo 正在准备最新 WOF 工具...
echo.

if not exist "%WOF_ROOT%" mkdir "%WOF_ROOT%" >nul 2>&1
if not exist "%WOF_STAGE%" mkdir "%WOF_STAGE%" >nul 2>&1

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference='Stop'; $ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -UseBasicParsing 'https://codeload.github.com/ouyong520/wof-ai-private/zip/refs/heads/main' -OutFile $env:WOF_ZIP; Expand-Archive -LiteralPath $env:WOF_ZIP -DestinationPath $env:WOF_STAGE -Force"
if errorlevel 1 goto :download_fail

set "WOF_PROJECT=%WOF_STAGE%\wof-ai-private-main"
if not exist "%WOF_PROJECT%\parallel\LIVE_PROOF_BUNDLE\unified_live_proof.py" goto :download_fail

del /q "%WOF_ZIP%" >nul 2>&1
set "WOF_UNIFIED_BOOTSTRAPPED=1"
call "%WOF_PROJECT%\parallel\LIVE_PROOF_BUNDLE\RUN_WOF_UNIFIED_LIVE_PROOF.cmd" --local
set "RC=%ERRORLEVEL%"
exit /b %RC%

:local_run
cd /d "%~dp0"
for %%I in ("%CD%\..\..") do set "WOF_PROJECT=%%~fI"
set "WOF_VENV=%WOF_ROOT%\venv"
set "PYBOOT="

if exist "%WOF_VENV%\Scripts\python.exe" goto :deps
where py >nul 2>&1
if not errorlevel 1 set "PYBOOT=py -3"
if defined PYBOOT goto :mkvenv
where python >nul 2>&1
if not errorlevel 1 set "PYBOOT=python"
if defined PYBOOT goto :mkvenv

echo 未找到 Python 3，正在尝试自动安装 Python 3.12...
where winget >nul 2>&1
if errorlevel 1 goto :python_fail
winget install --id Python.Python.3.12 -e --source winget --scope user --accept-source-agreements --accept-package-agreements --silent
where py >nul 2>&1
if not errorlevel 1 set "PYBOOT=py -3"
if not defined PYBOOT goto :python_fail

:mkvenv
echo 正在准备统一验证 Python 环境...
%PYBOOT% -m venv "%WOF_VENV%"
if errorlevel 1 goto :env_fail

:deps
echo 正在检查 PYLAUNCH / Browser Fleet / Recorder 依赖...
"%WOF_VENV%\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r "%WOF_PROJECT%\parallel\PYLAUNCH\requirements.txt"
if errorlevel 1 goto :env_fail
"%WOF_VENV%\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r "%WOF_PROJECT%\parallel\WOF052L_RECORDER\requirements.txt"
if errorlevel 1 goto :env_fail

set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
echo.
"%WOF_VENV%\Scripts\python.exe" "%WOF_PROJECT%\parallel\LIVE_PROOF_BUNDLE\unified_live_proof.py" --project-root "%WOF_PROJECT%"
set "RC=%ERRORLEVEL%"
echo.
if "%RC%"=="0" (
  echo 统一真人短验证已完成。
) else (
  echo 统一真人短验证未完成；请返回生成的总 JSON 或最终状态截图。
)
pause
exit /b %RC%

:download_fail
echo.
echo 无法下载或解压最新 WOF 工具。
echo 游戏本身没有受到影响。
echo 请确认 Windows 可以访问 GitHub，然后重新双击本文件。
if exist "%WOF_ZIP%" del /q "%WOF_ZIP%" >nul 2>&1
pause
exit /b 10

:python_fail
echo.
echo 没有找到可用的 Python 3，自动安装也没有成功。
echo 游戏本身没有受到影响。
echo 请安装 Python 3.11+ 后重新双击本文件。
pause
exit /b 11

:env_fail
echo.
echo WOF 统一验证运行环境准备失败。
echo 游戏和浏览器本身没有受到影响。
echo 请检查网络/Python 后重新双击本文件。
pause
exit /b 12
