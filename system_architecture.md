# Discord RSS Bot システムアーキテクチャ

## 1. システム概要

このシステムは、RSS/atomフィードを定期的に監視し、新しい記事をAIで処理（要約・分類）した後、Discordの適切なチャンネルに投稿するボットです。要約は自動的に日本語に翻訳されます。

## 2. システムコンポーネント

### 2.1 コアコンポーネント

1. **RSSフィードマネージャー**
   - フィードの登録・管理
   - 定期的なフィード確認
   - 新規記事の検出
   - 処理済み記事の管理

2. **AIプロセッサー**
   - LM Studio API連携
   - Google Gemini API連携
   - 記事の要約生成
   - 記事の要約生成（自動翻訳）
   - 記事のジャンル分類

3. **Discordボット**
   - スラッシュコマンド処理
   - チャンネル管理
   - メッセージ投稿
   - インタラクティブUI

4. **設定マネージャー**
   - 設定の読み込み・保存
   - 設定パネルの提供
   - 環境変数の管理

### 2.2 データストア

1. **設定ファイル (config.json)**
   - Discordトークン
   - チャンネルID
   - RSSフィードURL
   - 確認間隔
   - AI API設定
   - 管理者ID
   - ニュースカテゴリ設定

2. **処理済み記事データベース**
   - 記事ID
   - 処理日時
   - 投稿チャンネル

## 3. データフロー

1. **フィード監視フロー**
   - スケジューラーが設定された間隔でフィード確認を実行
   - 新規記事を検出
   - 処理済み記事と照合して重複を排除
   - 新規記事をAIプロセッサーに送信

2. **AI処理フロー**
   - 記事を受け取り
   - 設定に基づいて要約を生成（自動翻訳）
   - 必要に応じてジャンル分類を実行
   - 処理結果をDiscordボットに送信

3. **Discord投稿フロー**
   - 処理済み記事を受け取り
   - 適切なチャンネルを決定
   - Embedメッセージを作成
   - チャンネルに投稿
   - 処理済み記事データベースを更新

4. **コマンド処理フロー**
   - ユーザーからのスラッシュコマンドを受け取り
   - コマンドに応じた処理を実行
   - 結果をユーザーに返信

## 4. モジュール構成

```
discord_rss_bot/
├── bot.py                 # メインエントリーポイント
├── config/
│   ├── config_manager.py  # 設定管理クラス
│   └── default_config.py  # デフォルト設定
├── rss/
│   ├── feed_manager.py    # フィード管理クラス
│   ├── feed_parser.py     # フィード解析クラス
│   └── article_store.py   # 記事保存クラス
├── ai/
│   ├── ai_processor.py    # AI処理基底クラス
│   ├── lmstudio_api.py    # LM Studio API連携
│   ├── gemini_api.py      # Google Gemini API連携
│   ├── summarizer.py      # 要約機能（自動翻訳）
│   └── classifier.py      # 分類機能
├── discord_bot/
│   ├── bot_client.py      # Discordクライアント
│   ├── commands.py        # スラッシュコマンド
│   ├── ui_components.py   # UI要素
│   └── message_builder.py # メッセージ構築
├── utils/
│   ├── logger.py          # ロギング
│   ├── scheduler.py       # スケジューラー
│   └── helpers.py         # ヘルパー関数
└── data/
    ├── config.json        # 設定ファイル
    └── processed_articles.db # 処理済み記事DB
```

## 5. 技術スタック

1. **言語とフレームワーク**
   - Python 3.8+
   - discord.py (最新版)
   - aiohttp (非同期HTTP)
   - APScheduler (スケジューリング)

2. **データ処理**
   - feedparser (RSSパース)
   - SQLite (処理済み記事管理)
   - json (設定管理)

3. **AI API**
   - LM Studio API
   - Google Gemini API

4. **デプロイ**
   - Docker
   - docker-compose

## 6. 非機能要件の実現方法

### 6.1 性能要件

- APSchedulerを使用した正確なスケジューリング
- 非同期処理によるパフォーマンス最適化
- リトライメカニズムの実装
- バッチ処理による効率化

### 6.2 セキュリティ要件

- 環境変数による機密情報の管理
- 管理者IDによる権限制御
- 入力検証によるインジェクション対策

### 6.3 運用要件

- 構造化ロギングの実装
- ステータス監視コマンドの提供
- エラーハンドリングとリカバリー機能

