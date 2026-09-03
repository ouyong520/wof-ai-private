param(
    [string]$Repo
)

$ErrorActionPreference = 'Stop'

function Stop-Wof([string]$Message, [int]$Code = 1) {
    Write-Host ''
    Write-Host '=============================================='
    Write-Host $Message
    Write-Host '=============================================='
    Write-Host ''
    Read-Host 'Press Enter to close'
    exit $Code
}

if (-not $Repo) {
    $Repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
}
$Repo = (Resolve-Path $Repo).Path

if (-not (Test-Path (Join-Path $Repo '.git'))) {
    Stop-Wof 'This launcher must run from the wof-ai-private Git checkout.' 20
}
if (-not (Test-Path (Join-Path $Repo 'parallel\PYLAUNCH\render_authority_measurement_entry.py'))) {
    Stop-Wof 'Alpha runtime file is missing.' 21
}

Write-Host ''
Write-Host '=================================================='
Write-Host '             WOF Alpha Current Main'
Write-Host '=================================================='
Write-Host "Repo: $Repo"
Write-Host 'The game may stay open.'
Write-Host ''

$gitExe = $null
$git = Get-Command git.exe -ErrorAction SilentlyContinue
if ($git) {
    $gitExe = $git.Source
}
if (-not $gitExe) {
    $ghRoot = Join-Path $env:LOCALAPPDATA 'GitHubDesktop'
    if (Test-Path $ghRoot) {
        $candidate = Get-ChildItem -LiteralPath $ghRoot -Filter git.exe -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -match '\\resources\\app\\git\\cmd\\git\.exe$' } |
            Select-Object -First 1
        if ($candidate) { $gitExe = $candidate.FullName }
    }
}
if (-not $gitExe) {
    Stop-Wof 'Git was not found. Open GitHub Desktop first.' 22
}

$dirty = & $gitExe -C $Repo status --porcelain --untracked-files=all 2>$null
if ($LASTEXITCODE -ne 0) {
    Stop-Wof 'Could not read Git status.' 23
}
if ($dirty) {
    Write-Host 'Local uncommitted changes were found.'
    Stop-Wof 'Open GitHub Desktop and send a screenshot of the Changes tab.' 24
}

Write-Host '[1/4] Fetching latest main...'
& $gitExe -C $Repo fetch --quiet 'https://github.com/ouyong520/wof-ai-private.git' '+refs/heads/main:refs/remotes/wof-alpha-authority/main'
if ($LASTEXITCODE -ne 0) {
    Stop-Wof 'Could not fetch latest main from GitHub.' 25
}

$headSha = (& $gitExe -C $Repo rev-parse HEAD).Trim()
$mainSha = (& $gitExe -C $Repo rev-parse refs/remotes/wof-alpha-authority/main).Trim()
if (-not $headSha -or -not $mainSha) {
    Stop-Wof 'Could not resolve Git SHA.' 26
}

if ($headSha -ne $mainSha) {
    Write-Host 'Updating local checkout with fast-forward only...'
    & $gitExe -C $Repo merge --ff-only refs/remotes/wof-alpha-authority/main
    if ($LASTEXITCODE -ne 0) {
        Stop-Wof 'Fast-forward failed. Use Pull origin in GitHub Desktop, then run again.' 27
    }
    $headSha = (& $gitExe -C $Repo rev-parse HEAD).Trim()
}
if ($headSha -ne $mainSha) {
    Stop-Wof 'Local checkout is still not exact current main.' 28
}

Write-Host "Exact main: $headSha"
Write-Host ''

Write-Host '[2/4] Closing old WOF Alpha processes...'
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
    Write-Host '[3/4] Creating Python environment...'
    $pyLauncher = Get-Command py.exe -ErrorAction SilentlyContinue
    $pythonExe = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        & $pyLauncher.Source -3 -m venv $venv
    } elseif ($pythonExe) {
        & $pythonExe.Source -m venv $venv
    } else {
        Stop-Wof 'Python 3 was not found.' 29
    }
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $py)) {
        Stop-Wof 'Could not create the Python environment.' 30
    }
}

Write-Host '[3/4] Checking Alpha dependencies...'
& $py -m pip install --disable-pip-version-check -q -r (Join-Path $Repo 'parallel\PYLAUNCH\requirements.txt')
if ($LASTEXITCODE -ne 0) {
    Stop-Wof 'Could not install Alpha dependencies.' 31
}

$results = Join-Path $env:USERPROFILE 'Documents\WOF_RESULTS'
New-Item -ItemType Directory -Path $results -Force | Out-Null

$env:WOF_ALPHA_CURRENT_MAIN_SOURCE = '1'
$env:WOF_ALPHA_ACCEPTANCE_COMMIT = $headSha
$env:WOF_ALPHA_LIVE_ACCEPTANCE_HOLD = '1'
$env:WOF_ALPHA_MENU6_ATTACH_ONLY = '1'

$entry = Join-Path $Repo 'parallel\PYLAUNCH\render_authority_measurement_entry.py'
$workdir = Join-Path $Repo 'parallel\PYLAUNCH'

Write-Host '[4/4] Starting WOF Alpha...'
Write-Host 'No menu selection is needed.'
Write-Host 'If one-click fallback is requested, click the real P1 head once.'
Write-Host ''

Push-Location $workdir
try {
    & $py $entry --root $Repo --output-root $results
    $rc = $LASTEXITCODE
} catch {
    Write-Host "Start exception: $($_.Exception.Message)"
    $rc = 99
} finally {
    Pop-Location
}

Write-Host ''
Write-Host "WOF Alpha exited with code: $rc"
Write-Host "Results: $results"
if ($rc -ne 0) {
    Write-Host 'Send a screenshot of this window or the BLOCKED notification to ChatGPT.'
}
Read-Host 'Press Enter to close'
exit $rc
