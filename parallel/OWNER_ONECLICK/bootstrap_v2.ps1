param(
    [switch]$UpdateOnly,
    [string]$InstallRoot = '',
    [string]$LauncherPath = ''
)

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

if (-not $InstallRoot) {
    $base = if ($LauncherPath) { Split-Path -Parent ([IO.Path]::GetFullPath($LauncherPath)) } else { (Get-Location).Path }
    $InstallRoot = Join-Path $base 'WOF_Portable'
}
$InstallRoot = [IO.Path]::GetFullPath($InstallRoot)
if ($env:WOF_MANIFEST_URL) {
    $ManifestUrl = [string]$env:WOF_MANIFEST_URL
    if ($ManifestUrl -notmatch '^https://raw\.githubusercontent\.com/ouyong520/wof-ai-private/[0-9a-f]{40}/parallel/OWNER_ONECLICK/package_manifest\.json(?:\?.*)?$') {
        throw 'WOF_MANIFEST_URL 必须固定到官方项目的完整 commit SHA'
    }
} else {
    $ManifestUrl = 'https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/parallel/OWNER_ONECLICK/package_manifest.json?cb=' + [Guid]::NewGuid().ToString('N')
}
$ReleaseRoot = Join-Path $InstallRoot 'releases'
$LogDir = Join-Path $InstallRoot 'logs'
$LogFile = Join-Path $LogDir 'bootstrap.log'
$CurrentFile = Join-Path $InstallRoot 'current.txt'
$VenvDir = Join-Path $InstallRoot 'venv'
$DepsMarker = Join-Path $VenvDir 'wof-dependencies.ok'

function Ensure-Dir([string]$Path) { if (-not (Test-Path -LiteralPath $Path)) { New-Item -ItemType Directory -Path $Path -Force | Out-Null } }
function Log([string]$Message) { Ensure-Dir $LogDir; Add-Content -LiteralPath $LogFile -Value ('[{0}] {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Message) -Encoding UTF8 }
function Say([string]$Message) { Write-Host $Message; Log $Message }
function Fail([string]$OwnerMessage, [object]$Detail=$null, [int]$Code=1) {
    Write-Host ''; Write-Host $OwnerMessage -ForegroundColor Red
    Write-Host '旧版本工具仍然保留，游戏本身没有受到影响。'
    if ($Detail) { Write-Host ('技术详情：' + [string]$Detail) }
    Write-Host ('日志位置：' + $LogFile); Log ('FAIL: ' + $OwnerMessage + ' / ' + [string]$Detail); exit $Code
}
function Download-File([string]$Url, [string]$OutFile) {
    Ensure-Dir (Split-Path -Parent $OutFile)
    Invoke-WebRequest -UseBasicParsing -Uri $Url -OutFile $OutFile -TimeoutSec 45
    if (-not (Test-Path -LiteralPath $OutFile) -or (Get-Item -LiteralPath $OutFile).Length -le 0) { throw '下载失败或得到空文件：' + $Url }
}
function Get-GitBlobSha1([string]$Path) {
    $bytes = [IO.File]::ReadAllBytes($Path); $header = [Text.Encoding]::ASCII.GetBytes(('blob {0}' -f $bytes.Length) + [char]0)
    $all = New-Object byte[] ($header.Length + $bytes.Length); [Array]::Copy($header,0,$all,0,$header.Length); [Array]::Copy($bytes,0,$all,$header.Length,$bytes.Length)
    $sha = [Security.Cryptography.SHA1]::Create(); try { $hash = $sha.ComputeHash($all) } finally { $sha.Dispose() }
    return (($hash | ForEach-Object { $_.ToString('x2') }) -join '')
}
function Test-ReleaseIntegrity([string]$ReleaseDir, $Manifest) {
    if (-not (Test-Path -LiteralPath (Join-Path $ReleaseDir 'installed.ok'))) { return $false }
    foreach ($f in $Manifest.files) {
        $rel=[string]$f.path; $wanted=([string]$f.gitBlobSha).ToLowerInvariant(); $p=Join-Path $ReleaseDir ($rel -replace '/', '\')
        if (-not (Test-Path -LiteralPath $p)) { return $false }
        if ((Get-GitBlobSha1 $p) -ne $wanted) { return $false }
    }
    return $true
}
function Assert-VisibleOverlayManifest($Manifest) {
    if (-not $Manifest.components -or -not $Manifest.components.renderAuthorityV3) { throw '版本清单没有选择 Alpha production 顶部显示 runtime' }
    $ra = $Manifest.components.renderAuthorityV3
    if ([string]$ra.sliceARuntimeCommit -notmatch '^[0-9a-f]{40}$') { throw '版本清单缺少 Slice A exact runtime commit pin' }
    if ([string]$Manifest.sourceCommit -notmatch '^[0-9a-f]{40}$') { throw '版本清单 source commit 未固定' }
    if ([string]$ra.selectedNormalPath -ne 'production-top-overlay') { throw '版本清单 normal path 不是 production top overlay' }
    if ($ra.productionOverlayEnabled -ne $true) { throw '版本清单仍是 productionOverlayEnabled=false；拒绝安装为正式包' }
    if ($ra.productionOverlaySuppressed -ne $false) { throw '版本清单未证明 productionOverlaySuppressed=false；拒绝安装为正式包' }
    if ($ra.diagnosticOnly -ne $false) { throw 'diagnostic-only 候选不能安装为正式包' }
    if ($ra.whiteAcquisitionMarkerIsProduct -ne $false) { throw '白色 acquisition marker 不能冒充正式产品' }
    if ($ra.automaticSeedRequiredBeforeFallback -ne $true) { throw '正式包必须先自动获取 P1，再允许 fallback' }
    if ([int]$ra.ownerClickFallbackMaximumPerAuthorityGeneration -ne 1) { throw '正式包的一次点击 fallback 上限必须为 1' }
    if (-not $Manifest.safety) { throw '版本清单缺少 safety contract' }
    if ($Manifest.safety.readOnly -ne $true -or [int]$Manifest.safety.ramWrites -ne 0 -or $Manifest.safety.inputInjection -ne $false) { throw '版本清单破坏只读安全 contract' }
    if ($Manifest.safety.manualCalibration -ne $false) { throw '正式包禁止 manual calibration' }
    if ($Manifest.safety.legacyProjectionSelected -ne $false) { throw '正式包禁止选择 legacy projection' }
    if ($Manifest.safety.productionOverlayEnabled -ne $true -or $Manifest.safety.productionOverlaySuppressed -ne $false) { throw '正式包 safety metadata 未选择 production overlay' }
    if ($Manifest.components.projectionProof -and $Manifest.components.projectionProof.selected -ne $false) { throw 'legacy projection proof 不能成为 selected normal path' }
}
function Find-Python {
    try { $py=Get-Command py.exe -ErrorAction SilentlyContinue; if($py){$out=& $py.Source -3 -c 'import sys; print(sys.executable)' 2>$null;if($LASTEXITCODE -eq 0 -and $out){$p=($out|Select-Object -Last 1).Trim();if(Test-Path -LiteralPath $p){return $p}}} } catch {}
    try { $python=Get-Command python.exe -ErrorAction SilentlyContinue; if($python){$out=& $python.Source -c 'import sys; print(sys.executable)' 2>$null;if($LASTEXITCODE -eq 0 -and $out){$p=($out|Select-Object -Last 1).Trim();if(Test-Path -LiteralPath $p){return $p}}} } catch {}
    $localPrograms=Join-Path $env:LOCALAPPDATA 'Programs\Python'
    if(Test-Path -LiteralPath $localPrograms){foreach($p in (Get-ChildItem -LiteralPath $localPrograms -Directory -ErrorAction SilentlyContinue|Sort-Object Name -Descending|ForEach-Object{Join-Path $_.FullName 'python.exe'}|Where-Object{Test-Path -LiteralPath $_})){return $p}}
    return $null
}
function Ensure-Python {
    $p=Find-Python;if($p){return $p}
    Say '未找到 Python 3，正在尝试自动安装 Python 3.12...';$winget=Get-Command winget.exe -ErrorAction SilentlyContinue;if(-not $winget){return $null}
    try { & $winget.Source install --id Python.Python.3.12 -e --source winget --scope user --accept-source-agreements --accept-package-agreements --silent | Out-Null } catch { Log ('winget Python install error: '+$_.Exception.Message) }
    return (Find-Python)
}
function Prepare-Venv([string]$PythonExe,[string]$ReleaseDir,[string]$Version) {
    $venvPython=Join-Path $VenvDir 'Scripts\python.exe'
    if(-not(Test-Path -LiteralPath $venvPython)){Say '正在准备 portable Python 环境...'; & $PythonExe -m venv $VenvDir; if($LASTEXITCODE -ne 0 -or -not(Test-Path -LiteralPath $venvPython)){throw '创建 Python 虚拟环境失败'}}
    $markerValue='package='+$Version
    $needDeps=$true
    if(Test-Path -LiteralPath $DepsMarker){try{$needDeps=((Get-Content -LiteralPath $DepsMarker -Raw -Encoding UTF8).Trim() -ne $markerValue)}catch{}}
    if($needDeps){
        Say '正在准备本版本 Python 依赖...'
        foreach($req in @('parallel\PYLAUNCH\requirements.txt','parallel\WOF052L_RECORDER\requirements.txt')){$p=Join-Path $ReleaseDir $req;if(Test-Path -LiteralPath $p){& $venvPython -m pip install --disable-pip-version-check -q -r $p;if($LASTEXITCODE -ne 0){throw 'Python 依赖安装失败：'+$req}}}
        Set-Content -LiteralPath $DepsMarker -Value $markerValue -Encoding UTF8
    }
    return $venvPython
}

try {
    Ensure-Dir $InstallRoot; Ensure-Dir $ReleaseRoot; Ensure-Dir $LogDir
    Log ('bootstrap start updateOnly='+$UpdateOnly+' root='+$InstallRoot)
    Say '正在检查官方 package manifest...'
    $manifestTemp=Join-Path $env:TEMP ('wof_owner_manifest_'+[Guid]::NewGuid().ToString('N')+'.json'); Download-File $ManifestUrl $manifestTemp
    try{$manifest=Get-Content -LiteralPath $manifestTemp -Raw -Encoding UTF8|ConvertFrom-Json}finally{Remove-Item -LiteralPath $manifestTemp -Force -ErrorAction SilentlyContinue}
    if(-not $manifest.packageVersion){throw '版本清单缺少 packageVersion'}
    Assert-VisibleOverlayManifest $manifest
    $packageBase=[string]$manifest.baseUrl
    if($packageBase -notmatch '^https://raw\.githubusercontent\.com/ouyong520/wof-ai-private/[0-9a-f]{40}/$'){throw '版本清单下载源不是固定官方 commit'}
    if(-not $manifest.files -or $manifest.files.Count -lt 1){throw '版本清单没有文件'}
    $version=[string]$manifest.packageVersion;if($version -notmatch '^[A-Za-z0-9._-]+$'){throw '版本号格式不安全'}
    $releaseDir=Join-Path $ReleaseRoot $version
    $healthy=Test-ReleaseIntegrity $releaseDir $manifest
    if(-not $healthy){
        Say ('正在安装/修复 portable 工具版本 '+$version+'...')
        $stage=Join-Path $ReleaseRoot ($version+'.staging-'+[Guid]::NewGuid().ToString('N'));Ensure-Dir $stage
        try{
            $i=0;foreach($f in $manifest.files){$i++;$rel=[string]$f.path;$sha=([string]$f.gitBlobSha).ToLowerInvariant();if(-not $rel -or $rel.Contains('..') -or [IO.Path]::IsPathRooted($rel)){throw '清单包含不安全路径：'+$rel};if($sha -notmatch '^[0-9a-f]{40}$'){throw '清单缺少有效完整性哈希：'+$rel};Write-Host ('下载 {0}/{1}：{2}' -f $i,$manifest.files.Count,$rel);$dest=Join-Path $stage ($rel -replace '/', '\');Download-File ($packageBase+($rel -replace ' ','%20')) $dest;$actual=Get-GitBlobSha1 $dest;if($actual -ne $sha){throw ('文件完整性校验失败：{0} expected={1} actual={2}' -f $rel,$sha,$actual)}}
            $manifest|ConvertTo-Json -Depth 12|Set-Content -LiteralPath (Join-Path $stage 'PACKAGE_MANIFEST.json') -Encoding UTF8
            Set-Content -LiteralPath (Join-Path $stage 'installed.ok') -Value ('verified '+(Get-Date -Format o)) -Encoding UTF8
            if(-not(Test-ReleaseIntegrity $stage $manifest)){throw 'staging 完整性复核失败'}
            if(Test-Path -LiteralPath $releaseDir){$quarantine=$releaseDir+'.replaced-'+[Guid]::NewGuid().ToString('N');Move-Item -LiteralPath $releaseDir -Destination $quarantine}
            Move-Item -LiteralPath $stage -Destination $releaseDir
        }catch{Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue;throw}
        Say ('portable 工具版本 '+$version+' 已通过完整性检查。')
    }else{Say ('portable 工具版本已验证：'+$version)}
    $pointerTmp=$CurrentFile+'.tmp';Set-Content -LiteralPath $pointerTmp -Value $version -Encoding ASCII;Move-Item -LiteralPath $pointerTmp -Destination $CurrentFile -Force
    $pythonExe=Ensure-Python;if(-not $pythonExe){Fail '没有找到可用的 Python 3，自动安装也没有成功。' '请安装 Python 3.11+ 后重试。' 12}
    $venvPython=Prepare-Venv $pythonExe $releaseDir $version
    if($UpdateOnly){Say '更新/修复检查完成。退出工具箱后重新双击一键工具即可使用当前版本。';exit 0}
    $env:WOF_PACKAGED_MODE='1';$env:WOF_PACKAGE_VERSION=$version;$env:WOF_TOOLKIT_PYTHON=$venvPython
    $env:WOF_BOOTSTRAP_PATH=if($LauncherPath){[IO.Path]::GetFullPath($LauncherPath)}else{Join-Path $releaseDir 'WOF_一键工具.cmd'}
    $ownerToolkit=Join-Path $releaseDir 'parallel\OPTOOLKIT\owner_zh_cn.py';if(-not(Test-Path -LiteralPath $ownerToolkit)){throw '安装包中缺少中文 WOF 工具箱入口'}
    Say '正在打开中文 WOF 工具箱...'; & $venvPython $ownerToolkit --root $releaseDir; exit $LASTEXITCODE
}catch{
    $detail=[string]$_.Exception.Message
    if($detail -match '^文件完整性校验失败：'){Fail $detail $null 21}
    if($detail -match 'productionOverlay|diagnostic-only|Slice A exact|production top overlay|白色 acquisition marker|legacy projection'){Fail '当前官方候选还不是可发布的 WOF production 头顶显示包。' $detail 22}
    Fail 'WOF portable 工具准备失败。' $detail 20
}
