#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ヘルパーユーティリティ

様々なヘルパー関数を提供する
"""

import re
import hashlib
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

def generate_article_id(article: Dict[str, Any]) -> str:
    """
    記事のユニークIDを生成する
    
    Args:
        article: 記事データ
        
    Returns:
        記事のユニークID
    """
    # リンクとタイトルからハッシュを生成
    link = article.get("link", "")
    title = article.get("title", "")
    content = f"{link}|{title}"
    
    # SHA-256ハッシュを生成
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def parse_datetime(date_str: str) -> Optional[datetime]:
    """
    日付文字列をdatetimeオブジェクトに変換する
    
    Args:
        date_str: 日付文字列
        
    Returns:
        datetimeオブジェクト、変換できない場合はNone
    """
    try:
        # feedparserが既に変換している場合
        if isinstance(date_str, datetime):
            return date_str.replace(tzinfo=timezone.utc)
        
        # 一般的な日付形式を試行
        formats = [
            "%a, %d %b %Y %H:%M:%S %z",  # RFC 822
            "%a, %d %b %Y %H:%M:%S %Z",  # RFC 822 with timezone name
            "%Y-%m-%dT%H:%M:%S%z",       # ISO 8601
            "%Y-%m-%dT%H:%M:%SZ",        # ISO 8601 UTC
            "%Y-%m-%d %H:%M:%S",         # Simple format
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                # タイムゾーン情報がない場合はUTCとして扱う
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                continue
        
        # どの形式にも一致しない場合
        logger.warning(f"日付形式を解析できませんでした: {date_str}")
        return None
        
    except Exception as e:
        logger.error(f"日付解析中にエラーが発生しました: {e}", exc_info=True)
        return None

def clean_html(html_content: str) -> str:
    """
    HTMLタグを除去してプレーンテキストを取得する
    
    Args:
        html_content: HTML形式のコンテンツ
        
    Returns:
        プレーンテキスト
    """
    if not html_content:
        return ""
    
    # HTMLタグを除去
    text = re.sub(r"<[^>]+>", "", html_content)
    
    # 連続する空白を1つに置換
    text = re.sub(r"\s+", " ", text)
    
    # 前後の空白を除去
    return text.strip()


def get_channel_name_for_feed(feed_url: str, feed_title: str = None) -> str:
    """
    フィードURLからチャンネル名を生成する
    
    Args:
        feed_url: フィードURL
        feed_title: フィードタイトル（オプション）
        
    Returns:
        チャンネル名
    """
    if feed_title:
        # タイトルからチャンネル名を生成
        name = re.sub(r"[^\w\s-]", "", feed_title.lower())
        name = re.sub(r"\s+", "-", name)
        name = re.sub(r"-+", "-", name)
        
        # 先頭と末尾のハイフンを除去
        name = name.strip("-")
        
        # Discordのチャンネル名制限（100文字以下）
        if len(name) > 90:
            name = name[:90]
            
        return f"rss-{name}"
    else:
        # URLからドメイン部分を抽出
        match = re.search(r"https?://(?:www\.)?([^/]+)", feed_url)
        if match:
            domain = match.group(1)
            # サブドメインとTLDを除去
            parts = domain.split(".")
            if len(parts) > 2:
                domain = parts[-2]
            else:
                domain = parts[0]
                
            return f"rss-{domain}"
        else:
            # URLからドメインを抽出できない場合はハッシュを使用
            hash_str = hashlib.md5(feed_url.encode("utf-8")).hexdigest()[:8]
            return f"rss-feed-{hash_str}"




# Gemini API key selection
from typing import List


def select_gemini_api_key(keys: List[str]) -> str:
    """奇数日と偶数日で使用するGemini APIキーを切り替える"""
    if not keys:
        return ""
    if len(keys) == 1:
        return keys[0]
    day = datetime.now().day
    return keys[0] if day % 2 == 1 else keys[1]
