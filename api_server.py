#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
APIサーバー for Discord RSS Bot

PythonバックエンドロジックをFastAPIを介して提供する
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# 内部モジュールのインポート
from config.config_manager import ConfigManager
from rss.feed_manager import FeedManager
from ai.ai_processor import AIProcessor
from utils.logger import setup_logger

# 環境変数の読み込み
load_dotenv()

# ロガーのセットアップ
logger = setup_logger()

# --- FastAPIアプリケーションの初期化 ---
app = FastAPI(
    title="Discord RSS Bot API",
    description="Pythonバックエンドロジックを操作するためのAPI",
    version="1.0.0"
)

# --- グローバルオブジェクト ---
# アプリケーションの生存期間中に維持されるオブジェクト
app_state: Dict[str, Any] = {}

# --- イベントハンドラ ---
@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時に実行される"""
    logger.info("APIサーバーを起動しています...")
    try:
        # 設定の読み込み
        config_manager = ConfigManager()
        config = config_manager.load_config()
        app_state["config_manager"] = config_manager
        app_state["config"] = config

        # AIプロセッサーの初期化
        ai_processor = AIProcessor(config)
        app_state["ai_processor"] = ai_processor

        # フィードマネージャーの初期化
        feed_manager = FeedManager(config, ai_processor)
        app_state["feed_manager"] = feed_manager

        # スケジューラーのセットアップ
        scheduler = AsyncIOScheduler(timezone="UTC")
        check_interval = config.get("check_interval", 15)
        scheduler.add_job(feed_manager.check_feeds, "interval", minutes=check_interval)
        scheduler.start()
        app_state["scheduler"] = scheduler

        logger.info(f"APIサーバーの初期化が完了しました。フィードは{check_interval}分ごとに確認されます。")

    except Exception as e:
        logger.error(f"起動中にエラーが発生しました: {e}", exc_info=True)

@app.on_event("shutdown")
async def shutdown_event():
    """アプリケーション終了時に実行される"""
    logger.info("APIサーバーをシャットダウンしています...")
    scheduler = app_state.get("scheduler")
    if scheduler and scheduler.running:
        scheduler.shutdown()
    logger.info("スケジューラーを停止しました。")

# --- ルートエンドポイント ---
@app.get("/")
async def read_root():
    """ルートエンドポイント"""
    return {"message": "Discord RSS Bot APIへようこそ"}

# --- APIモデル定義 ---
class ConfigUpdate(BaseModel):
    key: str
    value: Any

class FeedAdd(BaseModel):
    url: str
    summary_type: str = "normal"

class FeedRemove(BaseModel):
    url: str

class FeedCheckNow(BaseModel):
    channel_id: str

class QARequest(BaseModel):
    original_message_id: str
    question: str

class ArticleAssociate(BaseModel):
    message_id: str
    channel_id: str
    original_article: Dict[str, Any]
    keywords_en: str

# --- APIエンドポイントの実装 ---

# Config Endpoints
@app.get("/api/config", summary="設定を取得")
async def get_config():
    """現在の設定全体を取得します"""
    return app_state["config"]

@app.post("/api/config", summary="設定を更新")
async def update_config(update_data: ConfigUpdate):
    """特定の設定キーの値を更新します"""
    config_manager = app_state["config_manager"]
    current_config = app_state["config"]

    # Pydanticモデルから辞書に変換
    update_dict = update_data.dict()
    key = update_dict['key']
    value = update_dict['value']

    # config辞書を更新
    current_config[key] = value

    # 保存
    config_manager.save_config()
    return {"message": f"設定 '{key}' を更新しました。", "new_value": value}

# Feed Endpoints
@app.get("/api/feeds", summary="全フィードを取得")
async def get_feeds():
    """登録されているすべてのフィードのリストを取得します"""
    feed_manager = app_state["feed_manager"]
    return feed_manager.get_feeds()

@app.post("/api/feeds", summary="フィードを追加")
async def add_feed(feed_data: FeedAdd):
    """新しいRSSフィードを追加します"""
    feed_manager = app_state["feed_manager"]
    success, message, feed_info = await feed_manager.add_feed(
        url=feed_data.url,
        summary_type=feed_data.summary_type
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)

    # feed_infoにchannel_idがまだないので、node側で作成してから再度更新する必要がある
    # ここではまずフィードの基本情報だけ追加する
    app_state["config_manager"].save_config()
    return {"message": message, "feed_info": feed_info}

@app.post("/api/feeds/assign-channel", summary="フィードにチャンネルを割り当て")
async def assign_channel_to_feed(url: str, channel_id: str, channel_name: str):
    """フィードにDiscordチャンネルIDを割り当てます"""
    feed_manager = app_state["feed_manager"]
    config_manager = app_state["config_manager"]
    feed = feed_manager.get_feed_by_url(url)
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")
    feed["channel_id"] = channel_id
    feed["channel_name"] = channel_name
    config_manager.save_config()
    return {"message": f"Feed {url} assigned to channel {channel_id}"}


@app.delete("/api/feeds", summary="フィードを削除")
async def remove_feed(feed_data: FeedRemove):
    """RSSフィードを削除します"""
    feed_manager = app_state["feed_manager"]
    success, message = await feed_manager.remove_feed(url=feed_data.url)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    app_state["config_manager"].save_config()
    return {"message": message}

@app.post("/api/feeds/check-now", summary="フィードを今すぐ確認")
async def check_feed_now(check_data: FeedCheckNow):
    """指定されたチャンネルのフィードをすぐに確認し、最新記事を投稿します"""
    feed_manager = app_state["feed_manager"]
    feed = next((f for f in feed_manager.get_feeds() if f.get("channel_id") == check_data.channel_id), None)
    if not feed:
        raise HTTPException(status_code=404, detail="このチャンネルにフィードが登録されていません。")

    try:
        # このコマンドは手動実行用なので、即時処理して結果を返す
        # 定期実行とは異なり、キューには入れない
        await feed_manager.check_feed(feed)

        # キューから最新のものを取得して返す（このチャンネル向けである保証はないが、高確率でそう）
        if feed_manager.articles_to_post:
            # Note: This is not guaranteed to be for the requested channel, but likely is.
            # A more robust solution might be needed if this is a problem.
            article_data = feed_manager.articles_to_post.popleft()
            return {"message": "記事を処理しました。", "article_data": article_data}
        else:
            return {"message": "新しい記事は見つかりませんでした。"}

    except Exception as e:
        logger.error(f"フィード確認中にAPIエラー: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Article Endpoints
@app.get("/api/articles-to-post", summary="投稿待ちの記事を取得")
async def get_article_to_post():
    """投稿を待っている記事のキューから記事を1つ取得します"""
    feed_manager = app_state["feed_manager"]
    if feed_manager.articles_to_post:
        article_data = feed_manager.articles_to_post.popleft()
        return article_data
    return None

@app.post("/api/articles/associate", summary="投稿済み記事を紐付け")
async def associate_article(association_data: ArticleAssociate):
    """Discordへの投稿後、メッセージIDと記事データを紐付けて保存します"""
    feed_manager = app_state["feed_manager"]
    try:
        await feed_manager.article_store.add_full_article(
            message_id=association_data.message_id,
            channel_id=association_data.channel_id,
            article=association_data.original_article,
            keywords_en=association_data.keywords_en,
        )
        return {"message": "Article associated successfully"}
    except Exception as e:
        logger.error(f"記事の紐付け中にエラー: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to associate article")

# Q&A Endpoint
@app.post("/api/qa", summary="質問応答")
async def answer_question(request: QARequest):
    """Botの投稿への返信に対して、AIを使用して回答を生成します"""
    feed_manager = app_state["feed_manager"]
    ai_processor = app_state["ai_processor"]

    original_article = await feed_manager.article_store.get_full_article(request.original_message_id)
    if not original_article:
        raise HTTPException(status_code=404, detail="元の記事が見つかりませんでした。")

    keywords = await ai_processor._generate_search_keywords(original_article, request.question)
    related_articles = await feed_manager.article_store.find_related_articles(keywords, request.original_message_id)
    answer = await ai_processor.answer_question(original_article, related_articles, request.question)

    return {"answer": answer}

# Channel Endpoint
@app.delete("/api/channels/{channel_id}", summary="チャンネル削除処理")
async def handle_channel_delete(channel_id: str):
    """チャンネルが削除された際のクリーンアップ処理"""
    feed_manager = app_state["feed_manager"]
    if not feed_manager:
        raise HTTPException(status_code=500, detail="FeedManagerが初期化されていません。")

    feeds = feed_manager.get_feeds()
    targets = [f.get("url") for f in feeds if f.get("channel_id") == channel_id]
    if not targets:
        return {"message": "関連するフィードはありません。"}

    for url in targets:
        await feed_manager.remove_feed(url, notify_channel=False)

    app_state["config_manager"].save_config()
    return {"message": f"チャンネル削除に伴い {len(targets)} 件のフィードを削除しました。"}


# --- サーバーの実行 ---
if __name__ == "__main__":
    port = int(os.environ.get("API_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
