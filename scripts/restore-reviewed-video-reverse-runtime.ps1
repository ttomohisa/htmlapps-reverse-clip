param(
  [Parameter(Mandatory=$true)][ValidateSet('single-thread','multi-thread')][string]$Variant,
  [Parameter(Mandatory=$true)][string]$Destination
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# This is an EXPIRING Actions backup, not a published GPL Release. Used only
# while the exact originally pinned experimental Builder 1.10.6 artifact
# is no longer downloadable. No release-approved status is ever created.
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$lock = Get-Content -Raw -Encoding UTF8 (Join-Path $root 'reverse-runtime.lock.json') | ConvertFrom-Json
if ([string]$lock.kind -cne 'experimental-dual-github-actions-artifact' -or
    [string]$lock.status -cne 'temporary-not-release' -or
    [long]$lock.artifactId -ne 11914029733 -or
    [string]$lock.builderCommit -cne '8e60da7cf9de644ce3f6cce9c007b17e6a385c53') {
  throw 'Reviewed backup is only permitted for the original experimental 1.10.6 runtime.'
}
$token = [string]$env:GITHUB_TOKEN
if ([string]::IsNullOrWhiteSpace($token)) { $token = [string]$env:GH_TOKEN }
if ([string]::IsNullOrWhiteSpace($token)) { throw 'GITHUB_TOKEN or GH_TOKEN is required for the temporary Actions backup.' }

function Sha256([string]$Path) {
  $f = [IO.File]::OpenRead($Path)
  try {
    $sha = [Security.Cryptography.SHA256]::Create()
    try { return (($sha.ComputeHash($f) | ForEach-Object { $_.ToString('x2') }) -join '') }
    finally { $sha.Dispose() }
  } finally { $f.Dispose() }
}

$pins = @{
  'ffmpeg-wasm-video-reverse-single-thread-v1.10.6.zip'='9087bf4d03b29d141e78c93e9de62a237f2d408f24b43caeef26072e6d3b21b0'
  'ffmpeg-wasm-video-reverse-multi-thread-v1.10.6.zip'='b577be491754ecfa96d0b86021184b82b2fc280f8881bd73cb5d52d83914d3bd'
  'ffmpeg-wasm-sources-v1.10.6.tar.gz'='9ceb47a5f46fb3484f8b1f6a8fa37e6d0dc4144aa09d78939ac9d23e8ab5ce92'
  'VIDEO_REVERSE_LICENSE_ADDENDUM.md'='e011d66e3451dbf5ffa5f67f26636749664a69d285a3cfc665a71e36635e15f3'
}
$stageNames = @(
  'ffmpeg-wasm-video-reverse-single-thread-v1.10.6.zip',
  'ffmpeg-wasm-video-reverse-multi-thread-v1.10.6.zip',
  'ffmpeg-wasm-sources-v1.10.6.tar.gz',
  'BUILDINFO-video-reverse-single-thread.txt',
  'BUILDINFO-video-reverse-multi-thread.txt',
  'SHA256SUMS.txt',
  'VIDEO_REVERSE_LICENSE_ADDENDUM.md',
  'VIDEO_REVERSE_PROMOTION_MANIFEST.json',
  'REVERSE_CLIP_RELEASE_LOCK_PROPOSAL.json',
  'REVIEW_RESTAGING_PROVENANCE.json'
)
if (Test-Path -LiteralPath $Destination) {
  if (@(Get-ChildItem -LiteralPath $Destination -Force).Count -gt 0) {
    throw 'Reviewed backup destination must be empty.'
  }
}
New-Item -ItemType Directory -Force -Path $Destination | Out-Null
$zip = Join-Path $Destination 'reviewed-actions-backup.zip'
$staged = Join-Path $Destination 'stage'
try {
  $headers = @{
    Accept = 'application/vnd.github+json'
    'User-Agent' = 'browser-kitty-reverse-clip/review-only-backup'
    Authorization = "Bearer $token"
  }
  $url = "https://api.github.com/repos/$($lock.builderRepository)/actions/artifacts/12145680508/zip"
  Invoke-WebRequest -Uri $url -Headers $headers -UseBasicParsing -OutFile $zip
  New-Item -ItemType Directory -Path $staged -Force | Out-Null
  Expand-Archive -LiteralPath $zip -DestinationPath $staged -Force
  $actual = @(Get-ChildItem -LiteralPath $staged -Force | ForEach-Object { $_.Name })
  if ($actual.Count -ne $stageNames.Count -or
      @($actual | Where-Object { $_ -notin $stageNames }).Count -gt 0) {
    throw 'Reviewed backup has missing or unexpected payloads.'
  }
  foreach ($name in $stageNames) {
    if (-not (Test-Path -LiteralPath (Join-Path $staged $name) -PathType Leaf)) {
      throw "Reviewed backup is missing a regular file: $name"
    }
  }
  foreach ($name in $pins.Keys) {
    if ((Sha256 (Join-Path $staged $name)) -cne $pins[$name]) {
      throw "Reviewed backup independent SHA-256 mismatch: $name"
    }
  }
  $originalChecks = @{}
  foreach ($line in @(Get-Content -LiteralPath (Join-Path $staged 'SHA256SUMS.txt'))) {
    if ($line -cnotmatch '^([a-f0-9]{64})  ([A-Za-z0-9._-]+)$') {
      throw 'Malformed original Builder checksum.'
    }
    if ($originalChecks.ContainsKey($Matches[2])) { throw 'Duplicate Builder checksum.' }
    $originalChecks[$Matches[2]] = $Matches[1]
  }
  if ($originalChecks.Count -ne 5) { throw 'Incorrect original Builder checksum count.' }
  foreach ($name in ($stageNames | Select-Object -First 5)) {
    if (-not $originalChecks.ContainsKey($name) -or
        (Sha256 (Join-Path $staged $name)) -cne $originalChecks[$name]) {
      throw "Original checked Builder file does not match: $name"
    }
  }
  $manifest = Get-Content -Raw -Encoding UTF8 (Join-Path $staged 'VIDEO_REVERSE_PROMOTION_MANIFEST.json') | ConvertFrom-Json
  if ([string]$manifest.status -cne 'review-only-not-published' -or
      [bool]$manifest.publicReleaseApproved -or [bool]$manifest.gplLegalReviewApproved -or
      [string]$manifest.exactCompiledBuilderSourceCommit -cne [string]$lock.builderCommit) {
    throw 'Reviewed backup must remain unpublished and unapproved.'
  }
  $proposal = Get-Content -Raw -Encoding UTF8 (Join-Path $staged 'REVERSE_CLIP_RELEASE_LOCK_PROPOSAL.json') | ConvertFrom-Json
  if ([string]$proposal.proposedLock.kind -cne 'review-only-proposed-github-release-st-mt' -or
      [string]$proposal.proposedLock.status -cne 'review-only-not-published' -or
      [bool]$proposal.releasePublished) {
    throw 'Reviewed backup app proposal is unexpectedly active.'
  }
  $binaryZip = Join-Path $staged "ffmpeg-wasm-video-reverse-$Variant-v1.10.6.zip"
  $out = Join-Path $Destination $Variant
  New-Item -ItemType Directory -Path $out -Force | Out-Null
  Expand-Archive -LiteralPath $binaryZip -DestinationPath $out -Force
  $entry = $lock.variants.PSObject.Properties[$Variant].Value
  foreach ($name in @('ffmpeg.js','ffmpeg.wasm')) {
    $expected = [string]$entry.assets.PSObject.Properties[$name].Value
    if ((Sha256 (Join-Path $out $name)) -cne $expected) {
      throw "Reviewed backup original locked $Variant asset differs: $name"
    }
  }
  if ((Sha256 (Join-Path $out 'browser-ffmpeg.js')) -cne [string]$lock.browserRuntimeSha256) {
    throw 'Reviewed backup browser loader does not match original lock.'
  }
  if ((Sha256 (Join-Path $out 'BUILDINFO.txt')) -cne
      (Sha256 (Join-Path $staged "BUILDINFO-video-reverse-$Variant.txt"))) {
    throw 'Reviewed backup inner and outer build information differs.'
  }
  foreach ($name in @('LICENSES/FFmpeg-COPYING.GPLv2','LICENSES/x264-COPYING',
      'LICENSES/Emscripten-LICENSE','THIRD_PARTY_NOTICES.md')) {
    if (-not (Test-Path -LiteralPath (Join-Path $out $name) -PathType Leaf)) {
      throw "Reviewed backup lacks original license file: $name"
    }
  }
  [IO.File]::WriteAllText((Join-Path $Destination 'REVIEW_ONLY_BACKUP_VERIFIED'),
                         'temporary-not-release', (New-Object Text.UTF8Encoding($false)))
  Write-Host "[Reverse WASM] Review-only backup ST/MT source/ZIP hashes and original $Variant lock verified."
} finally {
  Remove-Item -LiteralPath $zip -Force -ErrorAction SilentlyContinue
  Remove-Item -LiteralPath $staged -Recurse -Force -ErrorAction SilentlyContinue
}
