#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
スケジューラーユーティリティ

定期的なタスク実行のためのスケジューラー設定
"""

import logging
from typing import Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

def setup_scheduler(feed_manager: Any) -> AsyncIOScheduler:
    """
    スケジューラーをセットアップする
    
    Args:
        feed_manager: フィードマネージャーインスタンス
        
    Returns:
        設定済みのスケジューラー
    """
    scheduler = AsyncIOScheduler()
    
    # フィード確認ジョブの追加
    check_interval = feed_manager.config.get("check_interval", 15)  # デフォルト15分
    
    scheduler.add_job(
        feed_manager.check_feeds,
        IntervalTrigger(minutes=check_interval),
        id="check_feeds",
        replace_existing=True,
        name="フィード確認"
    )
    
    logger.info(f"フィード確認スケジュールを設定しました: {check_interval}分間隔")
    
    # スケジューラーの開始
    scheduler.start()
    logger.info("スケジューラーを開始しました")
    
    return scheduler

def update_check_interval(scheduler: AsyncIOScheduler, feed_manager: Any, interval: int) -> bool:
    """
    フィード確認間隔を更新する
    
    Args:
        scheduler: スケジューラーインスタンス
        feed_manager: フィードマネージャーインスタンス
        interval: 新しい確認間隔（分）
        
    Returns:
        更新成功の場合はTrue、失敗の場合はFalse
    """
    try:
        # 既存のジョブを削除
        scheduler.remove_job("check_feeds")
        
        # 新しいジョブを追加
        scheduler.add_job(
            feed_manager.check_feeds,
            IntervalTrigger(minutes=interval),
            id="check_feeds",
            replace_existing=True,
            name="フィード確認"
        )
        
        logger.info(f"フィード確認間隔を更新しました: {interval}分")
        return True
        
    except Exception as e:
        logger.error(f"フィード確認間隔の更新中にエラーが発生しました: {e}", exc_info=True)
        return False

