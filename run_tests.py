#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
テスト実行スクリプト

すべてのテストを実行する
"""

import os
import sys
import unittest
import logging

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_tests():
    """すべてのテストを実行する"""
    # テストディレクトリのパス
    tests_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests")
    
    # テストファイルの検索
    test_files = []
    for file in os.listdir(tests_dir):
        if file.startswith("test_") and file.endswith(".py"):
            test_files.append(file[:-3])  # .pyを除去
    
    if not test_files:
        logger.warning("テストファイルが見つかりません")
        return False
    
    logger.info(f"テストファイルを{len(test_files)}個見つけました: {', '.join(test_files)}")
    
    # テストスイートの作成
    suite = unittest.TestSuite()
    
    # テストの追加
    for test_file in test_files:
        try:
            # テストモジュールのインポート
            module_name = f"tests.{test_file}"
            __import__(module_name)
            module = sys.modules[module_name]
            
            # モジュール内のテストケースを追加
            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, type) and issubclass(obj, unittest.TestCase) and obj != unittest.TestCase:
                    suite.addTest(unittest.makeSuite(obj))
            
            logger.info(f"テストケースを追加しました: {test_file}")
            
        except Exception as e:
            logger.error(f"テストモジュールのロード中にエラーが発生しました: {test_file}: {e}", exc_info=True)
    
    # テストの実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 結果の表示
    logger.info(f"テスト結果: 実行={result.testsRun}, 成功={result.testsRun - len(result.failures) - len(result.errors)}, 失敗={len(result.failures)}, エラー={len(result.errors)}")
    
    return len(result.failures) == 0 and len(result.errors) == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

