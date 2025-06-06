#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
フィードパーサー

RSS/atomフィードの解析を行う
"""

import logging
import asyncio
import feedparser
import aiohttp
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from utils.helpers import clean_html

logger = logging.getLogger(__name__)

class FeedParser:
    """フィード解析クラス"""
    
    def __init__(self, timeout: int = 30):
        """
        初期化
        
        Args:
            timeout: リクエストタイムアウト（秒）
        """
        self.timeout = timeout
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """
        HTTPセッションを取得する
        
        Returns:
            aiohttp.ClientSession
        """
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers={"User-Agent": "Discord RSS Bot/1.0"}
            )
        return self.session
    
    async def parse_feed(self, url: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        フィードを解析する
        
        Args:
            url: フィードURL
            max_retries: 最大リトライ回数
            
        Returns:
            解析済みフィードデータ、失敗した場合はNone
        """
        retries = 0
        
        while retries < max_retries:
            try:
                # URLの検証
                parsed_url = urlparse(url)
                if not parsed_url.scheme or not parsed_url.netloc:
                    logger.error(f"無効なURL形式です: {url}")
                    return None
                
                # フィードの取得
                session = await self._get_session()
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.warning(f"フィード取得エラー: {url}, ステータス: {response.status}")
                        retries += 1
                        await asyncio.sleep(1)
                        continue
                    
                    content = await response.text()
                
                # フィードの解析（feedparserはブロッキング関数なのでrun_in_executorで実行）
                loop = asyncio.get_event_loop()
                feed_data = await loop.run_in_executor(None, lambda: feedparser.parse(content))
                
                # エラーチェック
                if hasattr(feed_data, "bozo") and feed_data.bozo and hasattr(feed_data, "bozo_exception"):
                    logger.warning(f"フィード解析警告: {url}, エラー: {feed_data.bozo_exception}")
                
                # エントリーがあるか確認
                if not hasattr(feed_data, "entries") or len(feed_data.entries) == 0:
                    logger.warning(f"フィードにエントリーがありません: {url}")
                    return None
                
                # フィードデータを辞書に変換
                feed_dict = self._convert_feed_to_dict(feed_data)
                
                return feed_dict
                
            except Exception as e:
                logger.error(f"フィード解析中にエラーが発生しました: {url}: {e}", exc_info=True)
                retries += 1
                await asyncio.sleep(1)
        
        logger.error(f"フィード解析に失敗しました（最大リトライ回数に達しました）: {url}")
        return None
    
    def _convert_feed_to_dict(self, feed_data: Any) -> Dict[str, Any]:
        """
        feedparserオブジェクトを辞書に変換する
        
        Args:
            feed_data: feedparserオブジェクト
            
        Returns:
            変換された辞書
        """
        # フィード情報
        feed_dict = {
            "feed": {
                "title": getattr(feed_data.feed, "title", "Unknown Feed"),
                "link": getattr(feed_data.feed, "link", ""),
                "description": getattr(feed_data.feed, "description", ""),
                "language": getattr(feed_data.feed, "language", "en"),
                "updated": getattr(feed_data.feed, "updated", ""),
            },
            "entries": []
        }
        
        # エントリー情報
        for entry in feed_data.entries:
            entry_dict = {
                "title": getattr(entry, "title", "No Title"),
                "link": getattr(entry, "link", ""),
                "published": getattr(entry, "published", getattr(entry, "updated", "")),
                "author": getattr(entry, "author", "Unknown Author"),
                "summary": clean_html(getattr(entry, "summary", "")),
            }
            
            # コンテンツがある場合は追加
            if hasattr(entry, "content"):
                content_value = entry.content[0].value if entry.content else ""
                entry_dict["content"] = clean_html(content_value)
            else:
                # contentがない場合はsummaryをcontentとして使用
                entry_dict["content"] = entry_dict["summary"]
            
            # メディア情報の抽出
            media_content = []
            
            # enclosuresがある場合（画像、音声、動画など）
            if hasattr(entry, "enclosures") and entry.enclosures:
                for enclosure in entry.enclosures:
                    if hasattr(enclosure, "type") and hasattr(enclosure, "href"):
                        media_content.append({
                            "url": enclosure.href,
                            "type": enclosure.type
                        })
            
            # media_contentがある場合（YouTubeなど）
            if hasattr(entry, "media_content") and entry.media_content:
                for media in entry.media_content:
                    if hasattr(media, "type") and hasattr(media, "url"):
                        media_content.append({
                            "url": media.url,
                            "type": media.type
                        })
            
            # media_thumbnailがある場合
            if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
                for thumbnail in entry.media_thumbnail:
                    if hasattr(thumbnail, "url"):
                        media_content.append({
                            "url": thumbnail.url,
                            "type": "image/thumbnail"
                        })
            
            # メディア情報を追加
            entry_dict["media"] = media_content
            
            # エントリーを追加
            feed_dict["entries"].append(entry_dict)
        
        return feed_dict
    
    async def close(self):
        """セッションを閉じる"""
        if self.session and not self.session.closed:
            await self.session.close()

