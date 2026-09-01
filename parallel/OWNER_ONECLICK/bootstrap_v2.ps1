param(
    [switch]$UpdateOnly
)

# Backward compatibility: packaged Toolkit v2 historically calls the stable CMD with
# "--update-only". Windows PowerShell 5.1 does not reliably bind that GNU-style token
# to the [switch] above, so also inspect the original process command line.
if ($args -contains '--update-only' -or [Environment]::CommandLine -match '(?i)(?:^|\s)--update-only(?:\s|$)') {
    $UpdateOnly = $true
}

$ErrorActionPreference = 'Stop'
$Utf8NoBom = New-Object Text.UTF8Encoding($false)
try { [Console]::OutputEncoding = $Utf8NoBom } catch {}
try { [Console]::InputEncoding = $Utf8NoBom } catch {}
$OutputEncoding = $Utf8NoBom
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ManifestBase = 'https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/'
$ManifestUrl = $ManifestBase + 'parallel/OWNER_ONECLICK/package_manifest.json'
$InstallRoot = Join-Path $env:LOCALAPPDATA 'WOF Future Danger\OwnerTools'
if (-not $env:LOCALAPPDATA) { $InstallRoot = Join-Path $env:TEMP 'WOF_Future_Danger\OwnerTools' }
$ReleaseRoot = Join-Path $InstallRoot 'releases'
$LogDir = Join-Path $InstallRoot 'logs'
$LogFile = Join-Path $LogDir 'bootstrap.log'
$CurrentFile = Join-Path $InstallRoot 'current.txt'
$VenvDir = Join-Path $InstallRoot 'venv'

function Ensure-Dir([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) { New-Item -ItemType Directory -Path $Path -Force | Out-Null }
}
function Log([string]$Message) {
    Ensure-Dir $LogDir
    $line = '[{0}] {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Message
    Add-Content -LiteralPath $LogFile -Value $line -Encoding UTF8
}
function Say([string]$Message) {
    Write-Host $Message
    Log $Message
}
function Fail([string]$OwnerMessage, [object]$Detail=$null, [int]$Code=1) {
    Write-Host ''
    Write-Host $OwnerMessage -ForegroundColor Red
    Write-Host '旧版本工具仍然保留，游戏本身没有受到影响。'
    if ($Detail) { Write-Host ('技术详情：' + [string]$Detail) }
    Write-Host ('日志位置：' + $LogFile)
    Log ('FAIL: ' + $OwnerMessage + ' / ' + [string]$Detail)
    exit $Code
}
function Download-File([string]$Url, [string]$OutFile) {
    $parent = Split-Path -Parent $OutFile
    Ensure-Dir $parent
    Invoke-WebRequest -UseBasicParsing -Uri $Url -OutFile $OutFile -TimeoutSec 45
    if (-not (Test-Path -LiteralPath $OutFile)) { throw '下载后文件不存在：' + $Url }
    if ((Get-Item -LiteralPath $OutFile).Length -le 0) { throw '下载到空文件：' + $Url }
}
function Get-GitBlobSha1([string]$Path) {
    $bytes = [IO.File]::ReadAllBytes($Path)
    $header = [Text.Encoding]::ASCII.GetBytes(('blob {0}' -f $bytes.Length) + [char]0)
    $all = New-Object byte[] ($header.Length + $bytes.Length)
    [Array]::Copy($header,0,$all,0,$header.Length)
    [Array]::Copy($bytes,0,$all,$header.Length,$bytes.Length)
    $sha = [Security.Cryptography.SHA1]::Create()
    try { $hash = $sha.ComputeHash($all) } finally { $sha.Dispose() }
    return (($hash | ForEach-Object { $_.ToString('x2') }) -join '')
}
function Find-Python {
    try {
        $py = Get-Command py.exe -ErrorAction SilentlyContinue
        if ($py) {
            $out = & $py.Source -3 -c 'import sys; print(sys.executable)' 2>$null
            if ($LASTEXITCODE -eq 0 -and $out) {
                $p = ($out | Select-Object -Last 1).Trim()
                if (Test-Path -LiteralPath $p) { return $p }
            }
        }
    } catch {}
    try {
        $python = Get-Command python.exe -ErrorAction SilentlyContinue
        if ($python) {
            $out = & $python.Source -c 'import sys; print(sys.executable)' 2>$null
            if ($LASTEXITCODE -eq 0 -and $out) {
                $p = ($out | Select-Object -Last 1).Trim()
                if (Test-Path -LiteralPath $p) { return $p }
            }
        }
    } catch {}
    $localPrograms = Join-Path $env:LOCALAPPDATA 'Programs\Python'
    if (Test-Path -LiteralPath $localPrograms) {
        $candidates = Get-ChildItem -LiteralPath $localPrograms -Directory -ErrorAction SilentlyContinue |
            Sort-Object Name -Descending |
            ForEach-Object { Join-Path $_.FullName 'python.exe' } |
            Where-Object { Test-Path -LiteralPath $_ }
        foreach ($p in $candidates) { return $p }
    }
    return $null
}
function Ensure-Python {
    $p = Find-Python
    if ($p) { return $p }
    Say '未找到 Python 3，正在尝试自动安装 Python 3.12...'
    $winget = Get-Command winget.exe -ErrorAction SilentlyContinue
    if (-not $winget) { return $null }
    try {
        & $winget.Source install --id Python.Python.3.12 -e --source winget --scope user --accept-source-agreements --accept-package-agreements --silent | Out-Null
    } catch { Log ('winget Python install error: ' + $_.Exception.Message) }
    Start-Sleep -Seconds 2
    return (Find-Python)
}
function Prepare-Venv([string]$PythonExe, [string]$ReleaseDir) {
    $venvPython = Join-Path $VenvDir 'Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $venvPython)) {
        Say '正在准备 Python 环境...'
        & $PythonExe -m venv $VenvDir
        if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $venvPython)) { throw '创建 Python 虚拟环境失败' }
    }
    $req1 = Join-Path $ReleaseDir 'parallel\PYLAUNCH\requirements.txt'
    $req2 = Join-Path $ReleaseDir 'parallel\WOF052L_RECORDER\requirements.txt'
    Say '正在检查 Python 依赖...'
    if (Test-Path -LiteralPath $req1) {
        & $venvPython -m pip install --disable-pip-version-check -q -r $req1
        if ($LASTEXITCODE -ne 0) { throw 'PYLAUNCH 依赖安装失败' }
    }
    if (Test-Path -LiteralPath $req2) {
        & $venvPython -m pip install --disable-pip-version-check -q -r $req2
        if ($LASTEXITCODE -ne 0) { throw 'Recorder 依赖安装失败' }
    }
    return $venvPython
}

try {
    Ensure-Dir $InstallRoot
    Ensure-Dir $ReleaseRoot
    Ensure-Dir $LogDir
    Log ('bootstrap start updateOnly=' + $UpdateOnly)

    Say '正在检查 WOF 工具更新...'
    $manifestTemp = Join-Path $env:TEMP ('wof_owner_manifest_' + [Guid]::NewGuid().ToString('N') + '.json')
    Download-File $ManifestUrl $manifestTemp
    try { $manifest = Get-Content -LiteralPath $manifestTemp -Raw -Encoding UTF8 | ConvertFrom-Json } catch { throw '版本清单读取失败：' + $_.Exception.Message }
    Remove-Item -LiteralPath $manifestTemp -Force -ErrorAction SilentlyContinue

    if (-not $manifest.packageVersion) { throw '版本清单缺少 packageVersion' }
    $packageBase = [string]$manifest.baseUrl
    if ($packageBase -notmatch '^https://raw\.githubusercontent\.com/ouyong520/wof-ai-private/[0-9a-f]{40}/$') { throw '版本清单下载源不是固定的官方项目 commit' }
    if (-not $manifest.files -or $manifest.files.Count -lt 1) { throw '版本清单没有文件' }
    $version = [string]$manifest.packageVersion
    if ($version -notmatch '^[A-Za-z0-9._-]+$') { throw '版本号格式不安全' }
    $releaseDir = Join-Path $ReleaseRoot $version
    $installedOk = Join-Path $releaseDir 'installed.ok'

    $needInstall = -not (Test-Path -LiteralPath $installedOk)
    if ($needInstall) {
        $stage = Join-Path $ReleaseRoot ($version + '.staging-' + [Guid]::NewGuid().ToString('N'))
        Ensure-Dir $stage
        try {
            $i = 0
            foreach ($f in $manifest.files) {
                $i++
                $rel = [string]$f.path
                $sha = ([string]$f.gitBlobSha).ToLowerInvariant()
                if (-not $rel -or $rel.Contains('..') -or [IO.Path]::IsPathRooted($rel)) { throw '清单包含不安全路径：' + $rel }
                if ($sha -notmatch '^[0-9a-f]{40}$') { throw '清单缺少有效完整性哈希：' + $rel }
                Write-Host ('下载 {0}/{1}：{2}' -f $i,$manifest.files.Count,$rel)
                $dest = Join-Path $stage ($rel -replace '/', '\')
                $url = $packageBase + ($rel -replace ' ', '%20')
                Download-File $url $dest
                $actual = Get-GitBlobSha1 $dest
                if ($actual -ne $sha) { throw ('文件完整性校验失败：{0} expected={1} actual={2}' -f $rel,$sha,$actual) }
            }
            $manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $stage 'PACKAGE_MANIFEST.json') -Encoding UTF8
            Set-Content -LiteralPath (Join-Path $stage 'installed.ok') -Value ('installed ' + (Get-Date -Format o)) -Encoding UTF8
            if (Test-Path -LiteralPath $releaseDir) { throw '目标版本目录已存在但不完整，请删除后重试：' + $releaseDir }
            Move-Item -LiteralPath $stage -Destination $releaseDir
            Say ('工具版本 ' + $version + ' 已下载并通过完整性检查。')
        } catch {
            Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue
            throw
        }
    } else {
        Say ('当前工具版本已就绪：' + $version)
    }

    $pointerTmp = $CurrentFile + '.tmp'
    Set-Content -LiteralPath $pointerTmp -Value $version -Encoding ASCII
    Move-Item -LiteralPath $pointerTmp -Destination $CurrentFile -Force

    $pythonExe = Ensure-Python
    if (-not $pythonExe) { Fail '没有找到可用的 Python 3，自动安装也没有成功。' '请确认 Windows 已安装 winget，或安装 Python 3.11+ 后重新双击。' 12 }
    $venvPython = Prepare-Venv $pythonExe $releaseDir

    $env:WOF_PACKAGED_MODE = '1'
    $env:WOF_PACKAGE_VERSION = $version
    $env:WOF_TOOLKIT_PYTHON = $venvPython
    $env:WOF_BOOTSTRAP_PATH = Join-Path $releaseDir 'WOF_一键工具.cmd'

    Say '工具已准备完成。'
    if ($UpdateOnly) {
        Say '更新检查结束。请回到工具箱继续操作；如果刚安装了新版本，退出后重新双击一键工具即可。'
        exit 0
    }

    # Start the exact same Simplified-Chinese owner surface that WOF_TOOLKIT.cmd
    # ultimately launches, but do it directly through the prepared venv. This avoids
    # a second UTF-8 batch parser and is reliable for Chinese/space install paths.
    $ownerToolkit = Join-Path $releaseDir 'parallel\OPTOOLKIT\owner_zh_cn.py'
    if (-not (Test-Path -LiteralPath $ownerToolkit)) { throw '安装包中缺少中文 WOF 工具箱入口' }
    Say '正在打开中文 WOF 工具箱...'
    & $venvPython $ownerToolkit --root $releaseDir
    exit $LASTEXITCODE
} catch {
    $detail = [string]$_.Exception.Message
    if ($detail -match '^文件完整性校验失败：') { Fail $detail $null 21 }
    Fail 'WOF 工具准备失败。' $detail 20
}
