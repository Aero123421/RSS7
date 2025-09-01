#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""記事ストアのテスト"""

import os
import sys
import unittest
import tempfile
import sqlite3
import asyncio
from datetime import datetime, timezone, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rss.article_store import ArticleStore


class TestArticleStore(unittest.TestCase):
    """記事ストアのテストケース"""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_articles.db")
        self.article_store = ArticleStore(self.db_path)
        self.test_articles = [
            {
                "article_id": "article1",
                "feed_url": "https://example.com/feed1",
                "channel_id": "channel1",
            },
            {
                "article_id": "article2",
                "feed_url": "https://example.com/feed1",
                "channel_id": "channel1",
            },
            {
                "article_id": "article3",
                "feed_url": "https://example.com/feed2",
                "channel_id": "channel2",
            },
        ]

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_add_processed_article(self) -> None:
        async def run() -> None:
            for article in self.test_articles:
                result = await self.article_store.add_processed_article(
                    article["article_id"], article["feed_url"], article["channel_id"]
                )
                self.assertTrue(result)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM processed_articles")
            count = cursor.fetchone()[0]
            conn.close()
            self.assertEqual(count, 3)

        asyncio.run(run())

    def test_is_article_processed(self) -> None:
        async def run() -> None:
            for article in self.test_articles:
                await self.article_store.add_processed_article(
                    article["article_id"], article["feed_url"], article["channel_id"]
                )
            for article in self.test_articles:
                result = await self.article_store.is_article_processed(article["article_id"])
                self.assertTrue(result)
            result = await self.article_store.is_article_processed("unknown_article")
            self.assertFalse(result)

        asyncio.run(run())

    def test_get_processed_articles(self) -> None:
        async def run() -> None:
            for article in self.test_articles:
                await self.article_store.add_processed_article(
                    article["article_id"], article["feed_url"], article["channel_id"]
                )
            all_articles = await self.article_store.get_processed_articles()
            self.assertEqual(len(all_articles), 3)
            feed1_articles = await self.article_store.get_processed_articles(
                "https://example.com/feed1"
            )
            self.assertEqual(len(feed1_articles), 2)
            feed2_articles = await self.article_store.get_processed_articles(
                "https://example.com/feed2"
            )
            self.assertEqual(len(feed2_articles), 1)
            unknown_articles = await self.article_store.get_processed_articles(
                "https://example.com/unknown"
            )
            self.assertEqual(len(unknown_articles), 0)

        asyncio.run(run())

    def test_cleanup_old_articles(self) -> None:
        async def run() -> None:
            for article in self.test_articles:
                await self.article_store.add_processed_article(
                    article["article_id"], article["feed_url"], article["channel_id"]
                )

            old_date = (datetime.now(timezone.utc) - timedelta(days=31)).isoformat()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            old_articles = [
                ("old_article1", "https://example.com/feed1", "channel1", old_date),
                ("old_article2", "https://example.com/feed2", "channel2", old_date),
            ]
            for old_article in old_articles:
                cursor.execute(
                    "INSERT INTO processed_articles (article_id, feed_url, channel_id, processed_at) VALUES (?, ?, ?, ?)",
                    old_article,
                )
            conn.commit()
            conn.close()
            all_articles = await self.article_store.get_processed_articles(limit=10)
            self.assertEqual(len(all_articles), 5)
            deleted_count = await self.article_store.cleanup_old_articles(30)
            self.assertEqual(deleted_count, 2)
            all_articles = await self.article_store.get_processed_articles(limit=10)
            self.assertEqual(len(all_articles), 3)

        asyncio.run(run())
