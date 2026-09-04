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

function Test-WofRepo([string]$Path) {
    if (-not $Path) { return $false }
    return (Test-Path (Join-Path $Path '.git')) -and
           (Test-Path (Join-Path $Path 'parallel\PYLAUNCH\render_authority_measurement_entry.py'))
}

function Find-WofRepo {
    $candidates = New-Object System.Collections.Generic.List[string]
    if ($env:WOF_ALPHA_REPO) { $candidates.Add($env:WOF_ALPHA_REPO) }
    if ($env:USERPROFILE) {
        $candidates.Add((Join-Path $env:USERPROFILE 'Documents\GitHub\wof-ai-private'))
        $candidates.Add((Join-Path $env:USERPROFILE 'Desktop\wof-ai-private'))
        $candidates.Add((Join-Path $env:USERPROFILE 'Downloads\wof-ai-private'))
        $candidates.Add((Join-Path $env:USERPROFILE 'source\repos\wof-ai-private'))
        $candidates.Add((Join-Path $env:USERPROFILE 'wof-ai-private'))
    }
    foreach ($drive in 'C','D','E','F','G') {
        $root = $drive + ':\'
        if (Test-Path $root) {
            $candidates.Add((Join-Path $root 'wof-ai-private'))
            $candidates.Add((Join-Path $root 'GitHub\wof-ai-private'))
            $candidates.Add((Join-Path $root 'github\wof-ai-private'))
            $candidates.Add((Join-Path $root 'Projects\wof-ai-private'))
            $candidates.Add((Join-Path $root 'projects\wof-ai-private'))
            $candidates.Add((Join-Path $root 'Code\wof-ai-private'))
            $candidates.Add((Join-Path $root 'code\wof-ai-private'))
        }
    }
    foreach ($candidate in ($candidates | Select-Object -Unique)) {
        if (Test-WofRepo $candidate) { return (Resolve-Path $candidate).Path }
    }
    return $null
}

if (-not $Repo) { $Repo = Find-WofRepo }
if (-not $Repo) {
    Stop-Wof 'Could not find the wof-ai-private Git checkout.' 20
}
$Repo = (Resolve-Path $Repo).Path
if (-not (Test-WofRepo $Repo)) {
    Stop-Wof 'The located folder is not a valid wof-ai-private Git checkout.' 21
}

Write-Host ''
Write-Host '=================================================='
Write-Host '             WOF Alpha Fast Retest'
Write-Host '=================================================='
Write-Host "Repo: $Repo"
Write-Host 'The game may stay open.'
Write-Host ''

$gitExe = $null
$git = Get-Command git.exe -ErrorAction SilentlyContinue
if ($git) { $gitExe = $git.Source }
if (-not $gitExe) {
    $ghRoot = Join-Path $env:LOCALAPPDATA 'GitHubDesktop'
    if (Test-Path $ghRoot) {
        $candidate = Get-ChildItem -LiteralPath $ghRoot -Filter git.exe -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -match '\\resources\\app\\git\\cmd\\git\.exe$' } |
            Select-Object -First 1
        if ($candidate) { $gitExe = $candidate.FullName }
    }
}
if (-not $gitExe) { Stop-Wof 'Git was not found.' 22 }

$dirty = & $gitExe -C $Repo status --porcelain --untracked-files=all 2>$null
if ($LASTEXITCODE -ne 0) { Stop-Wof 'Could not read Git status.' 23 }
if ($dirty) { Stop-Wof 'Local uncommitted changes were found.' 24 }

$managedRepo = $null
if ($env:LOCALAPPDATA) { $managedRepo = Join-Path $env:LOCALAPPDATA 'WOF_ALPHA_CURRENT_MAIN\repo' }
$isManagedRepo = $false
if ($managedRepo) {
    try { $isManagedRepo = ((Resolve-Path $Repo).Path -ieq (Resolve-Path $managedRepo -ErrorAction Stop).Path) } catch {}
}

if ($isManagedRepo) {
    Write-Host '[1/4] V4 already updated the managed repo; skipping duplicate network fetch.'
    $headSha = (& $gitExe -C $Repo rev-parse HEAD).Trim()
    $originSha = (& $gitExe -C $Repo rev-parse origin/main 2>$null).Trim()
    if (-not $headSha -or -not $originSha -or $headSha -ne $originSha) {
        Stop-Wof 'Managed repo is not exact origin/main. Run WOF_ALPHA_RUN_V4.cmd again.' 28
    }
} else {
    Write-Host '[1/4] Fetching latest main...'
    & $gitExe -C $Repo fetch --quiet 'https://github.com/ouyong520/wof-ai-private.git' '+refs/heads/main:refs/remotes/wof-alpha-authority/main'
    if ($LASTEXITCODE -ne 0) { Stop-Wof 'Could not fetch latest main from GitHub.' 25 }
    $headSha = (& $gitExe -C $Repo rev-parse HEAD).Trim()
    $mainSha = (& $gitExe -C $Repo rev-parse refs/remotes/wof-alpha-authority/main).Trim()
    if (-not $headSha -or -not $mainSha) { Stop-Wof 'Could not resolve Git SHA.' 26 }
    if ($headSha -ne $mainSha) {
        & $gitExe -C $Repo merge --ff-only refs/remotes/wof-alpha-authority/main
        if ($LASTEXITCODE -ne 0) { Stop-Wof 'Fast-forward failed.' 27 }
        $headSha = (& $gitExe -C $Repo rev-parse HEAD).Trim()
    }
    if ($headSha -ne $mainSha) { Stop-Wof 'Local checkout is still not exact current main.' 28 }
}

Write-Host "Exact main: $headSha"
Write-Host ''

Write-Host '[2/4] Closing old WOF Alpha processes...'
try {
    Get-CimInstance Win32_Process |
        Where-Object { $_.Name -match '^pythonw?\.exe$' -and $_.CommandLine -like '*render_authority_measurement_entry.py*' } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
} catch {}

$venv = Join-Path $env:LOCALAPPDATA 'WOF Alpha Current Main\venv'
$py = Join-Path $venv 'Scripts\python.exe'
$venvCreated = $false
if (-not (Test-Path $py)) {
    Write-Host '[3/4] First setup: creating Python environment...'
    $pyLauncher = Get-Command py.exe -ErrorAction SilentlyContinue
    $pythonExe = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($pyLauncher) { & $pyLauncher.Source -3 -m venv $venv }
    elseif ($pythonExe) { & $pythonExe.Source -m venv $venv }
    else { Stop-Wof 'Python 3 was not found.' 29 }
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $py)) { Stop-Wof 'Could not create the Python environment.' 30 }
    $venvCreated = $true
}

$requirements = Join-Path $Repo 'parallel\PYLAUNCH\requirements.txt'
$reqStamp = Join-Path $venv '.wof_alpha_requirements.sha256'
$reqHash = (Get-FileHash -LiteralPath $requirements -Algorithm SHA256).Hash
$installedHash = ''
if (Test-Path $reqStamp) { $installedHash = (Get-Content -LiteralPath $reqStamp -Raw -ErrorAction SilentlyContinue).Trim() }
if ($venvCreated -or $installedHash -ne $reqHash) {
    Write-Host '[3/4] Dependencies changed; installing once...'
    & $py -m pip install --disable-pip-version-check -q -r $requirements
    if ($LASTEXITCODE -ne 0) { Stop-Wof 'Could not install Alpha dependencies.' 31 }
    Set-Content -LiteralPath $reqStamp -Value $reqHash -Encoding ASCII
} else {
    Write-Host '[3/4] Dependencies unchanged; using cached environment.'
}

$results = Join-Path $env:USERPROFILE 'Documents\WOF_RESULTS'
New-Item -ItemType Directory -Path $results -Force | Out-Null

$env:WOF_ALPHA_CURRENT_MAIN_SOURCE = '1'
$env:WOF_ALPHA_ACCEPTANCE_COMMIT = $headSha
$env:WOF_ALPHA_LIVE_ACCEPTANCE_HOLD = '1'
Remove-Item Env:WOF_ALPHA_MENU6_ATTACH_ONLY -ErrorAction SilentlyContinue

$entry = Join-Path $Repo 'parallel\PYLAUNCH\render_authority_measurement_entry.py'
$workdir = Join-Path $Repo 'parallel\PYLAUNCH'

Write-Host '[4/4] Starting WOF Alpha...'
Write-Host 'No reinstall or redownload is needed for later retests.'
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

$feedback = Join-Path $results 'WOF_SEND_ME.zip'
$packages = Join-Path $results 'packages'
if (Test-Path $packages) {
    $latest = Get-ChildItem -LiteralPath $packages -Filter 'WOF_LIVE_ACCEPTANCE_*.zip' -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latest) {
        Copy-Item -LiteralPath $latest.FullName -Destination $feedback -Force
    }
}

Write-Host ''
Write-Host "WOF Alpha exited with code: $rc"
Write-Host "Results: $results"
if (Test-Path $feedback) { Write-Host "Feedback bundle: $feedback" }
if ($rc -ne 0) { Write-Host 'Send the BLOCKED screenshot, or upload WOF_SEND_ME.zip if requested.' }
Read-Host 'Press Enter to close'
exit $rc
