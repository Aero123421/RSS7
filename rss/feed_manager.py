#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
フィードマネージャー

RSSフィードの管理と監視を行う
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone, timedelta

from .feed_parser import FeedParser
from .article_store import ArticleStore
from utils.helpers import generate_article_id, parse_datetime

logger = logging.getLogger(__name__)

class FeedManager:
    """フィード管理クラス"""
    
    def __init__(self, config: Dict[str, Any], ai_processor: Any, discord_bot: Any):
        """
        初期化
        
        Args:
            config: 設定辞書
            ai_processor: AIプロセッサーインスタンス
            discord_bot: Discordボットインスタンス
        """
        self.config = config
        self.ai_processor = ai_processor
        self.discord_bot = discord_bot
        self.feed_parser = FeedParser()
        self.article_store = ArticleStore()
        self.checking = False  # フィード確認中フラグ
        self.article_queue: asyncio.Queue[Tuple[Dict[str, Any], Dict[str, Any]]] = asyncio.Queue()
        self.worker_task: Optional[asyncio.Task] = None

        logger.info("フィードマネージャーを初期化しました")

    def start_worker(self) -> None:
        """記事処理用ワーカーを開始する"""
        if not self.worker_task:
            self.worker_task = asyncio.create_task(self._queue_worker())
            logger.info("記事処理ワーカーを開始しました")

    async def _queue_worker(self) -> None:
        """キュー内の記事を順番に処理する"""
        while True:
            article, feed = await self.article_queue.get()
            try:
                channel_id = feed.get("channel_id")
                url = feed.get("url")
                processed = await self.ai_processor.process_article(article, feed)
                message_id = await self.discord_bot.post_article(processed, channel_id)
                if message_id:
                    await self.article_store.add_full_article(
                        str(message_id),
                        channel_id,
                        article,
                        processed.get("keywords_en", ""),
                    )
                article_id = generate_article_id(article)
                await self.article_store.add_processed_article(article_id, url, channel_id)
            except Exception as e:
                logger.error(f"キュー処理中にエラーが発生しました: {e}", exc_info=True)
            finally:
                await asyncio.sleep(10)
                self.article_queue.task_done()
    
    async def check_feeds(self) -> None:
        """すべてのフィードを確認する"""
        if self.checking:
            logger.info("前回のフィード確認がまだ実行中です。スキップします。")
            return
        
        try:
            self.checking = True
            logger.info("フィード確認を開始します")
            
            feeds = self.config.get("feeds", [])
            if not feeds:
                logger.info("登録されているフィードがありません")
                return
            
            for feed in feeds:
                try:
                    await self.check_feed(feed)
                    # フィード間の処理に少し間隔を空ける
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"フィード確認中にエラーが発生しました: {feed.get('url')}: {e}", exc_info=True)
            
            logger.info("すべてのフィード確認が完了しました")
            
        except Exception as e:
            logger.error(f"フィード確認中に予期しないエラーが発生しました: {e}", exc_info=True)
        
        finally:
            self.checking = False
    
    async def check_feed(self, feed: Dict[str, Any]) -> None:
        """
        単一のフィードを確認する
        
        Args:
            feed: フィード情報辞書
        """
        url = feed.get("url")
        channel_id = feed.get("channel_id")
        
        if not url or not channel_id:
            logger.warning(f"フィード情報が不完全です: {feed}")
            return
        
        logger.info(f"フィードを確認しています: {url}")
        
        # フィードを解析
        feed_data = await self.feed_parser.parse_feed(url)
        if not feed_data:
            logger.warning(f"フィードの解析に失敗しました: {url}")
            return
        
        # 新しい記事を取得
        new_articles = await self._get_new_articles(feed_data, feed)
        if not new_articles:
            logger.info(f"新しい記事はありません: {url}")
            return
        
        logger.info(f"{len(new_articles)}件の新しい記事を見つけました: {url}")
        
        # 最大処理数を制限
        max_articles = self.config.get("max_articles", 5)
        if len(new_articles) > max_articles:
            logger.info(f"処理数を{max_articles}件に制限します")
            new_articles = new_articles[:max_articles]
        
        # 記事をキューに追加
        for article in new_articles:
            await self.article_queue.put((article, feed))
    
    async def _get_new_articles(self, feed_data: Dict[str, Any], feed_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        新しい記事を取得する
        
        Args:
            feed_data: 解析済みフィードデータ
            feed_info: フィード情報辞書
            
        Returns:
            新しい記事のリスト
        """
        new_articles = []
        entries = feed_data.get("entries", [])
        
        # 記事を日付の新しい順にソート
        sorted_entries = self._sort_entries_by_date(entries)
        
        for entry in sorted_entries:
            # 記事IDを生成
            article_id = generate_article_id(entry)
            
            # 既に処理済みかチェック
            if await self.article_store.is_article_processed(article_id):
                continue
            
            # フィード情報を記事に追加
            entry["feed_title"] = feed_data.get("feed", {}).get("title", "Unknown Feed")
            entry["feed_url"] = feed_info.get("url")
            
            new_articles.append(entry)
        
        return new_articles
    
    def _sort_entries_by_date(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        記事を日付の新しい順にソートする
        
        Args:
            entries: 記事リスト
            
        Returns:
            ソート済み記事リスト
        """
        def get_entry_date(entry):
            # 日付フィールドを探す
            for date_field in ["published", "updated", "created"]:
                if date_field in entry:
                    dt = parse_datetime(entry[date_field])
                    if dt:
                        return dt
            
            # 日付が見つからない場合は現在時刻を返す
            return datetime.now(timezone.utc)
        
        # 日付でソート（新しい順）
        return sorted(entries, key=get_entry_date, reverse=True)
    
    async def add_feed(
        self,
        url: str,
        title: str = None,
        channel_id: str = None,
        summary_type: str = "normal",
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        フィードを追加する
        
        Args:
            url: フィードURL
            title: フィードタイトル（オプション）
            channel_id: チャンネルID（オプション）
            summary_type: 要約タイプ（short/normal/long）
            
        Returns:
            (成功フラグ, メッセージ, フィード情報)のタプル
        """
        try:
            # URLが既に登録されているか確認
            feeds = self.config.get("feeds", [])
            for feed in feeds:
                if feed.get("url") == url:
                    return False, "このフィードは既に登録されています", None
            
            # フィードを解析して有効性を確認
            feed_data = await self.feed_parser.parse_feed(url)
            if not feed_data:
                return False, "フィードの解析に失敗しました。有効なRSS/atomフィードであることを確認してください。", None
            
            # フィード情報を取得
            feed_title = title or feed_data.get("feed", {}).get("title", "Unknown Feed")
            
            # 新しいフィード情報を作成
            new_feed = {
                "url": url,
                "title": feed_title,
                "channel_id": channel_id,  # Noneの場合は後でチャンネル作成時に設定
                "added_at": datetime.now(timezone.utc).isoformat(),
                "summary_type": summary_type,
            }
            
            # 設定に追加
            feeds.append(new_feed)
            self.config["feeds"] = feeds
            
            return True, f"フィード「{feed_title}」を追加しました", new_feed
            
        except Exception as e:
            logger.error(f"フィード追加中にエラーが発生しました: {url}: {e}", exc_info=True)
            return False, f"エラーが発生しました: {str(e)}", None
    
    async def remove_feed(self, url: str, notify_channel: bool = True) -> Tuple[bool, str]:
        """
        フィードを削除する
        
        Args:
            url: フィードURL
            
        Returns:
            (成功フラグ, メッセージ)のタプル
        """
        try:
            feeds = self.config.get("feeds", [])
            
            # フィードを検索
            for i, feed in enumerate(feeds):
                if feed.get("url") == url:
                    # フィードを削除
                    removed_feed = feeds.pop(i)
                    self.config["feeds"] = feeds

                    channel_id = removed_feed.get("channel_id")
                    if notify_channel and channel_id:
                        await self.discord_bot.send_message(
                            channel_id,
                            "このRSSフィードは削除されました。不要であればチャンネルを削除してください。",
                        )

                    return True, f"フィード「{removed_feed.get('title', url)}」を削除しました"
            
            return False, "指定されたフィードが見つかりません"
            
        except Exception as e:
            logger.error(f"フィード削除中にエラーが発生しました: {url}: {e}", exc_info=True)
            return False, f"エラーが発生しました: {str(e)}"
    
    def get_feeds(self) -> List[Dict[str, Any]]:
        """
        登録されているフィードのリストを取得する
        
        Returns:
            フィードリスト
        """
        return self.config.get("feeds", [])

