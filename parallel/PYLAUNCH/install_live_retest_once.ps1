$ErrorActionPreference = 'Stop'

$Base = Join-Path $env:LOCALAPPDATA 'WOF_ALPHA_CURRENT_MAIN'
$Repo = Join-Path $Base 'repo'
$Key = Join-Path $env:USERPROFILE '.ssh\wof_alpha_github_ed25519'
$Pub = $Key + '.pub'
$SshConfig = Join-Path $env:USERPROFILE '.ssh\config'
$Remote = 'git@wof-alpha-github:ouyong520/wof-ai-private.git'
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

if (-not (Test-Path (Join-Path $Repo '.git'))) {
    Stop-Wof "Managed Alpha repo was not found: $Repo" 20
}
if (-not (Test-Path $Key) -or -not (Test-Path $Pub)) {
    Stop-Wof 'Dedicated SSH key was not created by the setup wrapper.' 21
}

$git = Get-Command git.exe -ErrorAction SilentlyContinue
if (-not $git) { Stop-Wof 'Git was not found.' 22 }
$GitExe = $git.Source

Write-Host ''
Write-Host '=================================================='
Write-Host '       WOF Alpha Permanent Test Setup'
Write-Host '=================================================='
Write-Host 'After this setup there is only ONE entry:'
Write-Host '  Desktop\WOF_ALPHA_TEST.cmd'
Write-Host ''

Write-Host '[1/4] Configuring GitHub SSH 22 update channel...'
New-Item -ItemType Directory -Path (Split-Path $SshConfig -Parent) -Force | Out-Null
$configText = ''
if (Test-Path $SshConfig) { $configText = Get-Content -LiteralPath $SshConfig -Raw -ErrorAction SilentlyContinue }
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
    Write-Host ''
    Write-Host 'ONE-TIME GitHub authorization is required.'
    $pubText = (Get-Content -LiteralPath $Pub -Raw).Trim()
    try { Set-Clipboard -Value $pubText } catch {}
    Write-Host 'The SSH public key is already copied to the clipboard.'
    Write-Host ''
    Write-Host 'On the GitHub page:'
    Write-Host '  Title: WOF Alpha updater'
    Write-Host '  Key type: Authentication Key'
    Write-Host '  Key: Ctrl+V'
    Write-Host '  Click: Add SSH key'
    Write-Host ''
    Write-Host 'You do NOT need to come back and press anything.'
    Write-Host 'This window will detect the authorization automatically.'
    try { Start-Process 'https://github.com/settings/ssh/new' } catch {}

    $deadline = (Get-Date).AddMinutes(10)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Seconds 3
        if (Test-RepoAccess) { break }
        Write-Host -NoNewline '.'
    }
    Write-Host ''
    if (-not (Test-RepoAccess)) {
        Stop-Wof 'SSH authorization was not detected. The setup is still safe to run again later.' 23
    }
}
Write-Host 'SSH22_AUTO_UPDATE_READY'

Write-Host '[2/4] Updating the managed Alpha source once...'
& $GitExe -C $Repo fetch --quiet $Remote '+refs/heads/main:refs/remotes/origin/main'
if ($LASTEXITCODE -ne 0) { Stop-Wof 'Could not fetch latest Alpha over SSH 22.' 24 }
& $GitExe -C $Repo reset --hard origin/main | Out-Null
if ($LASTEXITCODE -ne 0) { Stop-Wof 'Could not apply latest Alpha.' 25 }
& $GitExe -C $Repo clean -fd | Out-Null

$canonicalEntry = Join-Path $Repo 'WOF_ALPHA_TEST.cmd'
$loop = Join-Path $Repo 'parallel\PYLAUNCH\owner_live_retest_loop.ps1'
if (-not (Test-Path $canonicalEntry) -or -not (Test-Path $loop)) {
    Stop-Wof 'Latest main does not contain the permanent live retest workflow.' 26
}

Write-Host '[3/4] Installing the single Desktop test entry...'
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

Write-Host '[4/4] Starting permanent live retest mode...'
Write-Host ''
Write-Host 'From now on the workflow is:'
Write-Host '  You test -> send screenshot -> leave this running.'
Write-Host '  A new main commit appears -> changed files download automatically.'
Write-Host '  Alpha restarts automatically and reuses the Alpha Chrome/WOF when possible.'
Write-Host '  No new launcher download. No V5/V6/V7 files.'
Write-Host ''

Start-Process -FilePath $DesktopEntry
Write-Host 'Permanent workflow installed successfully.'
Write-Host 'Only use Desktop\WOF_ALPHA_TEST.cmd from now on.'
Start-Sleep -Seconds 3
exit 0
