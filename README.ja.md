# Reverse Clip / 動画逆再生

[![GitHub Pages](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/workflows/deploy-pages.yml)
[![Single HTML](https://img.shields.io/badge/distribution-single%20HTML-16624f)](https://ttomohisa.github.io/htmlapps-reverse-clip/)
[![App: MIT](https://img.shields.io/badge/app%20license-MIT-blue)](LICENSE)
[![FFmpeg: GPL](https://img.shields.io/badge/FFmpeg%20WASM-GPL--2.0--or--later-blue)](THIRD_PARTY_NOTICES.md)

[English README](README.md)

動画の好きな区間を逆再生したり、通常再生から逆再生へ折り返す「往復再生」のMP4を作るアプリです。動画をサーバーへアップロードせず、ブラウザ内で処理します。登録・インストールは不要です。

## デモ

### [GitHub PagesでReverse Clipを開く](https://ttomohisa.github.io/htmlapps-reverse-clip/)

通常のページは**シングルスレッド版（ST）**です。対応ブラウザ向けに[マルチスレッド版（MT）](https://ttomohisa.github.io/htmlapps-reverse-clip/mt/)も公開しています。Webページの読み込みには通信が必要ですが、選択した動画の変換処理は端末内で行います。

[![Reverse ClipでMP4を作成したPCの結果画面](assets/screenshot.png)](https://ttomohisa.github.io/htmlapps-reverse-clip/)

ローカルでサンプル動画を変換して保存・検証した、PC版Chromeの画面です。**Android実機による動作確認を表す画像ではありません。** 画面は未正式リリースのv0.9.0 RCです。

## 主な機能

- **好きな区間を逆再生** — 動画の開始・終了位置を選び、逆向きに再生するH.264 MP4を作れます。
- **往復再生MP4を作成** — 通常再生から逆再生へつなぎ、折り返し地点の重複フレームを除いて1本の動画にします。
- **対応動画は音声も逆再生** — 既定は音声なし。読み取れる音声トラックがある場合は、逆再生したAAC音声を付けられます。
- **結果を確認して保存** — 完成したMP4をプレビューし、ファイル名を変更して保存できます。
- **PCとスマートフォンで操作** — 「動画 → 編集 → 結果」のスマホ向け画面、日英切替、中止・再試行に対応します。
- **単一HTML・ローカル処理** — FFmpeg WASMなど必要な実行ファイルをHTMLに内包し、動画データを外部へ送信しません。

## すぐに使う

### Webで使う

[デモを開く](https://ttomohisa.github.io/htmlapps-reverse-clip/)だけで利用できます。アカウント登録もインストールも必要ありません。

### 単一HTMLをオフラインで使う

生成済みの**ST版**は、ブラウザで `file://` から直接開けます。現時点ではReverse Clipアプリ本体のバージョン付きGitHub Releaseは未公開で、v1.0.0を準備中です。

1. Windowsでこのリポジトリをダウンロード、またはクローンします。
2. `build-standalone.bat` を実行して単一HTMLを生成します。
3. `dist/index.html` または `dist/index.self-extract.html` を好きな場所へコピーします。
4. Chromeで開けば、インターネット接続なしで使用できます。

初回ビルドでは、バージョンを固定した依存ファイルを取得するためネット接続が必要です。FFmpeg WASMは[公開済みの専用Release](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/releases/tag/video-reverse-v1.10.6)から取得します。生成したST版HTMLを使うときに再ダウンロードすることはありません。**MT版は専用のWeb配信設定が必要**で、`file://` での直接利用は対象外です。

## 使い方

1. **動画：** 端末から短いH.264 MP4を選び、元動画をプレビューします。
2. **編集：** タイムラインや秒数入力で使いたい区間の開始・終了位置を指定します。
3. **逆再生**または**往復再生**を選びます。
4. 出力サイズを選びます。初期の実用範囲としては**長辺360pxまたは720px**を想定しています。高画質の選択肢は試験的な機能です。
5. 通常は**音声なし**のままで作成します。対応する音声が見つかった動画では、音声の逆再生も選べます。
6. MP4を作成します。処理を止めたいときは「中止」を使います。
7. **結果：** 完成動画を再生して確認し、ファイル名を入力して「MP4を保存」を押します。

未保存の結果がある状態で別の動画へ切り替えると、破棄の確認を表示します。変換に失敗した場合や出力が不完全な場合は、完成済みMP4として保存させません。なお、ダウンロード開始の表示だけでは、端末への保存完了を保証しません。

### 画面例

| PC表示（日本語） | スマホ幅（日本語） |
| --- | --- |
| ![Reverse ClipのPC結果画面](assets/screenshot.png) | ![Reverse Clipのスマホ幅の結果画面](assets/screenshot-mobile.png) |

[英語版PC画面](assets/screenshot-en.png) · [英語版スマホ幅画面](assets/screenshot-mobile-en.png) · [画像の検証記録](docs/release/RC_SCREENSHOT_ASSET_MANIFEST.json)

画像はPC版Chromeで実際にMP4を変換したときの画面を、PCとスマホ相当の表示幅で撮影したものです。Android実機の撮影画像ではありません。

## GitHub Pagesでの公開

`main` に変更が入ると、[公開ワークフロー](.github/workflows/deploy-pages.yml)が依存ファイルを固定してHTMLを生成し、GitHub Pagesへ配信します。

- `/`：通常のST版
- `/mt/`：同一オリジンの補助スクリプトで必要な隔離環境を用意したMT版

ほかのホスティング環境でMT版を使う場合も、対応するブラウザと隔離設定が必要です。

## 開発とビルド

```text
.
├─ src/index.template.html             # 日本語・英語を含むアプリ本体
├─ app.config.json                     # アプリの版数・出力先
├─ reverse-runtime.lock.json           # ST/MT WASMと対応ソースのハッシュ
├─ build-standalone.bat / .ps1          # Windows用の単一HTMLビルダー
├─ scripts/prepare-pages.ps1           # PagesのST/MT配信構成
├─ dist/index.html                     # 生成するST版HTML
├─ dist/index.self-extract.html        # 圧縮されたST版HTML
├─ dist/index.mt.html                  # 生成するMT版HTML
└─ .github/workflows/                   # ビルド検証・デプロイ
```

標準ビルドでは、MT版の自己展開HTMLと、読みやすいST版と同一内容の `reverse-clip.html` も生成します。生成物を直接編集せず、`src/index.template.html` などを変更してください。

PowerShellからのビルド・検証は次のコマンドで実行できます。

```powershell
./scripts/check-repository.ps1
```

FFmpeg WASMのバイナリ・対応ソース・ライセンス補足文書はSHA-256で固定しています。詳細は[製品仕様](APP_SPEC.md)、[開発計画](DEVELOPMENT_PLAN.md)、[開発への参加方法](CONTRIBUTING.md)、[v1.0.0公開準備](docs/release/V100_RELEASE_READINESS.md)を参照してください。

## プライバシーと通信

- 選択した動画はアプリから外部へ送信されません。読み込み・逆再生・プレビュー・MP4生成をブラウザ内で行います。
- 生成HTMLには `connect-src 'none'` を含むContent Security Policyがあり、実行時に外部CDNのFFmpeg等を読み込みません。
- Web版では最初にページを取得する通信があります。MT版の隔離用スクリプトも同一サイトから読み込みますが、動画のアップロードには使いません。
- Androidのファイル提供元によっては、動画を直接読み込めないことがあります。その場合に限り、**64MiB以下のファイル**を端末内のメモリへ一時コピーして再試行することがあります。サーバー送信ではありません。

## 制限事項

- **H.264 MP4が主な検証済み入力形式**です。初期の主対象はWindows ChromeとAndroid Chromeです。H.264 MOVや一部のフレームレート・回転動画はPC版Chromeで検証していますが、あらゆる撮影動画の動作を保証するものではありません。
- 出力は**H.264 MP4・15fps**です。元動画のフレームレートは保持しません。フレーム境界へ合わせるため、指定時刻がわずかに調整されることがあります。
- 通常利用では**0.5～5秒程度**の短い区間を想定しています。最大10秒の処理は試験的な対応で、1080p級は5秒までです。処理時間とメモリ使用量は端末によって異なります。
- **既定は音声なし**です。音声の逆再生は対応トラックだけ利用でき、複数音声トラックの選択には対応していません。
- HEVC/H.265、HDR・10-bitの色再現、iPhone Safariでの動作は**対応を保証していません**。
- MT版にはSharedArrayBufferと適切なcross-origin isolationが必要です。ローカルで直接開く場合はST版を使ってください。
- MP4の保存はブラウザへ依頼する方式です。見当たらない場合は端末のダウンロード先を確認してください。

## 使用ライブラリとライセンス

| 構成要素 | バージョン・参照先 | ライセンス | 用途 |
| --- | --- | --- | --- |
| Reverse Clipアプリ | このリポジトリ | [MIT](LICENSE) | UIと動画変換の操作 |
| FFmpeg + x264 WASM（ST/MT） | [Builder video-reverse-v1.10.6](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/releases/tag/video-reverse-v1.10.6) | GPL-2.0-or-later | 映像・音声処理 |
| coi-serviceworker（Pages MT版のみ） | 0.1.7、[固定コミット](coi-serviceworker.lock.json) | MIT | GitHub Pagesでの隔離環境 |

FFmpeg・x264・Emscripten等の[対応ソース](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/releases/download/video-reverse-v1.10.6/ffmpeg-wasm-sources-v1.10.6.tar.gz)と[GPL補足文書](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/releases/download/video-reverse-v1.10.6/VIDEO_REVERSE_LICENSE_ADDENDUM.md)は公開済みです。アプリ本体がMITでも、組み込まれたFFmpeg/x264 WASMのGPLライセンスは別に適用されます。詳細は[第三者ライセンス表記](THIRD_PARTY_NOTICES.md)を参照してください。

## 開発状況・コントリビューション

**v0.9.0 公開前RC準備版：** アプリのコードは`main`に統合済みですが、Reverse Clipアプリ本体のv1.0.0 GitHub Releaseはまだありません。従来のG2受入条件は未達成のまま履歴として保持し、最終G3判定を進めています。[v1.0.0の準備状況](docs/release/V100_RELEASE_READINESS.md) · [検証記録](docs/release/RC_CHECKLIST.md)

不具合や改善案はGitHub Issuesからお知らせください。[開発への参加方法](CONTRIBUTING.md)も参照できます。Browser Kitty本体への追加は**v1.0.0正式リリース後**に行います。
