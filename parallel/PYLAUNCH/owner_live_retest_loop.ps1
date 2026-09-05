$ErrorActionPreference = 'Stop'

$Base = Join-Path $env:LOCALAPPDATA 'WOF_ALPHA_CURRENT_MAIN'
$Repo = Join-Path $Base 'repo'
$Remote = 'git@wof-alpha-github:ouyong520/wof-ai-private.git'
$Results = Join-Path $env:USERPROFILE 'Documents\WOF_RESULTS'
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
    Write-Host "Starting Alpha: $Sha"
    Write-Host 'Chrome is owned by Alpha, but YOU choose the site/room.'
    Write-Host 'After you send a screenshot, leave this window open.'
    Write-Host 'When a new fix reaches main, it will update and restart automatically.'
    Write-Host '--------------------------------------------------'
    Write-Host ''

    Start-Process -FilePath $script:Py `
        -ArgumentList @($entry, '--root', $Repo, '--output-root', $Results, '--browser', 'chrome') `
        -WorkingDirectory $workdir | Out-Null
}

function Fetch-Latest {
    & $script:GitExe -C $Repo fetch --quiet $Remote '+refs/heads/main:refs/remotes/origin/main'
    return ($LASTEXITCODE -eq 0)
}

function Current-SelfHash {
    try { return (Get-FileHash -LiteralPath $SelfPath -Algorithm SHA256).Hash }
    catch { return '' }
}

function Restart-SelfIfChanged([string]$BeforeHash) {
    $afterHash = Current-SelfHash
    if (-not $BeforeHash -or -not $afterHash -or $BeforeHash -eq $afterHash) { return }

    Write-Host 'The live retest controller updated itself; restarting it automatically...'
    Stop-AlphaRuntime
    try {
        $script:Mutex.ReleaseMutex()
        $script:MutexReleased = $true
    } catch {}
    Start-Process -FilePath 'powershell.exe' `
        -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $SelfPath) `
        -WorkingDirectory (Split-Path $SelfPath -Parent) | Out-Null
    exit 0
}

$createdNew = $false
$script:Mutex = New-Object System.Threading.Mutex($true, 'Local\WOF_ALPHA_LIVE_RETEST_LOOP', [ref]$createdNew)
if (-not $createdNew) {
    Write-Host 'WOF Alpha live retest is already running.'
    Start-Sleep -Seconds 2
    exit 0
}

try {
    if (-not (Test-Path (Join-Path $Repo '.git'))) {
        Stop-Wof "Managed Alpha repo was not found: $Repo" 20
    }

    $git = Get-Command git.exe -ErrorAction SilentlyContinue
    if (-not $git) { Stop-Wof 'Git was not found.' 21 }
    $script:GitExe = $git.Source

    Write-Host ''
    Write-Host '=================================================='
    Write-Host '          WOF Alpha Live Retest'
    Write-Host '=================================================='
    Write-Host 'ONE test entry. No versioned launchers.'
    Write-Host 'Screenshot -> fix on main -> auto update -> auto restart.'
    Write-Host ''

    Ensure-PythonEnvironment

    $current = Git-Text @('-C', $Repo, 'rev-parse', '--verify', 'HEAD')
    if (-not $current) { Stop-Wof 'Could not read current Alpha commit.' 22 }

    Write-Host 'Checking latest Alpha over SSH 22...'
    if (Fetch-Latest) {
        $remoteSha = Git-Text @('-C', $Repo, 'rev-parse', '--verify', 'origin/main')
        if ($remoteSha -and $remoteSha -ne $current) {
            Write-Host "Applying latest main: $remoteSha"
            $selfBefore = Current-SelfHash
            Stop-AlphaRuntime
            & $script:GitExe -C $Repo reset --hard origin/main | Out-Null
            if ($LASTEXITCODE -ne 0) { Stop-Wof 'Could not apply latest Alpha.' 23 }
            & $script:GitExe -C $Repo clean -fd | Out-Null
            Restart-SelfIfChanged $selfBefore
            Ensure-PythonEnvironment
            $current = $remoteSha
        }
    } else {
        Write-Host 'SSH update is not ready; running the current cached Alpha.'
        Write-Host 'The permanent workflow becomes automatic as soon as SSH authorization is completed once.'
    }

    Stop-AlphaRuntime
    Start-AlphaRuntime $current
    $lastApplied = $current

    Write-Host ''
    Write-Host "Watching main every $PollSeconds seconds."
    Write-Host 'You do not need to relaunch anything between fixes.'
    Write-Host 'Close this window only when the testing session is finished.'
    Write-Host ''

    while ($true) {
        Start-Sleep -Seconds $PollSeconds
        if (-not (Fetch-Latest)) { continue }
        $remoteSha = Git-Text @('-C', $Repo, 'rev-parse', '--verify', 'origin/main')
        if (-not $remoteSha -or $remoteSha -eq $lastApplied) { continue }

        Write-Host ''
        Write-Host "New Alpha detected: $remoteSha"
        Write-Host 'Downloading changed files and restarting automatically...'

        $selfBefore = Current-SelfHash
        Stop-AlphaRuntime
        & $script:GitExe -C $Repo reset --hard origin/main | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host 'Update apply failed; keeping the watcher alive for the next retry.'
            continue
        }
        & $script:GitExe -C $Repo clean -fd | Out-Null
        Restart-SelfIfChanged $selfBefore
        Ensure-PythonEnvironment
        $lastApplied = $remoteSha
        Start-AlphaRuntime $lastApplied
        Write-Host 'Updated and reopened. Continue testing the same way.'
    }
}
finally {
    if (-not $script:MutexReleased) {
        try { $script:Mutex.ReleaseMutex() } catch {}
    }
    try { $script:Mutex.Dispose() } catch {}
}
