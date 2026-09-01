Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.IO.Compression.FileSystem

$canonical = @{
    wof = @{
        description = 'Warriors of Fate (World 921031)'
        browserRelation = 'EXACT SAME PROGRAM REVISION'
        files = @(
            @{ name = 'tk2e_23c.8f'; sha1 = '10b8cb53a4600e3e76f471a3eee8a600e93096fc' },
            @{ name = 'tk2e_22c.7f'; sha1 = '52c2d05279623d93b27856e6b76830796a089eae' }
        )
    }
    wofr1 = @{
        description = 'Warriors of Fate (World 921002)'
        browserRelation = 'DIFFERENT PROGRAM REVISION'
        files = @(
            @{ name = 'tk2e_23b.8f'; sha1 = '19e09ad6f9edc7997b030cddfe1d9c96d88135f2' },
            @{ name = 'tk2e_22b.7f'; sha1 = '9fb8ae06856fe115addfb6794c28978a4f6716ec' }
        )
    }
}

function Get-StreamSha1([System.IO.Stream] $stream) {
    $sha = [System.Security.Cryptography.SHA1]::Create()
    try {
        return ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        $sha.Dispose()
    }
}

$proc = Get-Process -Name @('WinKawaks', 'WinKawaks64', 'Kawaks') -ErrorAction SilentlyContinue |
    Sort-Object StartTime |
    Select-Object -First 1
if (-not $proc) {
    throw 'WinKawaks process not found. Start WinKawaks with WOF loaded, then rerun this same command. No gameplay is required.'
}

$exePath = $proc.Path
if (-not $exePath) {
    throw 'Could not resolve WinKawaks executable path.'
}
$exeDir = Split-Path -Parent $exePath
$title = [string]$proc.MainWindowTitle

$roots = @(
    $exeDir,
    (Join-Path $exeDir 'roms'),
    (Join-Path $exeDir 'rom')
) | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -Unique

$knownNames = @()
foreach ($setName in $canonical.Keys) {
    foreach ($f in $canonical[$setName].files) {
        $knownNames += ([string]$f.name).ToLowerInvariant()
    }
}
$knownNames = $knownNames | Select-Object -Unique

$zipFiles = @()
foreach ($root in $roots) {
    $leaf = Split-Path -Leaf $root
    if ($leaf -match '^(?i:roms?)$') {
        $zipFiles += @(Get-ChildItem -LiteralPath $root -Recurse -File -Filter 'wof*.zip' -ErrorAction SilentlyContinue)
    }
    else {
        $zipFiles += @(Get-ChildItem -LiteralPath $root -File -Filter 'wof*.zip' -ErrorAction SilentlyContinue)
    }
}
$zipFiles = @($zipFiles | Sort-Object FullName -Unique)

# Fallback only inside ordinary ROM directories if archive names are nonstandard.
if ($zipFiles.Count -eq 0) {
    foreach ($root in $roots) {
        if ((Split-Path -Leaf $root) -match '^(?i:roms?)$') {
            $zipFiles += @(Get-ChildItem -LiteralPath $root -Recurse -File -Filter '*.zip' -ErrorAction SilentlyContinue)
        }
    }
    $zipFiles = @($zipFiles | Sort-Object FullName -Unique)
}

$found = @()
foreach ($zip in $zipFiles) {
    $archive = $null
    try {
        $archive = [System.IO.Compression.ZipFile]::OpenRead($zip.FullName)
        foreach ($entry in $archive.Entries) {
            $member = ([string]$entry.Name).ToLowerInvariant()
            if ($knownNames -notcontains $member) {
                continue
            }
            $stream = $entry.Open()
            try {
                $digest = Get-StreamSha1 $stream
            }
            finally {
                $stream.Dispose()
            }
            $found += [pscustomobject]@{
                archive = $zip.FullName
                archiveName = $zip.Name
                member = $entry.Name
                path = $null
                bytes = [int64]$entry.Length
                sha1 = $digest
                error = $null
            }
        }
    }
    catch {
        $found += [pscustomobject]@{
            archive = $zip.FullName
            archiveName = $zip.Name
            member = $null
            path = $null
            bytes = $null
            sha1 = $null
            error = $_.Exception.Message
        }
    }
    finally {
        if ($archive) { $archive.Dispose() }
    }
}

# Also accept loose canonical program files, but only from the normal emulator/ROM roots.
foreach ($root in $roots) {
    $leaf = Split-Path -Leaf $root
    foreach ($name in $knownNames) {
        if ($leaf -match '^(?i:roms?)$') {
            $loose = @(Get-ChildItem -LiteralPath $root -Recurse -File -Filter $name -ErrorAction SilentlyContinue)
        }
        else {
            $loose = @(Get-ChildItem -LiteralPath $root -File -Filter $name -ErrorAction SilentlyContinue)
        }
        foreach ($file in $loose) {
            $digest = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA1).Hash.ToLowerInvariant()
            $found += [pscustomobject]@{
                archive = $null
                archiveName = $null
                member = $file.Name
                path = $file.FullName
                bytes = [int64]$file.Length
                sha1 = $digest
                error = $null
            }
        }
    }
}

$setMatches = @()
foreach ($setName in @('wof', 'wofr1')) {
    $def = $canonical[$setName]
    $expectedArchiveName = "$setName.zip"
    $expectedRows = @()
    $allMatched = $true

    foreach ($expected in $def.files) {
        $name = ([string]$expected.name).ToLowerInvariant()
        $sha1 = ([string]$expected.sha1).ToLowerInvariant()
        $hit = $found | Where-Object {
            if (-not $_.member) { return $false }
            $nameMatch = ([string]$_.member).ToLowerInvariant() -eq $name
            $hashMatch = ([string]$_.sha1).ToLowerInvariant() -eq $sha1
            $containerMatch = (-not $_.archiveName) -or (([string]$_.archiveName).ToLowerInvariant() -eq $expectedArchiveName)
            return $nameMatch -and $hashMatch -and $containerMatch
        } | Select-Object -First 1

        if (-not $hit) { $allMatched = $false }
        $expectedRows += [pscustomobject]@{
            name = $expected.name
            expectedSha1 = $sha1
            matched = [bool]$hit
            source = if ($hit) { if ($hit.archive) { "$($hit.archiveName)/$($hit.member)" } else { $hit.path } } else { $null }
        }
    }

    $setMatches += [pscustomobject]@{
        set = $setName
        expectedArchive = $expectedArchiveName
        description = $def.description
        canonicalProgramPairMatch = $allMatched
        browserRelation = $def.browserRelation
        files = $expectedRows
    }
}

$titleSet = $null
if ($title -match 'World 921031') { $titleSet = 'wof' }
elseif ($title -match 'World 921002') { $titleSet = 'wofr1' }

$matchedSets = @($setMatches | Where-Object { $_.canonicalProgramPairMatch })
$loadedSet = $null
$verdict = 'NOT YET PROVEN'
$reason = $null

if ($titleSet) {
    $titleMatch = $setMatches | Where-Object { $_.set -eq $titleSet -and $_.canonicalProgramPairMatch } | Select-Object -First 1
    if ($titleMatch) {
        $loadedSet = $titleSet
        $verdict = $titleMatch.browserRelation
        $reason = 'WinKawaks live title and the canonical program pair in the matching set container agree.'
    }
    else {
        $reason = 'WinKawaks title identifies a set, but the matching set container did not produce its canonical two-file SHA-1 program pair.'
    }
}
elseif ($matchedSets.Count -eq 1) {
    $loadedSet = $matchedSets[0].set
    $verdict = $matchedSets[0].browserRelation
    $reason = 'Exactly one canonical WOF set container matched, but the live title did not expose a recognized revision label.'
}
else {
    $reason = 'Cryptographic evidence is ambiguous or incomplete.'
}

$out = [ordered]@{
    probe = 'wof-local-winkawaks-rom-identity-v1'
    readOnly = $true
    writesGameMemory = $false
    process = [ordered]@{
        pid = $proc.Id
        exeName = $proc.ProcessName
        exePath = $exePath
        windowTitle = $title
        titleSetHint = $titleSet
    }
    searchedRoots = @($roots)
    candidateArchives = @($zipFiles | ForEach-Object { $_.FullName })
    relevantProgramFiles = @($found)
    canonicalSetMatches = @($setMatches)
    loadedSet = $loadedSet
    browserSet = 'wof'
    browserDescription = 'Warriors of Fate (World 921031)'
    browserFullCpuLogicalSha256 = '5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62'
    verdict = $verdict
    reason = $reason
}

$out | ConvertTo-Json -Depth 8
