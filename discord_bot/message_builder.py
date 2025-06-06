#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
メッセージビルダー

Discordメッセージの構築を行う
"""

import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

import discord

logger = logging.getLogger(__name__)

class MessageBuilder:
    """メッセージビルダークラス"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初期化
        
        Args:
            config: 設定辞書
        """
        self.config = config
        logger.info("メッセージビルダーを初期化しました")
    
    async def build_article_embed(self, article: Dict[str, Any]) -> discord.Embed:
        """
        記事のEmbedを構築する
        
        Args:
            article: 記事データ
            
        Returns:
            discord.Embed
        """
        try:
            # 基本情報の取得
            title = article.get("title", "無題")
            url = article.get("link", "")
            content = article.get("content", "")
            summary = article.get("summary", content[:200] + "..." if len(content) > 200 else content)
            published = article.get("published", "")
            author = article.get("author", "")
            feed_title = article.get("feed_title", "")
            
            # AI処理結果の取得
            summarized = article.get("summarized", False)
            classified = article.get("classified", False)
            category = article.get("category", "other")
            
            # カテゴリ情報の取得
            category_info = self._get_category_info(category)
            category_emoji = category_info.get("emoji", "📌")
            category_name = category_info.get("jp_name", category)
            
            # Embedカラーの設定
            color = self._get_category_color(category)
            
            # Embedの作成
            embed = discord.Embed(
                title=f"{category_emoji} {title}",
                url=url,
                color=color
            )
            
            # 要約があれば追加
            if summarized and article.get("summary"):
                embed.description = article.get("summary")
            else:
                # 要約がない場合は内容の先頭部分を表示
                embed.description = self._truncate_content(content)
            
            # フィード情報
            if feed_title:
                embed.add_field(name="フィード", value=feed_title, inline=True)
            
            # 著者情報
            if author:
                embed.add_field(name="著者", value=author, inline=True)
            
            # カテゴリ情報（分類されている場合）
            if classified:
                embed.add_field(name="カテゴリ", value=f"{category_emoji} {category_name}", inline=True)
            
            # 公開日時
            if published:
                try:
                    # 日時フォーマットの変換
                    dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
                    formatted_date = dt.strftime("%Y-%m-%d %H:%M")
                    embed.add_field(name="公開日時", value=formatted_date, inline=True)
                except:
                    embed.add_field(name="公開日時", value=published, inline=True)
            
            # サムネイル画像の設定
            if self.config.get("use_thumbnails", True) and article.get("image"):
                embed.set_thumbnail(url=article.get("image"))
            
            # フッター
            ai_info = []
            if summarized:
                ai_info.append("要約済み")
            if classified:
                ai_info.append("分類済み")
            
            if ai_info:
                embed.set_footer(text=f"AI処理: {', '.join(ai_info)}")
            
            return embed
            
        except Exception as e:
            logger.error(f"Embed構築中にエラーが発生しました: {e}", exc_info=True)
            
            # エラー時は簡易Embedを返す
            embed = discord.Embed(
                title=article.get("title", "無題"),
                url=article.get("link", ""),
                description="記事の表示中にエラーが発生しました。",
                color=discord.Color.red()
            )
            return embed
    
    def _truncate_content(self, content: str, max_length: int = 300) -> str:
        """
        コンテンツを適切な長さに切り詰める
        
        Args:
            content: 元のコンテンツ
            max_length: 最大文字数
            
        Returns:
            切り詰められたコンテンツ
        """
        # HTMLタグの除去
        content = re.sub(r'<[^>]+>', '', content)
        
        # 空白の正規化
        content = re.sub(r'\s+', ' ', content).strip()
        
        # 長さの制限
        if len(content) > max_length:
            return content[:max_length - 3] + "..."
        
        return content
    
    def _get_category_info(self, category: str) -> Dict[str, str]:
        """
        カテゴリ情報を取得する
        
        Args:
            category: カテゴリ名
            
        Returns:
            カテゴリ情報辞書
        """
        categories = self.config.get("categories", [])
        
        for cat in categories:
            if cat.get("name") == category:
                return cat
        
        # デフォルトカテゴリ
        return {"name": "other", "jp_name": "その他", "emoji": "📌"}
    
    def _get_category_color(self, category: str) -> discord.Color:
        """
        カテゴリに応じた色を取得する
        
        Args:
            category: カテゴリ名
            
        Returns:
            discord.Color
        """
        # カテゴリごとの色
        category_colors = {
            "technology": 0x3498db,  # 青
            "business": 0xf1c40f,    # 黄
            "politics": 0xe74c3c,    # 赤
            "entertainment": 0x9b59b6,  # 紫
            "sports": 0x2ecc71,      # 緑
            "science": 0x1abc9c,     # ターコイズ
            "health": 0xe67e22,      # オレンジ
            "other": 0x95a5a6        # グレー
        }
        
        return discord.Color(category_colors.get(category, self.config.get("embed_color", 0x3498db)))

