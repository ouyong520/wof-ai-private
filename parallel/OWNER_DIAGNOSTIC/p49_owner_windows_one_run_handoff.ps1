[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$MetadataRepoRoot,
  [Parameter(Mandatory=$true)][string]$SourceCheckout,
  [Parameter(Mandatory=$true)][string]$BrowserWebSocketUrl,
  [Parameter(Mandatory=$true)][string]$OutputDirectory
)
$ErrorActionPreference = 'Stop'
if (-not $env:LOCALAPPDATA) { Write-Error 'P49_BLOCKED_PRE_RUN: LOCALAPPDATA_NOT_SET'; exit 65 }
$ManagedPython = Join-Path $env:LOCALAPPDATA 'WOF Alpha Current Main\venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $ManagedPython -PathType Leaf)) {
  Write-Error "P49_BLOCKED_PRE_RUN: MANAGED_INTERPRETER_MISSING:$ManagedPython"
  exit 66
}
$Runner = Join-Path $PSScriptRoot 'p49_owner_windows_one_run_handoff.py'
if (-not (Test-Path -LiteralPath $Runner -PathType Leaf)) { Write-Error "P49_BLOCKED_PRE_RUN: RUNNER_MISSING:$Runner"; exit 67 }
& $ManagedPython $Runner --metadata-repo-root $MetadataRepoRoot --source-checkout $SourceCheckout --browser-websocket-url $BrowserWebSocketUrl --output-directory $OutputDirectory
exit $LASTEXITCODE
