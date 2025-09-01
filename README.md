# Discord RSS Bot

RSS/atomフィードを監視し、AIで処理してDiscordに投稿するボットシステム

![Discord RSS Bot](docs/images/discord_rss_bot_logo.png)

## 概要

Discord RSS Botは、RSS/atomフィードを定期的に監視し、取得した記事をAIで日本語に要約・分類してDiscordに投稿するボットです。ボットに返信する形で記事内容に関する質問を投げると、AIが回答を返すこともできます。主な機能は以下の通りです：

- **RSS/atom処理**
  - 複数フィードの登録・削除と自動確認
  - 設定間隔での新着取得と重複投稿防止
  - フィード追加時に専用チャンネルを自動作成
  - チャンネル削除時は対応するフィードも自動削除

- **AI処理**
  - Google Geminiによる要約・翻訳
  - 要約長(short/normal/long)に応じた最適なプロンプトで日本語要約
  - 要約は日本語のみで出力され、長文の場合は適度に改行されます
  - ジャンル分類（カテゴリはconfigでカスタマイズ可能）
  - 投稿済み記事への返信で質問に回答

- **Discord連携**
  - 処理記事をEmbed形式で自動投稿
  - ジャンルに応じたチャンネル振り分け
  - スラッシュコマンドによる管理
    - `/rss_config` 設定パネル
    - `/rss_check_now` 最新記事取得
    - `/rss_list_feeds` フィード一覧
    - `/addrss` フィード追加
    - `/rss_status` ステータス表示

## スクリーンショット

### 設定パネル
![設定パネル](docs/images/config_panel.png)

### 記事投稿
![記事投稿](docs/images/article_post.png)

### フィード一覧
![フィード一覧](docs/images/feed_list.png)

## 必要条件

- Docker と Docker Compose
- Discordアカウントとボットトークン
- （任意）Google Gemini APIキー

## クイックスタート

プロジェクトの実行はDocker Composeで行うのが最も簡単です。

```bash
# リポジトリのクローン
git clone https://github.com/yourusername/discord-rss-bot.git
cd discord-rss-bot

# 環境変数の設定
cp .env.example .env
# .envを編集してDiscordトークンなどを指定してください
# 必須項目: DISCORD_TOKEN, GUILD_ID, CLIENT_ID

# スラッシュコマンドの登録
# 初回起動時やコマンドを追加・変更した際に一度だけ実行します
npm install
npm run deploy

# ボットとAPIサーバーの起動
docker-compose up -d --build
```

コンテナを停止するには `docker-compose down` を実行します。

## ドキュメント

- [インストールガイド](docs/installation_guide.md)
- [ユーザーガイド](docs/user_guide.md)
- [APIリファレンス](docs/api_reference.md)
- [コントリビューションガイド](docs/contributing.md)
- [Docker環境での実行ガイド](docker_guide.md)

## 機能詳細

### RSS/atom処理機能

- 複数フィードの登録と管理
- 5分〜1時間の間隔で自動チェック
- 処理済み記事を記録して重複投稿を防止
- チャンネル削除に伴うフィードの自動削除

### AI処理機能

- Google Geminiで記事を要約・翻訳
- `short`/`normal`/`long` の要約長を指定可能
- ジャンル分類とカスタムカテゴリ設定
- 投稿された記事への質問応答

### Discord連携機能

- 処理記事をEmbedで自動投稿
- カテゴリ別チャンネル振り分け
- スラッシュコマンドとGUI設定パネル

## 設定

設定は`.env`または`data/config.json`を編集するか、`/rss_config`で変更します。主な項目は以下の通りです。

- Discordトークン、ギルドID、管理者ID
- フィードURL一覧と確認間隔
- 要約有無・文字数・分類有無
- カテゴリリスト、Embed色、サムネイル使用可否
- ログ出力レベルとファイル

## 貢献

貢献を歓迎します。詳細は[コントリビューションガイド](docs/contributing.md)を参照してください。

## ライセンス

このプロジェクトはMITライセンスで提供されています。詳細は[LICENSE](LICENSE)を参照してください。

## 謝辞

- [discord.js](https://discord.js.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [feedparser](https://github.com/kurtmckee/feedparser)
- [APScheduler](https://github.com/agronholm/apscheduler)
- [Google Generative AI](https://github.com/google/generative-ai-python)

## 作者

- Manus AI
