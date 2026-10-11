param(
  [switch]$ForceDownload
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$lock = Get-Content -LiteralPath (Join-Path $root 'reverse-runtime.lock.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$cache = Join-Path $root '.cache/reverse-runtime'
$paths = @{
  'ffmpeg.js' = Join-Path $cache 'ffmpeg.js'
  'ffmpeg.wasm' = Join-Path $cache 'ffmpeg.wasm'
  'browser-ffmpeg.js' = Join-Path $cache 'browser-ffmpeg.js'
}
function Hash([string]$Path) {
  $sha = [Security.Cryptography.SHA256]::Create()
  $stream = [IO.File]::OpenRead($Path)
  try { return ((($sha.ComputeHash($stream)) | ForEach-Object { $_.ToString('x2') }) -join '') }
  finally { $sha.Dispose(); $stream.Dispose() }
}
function ValidCache {
  foreach ($entry in $paths.GetEnumerator()) {
    if (-not (Test-Path -LiteralPath $entry.Value -PathType Leaf)) { return $false }
    if ((Hash $entry.Value) -ne [string]$lock.assets.($entry.Key)) { return $false }
  }
  return $true
}
if (-not $ForceDownload -and (ValidCache)) {
  Write-Host '[Reverse WASM] Using pinned verified local cache (no download).'
  exit 0
}

$token = [string]$env:GITHUB_TOKEN
if ([string]::IsNullOrWhiteSpace($token)) { $token = [string]$env:GH_TOKEN }
if ([string]::IsNullOrWhiteSpace($token)) {
  throw "Pinned reverse WASM cache is missing or invalid. GITHUB_TOKEN (or GH_TOKEN) with read access to the public Builder Actions artifact is needed for the first build. The cached assets are then usable offline."
}
New-Item -ItemType Directory -Force -Path $cache | Out-Null
$zip = Join-Path $cache 'builder-artifact.zip'
$extract = Join-Path $cache 'unpacked'
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $extract
Remove-Item -Force -ErrorAction SilentlyContinue $zip
$headers = @{
  'Accept' = 'application/vnd.github+json'
  'User-Agent' = 'browser-kitty-reverse-clip/0.1'
  'Authorization' = "Bearer $token"
}
$url = "https://api.github.com/repos/$($lock.builderRepository)/actions/artifacts/$($lock.artifactId)/zip"
Write-Host "[Reverse WASM] Fetching pinned experimental Builder artifact $($lock.artifactId)."
Invoke-WebRequest -Uri $url -Headers $headers -UseBasicParsing -OutFile $zip
Expand-Archive -LiteralPath $zip -DestinationPath $extract -Force
$manifestPath = Join-Path $extract 'manifest.json'
if (-not (Test-Path $manifestPath)) { throw "Builder artifact has no manifest.json." }
$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($manifest.profile -ne $lock.profile -or $manifest.builderVersion -ne $lock.builderVersion -or
    $manifest.binaryLicense -ne $lock.wasmLicense -or $manifest.runtime.threading -ne 'single-thread' -or
    -not $manifest.runtime.workerFsInput) {
  throw 'Builder artifact has an unexpected profile, license, or threading contract.'
}
foreach ($filename in @('ffmpeg.js','ffmpeg.wasm')) {
  $sourcePath = Join-Path $extract $filename
  if (-not (Test-Path $sourcePath)) { throw "Builder artifact missing $filename" }
  if ((Hash $sourcePath) -ne [string]$lock.assets.$filename) {
    throw "SHA-256 mismatch in Builder artifact: $filename"
  }
}
$runtimeUrl = "https://raw.githubusercontent.com/$($lock.builderRepository)/$($lock.builderCommit)/runtime/browser-ffmpeg.js"
Invoke-WebRequest -Uri $runtimeUrl -UseBasicParsing -Headers @{ 'User-Agent'='browser-kitty-reverse-clip/0.1' } -OutFile $paths['browser-ffmpeg.js']
if ((Hash $paths['browser-ffmpeg.js']) -ne [string]$lock.assets.'browser-ffmpeg.js') {
  throw 'SHA-256 mismatch in pinned Builder browser runtime.'
}
foreach ($filename in @('ffmpeg.js','ffmpeg.wasm')) { Copy-Item -LiteralPath (Join-Path $extract $filename) -Destination $paths[$filename] -Force }
if (-not (ValidCache)) { throw 'Pinned reverse WASM assets failed final cache verification.' }
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $extract
Remove-Item -Force -ErrorAction SilentlyContinue $zip
Write-Host '[Reverse WASM] Verified pinned WASM + JS + runtime. Runtime requires no external network.'
