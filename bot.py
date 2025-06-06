#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Discord RSS Bot - メインエントリーポイント

RSS/atomフィードを監視し、AIで処理してDiscordに投稿するボットシステム
"""

import os
import asyncio
import logging
from dotenv import load_dotenv

# 内部モジュールのインポート
from config.config_manager import ConfigManager
from discord_bot.bot_client import DiscordBot
from discord_bot.commands import set_managers
from rss.feed_manager import FeedManager
from ai.ai_processor import AIProcessor
from utils.logger import setup_logger
from utils.scheduler import setup_scheduler

# 環境変数の読み込み
load_dotenv()

async def main():
    """メイン関数"""
    # ロガーのセットアップ
    logger = setup_logger()
    logger.info("Discord RSS Botを起動しています...")
    
    try:
        # 設定の読み込み
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Discordボットの初期化
        discord_bot = DiscordBot(config)
        
        # AIプロセッサーの初期化
        ai_processor = AIProcessor(config)
        
        # フィードマネージャーの初期化
        feed_manager = FeedManager(config, ai_processor, discord_bot)
        
        # コマンドマネージャーの設定
        set_managers(feed_manager, config_manager)
        
        # スケジューラーのセットアップ
        scheduler = setup_scheduler(feed_manager)
        
        # スケジューラーをボットに関連付け（コマンドから参照できるように）
        discord_bot.bot.scheduler = scheduler
        
        # Discordボットの起動
        await discord_bot.start()
        
    except Exception as e:
        logger.error(f"起動中にエラーが発生しました: {e}", exc_info=True)
        return

if __name__ == "__main__":
    # asyncioイベントループの実行
    asyncio.run(main())

