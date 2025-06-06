#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Discordボットクライアント

Discordとの連携を行う
"""

import os
import logging
import asyncio
from typing import Dict, Any, List, Optional

import discord
from discord import app_commands
from discord.ext import commands

from .message_builder import MessageBuilder
from .commands import register_commands
from utils.helpers import get_channel_name_for_feed

logger = logging.getLogger(__name__)

class DiscordBot:
    """Discordボットクラス"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初期化
        
        Args:
            config: 設定辞書
        """
        self.config = config
        
        # Discordトークンの取得
        self.token = config.get("discord_token") or os.environ.get("DISCORD_TOKEN")
        if not self.token:
            logger.error("Discordトークンが設定されていません")
            raise ValueError("Discordトークンが設定されていません")
        
        # インテントの設定
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        # ボットの初期化
        self.bot = commands.Bot(command_prefix="!", intents=intents)
        
        # メッセージビルダーの初期化
        self.message_builder = MessageBuilder(config)
        
        # イベントハンドラの設定
        self._setup_event_handlers()
        
        logger.info("Discordボットを初期化しました")
    
    def _setup_event_handlers(self):
        """イベントハンドラを設定する"""
        
        @self.bot.event
        async def on_ready():
            """ボット起動時のイベントハンドラ"""
            logger.info(f"Discordボットとしてログインしました: {self.bot.user.name} ({self.bot.user.id})")
            
            # スラッシュコマンドの登録
            await register_commands(self.bot, self.config)
            
            # ステータスの設定
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name="RSS Feeds"
                )
            )
        
        @self.bot.event
        async def on_guild_join(guild):
            """サーバー参加時のイベントハンドラ"""
            logger.info(f"新しいサーバーに参加しました: {guild.name} ({guild.id})")
            
            # 管理者にDMで通知
            admin_ids = self.config.get("admin_ids", [])
            for admin_id in admin_ids:
                try:
                    admin = await self.bot.fetch_user(int(admin_id))
                    await admin.send(f"新しいサーバー「{guild.name}」に参加しました。")
                except Exception as e:
                    logger.error(f"管理者通知中にエラーが発生しました: {e}", exc_info=True)
    
    async def start(self):
        """ボットを起動する"""
        try:
            logger.info("Discordボットを起動しています...")
            await self.bot.start(self.token)
        except Exception as e:
            logger.error(f"ボット起動中にエラーが発生しました: {e}", exc_info=True)
            raise
    
    async def post_article(self, article: Dict[str, Any], channel_id: str) -> bool:
        """
        記事をDiscordチャンネルに投稿する
        
        Args:
            article: 記事データ
            channel_id: 投稿先チャンネルID
            
        Returns:
            投稿成功の場合はTrue、失敗の場合はFalse
        """
        try:
            # チャンネルの取得
            channel = self.bot.get_channel(int(channel_id))
            if not channel:
                logger.warning(f"チャンネルが見つかりません: {channel_id}")
                return False
            
            # Embedの構築
            embed = await self.message_builder.build_article_embed(article)
            
            # 投稿
            await channel.send(embed=embed)
            logger.info(f"記事を投稿しました: {article.get('title')} -> #{channel.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"記事投稿中にエラーが発生しました: {article.get('title')}: {e}", exc_info=True)
            return False
    
    async def create_feed_channel(self, guild_id: int, feed_info: Dict[str, Any]) -> Optional[str]:
        """
        フィード用のチャンネルを作成する
        
        Args:
            guild_id: サーバーID
            feed_info: フィード情報
            
        Returns:
            作成されたチャンネルID、失敗した場合はNone
        """
        try:
            # サーバーの取得
            guild = self.bot.get_guild(guild_id)
            if not guild:
                logger.warning(f"サーバーが見つかりません: {guild_id}")
                return None
            
            # チャンネル名の生成
            feed_title = feed_info.get("title", "Unknown Feed")
            feed_url = feed_info.get("url", "")
            channel_name = get_channel_name_for_feed(feed_url, feed_title)
            
            # カテゴリの取得
            category_id = self.config.get("category_id")
            category = None
            if category_id:
                category = guild.get_channel(int(category_id))
                if not category or not isinstance(category, discord.CategoryChannel):
                    logger.warning(f"カテゴリが見つかりません: {category_id}")
                    category = None
            
            # チャンネルの作成
            channel = await guild.create_text_channel(
                name=channel_name,
                category=category,
                topic=f"RSS Feed: {feed_title} | {feed_url}"
            )
            
            logger.info(f"フィードチャンネルを作成しました: #{channel.name} ({channel.id})")
            
            # チャンネルに初期メッセージを送信
            embed = discord.Embed(
                title=f"RSS Feed: {feed_title}",
                description=f"このチャンネルは「{feed_title}」のRSSフィード購読用に作成されました。",
                color=discord.Color(self.config.get("embed_color", 3447003))
            )
            embed.add_field(name="フィードURL", value=feed_url, inline=False)
            embed.add_field(name="更新頻度", value=f"{self.config.get('check_interval', 15)}分ごと", inline=True)
            
            await channel.send(embed=embed)
            
            return str(channel.id)
            
        except Exception as e:
            logger.error(f"チャンネル作成中にエラーが発生しました: {feed_info.get('title')}: {e}", exc_info=True)
            return None

