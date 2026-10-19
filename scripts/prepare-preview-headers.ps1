param()
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$dist = Join-Path $root 'dist'
if (-not (Test-Path (Join-Path $dist 'index.mt.html'))) {
  throw 'Build both ST and MT variants before preparing Preview headers.'
}
$headers = @'
# Keep the ST root portable. Only the MT entrypoints need COOP/COEP.
/index.mt.html
  Cross-Origin-Opener-Policy: same-origin
  Cross-Origin-Embedder-Policy: require-corp
  Cross-Origin-Resource-Policy: same-origin

/index.mt.self-extract.html
  Cross-Origin-Opener-Policy: same-origin
  Cross-Origin-Embedder-Policy: require-corp
  Cross-Origin-Resource-Policy: same-origin
'@
[IO.File]::WriteAllText((Join-Path $dist '_headers'), $headers, (New-Object Text.UTF8Encoding($false)))
Write-Host '[OK] Preview ST root remains non-isolated; MT files get COOP/COEP/CORP.'
