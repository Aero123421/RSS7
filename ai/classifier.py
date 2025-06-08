#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ジャンル分類機能

記事のジャンル分類を行う
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class Classifier:
    """ジャンル分類クラス"""
    
    def __init__(self, api):
        """
        初期化
        
        Args:
            api: APIインスタンス（GeminiAPI）
        """
        self.api = api
        logger.info("ジャンル分類機能を初期化しました")
    
    async def classify(self, title: str, content: str, categories: List[str] = None) -> str:
        """
        記事のジャンルを分類する
        
        Args:
            title: 記事タイトル
            content: 記事内容
            categories: 分類カテゴリリスト（指定がない場合はデフォルトカテゴリを使用）
            
        Returns:
            分類されたジャンル
        """
        if not title and not content:
            return "other"
        
        # カテゴリリストの設定
        if not categories or len(categories) == 0:
            categories = [
                "technology", "business", "politics", "entertainment", 
                "sports", "science", "health", "other"
            ]
        
        try:
            # 分類用のテキスト（タイトルと内容の先頭部分）
            classification_text = f"{title}\n\n{content[:500]}..."
            
            # 分類プロンプトの作成
            categories_str = ", ".join(categories)
            prompt = f"""
次の記事のジャンルを以下のカテゴリから最も適切なもの一つだけ選んでください:
{categories_str}

記事:
{classification_text}

出力は選んだカテゴリ名のみを英語で一語だけ返してください。余計な説明や句読点、改行は不要です。
"""
            
            # APIを使用して分類
            result = await self.api.generate_text(prompt, max_tokens=50, temperature=0.1)
            
            # 結果の正規化
            result = result.strip().lower()
            
            # カテゴリリストに含まれるか確認
            for category in categories:
                if category.lower() in result:
                    return category
            
            # 該当するカテゴリがない場合はその他
            return "other"
            
        except Exception as e:
            logger.error(f"ジャンル分類中にエラーが発生しました: {e}", exc_info=True)
            # エラーの場合はその他を返す
            return "other"

# テスト用コード

