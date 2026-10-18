param(
  [Parameter(Mandatory=$true)]
  [ValidateSet('single-thread','multi-thread')]
  [string]$Variant,
  [switch]$ForceDownload,
  [switch]$UseAuditedReviewFallback
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
# Fail closed if an unapproved staging proposal is copied into the live lock.
# A published ZIP and a proposed tag alone do not authorize application release.
if ($isRelease -and [string]$lock.status -cne 'release-approved') {
  throw 'Public Builder Release import requires explicit release-approved status.'
}
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
  $noticeAsset = [string]$lock.supplementalNoticeAsset
  $noticeSha = [string]$lock.supplementalNoticeSha256
  if ($version -notmatch '^\d+\.\d+\.\d+$' -or
      $tag -cnotin @("v$version","video-reverse-v$version") -or
      $assetName -cne "ffmpeg-wasm-video-reverse-$Variant-v$version.zip" -or
      $archiveSha -cnotmatch '^[a-f0-9]{64}$' -or
      $sourceAsset -cne "ffmpeg-wasm-sources-v$version.tar.gz" -or
      $sourceSha -cnotmatch '^[a-f0-9]{64}$' -or
      $noticeAsset -cne 'VIDEO_REVERSE_LICENSE_ADDENDUM.md' -or
      $noticeSha -cnotmatch '^[a-f0-9]{64}$') {
    throw 'Invalid pinned Builder Release version, profile tag, hashes, GPL notice or source metadata.'
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
$releaseNoticeProof = Join-Path $root '.cache/reverse-runtime/video-reverse-gpl-addendum.md'
function Verified-ReleaseNotice() {
  if (-not $isRelease) { return $true }
  if (-not (Test-Path -LiteralPath $releaseNoticeProof -PathType Leaf)) { return $false }
  if ((Get-Hash $releaseNoticeProof) -cne $noticeSha) { return $false }
  $noticeText = Get-Content -Raw -Encoding UTF8 -LiteralPath $releaseNoticeProof
  return $noticeText.Contains('video-reverse') -and
         $noticeText.Contains('GPL-2.0-or-later') -and
         $noticeText.Contains('x264')
}
$releaseArchiveProof = Join-Path $cache 'verified-release-archive.json'
function Verified-ReleaseArchive() {
  if (-not $isRelease) { return $true }
  if (-not (Test-Path -LiteralPath $releaseArchiveProof -PathType Leaf)) { return $false }
  try {
    $proof = Get-Content -Raw -Encoding UTF8 -LiteralPath $releaseArchiveProof | ConvertFrom-Json
    return $proof.tag -ceq $tag -and
           $proof.asset -ceq $assetName -and
           $proof.sha256 -ceq $archiveSha -and
           $proof.sourceSha256 -ceq $sourceSha -and
           $proof.noticeSha256 -ceq $noticeSha
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
    if (-not (Verified-SourceRelease) -or -not (Verified-ReleaseNotice) -or
        -not (Verified-ReleaseArchive)) { return $false }
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
if (-not $ForceDownload -and -not $UseAuditedReviewFallback -and (Cached)) {
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
  Remove-Item -Recurse -Force -ErrorAction SilentlyContinue (Join-Path $cache 'reviewed-binary-extract')
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
    if (-not (Verified-ReleaseNotice)) {
      New-Item -ItemType Directory -Path (Split-Path -Parent $releaseNoticeProof) -Force | Out-Null
      Invoke-WebRequest -Uri "$releaseBase/$noticeAsset" -UseBasicParsing -OutFile $releaseNoticeProof
      if (-not (Verified-ReleaseNotice)) {
        Remove-Item -LiteralPath $releaseNoticeProof -Force -ErrorAction SilentlyContinue
        throw 'Supplemental GPL video-reverse notice SHA-256 mismatch or missing profile details.'
      }
    }
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
    $legacyAvailable = $false
    if (-not $UseAuditedReviewFallback) {
      Write-Host "[Reverse WASM] Downloading $Variant from pinned Builder artifact $($lock.artifactId)"
      try {
        Invoke-WebRequest -Uri $url -Headers $headers -UseBasicParsing -OutFile $zip
        $legacyAvailable = $true
      } catch {
        $statusCode = $null
        if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
          $statusCode = [int]$_.Exception.Response.StatusCode
        }
        # Only a confirmed expired/not-found Actions artifact may activate this
        # reviewed, still temporary fallback. Auth/server failures stay fatal.
        if ($statusCode -notin @(404,410)) { throw }
        Write-Warning "Original temporary Builder artifact unavailable (HTTP $statusCode). Trying SHA-pinned review-only preservation copy."
      }
    }
    if ($legacyAvailable) {
      Expand-Archive -LiteralPath $zip -DestinationPath $extract -Force
      $variantDir = Join-Path $extract $Variant
    } else {
      # The review artifact is temporary and must NEVER be treated as a
      # published/approved GPL Release. It is only a byte-identical archive
      # backup of the compiled source and binary already locked above.
      if ([string]$lock.status -cne 'temporary-not-release' -or
          [int64]$lock.artifactId -ne 11914029733 -or
          [string]$lock.builderCommit -cne '8e60da7cf9de644ce3f6cce9c007b17e6a385c53' -or
          [string]$lock.builderVersion -cne '1.10.6') {
        throw 'Audited fallback is only available for exact experimental Builder 1.10.6 lock.'
      }
      $reviewArtifactId = 12145680508
      $reviewUrl = "https://api.github.com/repos/$($lock.builderRepository)/actions/artifacts/$reviewArtifactId/zip"
      Write-Host "[Reverse WASM] Using review-only archived source + WASM (artifact $reviewArtifactId; NOT a GitHub Release)"
      Remove-Item -LiteralPath $zip -Force -ErrorAction SilentlyContinue
      Invoke-WebRequest -Uri $reviewUrl -Headers $headers -UseBasicParsing -OutFile $zip
      Expand-Archive -LiteralPath $zip -DestinationPath $extract -Force
      $expectedStageNames = @(
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
      $actualStageNames = @(Get-ChildItem -LiteralPath $extract -Force | ForEach-Object { $_.Name })
      if ((@($actualStageNames | Where-Object { $_ -notin $expectedStageNames }).Count -ne 0) -or
          (@($expectedStageNames | Where-Object { $_ -notin $actualStageNames }).Count -ne 0)) {
        throw 'Reviewed backup has missing or unexpected files.'
      }
      foreach ($name in $expectedStageNames) {
        if (-not (Test-Path -LiteralPath (Join-Path $extract $name) -PathType Leaf)) {
          throw "Reviewed backup has unexpected non-file payload: $name"
        }
      }
      $sourcePath = Join-Path $extract 'ffmpeg-wasm-sources-v1.10.6.tar.gz'
      $noticePath = Join-Path $extract 'VIDEO_REVERSE_LICENSE_ADDENDUM.md'
      $pins = @{
        'ffmpeg-wasm-video-reverse-single-thread-v1.10.6.zip'='9087bf4d03b29d141e78c93e9de62a237f2d408f24b43caeef26072e6d3b21b0'
        'ffmpeg-wasm-video-reverse-multi-thread-v1.10.6.zip'='b577be491754ecfa96d0b86021184b82b2fc280f8881bd73cb5d52d83914d3bd'
        'ffmpeg-wasm-sources-v1.10.6.tar.gz'='9ceb47a5f46fb3484f8b1f6a8fa37e6d0dc4144aa09d78939ac9d23e8ab5ce92'
        'VIDEO_REVERSE_LICENSE_ADDENDUM.md'='e011d66e3451dbf5ffa5f67f26636749664a69d285a3cfc665a71e36635e15f3'
      }
      foreach ($name in $pins.Keys) {
        if ((Get-Hash (Join-Path $extract $name)) -cne $pins[$name]) {
          throw "Reviewed fallback SHA-256 mismatch: $name"
        }
      }
      $stageManifest = Get-Content -Raw -Encoding UTF8 (Join-Path $extract 'VIDEO_REVERSE_PROMOTION_MANIFEST.json') | ConvertFrom-Json
      if ([string]$stageManifest.status -cne 'review-only-not-published' -or
          [bool]$stageManifest.publicReleaseApproved -or
          [bool]$stageManifest.gplLegalReviewApproved -or
          [string]$stageManifest.exactCompiledBuilderSourceCommit -cne [string]$lock.builderCommit) {
        throw 'Reviewed fallback improperly marked as a Release.'
      }
      $proposal = Get-Content -Raw -Encoding UTF8 (Join-Path $extract 'REVERSE_CLIP_RELEASE_LOCK_PROPOSAL.json') | ConvertFrom-Json
      if ([string]$proposal.proposedLock.kind -cne 'review-only-proposed-github-release-st-mt' -or
          [string]$proposal.proposedLock.status -cne 'review-only-not-published' -or
          [bool]$proposal.releasePublished -or [bool]$proposal.legalApprovalRecorded) {
        throw 'Reviewed fallback proposal must remain non-activatable.'
      }
      $sourceChecksums = @{}
      foreach ($line in @(Get-Content -LiteralPath (Join-Path $extract 'SHA256SUMS.txt'))) {
        if ($line -cnotmatch '^([a-f0-9]{64})  ([A-Za-z0-9._-]+)
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
    if ($variantDir -eq (Join-Path $cache 'reviewed-binary-extract')) {
      Assert-File 'browser-ffmpeg.js' $variantDir $entry.assets
      Copy-Item -LiteralPath (Join-Path $variantDir 'browser-ffmpeg.js') -Destination $loader -Force
    } else {
      $runtimeUrl = "https://raw.githubusercontent.com/$($lock.builderRepository)/$($lock.builderCommit)/runtime/browser-ffmpeg.js"
      Invoke-WebRequest -Uri $runtimeUrl -UseBasicParsing -Headers @{'User-Agent'='browser-kitty-reverse-clip/0.1'} -OutFile $loader
    }
  }
  Assert-File 'browser-ffmpeg.js' $cache $entry.assets
  foreach ($name in @('ffmpeg.js','ffmpeg.wasm')) {
    Copy-Item -LiteralPath (Join-Path $variantDir $name) -Destination (Join-Path $cache $name) -Force
  }
  Copy-Item -LiteralPath $manifestFile -Destination (Join-Path $cache 'manifest.json') -Force
  if ($isRelease) {
    # Only create this marker *after* the public binary ZIP has been fetched
    # and its hash and contained license/JS/WASM assets were checked.
    $proof = @{ tag=$tag; asset=$assetName; sha256=$archiveSha; sourceSha256=$sourceSha; noticeSha256=$noticeSha } |
      ConvertTo-Json -Compress
    [IO.File]::WriteAllText($releaseArchiveProof, $proof, (New-Object Text.UTF8Encoding($false)))
  }
  if (-not (Cached)) { throw "Pinned $Variant runtime cache failed final validation." }
  Write-Host "[Reverse WASM] $Variant JS/WASM and metadata verified. No runtime downloads."
} finally {
  Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $extract
  Remove-Item -Force -ErrorAction SilentlyContinue $zip
}
) {
          throw 'Original reviewed checksum file has invalid entries.'
        }
        if ($sourceChecksums.ContainsKey($Matches[2])) { throw 'Duplicate original reviewed checksum entry.' }
        $sourceChecksums[$Matches[2]] = $Matches[1]
      }
      if ($sourceChecksums.Count -ne 5) { throw 'Expected exactly five original Builder source/binary checksums.' }
      foreach ($name in @(
        'ffmpeg-wasm-video-reverse-single-thread-v1.10.6.zip',
        'ffmpeg-wasm-video-reverse-multi-thread-v1.10.6.zip',
        'ffmpeg-wasm-sources-v1.10.6.tar.gz',
        'BUILDINFO-video-reverse-single-thread.txt',
        'BUILDINFO-video-reverse-multi-thread.txt')) {
        if (-not $sourceChecksums.ContainsKey($name) -or
            (Get-Hash (Join-Path $extract $name)) -cne $sourceChecksums[$name]) {
          throw "Original Builder checksum differs in reviewed fallback: $name"
        }
      }
      $noticeText = Get-Content -Raw -Encoding UTF8 -LiteralPath $noticePath
      if (-not $noticeText.Contains('GPL-2.0-or-later') -or
          -not $noticeText.Contains('video-reverse') -or
          -not $noticeText.Contains('x264')) {
        throw 'Reviewed fallback GPL notice is incomplete.'
      }
      $binaryArchive = Join-Path $extract "ffmpeg-wasm-video-reverse-$Variant-v1.10.6.zip"
      $innerExtract = Join-Path $cache 'reviewed-binary-extract'
      Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $innerExtract
      Expand-Archive -LiteralPath $binaryArchive -DestinationPath $innerExtract -Force
      $variantDir = $innerExtract
      # The inner ffmpeg.js, ffmpeg.wasm and browser-ffmpeg.js remain
      # validated below against the existing app lock SHA-256 values.
      $buildInfoName = "BUILDINFO-video-reverse-$Variant.txt"
      if ((Get-Hash (Join-Path $extract $buildInfoName)) -cne (Get-Hash (Join-Path $variantDir 'BUILDINFO.txt'))) {
        throw "Reviewed fallback original BUILDINFO does not match $Variant binary."
      }
      foreach ($notice in @('LICENSES/FFmpeg-COPYING.GPLv2',
          'LICENSES/x264-COPYING','LICENSES/Emscripten-LICENSE','THIRD_PARTY_NOTICES.md')) {
        if (-not (Test-Path -LiteralPath (Join-Path $variantDir $notice) -PathType Leaf)) {
          throw "Reviewed fallback missing license notice: $notice"
        }
      }
    }
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
    $proof = @{ tag=$tag; asset=$assetName; sha256=$archiveSha; sourceSha256=$sourceSha; noticeSha256=$noticeSha } |
      ConvertTo-Json -Compress
    [IO.File]::WriteAllText($releaseArchiveProof, $proof, (New-Object Text.UTF8Encoding($false)))
  }
  if (-not (Cached)) { throw "Pinned $Variant runtime cache failed final validation." }
  Write-Host "[Reverse WASM] $Variant JS/WASM and metadata verified. No runtime downloads."
} finally {
  Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $extract
  Remove-Item -Force -ErrorAction SilentlyContinue $zip
}
