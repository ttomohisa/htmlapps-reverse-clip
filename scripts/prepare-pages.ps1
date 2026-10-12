param()
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$dist = Join-Path $root 'dist'
$pages = Join-Path $root 'pages-dist'
$mtDir = Join-Path $pages 'mt'
$swPath = Join-Path $root 'vendor/coi-serviceworker/coi-serviceworker.js'
$lockPath = Join-Path $root 'coi-serviceworker.lock.json'
$stPath = Join-Path $dist 'index.html'
$mtPath = Join-Path $dist 'index.mt.html'
foreach ($path in @($swPath,$lockPath,$stPath,$mtPath)) {
  if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
    throw "GitHub Pages build input missing: $path"
  }
}
$lock = Get-Content -Raw -Encoding UTF8 $lockPath | ConvertFrom-Json
$sha = [Security.Cryptography.SHA256]::Create()
try {
  $bytes = [IO.File]::ReadAllBytes($swPath)
  $actual = ($sha.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') }) -join ''
} finally { $sha.Dispose() }
if ([string]$lock.version -ne '0.1.7' -or [string]$lock.sha256 -ne $actual -or
    [string]$lock.commit -ne '7b1d2a092d0d2dd2b7270b6f12f13605de26f214') {
  throw 'Pinned same-origin COI Service Worker failed identity/SHA-256 verification.'
}
$st = Get-Content -Raw -Encoding UTF8 $stPath
$mt = Get-Content -Raw -Encoding UTF8 $mtPath
if (-not $st.Contains('const RUNTIME_VARIANT = "single-thread";') -or
    -not $mt.Contains('const RUNTIME_VARIANT = "multi-thread";')) {
  throw 'ST and MT generated outputs have an unexpected threading marker.'
}
if ($st.Contains('coi-serviceworker.js') -or $mt.Contains('coi-serviceworker.js')) {
  throw 'Standalone HTML may not depend on the Pages-only Service Worker.'
}
if (-not $mt.Contains('</head>')) { throw 'MT HTML lacks </head> for Pages bootstrap.' }
$bootstrap = @'
  <!-- GitHub Pages MT only. On Browser Kitty the isolation headers come from Cloudflare. -->
  <script>
    if (globalThis.crossOriginIsolated === false) {
      window.coi = {
        coepCredentialless: () => false,
        coepDegrade: () => false,
        quiet: true
      };
      const sw = document.createElement("script");
      sw.src = "./coi-serviceworker.js";
      document.head.appendChild(sw);
    }
  </script>
'@
if (Test-Path $pages) { Remove-Item $pages -Recurse -Force }
New-Item -ItemType Directory -Force $mtDir | Out-Null
Copy-Item -LiteralPath $stPath -Destination (Join-Path $pages 'index.html')
Copy-Item -LiteralPath $swPath -Destination (Join-Path $mtDir 'coi-serviceworker.js')
$mtPages = $mt.Replace('</head>', $bootstrap + [Environment]::NewLine + '</head>')
[IO.File]::WriteAllText((Join-Path $mtDir 'index.html'), $mtPages, (New-Object Text.UTF8Encoding($false)))
[IO.File]::WriteAllText((Join-Path $pages '.nojekyll'), '', (New-Object Text.UTF8Encoding($false)))
Write-Host '[OK] Pages root = ST; /mt/ = MT with pinned same-origin COI fallback.'
