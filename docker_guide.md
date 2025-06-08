# Docker環境での実行ガイド

このドキュメントでは、Discord RSS Botを Docker 環境で実行する方法について説明します。

## 前提条件

- Docker がインストールされていること
- Docker Compose がインストールされていること
- Discordボットトークンを取得済みであること

## セットアップ手順

### 1. 環境変数の設定

`.env.example` ファイルをコピーして `.env` ファイルを作成し、必要な環境変数を設定します。

```bash
cp .env.example .env
```

`.env` ファイルを編集して、以下の項目を設定します：

```
# Discord設定
DISCORD_TOKEN=your_discord_token_here

# Google Gemini API設定（Gemini APIを使用する場合）
# `GEMINI_API_1` と `GEMINI_API_2` にキーを設定すると、
# 奇数日と偶数日で自動的に切り替えます
GEMINI_API_1=
GEMINI_API_2=
# 単一キーのみ使用する場合は GEMINI_API_KEY を設定
# GEMINI_API_KEY=your_gemini_api_key_here

# LM Studio API設定（LM Studioを使用する場合）
# LM Studio APIコンテナを起動する場合は、以下のURLを指定してください
# LMSTUDIO_API_URL=http://lmstudio-api:1234/v1
```

### 2. データディレクトリの作成

設定ファイルやログを保存するためのデータディレクトリを作成します。

```bash
mkdir -p data
```

### 3. Docker Composeでの起動

#### 3.1 LM Studio APIを使用しない場合

LM Studio APIを使用せず、Google Gemini APIのみを使用する場合は、以下のコマンドでボットを起動します。

```bash
docker-compose up -d discord-rss-bot
```

#### 3.2 LM Studio APIを使用する場合

LM Studio APIを使用する場合は、`docker-compose.yml` ファイルの `lmstudio-api` サービスのコメントを解除し、モデルパスを設定します。

```yaml
lmstudio-api:
  image: lmstudio/api:latest
  container_name: lmstudio-api
  restart: unless-stopped
  ports:
    - "1234:1234"
  volumes:
    - ./models:/models
  environment:
    - MODEL_PATH=/models/your-model.gguf
  networks:
    - bot-network
```

モデルファイル（.gguf形式）を `models` ディレクトリに配置します。

```bash
mkdir -p models
# モデルファイルを models ディレクトリにコピー
```

その後、以下のコマンドで両方のサービスを起動します。

```bash
docker-compose up -d
```

### 4. ログの確認

ボットのログを確認するには、以下のコマンドを実行します。

```bash
docker-compose logs -f discord-rss-bot
```

## 設定ファイル

Docker環境では、設定ファイルは `data` ディレクトリにマウントされます。設定を変更する場合は、`data/config.json` ファイルを編集するか、Discordのスラッシュコマンドを使用して設定を変更してください。

## コンテナの停止

ボットを停止するには、以下のコマンドを実行します。

```bash
docker-compose down
```

## コンテナの再起動

設定を変更した後など、ボットを再起動するには、以下のコマンドを実行します。

```bash
docker-compose restart discord-rss-bot
```

## トラブルシューティング

### ボットが起動しない場合

1. `.env` ファイルが正しく設定されているか確認してください。
2. ログを確認して、エラーメッセージを確認してください。

```bash
docker-compose logs discord-rss-bot
```

### LM Studio APIに接続できない場合

1. LM Studio APIサービスが起動しているか確認してください。
2. モデルファイルが正しく配置されているか確認してください。
3. `.env` ファイルの `LMSTUDIO_API_URL` が正しく設定されているか確認してください。

### データが保存されない場合

1. `data` ディレクトリのパーミッションを確認してください。
2. コンテナ内のユーザーが `data` ディレクトリに書き込み権限を持っているか確認してください。

```bash
chmod -R 777 data
```

## 更新方法

新しいバージョンのボットをデプロイする場合は、以下の手順で更新します。

1. 最新のコードを取得します。
2. 以下のコマンドでイメージを再ビルドし、コンテナを再起動します。

```bash
docker-compose build discord-rss-bot
docker-compose up -d discord-rss-bot
```

