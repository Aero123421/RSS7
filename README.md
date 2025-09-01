#  Discord Bot

RSS/Atom フィードを監視し、取得した記事を AI で処理して Discord に投稿するボットです。

![Discord RSS Bot](docs/images/discord_rss_bot_logo.png)

## Quick Start (No Docker, Windows 11)

PowerShell を開き、以下の手順でボットを起動します。

```powershell
# リポジトリのクローン
 git clone https://github.com/Aero123421/RSS7.git
 cd RSS7

# 環境変数の設定
 copy .env.example .env   # DISCORD_TOKEN / CLIENT_ID / GUILD_ID を編集

# Python 仮想環境
 py -m venv .venv
 .\.venv\Scripts\Activate.ps1
 py -m pip install -U pip
 py -m pip install -r requirements.txt

# スラッシュコマンド登録（初回/変更時）
 npm install
 npm run deploy

# API サーバー（別ターミナル）
 py -m uvicorn api_server:app --reload

# ボット起動
 py -m src.bot
```

## 設定 (.env)

| 変数名 | 説明 |
| --- | --- |
| `DISCORD_TOKEN` | Discord ボットトークン *(必須)* |
| `CLIENT_ID` | アプリケーションの Client ID *(必須)* |
| `GUILD_ID` | 開発用ギルド ID *(必須)* |
| `API_BASE_URL` | API サーバー URL (省略可) |
| `GOOGLE_API_KEY` | Google Gemini API キー (省略可) |

起動時に必須キーが無い場合は、欠落したキー名を表示して停止します。

## 開発コマンド

```bash
# 事前に pre-commit をインストール
pre-commit install

# Lint & Format & Type Check
pre-commit run --all-files

# テスト
pytest -q
```

## GitHub Actions CI

`windows-latest` と `ubuntu-latest` 上で Python 3.10 / 3.11 / 3.12 を用いた lint・型チェック・テストを実行します。

## トラブルシュート

- **ログイン失敗**: `Invalid DISCORD_TOKEN` が表示されたら `.env` を確認して再実行してください。
- **コマンドが表示されない**: `npm run deploy` を再実行し数分待ってから確認します。
- **API サーバー未起動**: 別ターミナルで `py -m uvicorn api_server:app --reload` を実行してください。

## セキュリティ

`.env` や `data/` などの機密情報はコミットされないよう `.gitignore` で保護されています。トークンや API キーは絶対に公開リポジトリにコミットしないでください。

## ライセンス

MIT License. 詳細は [LICENSE](LICENSE) を参照してください。

