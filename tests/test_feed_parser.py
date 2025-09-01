#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""フィードパーサーのテスト"""

import os
import sys
import unittest
from unittest.mock import MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rss.feed_parser import FeedParser


class TestFeedParser(unittest.TestCase):
    """フィードパーサーのテストケース"""

    def setUp(self) -> None:
        self.feed_data = {
            "feed": {
                "title": "Test Feed",
                "link": "https://example.com",
                "description": "Test feed description",
                "language": "en",
                "updated": "2025-01-01T12:00:00Z",
            },
            "entries": [
                {
                    "title": "Article 1",
                    "link": "https://example.com/article1",
                    "summary": "Summary 1",
                    "content": [{"value": "Content 1"}],
                    "published": "2025-01-01T12:00:00Z",
                    "author": "Author 1",
                },
                {
                    "title": "Article 2",
                    "link": "https://example.com/article2",
                    "summary": "Summary 2",
                    "content": [{"value": "Content 2"}],
                    "published": "2025-01-02T12:00:00Z",
                    "author": "Author 2",
                },
            ],
        }

    def test_convert_feed_to_dict(self) -> None:
        mock_feed = MagicMock()
        mock_feed.feed.title = "Test Feed"
        mock_feed.feed.link = "https://example.com"
        mock_feed.feed.description = "Test feed description"
        mock_feed.feed.language = "en"
        mock_feed.feed.updated = "2025-01-01T12:00:00Z"
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
        parser = FeedParser()
        result = parser._convert_feed_to_dict(mock_feed)
        self.assertEqual(result["feed"]["title"], "Test Feed")
        self.assertEqual(result["feed"]["link"], "https://example.com")
        self.assertEqual(result["feed"]["description"], "Test feed description")
        self.assertEqual(len(result["entries"]), 2)
        self.assertEqual(result["entries"][0]["title"], "Article 1")
        self.assertEqual(result["entries"][0]["link"], "https://example.com/article1")
        self.assertEqual(result["entries"][0]["content"], "Content 1")
        self.assertEqual(result["entries"][0]["published"], "2025-01-01T12:00:00Z")
        self.assertEqual(result["entries"][0]["author"], "Author 1")

    # ネットワーク越しの解析関数はモックが複雑になるため、
    # ここでは _convert_feed_to_dict のテストのみに留める。
