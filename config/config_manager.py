#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
設定管理モジュール

設定の読み込み、保存、検証を行う
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from .default_config import DEFAULT_CONFIG

logger = logging.getLogger(__name__)

class ConfigManager:
    """設定管理クラス"""
    
    def __init__(self, config_path: str = None):
        """
        初期化
        
        Args:
            config_path: 設定ファイルのパス（指定がない場合はデフォルト）
        """
        self.config_path = config_path or os.path.join("data", "config.json")
        self.config = {}
    
    def load_config(self) -> Dict[str, Any]:
        """
        設定を読み込む
        
        Returns:
            設定辞書
        """
        try:
            # 設定ファイルが存在するか確認
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                logger.info(f"設定を読み込みました: {self.config_path}")
            else:
                # 存在しない場合はデフォルト設定を使用
                self.config = DEFAULT_CONFIG.copy()
                logger.info("設定ファイルが見つからないため、デフォルト設定を使用します")
                
                # デフォルト設定を保存
                self.save_config()
            
            # 設定の検証と更新
            self._validate_and_update_config()
            
            return self.config
        
        except Exception as e:
            logger.error(f"設定の読み込み中にエラーが発生しました: {e}", exc_info=True)
            logger.info("デフォルト設定を使用します")
            self.config = DEFAULT_CONFIG.copy()
            return self.config
    
    def save_config(self) -> bool:
        """
        設定を保存する
        
        Returns:
            保存成功の場合はTrue、失敗の場合はFalse
        """
        try:
            # ディレクトリが存在するか確認
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            
            logger.info(f"設定を保存しました: {self.config_path}")
            return True
        
        except Exception as e:
            logger.error(f"設定の保存中にエラーが発生しました: {e}", exc_info=True)
            return False
    
    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """
        設定を更新する
        
        Args:
            new_config: 新しい設定辞書
            
        Returns:
            更新成功の場合はTrue、失敗の場合はFalse
        """
        try:
            self.config.update(new_config)
            return self.save_config()
        
        except Exception as e:
            logger.error(f"設定の更新中にエラーが発生しました: {e}", exc_info=True)
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """
        現在の設定を取得する
        
        Returns:
            設定辞書
        """
        return self.config
    
    def _validate_and_update_config(self):
        """設定の検証と更新"""
        # デフォルト設定のキーがない場合は追加
        for key, value in DEFAULT_CONFIG.items():
            if key not in self.config:
                self.config[key] = value
                logger.info(f"設定に不足しているキーを追加しました: {key}")
        
        # 必須項目の検証
        required_keys = ["discord_token", "check_interval", "admin_ids"]
        for key in required_keys:
            if not self.config.get(key):
                logger.warning(f"必須設定が不足しています: {key}")
                
                # 環境変数から取得を試みる
                env_key = f"DISCORD_RSS_{key.upper()}"
                if os.environ.get(env_key):
                    self.config[key] = os.environ.get(env_key)
                    logger.info(f"環境変数から設定を読み込みました: {key}")
                    
        # 環境変数からDiscordトークンを取得（.envファイルから）
        if not self.config.get("discord_token") and os.environ.get("DISCORD_TOKEN"):
            self.config["discord_token"] = os.environ.get("DISCORD_TOKEN")
            logger.info("環境変数からDiscordトークンを読み込みました")
            
        # 環境変数からGemini APIキーを取得（.envファイルから）
        if not self.config.get("gemini_api_key") and os.environ.get("GEMINI_API_KEY"):
            self.config["gemini_api_key"] = os.environ.get("GEMINI_API_KEY")
            logger.info("環境変数からGemini APIキーを読み込みました")

        if not self.config.get("gemini_api_keys") and os.environ.get("GEMINI_API_KEYS"):
            keys = [k.strip() for k in os.environ.get("GEMINI_API_KEYS").split(',') if k.strip()]
            self.config["gemini_api_keys"] = keys
            logger.info("環境変数からGemini APIキーのリストを読み込みました")

