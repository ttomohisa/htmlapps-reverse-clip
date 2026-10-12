param(
  [Parameter(Mandatory=$true)]
  [ValidateSet('single-thread','multi-thread')]
  [string]$Variant,
  [switch]$ForceDownload
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$lock = Get-Content -LiteralPath (Join-Path $root 'reverse-runtime.lock.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if ([int]$lock.schemaVersion -ne 2) { throw 'Reverse WASM lock schemaVersion 2 is required.' }
$entry = $lock.variants.PSObject.Properties[$Variant].Value
if (-not $entry) { throw "Pinned reverse WASM lock has no $Variant entry." }
$cache = Join-Path $root ".cache/reverse-runtime/$Variant"
$files = @('ffmpeg.js','ffmpeg.wasm','browser-ffmpeg.js')
function Get-Hash([string]$Path) {
  $stream = [IO.File]::OpenRead($Path)
  $algorithm = [Security.Cryptography.SHA256]::Create()
  try {
    return (($algorithm.ComputeHash($stream) | ForEach-Object { $_.ToString('x2') }) -join '')
  } finally { $algorithm.Dispose(); $stream.Dispose() }
}
function Assert-File([string]$Filename, [string]$Root, [object]$Hashes) {
  $path = Join-Path $Root $Filename
  if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Pinned runtime is missing $Filename" }
  $expected = if ($Filename -eq 'browser-ffmpeg.js') { [string]$lock.browserRuntimeSha256 } else { [string]$Hashes.$Filename }
  if ($expected -notmatch '^[a-f0-9]{64}$' -or (Get-Hash $path) -ne $expected) {
    throw "Pinned $Variant runtime SHA-256 mismatch: $Filename"
  }
}
function Cached() {
  try {
    foreach($name in $files){Assert-File $name $cache $entry.assets}
    $manifestFile = Join-Path $cache 'manifest.json'
    if (-not (Test-Path -LiteralPath $manifestFile)) { return $false }
    $m = Get-Content -Raw -Encoding UTF8 $manifestFile | ConvertFrom-Json
    Assert-Manifest $m
    return $true
  } catch { return $false }
}
function Assert-Manifest($m) {
  if ($m.profile -ne $lock.profile -or $m.builderVersion -ne $lock.builderVersion -or
      $m.binaryLicense -ne $lock.wasmLicense -or $m.runtime.threading -ne $Variant -or
      -not $m.runtime.workerFsInput) {
    throw "Pinned $Variant runtime has unexpected profile/version/license/threading."
  }
  $isMt = $Variant -eq 'multi-thread'
  if ([bool]$m.runtime.requiresCrossOriginIsolation -ne $isMt -or
      [bool]$m.runtime.requiresSharedArrayBuffer -ne $isMt -or
      [bool]$m.runtime.fileProtocolSingleHtml -eq $isMt) {
    throw "Pinned $Variant runtime has incorrect isolation/file:// contract."
  }
  if ($isMt -and [int]$m.runtime.pthreadPoolSize -lt 1) {
    throw "Pinned $Variant runtime has no pthread pool."
  }
}
if (-not $ForceDownload -and (Cached)) {
  Write-Host "[Reverse WASM] Using verified cached $Variant runtime."
  return
}
$token = [string]$env:GITHUB_TOKEN
if ([string]::IsNullOrWhiteSpace($token)) { $token = [string]$env:GH_TOKEN }
if ([string]::IsNullOrWhiteSpace($token)) {
  throw "Pinned $Variant runtime cache is absent. GITHUB_TOKEN/ GH_TOKEN is required to download the temporary GitHub Actions artifact at build time. Browser users need no token."
}
New-Item -ItemType Directory -Force -Path $cache | Out-Null
$zip = Join-Path $cache 'builder-artifact.zip'
$extract = Join-Path $cache 'extract'
try {
  Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $extract
  Remove-Item -Force -ErrorAction SilentlyContinue $zip
  $headers = @{
    Accept = 'application/vnd.github+json'
    'User-Agent' = 'browser-kitty-reverse-clip/0.1'
    Authorization = "Bearer $token"
  }
  $url = "https://api.github.com/repos/$($lock.builderRepository)/actions/artifacts/$($lock.artifactId)/zip"
  Write-Host "[Reverse WASM] Downloading $Variant from pinned Builder artifact $($lock.artifactId)"
  Invoke-WebRequest -Uri $url -Headers $headers -UseBasicParsing -OutFile $zip
  Expand-Archive -LiteralPath $zip -DestinationPath $extract -Force
  $variantDir = Join-Path $extract $Variant
  $manifest = Get-Content -Raw -Encoding UTF8 (Join-Path $variantDir 'manifest.json') | ConvertFrom-Json
  Assert-Manifest $manifest
  foreach($name in @('ffmpeg.js','ffmpeg.wasm')){Assert-File $name $variantDir $entry.assets}
  $runtimeUrl = "https://raw.githubusercontent.com/$($lock.builderRepository)/$($lock.builderCommit)/runtime/browser-ffmpeg.js"
  $loader = Join-Path $cache 'browser-ffmpeg.js'
  Invoke-WebRequest -Uri $runtimeUrl -UseBasicParsing -Headers @{'User-Agent'='browser-kitty-reverse-clip/0.1'} -OutFile $loader
  Assert-File 'browser-ffmpeg.js' $cache $entry.assets
  foreach($name in @('ffmpeg.js','ffmpeg.wasm')) {
    Copy-Item -LiteralPath (Join-Path $variantDir $name) -Destination (Join-Path $cache $name) -Force
  }
  Copy-Item -LiteralPath (Join-Path $variantDir 'manifest.json') -Destination (Join-Path $cache 'manifest.json') -Force
  if (-not (Cached)) { throw "Pinned $Variant runtime cache failed final validation." }
  Write-Host "[Reverse WASM] $Variant JS/WASM and metadata verified. No runtime downloads."
} finally {
  Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $extract
  Remove-Item -Force -ErrorAction SilentlyContinue $zip
}
