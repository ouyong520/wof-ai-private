$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = 'WOF Alpha 一键直接运行'

function Stop-Wof([string]$Message, [int]$Code = 1) {
    Write-Host ''
    Write-Host '=============================================='
    Write-Host $Message
    Write-Host '=============================================='
    Write-Host ''
    Read-Host '按回车关闭'
    exit $Code
}

$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
if (-not (Test-Path (Join-Path $repo '.git'))) {
    Stop-Wof '这个启动文件必须从 GitHub Desktop 的 wof-ai-private 项目目录运行。' 20
}
if (-not (Test-Path (Join-Path $repo 'parallel\PYLAUNCH\render_authority_measurement_entry.py'))) {
    Stop-Wof 'Alpha runtime 文件缺失。' 21
}

Write-Host ''
Write-Host '=================================================='
Write-Host '           WOF Alpha 一键直接运行'
Write-Host '=================================================='
Write-Host '游戏可以继续开着。'
Write-Host "项目：$repo"
Write-Host ''

$git = Get-Command git.exe -ErrorAction SilentlyContinue
if (-not $git) {
    $ghRoot = Join-Path $env:LOCALAPPDATA 'GitHubDesktop'
    if (Test-Path $ghRoot) {
        $candidate = Get-ChildItem -LiteralPath $ghRoot -Filter git.exe -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -match '\\resources\\app\\git\\cmd\\git\.exe$' } |
            Select-Object -First 1
        if ($candidate) { $gitExe = $candidate.FullName }
    }
} else {
    $gitExe = $git.Source
}
if (-not $gitExe) {
    Stop-Wof '没有找到 Git。请先打开 GitHub Desktop。' 22
}

$dirty = & $gitExe -C $repo status --porcelain --untracked-files=all 2>$null
if ($LASTEXITCODE -ne 0) { Stop-Wof '无法读取 Git 状态。' 23 }
if ($dirty) {
    Write-Host '项目里存在未提交 Changes，为避免覆盖文件已停止。'
    Stop-Wof '请把 GitHub Desktop 的 Changes 页面截图发给 ChatGPT。' 24
}

Write-Host '[1/4] 同步 GitHub 最新 main...'
& $gitExe -C $repo fetch --quiet 'https://github.com/ouyong520/wof-ai-private.git' '+refs/heads/main:refs/remotes/wof-alpha-authority/main'
if ($LASTEXITCODE -ne 0) { Stop-Wof '连接 GitHub 获取最新 main 失败。' 25 }

$headSha = (& $gitExe -C $repo rev-parse HEAD).Trim()
$mainSha = (& $gitExe -C $repo rev-parse refs/remotes/wof-alpha-authority/main).Trim()
if (-not $headSha -or -not $mainSha) { Stop-Wof '无法确认 Git SHA。' 26 }
if ($headSha -ne $mainSha) {
    Write-Host '本地不是最新 main，正在安全更新...'
    & $gitExe -C $repo merge --ff-only refs/remotes/wof-alpha-authority/main
    if ($LASTEXITCODE -ne 0) { Stop-Wof '无法自动更新，请在 GitHub Desktop 点 Pull origin 后再运行。' 27 }
    $headSha = (& $gitExe -C $repo rev-parse HEAD).Trim()
}
if ($headSha -ne $mainSha) { Stop-Wof '本地仍不是最新 main。' 28 }

Write-Host "当前 exact main：$headSha"
Write-Host ''

Write-Host '[2/4] 关闭旧 WOF Alpha 状态进程...'
try {
    Get-CimInstance Win32_Process |
        Where-Object { $_.Name -match '^pythonw?\.exe$' -and $_.CommandLine -like '*render_authority_measurement_entry.py*' } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
} catch {}

$venv = Join-Path $env:LOCALAPPDATA 'WOF Alpha Current Main\venv'
$py = Join-Path $venv 'Scripts\python.exe'
if (-not (Test-Path $py)) {
    Write-Host '[3/4] 第一次运行，创建 Alpha Python 环境...'
    $pyLauncher = Get-Command py.exe -ErrorAction SilentlyContinue
    $pythonExe = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        & $pyLauncher.Source -3 -m venv $venv
    } elseif ($pythonExe) {
        & $pythonExe.Source -m venv $venv
    } else {
        Stop-Wof '电脑没有找到 Python 3。把这个窗口截图发给 ChatGPT。' 29
    }
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $py)) { Stop-Wof '创建 Python 环境失败。' 30 }
}

Write-Host '[3/4] 检查 Alpha 依赖...'
& $py -m pip install --disable-pip-version-check -q -r (Join-Path $repo 'parallel\PYLAUNCH\requirements.txt')
if ($LASTEXITCODE -ne 0) { Stop-Wof '安装 Alpha 依赖失败，请检查网络。' 31 }

$results = Join-Path $env:USERPROFILE 'Documents\WOF_RESULTS'
New-Item -ItemType Directory -Path $results -Force | Out-Null
$env:WOF_ALPHA_CURRENT_MAIN_SOURCE = '1'
$env:WOF_ALPHA_ACCEPTANCE_COMMIT = $headSha
$env:WOF_ALPHA_LIVE_ACCEPTANCE_HOLD = '1'
$env:WOF_ALPHA_MENU6_ATTACH_ONLY = '1'

$entry = Join-Path $repo 'parallel\PYLAUNCH\render_authority_measurement_entry.py'
Write-Host '[4/4] 启动 WOF Alpha...'
Write-Host '不用按菜单 6。游戏已打开的话会直接复用。'
Write-Host '如果提示“需要一次点击 P1 真实头部”，只点一次自己人物的头。'
Write-Host ''

Push-Location (Join-Path $repo 'parallel\PYLAUNCH')
try {
    & $py $entry --root $repo --output-root $results
    $rc = $LASTEXITCODE
} catch {
    Write-Host "启动异常：$($_.Exception.Message)"
    $rc = 99
} finally {
    Pop-Location
}

Write-Host ''
Write-Host "WOF Alpha 已结束，代码：$rc"
Write-Host "结果目录：$results"
if ($rc -ne 0) { Write-Host '把这个窗口或右下角 BLOCKED 截图发给 ChatGPT。' }
Read-Host '按回车关闭'
exit $rc
