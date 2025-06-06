#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
記事ストアのテスト
"""

import os
import sys
import unittest
import tempfile
import sqlite3
import asyncio
from datetime import datetime, timezone, timedelta

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# テスト対象のモジュールをインポート
from rss.article_store import ArticleStore

class TestArticleStore(unittest.TestCase):
    """記事ストアのテストケース"""
    
    def setUp(self):
        """テスト前の準備"""
        # 一時ファイルを作成
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_articles.db")
        
        # 記事ストアの初期化
        self.article_store = ArticleStore(self.db_path)
        
        # テスト用の記事データ
        self.test_articles = [
            {
                "article_id": "article1",
                "feed_url": "https://example.com/feed1",
                "channel_id": "channel1"
            },
            {
                "article_id": "article2",
                "feed_url": "https://example.com/feed1",
                "channel_id": "channel1"
            },
            {
                "article_id": "article3",
                "feed_url": "https://example.com/feed2",
                "channel_id": "channel2"
            }
        ]
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        # 一時ディレクトリを削除
        self.temp_dir.cleanup()
    
    async def test_add_processed_article(self):
        """記事追加テスト"""
        # 記事の追加
        for article in self.test_articles:
            result = await self.article_store.add_processed_article(
                article["article_id"],
                article["feed_url"],
                article["channel_id"]
            )
            self.assertTrue(result)
        
        # データベースに記事が追加されたか確認
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM processed_articles")
        count = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(count, 3)
    
    async def test_is_article_processed(self):
        """記事処理済みチェックテスト"""
        # 記事の追加
        for article in self.test_articles:
            await self.article_store.add_processed_article(
                article["article_id"],
                article["feed_url"],
                article["channel_id"]
            )
        
        # 処理済み記事のチェック
        for article in self.test_articles:
            result = await self.article_store.is_article_processed(article["article_id"])
            self.assertTrue(result)
        
        # 未処理の記事のチェック
        result = await self.article_store.is_article_processed("unknown_article")
        self.assertFalse(result)
    
    async def test_get_processed_articles(self):
        """記事取得テスト"""
        # 記事の追加
        for article in self.test_articles:
            await self.article_store.add_processed_article(
                article["article_id"],
                article["feed_url"],
                article["channel_id"]
            )
        
        # すべての記事を取得
        all_articles = await self.article_store.get_processed_articles()
        self.assertEqual(len(all_articles), 3)
        
        # 特定のフィードの記事を取得
        feed1_articles = await self.article_store.get_processed_articles("https://example.com/feed1")
        self.assertEqual(len(feed1_articles), 2)
        
        feed2_articles = await self.article_store.get_processed_articles("https://example.com/feed2")
        self.assertEqual(len(feed2_articles), 1)
        
        # 存在しないフィードの記事を取得
        unknown_articles = await self.article_store.get_processed_articles("https://example.com/unknown")
        self.assertEqual(len(unknown_articles), 0)
    
    async def test_cleanup_old_articles(self):
        """古い記事のクリーンアップテスト"""
        # 現在の記事を追加
        for article in self.test_articles:
            await self.article_store.add_processed_article(
                article["article_id"],
                article["feed_url"],
                article["channel_id"]
            )
        
        # 古い記事を手動で追加（SQLiteを直接操作）
        old_date = (datetime.now(timezone.utc) - timedelta(days=31)).isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        old_articles = [
            ("old_article1", "https://example.com/feed1", "channel1", old_date),
            ("old_article2", "https://example.com/feed2", "channel2", old_date)
        ]
        
        for article in old_articles:
            cursor.execute(
                'INSERT INTO processed_articles (article_id, feed_url, channel_id, processed_at) VALUES (?, ?, ?, ?)',
                article
            )
        
        conn.commit()
        conn.close()
        
        # 追加後の記事数を確認
        all_articles = await self.article_store.get_processed_articles(limit=10)
        self.assertEqual(len(all_articles), 5)
        
        # 古い記事をクリーンアップ（30日以上前）
        deleted_count = await self.article_store.cleanup_old_articles(30)
        self.assertEqual(deleted_count, 2)
        
        # クリーンアップ後の記事数を確認
        all_articles = await self.article_store.get_processed_articles(limit=10)
        self.assertEqual(len(all_articles), 3)

# 非同期テストのためのヘルパー関数
def run_async_test(coro):
    return asyncio.get_event_loop().run_until_complete(coro)

if __name__ == "__main__":
    # 非同期テストの実行
    test_store = TestArticleStore()
    run_async_test(test_store.test_add_processed_article())
    run_async_test(test_store.test_is_article_processed())
    run_async_test(test_store.test_get_processed_articles())
    run_async_test(test_store.test_cleanup_old_articles())

