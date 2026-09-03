@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul 2>&1
title WOF Alpha 一键直接运行 V3

set "SELF=%~f0"
set "TMPPS=%TEMP%\WOF_Alpha_V3_%RANDOM%_%RANDOM%.ps1"

for /f "tokens=1 delims=:" %%N in ('findstr /n /b /c:"#__POWERSHELL_PAYLOAD__" "%SELF%"') do set "MARK=%%N"
if not defined MARK (
  echo.
  echo 启动文件损坏：找不到内部 PowerShell 段。
  echo 请把这个窗口截图发给 ChatGPT。
  echo.
  pause
  exit /b 90
)

set /a SKIP=MARK
more +%SKIP% "%SELF%" > "%TMPPS%"
if errorlevel 1 (
  echo.
  echo 无法释放内部启动脚本。
  echo 请把这个窗口截图发给 ChatGPT。
  echo.
  pause
  exit /b 91
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%TMPPS%"
set "RC=%ERRORLEVEL%"
del /q "%TMPPS%" >nul 2>&1

echo.
if not "%RC%"=="0" (
  echo WOF Alpha V3 返回错误代码：%RC%
  echo 请把这个窗口截图发给 ChatGPT。
)
echo.
pause
exit /b %RC%

#__POWERSHELL_PAYLOAD__

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = 'WOF Alpha 一键直接运行 V3'

function Stop-Wof([string]$Message, [int]$Code = 1) {
    Write-Host ""
    Write-Host "=============================================="
    Write-Host $Message
    Write-Host "=============================================="
    Write-Host ""
    Read-Host "按回车返回"
    exit $Code
}

Write-Host ""
Write-Host "=================================================="
Write-Host "           WOF Alpha 一键直接运行 V3"
Write-Host "=================================================="
Write-Host "游戏可以继续开着。"
Write-Host ""

$repo = $null
$common = @(
    (Join-Path $env:USERPROFILE 'Documents\GitHub\wof-ai-private'),
    (Join-Path $env:USERPROFILE 'Desktop\wof-ai-private'),
    (Join-Path $env:USERPROFILE 'Downloads\wof-ai-private'),
    (Join-Path $env:USERPROFILE 'source\repos\wof-ai-private'),
    (Join-Path $env:USERPROFILE 'wof-ai-private')
)
foreach ($c in $common) {
    if ((Test-Path (Join-Path $c '.git')) -and
        (Test-Path (Join-Path $c 'parallel\PYLAUNCH\render_authority_measurement_entry.py'))) {
        $repo = $c
        break
    }
}

if (-not $repo) {
    Write-Host "正在自动寻找 wof-ai-private 项目..."
    $roots = @(
        $env:USERPROFILE,
        'C:\',
        'D:\',
        'E:\'
    ) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -Unique

    foreach ($root in $roots) {
        try {
            $hits = Get-ChildItem -LiteralPath $root -Directory -Filter 'wof-ai-private' -Recurse -ErrorAction SilentlyContinue
            foreach ($h in $hits) {
                if ((Test-Path (Join-Path $h.FullName '.git')) -and
                    (Test-Path (Join-Path $h.FullName 'parallel\PYLAUNCH\render_authority_measurement_entry.py'))) {
                    $repo = $h.FullName
                    break
                }
            }
        } catch {}
        if ($repo) { break }
    }
}

if (-not $repo) {
    Stop-Wof "没有找到 GitHub Desktop 下载的 wof-ai-private 项目。请把这个窗口截图发给 ChatGPT。" 20
}

Write-Host "找到项目："
Write-Host $repo
Write-Host ""

$gitExe = $null
$gitCmd = Get-Command git.exe -ErrorAction SilentlyContinue
if ($gitCmd) {
    $gitExe = $gitCmd.Source
}
if (-not $gitExe) {
    $ghRoot = Join-Path $env:LOCALAPPDATA 'GitHubDesktop'
    if (Test-Path $ghRoot) {
        $gitCandidate = Get-ChildItem -LiteralPath $ghRoot -Filter git.exe -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -match '\\resources\\app\\git\\cmd\\git\.exe$' } |
            Select-Object -First 1
        if ($gitCandidate) { $gitExe = $gitCandidate.FullName }
    }
}
if (-not $gitExe) {
    Stop-Wof "没有找到 Git。请先打开 GitHub Desktop，确认项目能正常显示。" 21
}

$dirty = & $gitExe -C $repo status --porcelain --untracked-files=all 2>$null
if ($LASTEXITCODE -ne 0) {
    Stop-Wof "无法读取项目 Git 状态。" 22
}
if ($dirty) {
    Write-Host "项目里存在未提交 Changes，为避免覆盖文件已停止。"
    Stop-Wof "请打开 GitHub Desktop，把 Changes 页面截图发给 ChatGPT。" 23
}

Write-Host "[1/4] 同步 GitHub 最新 main..."
& $gitExe -C $repo fetch --quiet 'https://github.com/ouyong520/wof-ai-private.git' '+refs/heads/main:refs/remotes/wof-alpha-authority/main'
if ($LASTEXITCODE -ne 0) {
    Stop-Wof "连接 GitHub 获取 main 失败，请检查网络。" 24
}

$headSha = (& $gitExe -C $repo rev-parse HEAD).Trim()
$mainSha = (& $gitExe -C $repo rev-parse refs/remotes/wof-alpha-authority/main).Trim()
if (-not $headSha -or -not $mainSha) {
    Stop-Wof "无法确认 Git SHA。" 25
}

if ($headSha -ne $mainSha) {
    Write-Host "本地不是最新 main，正在安全更新..."
    & $gitExe -C $repo merge --ff-only refs/remotes/wof-alpha-authority/main
    if ($LASTEXITCODE -ne 0) {
        Stop-Wof "无法自动更新。请打开 GitHub Desktop 点 Pull origin 后再试。" 26
    }
    $headSha = (& $gitExe -C $repo rev-parse HEAD).Trim()
}

Write-Host "当前 exact main：$headSha"
Write-Host ""

Write-Host "[2/4] 关闭旧 WOF Alpha 进程..."
try {
    Get-CimInstance Win32_Process |
        Where-Object {
            $_.Name -match '^pythonw?\.exe$' -and
            $_.CommandLine -like '*render_authority_measurement_entry.py*'
        } |
        ForEach-Object {
            Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        }
} catch {}

$venv = Join-Path $env:LOCALAPPDATA 'WOF Alpha Current Main\venv'
$py = Join-Path $venv 'Scripts\python.exe'

if (-not (Test-Path $py)) {
    Write-Host "[3/4] 第一次运行，创建 Alpha Python 环境..."
    $pyLauncher = Get-Command py.exe -ErrorAction SilentlyContinue
    $pythonExe = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        & $pyLauncher.Source -3 -m venv $venv
    } elseif ($pythonExe) {
        & $pythonExe.Source -m venv $venv
    } else {
        Stop-Wof "电脑没有找到 Python 3。请把这个窗口截图发给 ChatGPT。" 28
    }
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $py)) {
        Stop-Wof "创建 Python 环境失败。" 29
    }
}

Write-Host "[3/4] 检查 Alpha 依赖..."
$requirements = Join-Path $repo 'parallel\PYLAUNCH\requirements.txt'
& $py -m pip install --disable-pip-version-check -q -r $requirements
if ($LASTEXITCODE -ne 0) {
    Stop-Wof "安装 Alpha 依赖失败，请检查网络。" 30
}

$results = Join-Path $env:USERPROFILE 'Documents\WOF_RESULTS'
New-Item -ItemType Directory -Path $results -Force | Out-Null

$env:WOF_ALPHA_CURRENT_MAIN_SOURCE = '1'
$env:WOF_ALPHA_ACCEPTANCE_COMMIT = $headSha
$env:WOF_ALPHA_LIVE_ACCEPTANCE_HOLD = '1'
$env:WOF_ALPHA_MENU6_ATTACH_ONLY = '1'

$entry = Join-Path $repo 'parallel\PYLAUNCH\render_authority_measurement_entry.py'
$workdir = Join-Path $repo 'parallel\PYLAUNCH'

Write-Host "[4/4] 启动 WOF Alpha..."
Write-Host ""
Write-Host "不用按菜单 6。"
Write-Host "游戏已打开的话会直接复用。"
Write-Host "只有自动定位失败时，才会要求你点一次 P1 真实头部。"
Write-Host ""
Write-Host "SHA：$headSha"
Write-Host "=================================================="
Write-Host ""

Push-Location $workdir
try {
    & $py $entry --root $repo --output-root $results
    $rc = $LASTEXITCODE
} catch {
    Write-Host "启动异常：$($_.Exception.Message)"
    $rc = 99
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "WOF Alpha 已结束，代码：$rc"
Write-Host "结果目录：$results"
Write-Host "如果出现 BLOCKED，直接截图给 ChatGPT。"
Read-Host "按回车关闭"
exit $rc
