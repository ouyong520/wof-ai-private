@echo off
chcp 65001 >nul
setlocal EnableExtensions

title WOF 统一 Windows 真人短验证

set "WOF_ROOT=%LOCALAPPDATA%\WOF Future Danger\UnifiedLiveProof"
if not defined LOCALAPPDATA set "WOF_ROOT=%TEMP%\WOF_Future_Danger\UnifiedLiveProof"

if /I "%~1"=="--local" goto :local_run
if defined WOF_UNIFIED_BOOTSTRAPPED goto :local_run

set "WOF_STAGE=%WOF_ROOT%\stage_%RANDOM%_%RANDOM%"
set "WOF_ZIP=%TEMP%\wof-ai-private-snapshot-%RANDOM%_%RANDOM%.zip"
set "WOF_SNAPSHOT_MANIFEST=%WOF_STAGE%\UNIFIED_SNAPSHOT_MANIFEST.json"

echo.
echo ============================================================
echo   WOF 统一 Windows 真人短验证
echo ============================================================
echo.
echo 先执行仓库侧预检；预检未通过时不会启动 Browser，也不需要进入 WOF。
echo 只读模式：开启
echo 游戏内存写入：0
echo 游戏输入注入：无
echo.
echo 正在解析并下载同一个最新 GitHub snapshot...
echo.

if not exist "%WOF_ROOT%" mkdir "%WOF_ROOT%" >nul 2>&1
if not exist "%WOF_STAGE%" mkdir "%WOF_STAGE%" >nul 2>&1

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference='Stop'; $ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; $h=@{'User-Agent'='WOF-Unified-Preflight'}; $r=Invoke-RestMethod -Headers $h 'https://api.github.com/repos/ouyong520/wof-ai-private/commits/main'; $sha=[string]$r.sha; if($sha -notmatch '^[0-9a-fA-F]{40}$'){throw 'main commit SHA invalid'}; $resolved=[DateTime]::UtcNow.ToString('o'); $zip='https://codeload.github.com/ouyong520/wof-ai-private/zip/'+$sha; Invoke-WebRequest -UseBasicParsing -Headers $h $zip -OutFile $env:WOF_ZIP; Expand-Archive -LiteralPath $env:WOF_ZIP -DestinationPath $env:WOF_STAGE -Force; $r2=Invoke-RestMethod -Headers $h 'https://api.github.com/repos/ouyong520/wof-ai-private/commits/main'; if(([string]$r2.sha).ToLowerInvariant() -ne $sha.ToLowerInvariant()){throw 'main changed while snapshot was downloading; retry required'}; $components=[ordered]@{liveProof=$sha;browserFleet=$sha;pylaunch=$sha;recorder=$sha}; $meta=[ordered]@{schema='wof-unified-snapshot-manifest-v1';source='github-main-exact-sha';snapshotCommit=$sha.ToLowerInvariant();resolvedAtUtc=$resolved;components=$components}; $meta | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $env:WOF_SNAPSHOT_MANIFEST -Encoding UTF8"
if errorlevel 1 goto :download_fail

set "WOF_PROJECT="
for /d %%D in ("%WOF_STAGE%\wof-ai-private-*") do if not defined WOF_PROJECT set "WOF_PROJECT=%%~fD"
if not defined WOF_PROJECT goto :download_fail
if not exist "%WOF_PROJECT%\parallel\LIVE_PROOF_BUNDLE\unified_preflight_entrypoint.py" goto :download_fail

del /q "%WOF_ZIP%" >nul 2>&1
set "WOF_UNIFIED_BOOTSTRAPPED=1"
call "%WOF_PROJECT%\parallel\LIVE_PROOF_BUNDLE\RUN_WOF_UNIFIED_LIVE_PROOF.cmd" --local
set "RC=%ERRORLEVEL%"
exit /b %RC%

:local_run
cd /d "%~dp0"
for %%I in ("%CD%\..\..") do set "WOF_PROJECT=%%~fI"
set "WOF_VENV=%WOF_ROOT%\venv"
set "WOF_PREFLIGHT_STATUS=%WOF_ROOT%\UNIFIED_PREFLIGHT_STATUS.json"
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
echo 正在准备安全离线 regression 所需依赖...
"%WOF_VENV%\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r "%WOF_PROJECT%\parallel\PYLAUNCH\requirements.txt"
if errorlevel 1 goto :env_fail
"%WOF_VENV%\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r "%WOF_PROJECT%\parallel\WOF052L_RECORDER\requirements.txt"
if errorlevel 1 goto :env_fail

set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
echo.
if defined WOF_SNAPSHOT_MANIFEST (
  "%WOF_VENV%\Scripts\python.exe" "%WOF_PROJECT%\parallel\LIVE_PROOF_BUNDLE\unified_preflight_entrypoint.py" --project-root "%WOF_PROJECT%" --snapshot-manifest "%WOF_SNAPSHOT_MANIFEST%" --preflight-status-out "%WOF_PREFLIGHT_STATUS%"
) else (
  "%WOF_VENV%\Scripts\python.exe" "%WOF_PROJECT%\parallel\LIVE_PROOF_BUNDLE\unified_preflight_entrypoint.py" --project-root "%WOF_PROJECT%" --preflight-status-out "%WOF_PREFLIGHT_STATUS%"
)
set "RC=%ERRORLEVEL%"
echo.
if "%RC%"=="20" (
  echo 仓库侧预检已阻断。Browser 未启动；你现在不需要进入 WOF。
  echo JSON：%WOF_PREFLIGHT_STATUS%
  exit /b 20
)
if "%RC%"=="0" (
  echo 统一真人短验证已完成。
) else (
  echo 统一真人短验证未完成；如果 Browser 已进入真人阶段，请返回生成的总 JSON 或最终状态截图。
)
pause
exit /b %RC%

:download_fail
echo.
echo 无法取得一个可验证且一致的最新 WOF snapshot。
echo Browser 未启动，游戏本身没有受到影响，也不需要进入 WOF。
if exist "%WOF_ZIP%" del /q "%WOF_ZIP%" >nul 2>&1
exit /b 10

:python_fail
echo.
echo 没有找到可用的 Python 3，自动安装也没有成功。
echo Browser 未启动，游戏本身没有受到影响。
exit /b 11

:env_fail
echo.
echo WOF 统一验证运行环境准备失败。
echo Browser 未启动，游戏本身没有受到影响。
exit /b 12
