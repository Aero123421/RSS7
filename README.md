# Discord RSS Bot

RSS/atomフィードを監視し、AIで処理してDiscordに投稿するボットシステム

![Discord RSS Bot](docs/images/discord_rss_bot_logo.png)

## 概要

Discord RSS Botは、RSS/atomフィードを監視し、新規記事をAIで処理してDiscordに投稿するボットシステムです。主な機能は以下の通りです：

- **RSS/atom処理機能**
  - 複数のRSS、atomフィードの登録と管理
  - 設定可能な間隔での自動フィード確認
  - 重複投稿防止のための処理済み記事管理
  - フィード登録時の専用チャンネル自動作成

- **AI処理機能**
  - LM Studio APIまたはGoogle Gemini APIによる記事処理
  - 日本語への翻訳
  - 指定文字数での要約生成
  - ジャンル分類（オプション）

- **Discord連携機能**
  - 処理済み記事のチャンネルへの自動投稿
  - ジャンルベースのチャンネル振り分け
  - スラッシュコマンドによる操作
    - `/rss_config` - 設定パネル表示
    - `/rss_check_now` - 即時フィード確認
    - `/rss_list_feeds` - フィード一覧表示
    - `/addrss` - RSS,atomのURL新規追加
    - `/rss_list_channels` - チャンネル一覧表示
    - `/rss_status` - ステータス確認

## スクリーンショット

### 設定パネル
![設定パネル](docs/images/config_panel.png)

### 記事投稿
![記事投稿](docs/images/article_post.png)

### フィード一覧
![フィード一覧](docs/images/feed_list.png)

## 必要条件

- Python 3.8以上
- Discordアカウントとボットトークン
- （オプション）Google Gemini APIキー
- （オプション）LM Studio（ローカルLLM実行環境）

## クイックスタート

### 通常インストール

```bash
# リポジトリのクローン
git clone https://github.com/yourusername/discord-rss-bot.git
cd discord-rss-bot

# 仮想環境のセットアップ
python -m venv venv
source venv/bin/activate  # Linuxの場合
# または
venv\Scripts\activate  # Windowsの場合

# 依存パッケージのインストール
pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env
# .envファイルを編集してDiscordトークンなどを設定

# ボットの起動
python bot.py
```

### Docker環境でのインストール

```bash
# リポジトリのクローン
git clone https://github.com/yourusername/discord-rss-bot.git
cd discord-rss-bot

# 環境変数の設定
cp .env.example .env
# .envファイルを編集してDiscordトークンなどを設定

# Dockerコンテナの起動
docker-compose up -d
```

## ドキュメント

- [インストールガイド](docs/installation_guide.md)
- [ユーザーガイド](docs/user_guide.md)
- [APIリファレンス](docs/api_reference.md)
- [コントリビューションガイド](docs/contributing.md)
- [Docker環境での実行ガイド](docker_guide.md)

## 機能詳細

### RSS/atom処理機能

- 複数のRSS、atomフィードの登録と管理
- 設定可能な間隔（5分、15分、30分、1時間）での自動フィード確認
- 重複投稿防止のための処理済み記事管理
- フィード登録時の専用チャンネル自動作成

### AI処理機能

- LM Studio APIまたはGoogle Gemini APIによる記事処理
- 日本語への翻訳（英語記事の場合）
- 指定文字数での要約生成
- ジャンル分類（テクノロジー、ビジネス、政治、エンタメ、スポーツ、科学、健康、その他）

### Discord連携機能

- 処理済み記事のチャンネルへの自動投稿
- ジャンルベースのチャンネル振り分け
- スラッシュコマンドによる操作
- GUIベースの設定パネル
- エンベッドメッセージによる視覚的な記事表示

## 設定

設定は以下の方法で行えます：

1. `.env`ファイルでの環境変数設定
2. `data/config.json`ファイルでの詳細設定
3. Discordのスラッシュコマンド`/rss_config`での設定

主な設定項目：

- Discordトークン
- チャンネルID
- RSSフィードURL
- 確認間隔
- AIプロバイダ（LM Studio / Google Gemini）
- 翻訳・要約・分類の有効/無効
- 要約文字数
- カテゴリ設定

## 貢献

プロジェクトへの貢献を歓迎します！詳細は[コントリビューションガイド](docs/contributing.md)を参照してください。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 謝辞

- [discord.py](https://github.com/Rapptz/discord.py)
- [feedparser](https://github.com/kurtmckee/feedparser)
- [APScheduler](https://github.com/agronholm/apscheduler)
- [Google Generative AI](https://github.com/google/generative-ai-python)

## 作者

- Manus AI

