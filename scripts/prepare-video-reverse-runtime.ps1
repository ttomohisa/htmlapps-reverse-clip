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
$sourceKind = [string]$lock.kind
if ($sourceKind -notin @('experimental-dual-github-actions-artifact', 'github-release-st-mt')) {
  throw "Unsupported reverse runtime source kind: $sourceKind"
}
$isRelease = $sourceKind -eq 'github-release-st-mt'
$entry = $lock.variants.PSObject.Properties[$Variant].Value
if (-not $entry) { throw "Pinned reverse WASM lock has no $Variant entry." }
if ($isRelease) {
  # Validate the *release source*, version and archive lock BEFORE any
  # previously populated experimental cache can satisfy Cached().
  $version = [string]$lock.builderVersion
  $tag = [string]$lock.builderTag
  $assetName = [string]$entry.releaseAsset
  $archiveSha = [string]$entry.releaseArchiveSha256
  $sourceAsset = [string]$lock.correspondingSourceAsset
  $sourceSha = [string]$lock.correspondingSourceSha256
  if ($version -notmatch '^\d+\.\d+\.\d+$' -or
      $tag -cnotin @("v$version","video-reverse-v$version") -or
      $assetName -cne "ffmpeg-wasm-video-reverse-$Variant-v$version.zip" -or
      $archiveSha -cnotmatch '^[a-f0-9]{64}$' -or
      $sourceAsset -cne "ffmpeg-wasm-sources-v$version.tar.gz" -or
      $sourceSha -cnotmatch '^[a-f0-9]{64}$') {
    throw 'Invalid pinned Builder Release version, profile tag, hashes or source metadata.'
  }
}
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
$releaseSourceProof = Join-Path $root '.cache/reverse-runtime/corresponding-source.tar.gz'
$releaseArchiveProof = Join-Path $cache 'verified-release-archive.json'
function Verified-ReleaseArchive() {
  if (-not $isRelease) { return $true }
  if (-not (Test-Path -LiteralPath $releaseArchiveProof -PathType Leaf)) { return $false }
  try {
    $proof = Get-Content -Raw -Encoding UTF8 -LiteralPath $releaseArchiveProof | ConvertFrom-Json
    return $proof.tag -ceq $tag -and
           $proof.asset -ceq $assetName -and
           $proof.sha256 -ceq $archiveSha -and
           $proof.sourceSha256 -ceq $sourceSha
  } catch { return $false }
}
function Verified-SourceRelease() {
  # Do not accept locally cached WASM as a reviewed Release unless the
  # exact SHA-256 pinned corresponding source was downloaded and retained.
  if (-not $isRelease) { return $true }
  $expected = [string]$lock.correspondingSourceSha256
  if ($expected -cnotmatch '^[a-f0-9]{64}$' -or
      -not (Test-Path -LiteralPath $releaseSourceProof -PathType Leaf)) {
    return $false
  }
  return (Get-Hash $releaseSourceProof) -ceq $expected
}
function Cached() {
  try {
    if (-not (Verified-SourceRelease) -or -not (Verified-ReleaseArchive)) { return $false }
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
$token = ''
if (-not $isRelease) {
  $token = [string]$env:GITHUB_TOKEN
  if ([string]::IsNullOrWhiteSpace($token)) { $token = [string]$env:GH_TOKEN }
  if ([string]::IsNullOrWhiteSpace($token)) {
    throw "Pinned $Variant cache is absent. GITHUB_TOKEN or GH_TOKEN is required for temporary Builder Actions artifacts."
  }
}
New-Item -ItemType Directory -Force -Path $cache | Out-Null
$zip = Join-Path $cache 'builder-artifact.zip'
$extract = Join-Path $cache 'extract'
try {
  Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $extract
  Remove-Item -Force -ErrorAction SilentlyContinue $zip
  if ($isRelease) {
    # A reviewed, immutable public Release needs no token. All source and
    # binary identifiers must be pinned; never resolve 'latest'.
    $version = [string]$lock.builderVersion
    $tag = [string]$lock.builderTag
    $assetName = [string]$entry.releaseAsset
    $archiveSha = [string]$entry.releaseArchiveSha256
    $sourceAsset = [string]$lock.correspondingSourceAsset
    $sourceSha = [string]$lock.correspondingSourceSha256
    if ($version -notmatch '^\d+\.\d+\.\d+$' -or $tag -cnotin @("v$version","video-reverse-v$version") -or
        $assetName -cne "ffmpeg-wasm-video-reverse-$Variant-v$version.zip" -or
        $archiveSha -cnotmatch '^[a-f0-9]{64}$' -or
        $sourceAsset -cne "ffmpeg-wasm-sources-v$version.tar.gz" -or
        $sourceSha -cnotmatch '^[a-f0-9]{64}$') {
      throw "Invalid pinned Builder Release version, archive hash or corresponding-source metadata."
    }
    $releaseBase = "https://github.com/$($lock.builderRepository)/releases/download/$tag"
    if (-not (Verified-SourceRelease)) {
      $sourceDir = Split-Path -Parent $releaseSourceProof
      New-Item -ItemType Directory -Path $sourceDir -Force | Out-Null
      Write-Host "[Reverse WASM] Verifying corresponding source $tag / $sourceAsset"
      Invoke-WebRequest -Uri "$releaseBase/$sourceAsset" -UseBasicParsing -OutFile $releaseSourceProof
      if (-not (Verified-SourceRelease)) {
        Remove-Item -LiteralPath $releaseSourceProof -Force -ErrorAction SilentlyContinue
        throw 'Corresponding GPL source archive SHA-256 mismatch.'
      }
    }
    $url = "$releaseBase/$assetName"
    Write-Host "[Reverse WASM] Downloading fixed Builder Release $tag / $assetName"
    Invoke-WebRequest -Uri $url -UseBasicParsing -OutFile $zip
    if ((Get-Hash $zip) -cne $archiveSha) {
      throw "Pinned $Variant Builder Release archive SHA-256 mismatch."
    }
    Expand-Archive -LiteralPath $zip -DestinationPath $extract -Force
    $variantDir = $extract
    foreach ($notice in @('LICENSES/FFmpeg-COPYING.GPLv2',
        'LICENSES/x264-COPYING', 'LICENSES/Emscripten-LICENSE',
        'THIRD_PARTY_NOTICES.md', 'BUILDINFO.txt')) {
      if (-not (Test-Path -LiteralPath (Join-Path $variantDir $notice) -PathType Leaf)) {
        throw "Pinned Builder Release is missing license/build notice: $notice"
      }
    }
  } else {
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
  }

  $manifestFile = Join-Path $variantDir 'manifest.json'
  $manifest = Get-Content -Raw -Encoding UTF8 $manifestFile | ConvertFrom-Json
  Assert-Manifest $manifest
  foreach ($name in @('ffmpeg.js', 'ffmpeg.wasm')) {
    Assert-File $name $variantDir $entry.assets
  }
  $loader = Join-Path $cache 'browser-ffmpeg.js'
  if ($isRelease) {
    Assert-File 'browser-ffmpeg.js' $variantDir $entry.assets
    Copy-Item -LiteralPath (Join-Path $variantDir 'browser-ffmpeg.js') -Destination $loader -Force
  } else {
    $runtimeUrl = "https://raw.githubusercontent.com/$($lock.builderRepository)/$($lock.builderCommit)/runtime/browser-ffmpeg.js"
    Invoke-WebRequest -Uri $runtimeUrl -UseBasicParsing -Headers @{'User-Agent'='browser-kitty-reverse-clip/0.1'} -OutFile $loader
  }
  Assert-File 'browser-ffmpeg.js' $cache $entry.assets
  foreach ($name in @('ffmpeg.js','ffmpeg.wasm')) {
    Copy-Item -LiteralPath (Join-Path $variantDir $name) -Destination (Join-Path $cache $name) -Force
  }
  Copy-Item -LiteralPath $manifestFile -Destination (Join-Path $cache 'manifest.json') -Force
  if ($isRelease) {
    # Only create this marker *after* the public binary ZIP has been fetched
    # and its hash and contained license/JS/WASM assets were checked.
    $proof = @{ tag=$tag; asset=$assetName; sha256=$archiveSha; sourceSha256=$sourceSha } |
      ConvertTo-Json -Compress
    [IO.File]::WriteAllText($releaseArchiveProof, $proof, (New-Object Text.UTF8Encoding($false)))
  }
  if (-not (Cached)) { throw "Pinned $Variant runtime cache failed final validation." }
  Write-Host "[Reverse WASM] $Variant JS/WASM and metadata verified. No runtime downloads."
} finally {
  Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $extract
  Remove-Item -Force -ErrorAction SilentlyContinue $zip
}
