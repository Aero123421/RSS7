#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ロギングユーティリティ

ロギングの設定と初期化を行う
"""

import os
import logging
import logging.handlers
from pathlib import Path

def setup_logger(log_level: str = "INFO", log_file: str = None) -> logging.Logger:
    """
    ロガーをセットアップする
    
    Args:
        log_level: ログレベル
        log_file: ログファイルのパス
        
    Returns:
        設定済みのロガー
    """
    # ルートロガーの取得
    logger = logging.getLogger()
    
    # ログレベルの設定
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # フォーマッターの作成
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # コンソールハンドラーの設定
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # ファイルハンドラーの設定（指定がある場合）
    if log_file:
        # ディレクトリが存在するか確認
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # ファイルハンドラーの作成
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

