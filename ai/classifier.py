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
            api: APIインスタンス（LMStudioAPIまたはGeminiAPI）
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
以下の記事を次のカテゴリのいずれかに分類してください: {categories_str}

記事:
{classification_text}

回答は分類されたカテゴリ名のみを出力してください。余計な説明は不要です。
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
async def test_classifier():
    """ジャンル分類機能のテスト"""
    import asyncio
    from lmstudio_api import LMStudioAPI
    
    # APIインスタンスの作成
    api = LMStudioAPI()
    
    # 分類インスタンスの作成
    classifier = Classifier(api)
    
    try:
        # テスト記事
        test_articles = [
            {
                "title": "新型スマートフォンの発売日が決定、AI機能を強化",
                "content": "大手メーカーは次世代スマートフォンの発売日を発表した。新モデルは人工知能機能が大幅に強化され、ユーザー体験の向上が期待されている。カメラ性能も向上し、暗所での撮影能力が改善されている。"
            },
            {
                "title": "株式市場が急落、世界経済の先行き不安",
                "content": "昨日の株式市場は大幅な下落となった。米国の金利政策や世界的なインフレ懸念が投資家心理に影響を与えている。アナリストは今後の動向に注意が必要だと警告している。"
            },
            {
                "title": "新作映画が興行収入記録を更新",
                "content": "先週公開された新作映画が、初週の興行収入で歴代最高記録を更新した。有名監督と人気俳優の組み合わせが観客を魅了し、SNSでも話題となっている。続編の制作も既に決定している。"
            }
        ]
        
        # カテゴリリスト
        categories = ["technology", "business", "entertainment", "sports", "politics", "science", "health", "other"]
        
        # 各記事の分類テスト
        for article in test_articles:
            print(f"記事タイトル: {article['title']}")
            category = await classifier.classify(article["title"], article["content"], categories)
            print(f"分類結果: {category}\n")
        
    finally:
        # セッションを閉じる
        await api.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_classifier())

