$ErrorActionPreference = 'Stop'

$Base = Join-Path $env:LOCALAPPDATA 'WOF_ALPHA_CURRENT_MAIN'
$Repo = Join-Path $Base 'repo'
$Remote = 'git@wof-alpha-github:ouyong520/wof-ai-private.git'
$LiveBranch = 'alpha-live'
$RemoteRef = 'origin/alpha-live'
$Results = Join-Path $env:USERPROFILE 'Documents\WOF_RESULTS'
$LatestFeedback = Join-Path $Results 'LATEST_ALPHA_FEEDBACK.txt'
$PollSeconds = 6
$SelfPath = $MyInvocation.MyCommand.Path
$script:MutexReleased = $false

function Stop-Wof([string]$Message, [int]$Code = 1) {
    Write-Host ''
    Write-Host '=============================================='
    Write-Host $Message
    Write-Host '=============================================='
    Write-Host ''
    Read-Host 'Press Enter to close'
    exit $Code
}

function Git-Text([string[]]$Args) {
    $out = & $script:GitExe @Args 2>$null
    if ($LASTEXITCODE -ne 0) { return $null }
    return (($out | Out-String).Trim())
}

function Write-LatestFeedback([string]$Status, [string]$Sha, [string]$Message) {
    try {
        New-Item -ItemType Directory -Path $Results -Force | Out-Null
        $lines = @(
            'WOF Alpha latest feedback',
            ('status=' + $Status),
            ('alphaLiveCommit=' + $Sha),
            ('updatedAt=' + (Get-Date).ToString('yyyy-MM-dd HH:mm:ss zzz')),
            ('resultsFolder=' + $Results),
            'updateChannel=alpha-live over GitHub SSH port 22',
            'browserWofPolicy=preserve current Browser/WOF when safe',
            ('message=' + $Message),
            'ownerFeedback=Send one screenshot or one-line observation for this commit.'
        )
        [System.IO.File]::WriteAllLines(
            $LatestFeedback,
            $lines,
            (New-Object System.Text.UTF8Encoding($false))
        )
    } catch {}
}

function Stop-AlphaRuntime {
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
}

function Ensure-PythonEnvironment {
    $script:Venv = Join-Path $env:LOCALAPPDATA 'WOF Alpha Current Main\venv'
    $script:Py = Join-Path $script:Venv 'Scripts\python.exe'
    $requirements = Join-Path $Repo 'parallel\PYLAUNCH\requirements.txt'
    if (-not (Test-Path $requirements)) { Stop-Wof 'Alpha requirements.txt is missing.' 31 }

    if (-not (Test-Path $script:Py)) {
        Write-Host 'First local setup: creating Python environment...'
        $launcher = Get-Command py.exe -ErrorAction SilentlyContinue
        $python = Get-Command python.exe -ErrorAction SilentlyContinue
        if ($launcher) { & $launcher.Source -3 -m venv $script:Venv }
        elseif ($python) { & $python.Source -m venv $script:Venv }
        else { Stop-Wof 'Python 3 was not found.' 32 }
        if ($LASTEXITCODE -ne 0 -or -not (Test-Path $script:Py)) {
            Stop-Wof 'Could not create the Python environment.' 33
        }
    }

    $stamp = Join-Path $script:Venv '.wof_alpha_requirements.sha256'
    $hash = (Get-FileHash -LiteralPath $requirements -Algorithm SHA256).Hash
    $oldHash = ''
    if (Test-Path $stamp) {
        $oldHash = (Get-Content -LiteralPath $stamp -Raw -ErrorAction SilentlyContinue).Trim()
    }
    if ($oldHash -ne $hash) {
        Write-Host 'Alpha dependencies changed; updating once...'
        & $script:Py -m pip install --disable-pip-version-check -q -r $requirements
        if ($LASTEXITCODE -ne 0) { Stop-Wof 'Could not install Alpha dependencies.' 34 }
        Set-Content -LiteralPath $stamp -Value $hash -Encoding ASCII
    }
}

function Start-AlphaRuntime([string]$Sha) {
    $entry = Join-Path $Repo 'parallel\PYLAUNCH\render_authority_measurement_entry.py'
    $workdir = Join-Path $Repo 'parallel\PYLAUNCH'
    if (-not (Test-Path $entry)) { Stop-Wof 'Alpha runtime entry is missing.' 35 }

    New-Item -ItemType Directory -Path $Results -Force | Out-Null
    $env:WOF_ALPHA_CURRENT_MAIN_SOURCE = '1'
    $env:WOF_ALPHA_ACCEPTANCE_COMMIT = $Sha
    $env:WOF_ALPHA_LIVE_ACCEPTANCE_HOLD = '1'
    $env:WOF_ALPHA_OWNER_NAVIGATES = '1'
    Remove-Item Env:WOF_ALPHA_MENU6_ATTACH_ONLY -ErrorAction SilentlyContinue

    Write-Host ''
    Write-Host '--------------------------------------------------'
    Write-Host "Starting controlled Alpha live release: $Sha"
    Write-Host 'The Alpha runtime is restarting; keep the current Browser/WOF when possible.'
    Write-Host 'Latest feedback path: Documents\WOF_RESULTS\LATEST_ALPHA_FEEDBACK.txt'
    Write-Host '--------------------------------------------------'
    Write-Host ''

    Start-Process -FilePath $script:Py `
        -ArgumentList @($entry, '--root', $Repo, '--output-root', $Results, '--browser', 'chrome') `
        -WorkingDirectory $workdir | Out-Null
    Write-LatestFeedback 'RUNNING' $Sha 'Controlled Alpha runtime started.'
}

function Fetch-Latest {
    & $script:GitExe -C $Repo fetch --quiet origin '+refs/heads/alpha-live:refs/remotes/origin/alpha-live'
    return ($LASTEXITCODE -eq 0)
}

function Current-SelfHash {
    try { return (Get-FileHash -LiteralPath $SelfPath -Algorithm SHA256).Hash }
    catch { return '' }
}

function Restart-SelfIfChanged([string]$BeforeHash, [string]$Sha) {
    $afterHash = Current-SelfHash
    if (-not $BeforeHash -or -not $afterHash -or $BeforeHash -eq $afterHash) { return }

    Write-Host 'The Alpha live controller updated itself; restarting the controller safely...'
    Write-LatestFeedback 'CONTROLLER_RESTART' $Sha 'Updater changed and is restarting itself.'
    Stop-AlphaRuntime
    try {
        $script:Mutex.ReleaseMutex()
        $script:MutexReleased = $true
    } catch {}
    Start-Process -FilePath 'powershell.exe' `
        -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ('"' + $SelfPath + '"')) `
        -WorkingDirectory (Split-Path $SelfPath -Parent) | Out-Null
    exit 0
}

function Release-HasRequiredFiles([string]$Sha) {
    foreach ($path in @(
        'WOF_ALPHA_TEST.cmd',
        'parallel/PYLAUNCH/owner_live_retest_loop.ps1',
        'parallel/PYLAUNCH/render_authority_measurement_entry.py',
        'parallel/PYLAUNCH/requirements.txt'
    )) {
        & $script:GitExe -C $Repo cat-file -e ($Sha + ':' + $path) 2>$null
        if ($LASTEXITCODE -ne 0) { return $false }
    }
    return $true
}

function Apply-LiveRelease([string]$TargetSha, [string]$PreviousSha) {
    if (-not (Release-HasRequiredFiles $TargetSha)) {
        Write-LatestFeedback 'RELEASE_REJECTED' $PreviousSha "alpha-live $TargetSha is missing required permanent-runtime files."
        Write-Host "Rejected incomplete alpha-live release: $TargetSha"
        return $false
    }

    $selfBefore = Current-SelfHash
    Write-LatestFeedback 'UPDATING' $PreviousSha "Applying controlled alpha-live release $TargetSha."
    Stop-AlphaRuntime
    & $script:GitExe -C $Repo reset --hard $TargetSha | Out-Null
    if ($LASTEXITCODE -ne 0) {
        & $script:GitExe -C $Repo reset --hard $PreviousSha | Out-Null
        Write-LatestFeedback 'UPDATE_APPLY_FAILED' $PreviousSha "Could not apply $TargetSha; restored prior commit."
        Ensure-PythonEnvironment
        Start-AlphaRuntime $PreviousSha
        return $false
    }
    & $script:GitExe -C $Repo clean -fd | Out-Null
    Restart-SelfIfChanged $selfBefore $TargetSha
    Ensure-PythonEnvironment
    Start-AlphaRuntime $TargetSha
    return $true
}

$createdNew = $false
$script:Mutex = New-Object System.Threading.Mutex($true, 'Local\WOF_ALPHA_LIVE_RETEST_LOOP', [ref]$createdNew)
if (-not $createdNew) {
    Write-Host 'WOF Alpha permanent test controller is already running.'
    Start-Sleep -Seconds 2
    exit 0
}

try {
    if (-not (Test-Path (Join-Path $Repo '.git'))) {
        Stop-Wof "Managed Alpha repo was not found: $Repo. Run WOF_ALPHA_SETUP_ONCE.cmd once." 20
    }

    $git = Get-Command git.exe -ErrorAction SilentlyContinue
    if (-not $git) { Stop-Wof 'Git for Windows was not found.' 21 }
    $script:GitExe = $git.Source

    & $script:GitExe -C $Repo remote set-url origin $Remote
    if ($LASTEXITCODE -ne 0) { Stop-Wof 'Could not configure the Alpha SSH remote.' 22 }

    Write-Host ''
    Write-Host '=================================================='
    Write-Host '          WOF Alpha Permanent Test'
    Write-Host '=================================================='
    Write-Host 'ONE Desktop entry. Controlled alpha-live updates only.'
    Write-Host 'GitHub update transport: SSH port 22.'
    Write-Host ''

    Ensure-PythonEnvironment

    $current = Git-Text @('-C', $Repo, 'rev-parse', '--verify', 'HEAD')
    if (-not $current) { Stop-Wof 'Could not read current Alpha commit.' 23 }

    Write-LatestFeedback 'STARTING' $current 'Permanent controller started; checking alpha-live.'
    Stop-AlphaRuntime
    Start-AlphaRuntime $current

    Write-Host 'Checking controlled alpha-live over SSH 22...'
    if (Fetch-Latest) {
        $remoteSha = Git-Text @('-C', $Repo, 'rev-parse', '--verify', $RemoteRef)
        if ($remoteSha -and $remoteSha -ne $current) {
            Write-Host "Applying controlled alpha-live release: $remoteSha"
            if (Apply-LiveRelease $remoteSha $current) {
                $current = $remoteSha
            }
        }
    } else {
        Write-LatestFeedback 'SSH_UPDATE_UNAVAILABLE' $current 'Could not fetch alpha-live over SSH 22; current cached Alpha remains runnable.'
        Write-Host 'SSH update is temporarily unavailable; current cached Alpha remains running.'
    }

    $lastApplied = $current
    Write-Host ''
    Write-Host "Watching alpha-live every $PollSeconds seconds."
    Write-Host 'Unrelated main/docs commits do not restart Alpha.'
    Write-Host 'You do not need a new ZIP, CMD, or path between fixes.'
    Write-Host ''

    while ($true) {
        Start-Sleep -Seconds $PollSeconds
        if (-not (Fetch-Latest)) { continue }
        $remoteSha = Git-Text @('-C', $Repo, 'rev-parse', '--verify', $RemoteRef)
        if (-not $remoteSha -or $remoteSha -eq $lastApplied) { continue }

        Write-Host ''
        Write-Host "New controlled Alpha release detected: $remoteSha"
        if (Apply-LiveRelease $remoteSha $lastApplied) {
            $lastApplied = $remoteSha
            Write-Host 'Alpha runtime updated and restarted. Continue testing in the same Browser/WOF when available.'
        } else {
            Write-Host 'Update was rejected/rolled back; current Alpha remains active.'
        }
    }
}
finally {
    if (-not $script:MutexReleased) {
        try { $script:Mutex.ReleaseMutex() } catch {}
    }
    try { $script:Mutex.Dispose() } catch {}
}
