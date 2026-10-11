# Reverse Clip / 動画逆再生

**開発状況：v0.1.0 技術検証中（Gate G1 未合格）。** 現段階は動画の逆再生アプリではなく、実機診断用の試験版です。

[製品仕様](APP_SPEC.md) · [開発計画](DEVELOPMENT_PLAN.md) · [検証記録](docs/feasibility/G1.md) · [English README](README.md)

## 目的

動画の短い区間を選択し、サーバーへアップロードせずに逆再生／往復再生のMP4を作成します。目標は標準720p/10秒、高画質1080p/5秒。いずれもスマホ実機での技術検証が必要です。

## v0.1.0でできること

- 動画の選択／端末が対応していれば撮影、プレビュー、区間設定、ファイル情報の取得。
- メモリ概算の確認、動画シーク・Worker・基本WASMのブラウザー内テスト。
- 明示的な操作による診断JSONファイルの保存。ファイル名や動画内容は出力しません。
- ネイティブFFmpegによる逆再生・往復再生・分割逆再生のフレーム順序テスト（Node.jsから実行）。

**未実装：** 動画の逆再生処理、MP4出力、音声逆再生、実機での安定動作、専用FFmpeg WASM。検証が完了したとは扱いません。

## ビルドと検証

現行の `htmlapps-template` 構成を使用します。Windowsでは `build-standalone.bat`、成果物は `dist/index.html` と `dist/index.self-extract.html`、ルート配布コピーは `reverse-clip.html` です。

```shell
node --test tests/feasibility/native-reverse.test.mjs
```

上記はローカルPCにNode.js 20以降とFFmpegの実行ファイルが必要な**任意のネイティブ試験**です。単一HTML自体の利用にそれらのインストールは必要ありません。

## プライバシー

選択した動画はブラウザー内のObject URLでプレビューし、アプリから外部送信しません。CSPは `connect-src 'none'`。診断JSONはユーザー操作時のみ出力し、動画そのものやファイル名は含みません。

## 対応環境

Chrome/Edgeを優先。iPhone Safari／Android Chromeは今後の実機確認が必要です。ブラウザー側の再生可否は端末・コーデックによって変わります。

## ライセンス

アプリのコードはMIT。FFmpeg/x264 WASM導入時は、対応ソース、ライセンス、固定リリースとハッシュを別途明記します。
