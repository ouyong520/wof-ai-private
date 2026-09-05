$ErrorActionPreference = 'Stop'

$Base = Join-Path $env:LOCALAPPDATA 'WOF_ALPHA_CURRENT_MAIN'
$Repo = Join-Path $Base 'repo'
$Key = Join-Path $env:USERPROFILE '.ssh\wof_alpha_github_ed25519'
$Pub = $Key + '.pub'
$SshConfig = Join-Path $env:USERPROFILE '.ssh\config'
$Remote = 'git@wof-alpha-github:ouyong520/wof-ai-private.git'
$LiveBranch = 'alpha-live'
$Desktop = [Environment]::GetFolderPath('Desktop')
$DesktopEntry = Join-Path $Desktop 'WOF_ALPHA_TEST.cmd'

function Stop-Wof([string]$Message, [int]$Code = 1) {
    Write-Host ''
    Write-Host '=============================================='
    Write-Host $Message
    Write-Host '=============================================='
    Write-Host ''
    Read-Host 'Press Enter to close'
    exit $Code
}

function Stop-OldAlphaRuntime {
    try {
        Get-CimInstance Win32_Process | Where-Object {
            ($_.Name -match '^pythonw?\.exe$' -and $_.CommandLine -like '*render_authority_measurement_entry.py*') -or
            ($_.Name -match '^powershell\.exe$' -and (
                $_.CommandLine -like '*wof_alpha_run_forever.ps1*' -or
                $_.CommandLine -like '*start_alpha_current_main.ps1*' -or
                $_.CommandLine -like '*owner_live_retest_loop.ps1*'
            ))
        } | ForEach-Object {
            if ($_.ProcessId -ne $PID) {
                Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
            }
        }
    } catch {}
}

if (-not (Test-Path (Join-Path $Repo '.git'))) {
    Stop-Wof "Managed Alpha repo was not found: $Repo. Run WOF_ALPHA_SETUP_ONCE.cmd once." 20
}
if (-not (Test-Path $Key) -or -not (Test-Path $Pub)) {
    Stop-Wof 'Dedicated Alpha SSH key is missing. Run WOF_ALPHA_SETUP_ONCE.cmd once.' 21
}

$git = Get-Command git.exe -ErrorAction SilentlyContinue
if (-not $git) { Stop-Wof 'Git for Windows was not found.' 22 }
$GitExe = $git.Source

Write-Host ''
Write-Host '=================================================='
Write-Host '       WOF Alpha Permanent Test Setup'
Write-Host '=================================================='
Write-Host 'After this setup there is only ONE entry:'
Write-Host '  Desktop\WOF_ALPHA_TEST.cmd'
Write-Host ''

Write-Host '[1/4] Configuring the dedicated GitHub SSH port 22 host...'
New-Item -ItemType Directory -Path (Split-Path $SshConfig -Parent) -Force | Out-Null
$configText = ''
if (Test-Path $SshConfig) {
    $configText = Get-Content -LiteralPath $SshConfig -Raw -ErrorAction SilentlyContinue
    if ($null -eq $configText) { $configText = '' }
}
$begin = '# WOF_ALPHA_BEGIN'
$end = '# WOF_ALPHA_END'
$start = $configText.IndexOf($begin)
if ($start -ge 0) {
    $finish = $configText.IndexOf($end, $start)
    if ($finish -ge 0) {
        $finish += $end.Length
        $configText = ($configText.Substring(0, $start) + $configText.Substring($finish)).TrimEnd()
    }
}
$keyForward = $Key.Replace('\','/')
$block = @"
# WOF_ALPHA_BEGIN
Host wof-alpha-github
    HostName github.com
    Port 22
    User git
    IdentityFile $keyForward
    IdentitiesOnly yes
    BatchMode yes
    StrictHostKeyChecking accept-new
    ConnectTimeout 8
# WOF_ALPHA_END
"@
if ($configText) { $configText = $configText.TrimEnd() + "`r`n`r`n" + $block.Trim() + "`r`n" }
else { $configText = $block.Trim() + "`r`n" }
[System.IO.File]::WriteAllText($SshConfig, $configText, (New-Object System.Text.UTF8Encoding($false)))

function Test-RepoAccess {
    & $GitExe ls-remote $Remote HEAD *> $null
    return ($LASTEXITCODE -eq 0)
}

if (-not (Test-RepoAccess)) {
    Stop-Wof 'GitHub SSH port 22 is not authorized. Run WOF_ALPHA_SETUP_ONCE.cmd again to complete the one-time key authorization.' 23
}
Write-Host 'SSH22_AUTO_UPDATE_READY'

Write-Host '[2/4] Pinning this managed repo to the controlled alpha-live release...'
& $GitExe -C $Repo remote set-url origin $Remote
if ($LASTEXITCODE -ne 0) { Stop-Wof 'Could not configure the managed Alpha remote.' 24 }
& $GitExe -C $Repo fetch --quiet origin '+refs/heads/alpha-live:refs/remotes/origin/alpha-live'
if ($LASTEXITCODE -ne 0) { Stop-Wof 'Could not fetch alpha-live over GitHub SSH port 22.' 25 }
& $GitExe -C $Repo reset --hard 'origin/alpha-live' | Out-Null
if ($LASTEXITCODE -ne 0) { Stop-Wof 'Could not apply the controlled alpha-live release.' 26 }
& $GitExe -C $Repo clean -fd | Out-Null

$canonicalEntry = Join-Path $Repo 'WOF_ALPHA_TEST.cmd'
$loop = Join-Path $Repo 'parallel\PYLAUNCH\owner_live_retest_loop.ps1'
if (-not (Test-Path $canonicalEntry) -or -not (Test-Path $loop)) {
    Stop-Wof 'The controlled alpha-live release is missing the permanent test workflow.' 27
}

Write-Host '[3/4] Installing the single permanent Desktop test entry...'
$oldDir = Join-Path $Base 'old_launchers_backup'
New-Item -ItemType Directory -Path $oldDir -Force | Out-Null
foreach ($name in @('WOF_ALPHA_RUN.cmd','WOF_ALPHA_RUN_V2.cmd','WOF_ALPHA_RUN_V3.cmd','WOF_ALPHA_RUN_V4.cmd','WOF_ALPHA_RUN_V4_FIXED.cmd')) {
    $old = Join-Path $Desktop $name
    if (Test-Path $old) {
        $dest = Join-Path $oldDir ($name + '.' + (Get-Date -Format 'yyyyMMdd_HHmmss'))
        Move-Item -LiteralPath $old -Destination $dest -Force -ErrorAction SilentlyContinue
    }
}
Copy-Item -LiteralPath $canonicalEntry -Destination $DesktopEntry -Force

Write-Host '[4/4] Starting the permanent alpha-live controller...'
Stop-OldAlphaRuntime
Write-Host ''
Write-Host 'From now on:'
Write-Host '  use the same Desktop\WOF_ALPHA_TEST.cmd forever;'
Write-Host '  only controlled alpha-live releases trigger an update/restart;'
Write-Host '  Git updates use GitHub SSH port 22, not Git HTTPS/443;'
Write-Host '  the Alpha runtime restarts while the Browser/WOF is preserved when safe;'
Write-Host '  latest feedback is always at Documents\WOF_RESULTS\LATEST_ALPHA_FEEDBACK.txt.'
Write-Host ''

Start-Process -FilePath 'cmd.exe' -ArgumentList @('/c', ('"' + $DesktopEntry + '"')) | Out-Null
Write-Host 'Permanent workflow installed successfully.'
Start-Sleep -Seconds 2
exit 0
