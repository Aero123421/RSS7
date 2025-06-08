#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
設定マネージャーのテスト
"""

import os
import sys
import json
import unittest
import tempfile
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# テスト対象のモジュールをインポート
from config.config_manager import ConfigManager
from config.default_config import DEFAULT_CONFIG

class TestConfigManager(unittest.TestCase):
    """設定マネージャーのテストケース"""
    
    def setUp(self):
        """テスト前の準備"""
        # 一時ファイルを作成
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self.temp_dir.name, "test_config.json")
        
        # テスト用の設定
        self.test_config = {
            "discord_token": "test_token",
            "check_interval": 30,
            "ai_provider": "gemini"
        }
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        # 一時ディレクトリを削除
        self.temp_dir.cleanup()
    
    def test_load_default_config(self):
        """デフォルト設定の読み込みテスト"""
        # 設定ファイルが存在しない場合
        config_manager = ConfigManager(self.config_path)
        config = config_manager.load_config()
        
        # デフォルト設定が読み込まれるか確認
        self.assertEqual(config.get("check_interval"), DEFAULT_CONFIG.get("check_interval"))
        self.assertEqual(config.get("ai_provider"), DEFAULT_CONFIG.get("ai_provider"))
    
    def test_save_and_load_config(self):
        """設定の保存と読み込みテスト"""
        # 設定の保存
        config_manager = ConfigManager(self.config_path)
        config_manager.config = self.test_config.copy()
        result = config_manager.save_config()
        
        # 保存が成功したか確認
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.config_path))
        
        # 保存された内容を確認
        with open(self.config_path, "r", encoding="utf-8") as f:
            saved_config = json.load(f)
        
        self.assertEqual(saved_config.get("discord_token"), self.test_config.get("discord_token"))
        self.assertEqual(saved_config.get("check_interval"), self.test_config.get("check_interval"))
        
        # 新しいインスタンスで読み込み
        new_config_manager = ConfigManager(self.config_path)
        loaded_config = new_config_manager.load_config()
        
        # 読み込まれた内容を確認
        self.assertEqual(loaded_config.get("discord_token"), self.test_config.get("discord_token"))
        self.assertEqual(loaded_config.get("check_interval"), self.test_config.get("check_interval"))
    
    def test_update_config(self):
        """設定の更新テスト"""
        # 初期設定
        config_manager = ConfigManager(self.config_path)
        config_manager.config = self.test_config.copy()
        config_manager.save_config()
        
        # 設定の更新
        update_config = {
            "check_interval": 15
        }
        
        result = config_manager.update_config(update_config)
        self.assertTrue(result)
        
        # 更新された内容を確認
        self.assertEqual(config_manager.config.get("check_interval"), 15)
        self.assertEqual(config_manager.config.get("discord_token"), self.test_config.get("discord_token"))
    
    def test_validate_and_update_config(self):
        """設定の検証と更新テスト"""
        # 不完全な設定
        incomplete_config = {
            "discord_token": "test_token"
        }
        
        # 設定マネージャーの初期化
        config_manager = ConfigManager(self.config_path)
        config_manager.config = incomplete_config
        
        # 検証と更新
        config_manager._validate_and_update_config()
        
        # デフォルト値が追加されたか確認
        self.assertEqual(config_manager.config.get("check_interval"), DEFAULT_CONFIG.get("check_interval"))
        self.assertEqual(config_manager.config.get("ai_provider"), DEFAULT_CONFIG.get("ai_provider"))
        self.assertEqual(config_manager.config.get("discord_token"), "test_token")

if __name__ == "__main__":
    unittest.main()

