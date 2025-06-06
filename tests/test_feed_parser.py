#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
フィードパーサーのテスト
"""

import os
import sys
import unittest
import asyncio
from unittest.mock import patch, MagicMock

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# テスト対象のモジュールをインポート
from rss.feed_parser import FeedParser

class TestFeedParser(unittest.TestCase):
    """フィードパーサーのテストケース"""
    
    def setUp(self):
        """テスト前の準備"""
        # テスト用のフィードデータ
        self.feed_data = {
            "feed": {
                "title": "Test Feed",
                "link": "https://example.com",
                "description": "Test feed description",
                "language": "en",
                "updated": "2025-01-01T12:00:00Z"
            },
            "entries": [
                {
                    "title": "Article 1",
                    "link": "https://example.com/article1",
                    "summary": "Summary 1",
                    "content": [{"value": "Content 1"}],
                    "published": "2025-01-01T12:00:00Z",
                    "author": "Author 1"
                },
                {
                    "title": "Article 2",
                    "link": "https://example.com/article2",
                    "summary": "Summary 2",
                    "content": [{"value": "Content 2"}],
                    "published": "2025-01-02T12:00:00Z",
                    "author": "Author 2"
                }
            ]
        }
    
    def test_convert_feed_to_dict(self):
        """フィードデータの変換テスト"""
        # モックのfeedparserオブジェクトを作成
        mock_feed = MagicMock()
        mock_feed.feed.title = "Test Feed"
        mock_feed.feed.link = "https://example.com"
        mock_feed.feed.description = "Test feed description"
        mock_feed.feed.language = "en"
        mock_feed.feed.updated = "2025-01-01T12:00:00Z"
        
        # モックのエントリーを作成
        entry1 = MagicMock()
        entry1.title = "Article 1"
        entry1.link = "https://example.com/article1"
        entry1.summary = "Summary 1"
        entry1.content = [MagicMock(value="Content 1")]
        entry1.published = "2025-01-01T12:00:00Z"
        entry1.author = "Author 1"
        
        entry2 = MagicMock()
        entry2.title = "Article 2"
        entry2.link = "https://example.com/article2"
        entry2.summary = "Summary 2"
        entry2.content = [MagicMock(value="Content 2")]
        entry2.published = "2025-01-02T12:00:00Z"
        entry2.author = "Author 2"
        
        mock_feed.entries = [entry1, entry2]
        
        # フィードパーサーの初期化
        parser = FeedParser()
        
        # フィードデータの変換
        result = parser._convert_feed_to_dict(mock_feed)
        
        # 結果の確認
        self.assertEqual(result["feed"]["title"], "Test Feed")
        self.assertEqual(result["feed"]["link"], "https://example.com")
        self.assertEqual(result["feed"]["description"], "Test feed description")
        self.assertEqual(len(result["entries"]), 2)
        self.assertEqual(result["entries"][0]["title"], "Article 1")
        self.assertEqual(result["entries"][0]["link"], "https://example.com/article1")
        self.assertEqual(result["entries"][0]["content"], "Content 1")
        self.assertEqual(result["entries"][0]["published"], "2025-01-01T12:00:00Z")
        self.assertEqual(result["entries"][0]["author"], "Author 1")
    
    @patch("aiohttp.ClientSession.get")
    @patch("feedparser.parse")
    async def test_parse_feed(self, mock_parse, mock_get):
        """フィード解析テスト"""
        # モックの設定
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = asyncio.coroutine(lambda: "<rss>...</rss>")
        mock_get.return_value.__aenter__.return_value = mock_response
        mock_parse.return_value = MagicMock()
        mock_parse.return_value.entries = [MagicMock(), MagicMock()]
        mock_parse.return_value.feed.title = "Test Feed"
        
        # フィードパーサーの初期化
        parser = FeedParser()
        
        # フィードの解析
        result = await parser.parse_feed("https://example.com/rss")
        
        # 結果の確認
        self.assertIsNotNone(result)
        mock_get.assert_called_once_with("https://example.com/rss")
        mock_parse.assert_called_once()

# 非同期テストのためのヘルパー関数
def run_async_test(coro):
    return asyncio.get_event_loop().run_until_complete(coro)

if __name__ == "__main__":
    # 非同期テストの実行
    test_parse_feed = TestFeedParser().test_parse_feed
    run_async_test(test_parse_feed)
    
    # その他のテストの実行
    unittest.main()

