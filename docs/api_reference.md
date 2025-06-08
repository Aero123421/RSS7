# Discord RSS Bot API リファレンス

このドキュメントでは、Discord RSS Botの内部APIとモジュール構造について説明します。

## 目次

1. [モジュール構造](#モジュール構造)
2. [設定モジュール](#設定モジュール)
3. [RSSモジュール](#rssモジュール)
4. [AIモジュール](#aiモジュール)
5. [Discordモジュール](#discordモジュール)
6. [ユーティリティモジュール](#ユーティリティモジュール)

## モジュール構造

Discord RSS Botは以下のモジュールで構成されています：

```
discord_rss_bot/
├── bot.py                  # メインエントリーポイント
├── config/                 # 設定管理モジュール
│   ├── __init__.py
│   ├── config_manager.py   # 設定マネージャー
│   └── default_config.py   # デフォルト設定
├── rss/                    # RSSフィード処理モジュール
│   ├── __init__.py
│   ├── feed_manager.py     # フィード管理
│   ├── feed_parser.py      # フィード解析
│   └── article_store.py    # 記事ストア
├── ai/                     # AI処理モジュール
│   ├── __init__.py
│   ├── ai_processor.py     # AIプロセッサー基底クラス
│   ├── gemini_api.py       # Google Gemini API連携
│   ├── summarizer.py       # 要約機能（翻訳を兼ねる）
│   └── classifier.py       # ジャンル分類機能
├── discord_bot/            # Discord連携モジュール
│   ├── __init__.py
│   ├── bot_client.py       # Discordボットクライアント
│   ├── commands.py         # スラッシュコマンド
│   ├── ui_components.py    # UIコンポーネント
│   └── message_builder.py  # メッセージビルダー
└── utils/                  # ユーティリティモジュール
    ├── __init__.py
    ├── logger.py           # ロガー
    ├── scheduler.py        # スケジューラー
    └── helpers.py          # ヘルパー関数
```

## 設定モジュール

### ConfigManager

設定の読み込み、保存、更新を行うクラスです。

```python
from config.config_manager import ConfigManager

# 初期化
config_manager = ConfigManager("path/to/config.json")

# 設定の読み込み
config = config_manager.load_config()

# 設定の更新
config_manager.update_config({
    "check_interval": 30,
    "ai_provider": "gemini"
})

# 設定の保存
config_manager.save_config()
```

### DEFAULT_CONFIG

デフォルト設定を定義する定数です。

```python
from config.default_config import DEFAULT_CONFIG

# デフォルト設定の取得
default_check_interval = DEFAULT_CONFIG["check_interval"]
```

## RSSモジュール

### FeedManager

RSSフィードの管理を行うクラスです。

```python
from rss.feed_manager import FeedManager

# 初期化
feed_manager = FeedManager(config)

# フィードの追加
await feed_manager.add_feed({
    "url": "https://example.com/feed.xml",
    "channel_id": "123456789012345678"
})

# フィードの削除
await feed_manager.remove_feed("https://example.com/feed.xml")

# フィードの取得
feeds = await feed_manager.get_feeds()

# フィードの確認
await feed_manager.check_feeds()
```

### FeedParser

RSSフィードの解析を行うクラスです。

```python
from rss.feed_parser import FeedParser

# 初期化
parser = FeedParser(timeout=30)

# フィードの解析
feed_data = await parser.parse_feed("https://example.com/feed.xml")

# セッションのクローズ
await parser.close()
```

### ArticleStore

処理済み記事の管理を行うクラスです。

```python
from rss.article_store import ArticleStore

# 初期化
article_store = ArticleStore("path/to/articles.db")

# 記事の追加
await article_store.add_processed_article(
    article_id="unique_article_id",
    feed_url="https://example.com/feed.xml",
    channel_id="123456789012345678"
)

# 記事の確認
is_processed = await article_store.is_article_processed("unique_article_id")

# 記事の取得
articles = await article_store.get_processed_articles(
    feed_url="https://example.com/feed.xml",
    limit=10
)

# 古い記事のクリーンアップ
deleted_count = await article_store.cleanup_old_articles(days=30)
```

## AIモジュール

### AIProcessor

AIプロセッサーの基底クラスです。

```python
from ai.ai_processor import AIProcessor

# 初期化（抽象クラスなので直接インスタンス化はしない）
# processor = AIProcessor(config)

# 要約（自動翻訳を含む）
# summary = await processor.summarize(text, max_length=200, summary_type="normal")

# ジャンル分類
# category = await processor.classify(text)
```


### GeminiAPI

Google Gemini APIを使用したAIプロセッサーです。内部では
`google-generativeai` ライブラリを利用します。

```python
from ai.gemini_api import GeminiAPI

# 初期化
processor = GeminiAPI(api_key="YOUR_API_KEY", model="gemini-1.5-pro")

# 要約（自動翻訳を含む）
summary = await processor.summarize(text, max_length=200, summary_type="normal")

# ジャンル分類
category = await processor.classify(text)
```

### Summarizer

要約機能を提供するクラスです。

```python
from ai.summarizer import Summarizer

# 初期化
summarizer = Summarizer(ai_processor)

# 要約
summary = await summarizer.summarize(text, max_length=200, summary_type="normal")
```

### Classifier

ジャンル分類機能を提供するクラスです。

```python
from ai.classifier import Classifier

# 初期化
classifier = Classifier(ai_processor, categories)

# ジャンル分類
category = await classifier.classify(text)
```

## Discordモジュール

### DiscordBot

Discordボットクライアントを提供するクラスです。

```python
from discord_bot.bot_client import DiscordBot

# 初期化
bot = DiscordBot(config, ai_processor)

# 起動
await bot.start()

# 停止
await bot.close()
```

### Commands

スラッシュコマンドを提供するモジュールです。

```python
from discord_bot.commands import register_commands, set_managers

# コマンドの登録
register_commands(bot)

# マネージャーの設定
set_managers(
    config_manager=config_manager,
    feed_manager=feed_manager,
    article_store=article_store,
    ai_processor=ai_processor
)
```

### UIComponents

UIコンポーネント（ボタン、セレクトメニューなど）を提供するモジュールです。

```python
from discord_bot.ui_components import ConfigView, FeedListView

# 設定ビューの作成
config_view = ConfigView(config, config_manager, feed_manager)

# フィードリストビューの作成
feed_list_view = FeedListView(feed_manager)

```

### MessageBuilder

メッセージビルダーを提供するクラスです。

```python
from discord_bot.message_builder import MessageBuilder

# 初期化
message_builder = MessageBuilder(config)

# 記事エンベッドの構築
embed = await message_builder.build_article_embed(article)
```

## ユーティリティモジュール

### Logger

ロギング機能を提供するモジュールです。

```python
from utils.logger import setup_logger

# ロガーのセットアップ
logger = setup_logger(
    name="discord_rss_bot",
    log_level="INFO",
    log_file="path/to/log.log"
)

# ログの出力
logger.info("情報メッセージ")
logger.warning("警告メッセージ")
logger.error("エラーメッセージ")
```

### Scheduler

スケジューリング機能を提供するクラスです。

```python
from utils.scheduler import Scheduler

# 初期化
scheduler = Scheduler()

# ジョブの追加
job_id = scheduler.add_job(
    func=my_function,
    trigger="interval",
    minutes=15,
    args=[arg1, arg2]
)

# ジョブの削除
scheduler.remove_job(job_id)

# スケジューラーの開始
scheduler.start()

# スケジューラーの停止
scheduler.shutdown()
```

### Helpers

ヘルパー関数を提供するモジュールです。

```python
from utils.helpers import clean_html, generate_id, format_datetime

# HTMLクリーニング
clean_text = clean_html("<p>テキスト</p>")

# ID生成
unique_id = generate_id()

# 日時フォーマット
formatted_date = format_datetime("2025-01-01T12:00:00Z")
```

