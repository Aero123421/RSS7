#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AIプロセッサーのテスト
"""

import asyncio
import sys
import os
import logging
from typing import Dict, Any

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# AIモジュールのインポート
from ai.lmstudio_api import LMStudioAPI
from ai.summarizer import Summarizer
from ai.classifier import Classifier

async def test_ai_functions():
    """AI機能のテスト"""
    # LM Studio APIの初期化
    api_url = os.environ.get("LMSTUDIO_API_URL", "http://localhost:1234/v1")
    api = LMStudioAPI(api_url)
    
    try:
        # テスト記事
        article = {
            "title": "Artificial Intelligence Breakthrough: New Model Surpasses Human Performance",
            "content": """
Researchers at a leading AI lab have announced a breakthrough in artificial intelligence technology. 
Their new model has demonstrated capabilities that surpass human performance in several key areas, 
including complex problem-solving, language understanding, and creative tasks.

The model, which uses a novel architecture combining transformer networks with reinforcement learning, 
was trained on a diverse dataset spanning multiple domains. According to the research team, this approach 
has enabled the AI to develop a more robust understanding of context and nuance than previous models.

"This represents a significant step forward in AI development," said the lead researcher. "While we're 
excited about the capabilities, we're equally focused on ensuring responsible deployment and addressing 
potential ethical concerns."

Industry experts suggest this breakthrough could have far-reaching implications for fields ranging from 
healthcare and scientific research to creative industries and education. However, they also caution that 
such advanced AI systems require careful governance frameworks to manage risks and ensure benefits are 
widely distributed.

The research team plans to publish detailed findings in a peer-reviewed journal next month, along with 
technical documentation describing the model's architecture and training methodology.
"""
        }
        
        
        print("=== 要約テスト ===")
        summarizer = Summarizer(api)
        summary = await summarizer.summarize(article["content"], 200, "normal")
        print(f"要約（200文字）: {summary}")
        print(f"文字数: {len(summary)}")
        print()
        
        print("=== ジャンル分類テスト ===")
        classifier = Classifier(api)
        categories = ["technology", "business", "entertainment", "sports", "politics", "science", "health", "other"]
        category = await classifier.classify(article["title"], article["content"], categories)
        print(f"分類結果: {category}")
        
    finally:
        # セッションを閉じる
        await api.close()

if __name__ == "__main__":
    asyncio.run(test_ai_functions())

