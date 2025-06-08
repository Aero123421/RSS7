# Discord RSS Bot インストールガイド

このガイドでは、Discord RSS Botのインストール方法と初期設定について説明します。

## 目次

1. [前提条件](#前提条件)
2. [インストール方法](#インストール方法)
   - [通常インストール](#通常インストール)
   - [Docker環境でのインストール](#docker環境でのインストール)
3. [初期設定](#初期設定)
   - [Discordボットの作成](#discordボットの作成)
   - [環境変数の設定](#環境変数の設定)
   - [設定ファイルの編集](#設定ファイルの編集)
4. [起動方法](#起動方法)
5. [トラブルシューティング](#トラブルシューティング)

## 前提条件

Discord RSS Botを使用するには、以下の前提条件が必要です：

- Python 3.8以上
- Discordアカウントとボットトークン
- （オプション）Google Gemini APIキー
- （オプション）LM Studio（ローカルLLM実行環境）

## インストール方法

### 通常インストール

1. リポジトリをクローンします：

```bash
git clone https://github.com/yourusername/discord-rss-bot.git
cd discord-rss-bot
```

2. 仮想環境を作成し、有効化します：

```bash
python -m venv venv
source venv/bin/activate  # Linuxの場合
# または
venv\Scripts\activate  # Windowsの場合
```

3. 依存パッケージをインストールします：

```bash
pip install -r requirements.txt
```

4. 環境変数ファイルを作成します：

```bash
cp .env.example .env
```

5. `.env`ファイルを編集して、必要な環境変数を設定します。

### Docker環境でのインストール

1. リポジトリをクローンします：

```bash
git clone https://github.com/yourusername/discord-rss-bot.git
cd discord-rss-bot
```

2. 環境変数ファイルを作成します：

```bash
cp .env.example .env
```

3. `.env`ファイルを編集して、必要な環境変数を設定します。

4. Dockerコンテナをビルドして起動します：

```bash
docker-compose up -d
```

## 初期設定

### Discordボットの作成

1. [Discord Developer Portal](https://discord.com/developers/applications)にアクセスします。

2. 「New Application」をクリックして、新しいアプリケーションを作成します。

3. 「Bot」タブをクリックし、「Add Bot」をクリックしてボットを作成します。

4. 「Reset Token」をクリックして、ボットトークンを取得します。このトークンは`.env`ファイルに設定します。

5. 「OAuth2」タブをクリックし、「URL Generator」を選択します。

6. 以下のスコープとボット権限を選択します：
   - スコープ：`bot`, `applications.commands`
   - ボット権限：`Send Messages`, `Embed Links`, `Attach Files`, `Read Message History`, `Add Reactions`, `Use Slash Commands`, `Manage Channels`

7. 生成されたURLをブラウザで開き、ボットをサーバーに招待します。

### 環境変数の設定

`.env`ファイルに以下の環境変数を設定します：

```
# Discord設定
DISCORD_TOKEN=your_discord_token_here

# Google Gemini API設定（Gemini APIを使用する場合）
# GEMINI_API_KEYS に gemini1 と gemini2 のキーをカンマ区切りで設定すると、
# ボットは奇数日と偶数日でキーを切り替えます
# 例: GEMINI_API_KEYS=gemini_key1,gemini_key2
GEMINI_API_KEYS=
# 1つだけ指定する場合は GEMINI_API_KEY を使用
# GEMINI_API_KEY=your_gemini_api_key_here

# YouTube Data API設定（YouTube再生リスト監視に使用）
# YOUTUBE_API_KEY=your_youtube_api_key_here

# LM Studio API設定（LM Studioを使用する場合）
# ローカル実行時は http://localhost:1234/v1
# Docker 環境でボットとAPIを同時に起動する場合は
#   http://lmstudio-api:1234/v1 を指定してください
# ボットのみをコンテナで動かし、APIを別ホストで実行する場合は
#   そのホストのURLを LMSTUDIO_API_URL に設定します。
#   パスには /chat/completions を付けず、/v1 までを指定してください。
#   例: Windows/Macでは http://host.docker.internal:1234/v1
#       Linuxでは http://172.17.0.1:1234/v1
# LMSTUDIO_API_URL=http://lmstudio-api:1234/v1
```

### 設定ファイルの編集

初回起動時に`data/config.json`が自動的に作成されます。必要に応じて、このファイルを編集して設定をカスタマイズできます。

または、Discordのスラッシュコマンド`/rss_config`を使用して、ボットの設定を行うこともできます。

## 起動方法

### 通常インストールの場合

```bash
python bot.py
```

### Docker環境の場合

```bash
docker-compose up -d
```

ボットが正常に起動すると、Discordサーバーでスラッシュコマンドが使用できるようになります。

## トラブルシューティング

### ボットが起動しない場合

1. `.env`ファイルが正しく設定されているか確認してください。
2. ログファイル（`data/bot.log`）を確認して、エラーメッセージを確認してください。
3. Discordボットトークンが有効であることを確認してください。

### スラッシュコマンドが表示されない場合

1. ボットが正常に起動しているか確認してください。
2. ボットをサーバーに再招待してみてください。
3. Discordのキャッシュをクリアしてみてください。

### RSSフィードが取得できない場合

1. フィードURLが有効であることを確認してください。
2. ネットワーク接続を確認してください。
3. フィードのフォーマットがRSSまたはAtomであることを確認してください。

### AI処理が機能しない場合

1. 選択したAIプロバイダ（LM StudioまたはGoogle Gemini）の設定が正しいことを確認してください。
2. APIキーが有効であることを確認してください。
3. LM Studioを使用している場合は、LM Studio APIサーバーが起動していることを確認してください。

