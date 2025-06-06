#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AIプロセッサー

記事のAI処理（翻訳、要約、分類）を行う
"""

import logging
from typing import Dict, Any, Optional, List

from .lmstudio_api import LMStudioAPI
from .gemini_api import GeminiAPI
from .summarizer import Summarizer
from .classifier import Classifier

logger = logging.getLogger(__name__)

class AIProcessor:
    """AI処理クラス"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初期化
        
        Args:
            config: 設定辞書
        """
        self.config = config
        
        # モデルの選択
        ai_model = config.get("ai_model", "lmstudio")

        if ai_model.startswith("gemini"):
            api_key = config.get("gemini_api_key", "")
            self.api = GeminiAPI(api_key, model=ai_model)
            logger.info(f"Google Gemini APIを使用します: {ai_model}")
        else:
            api_url = config.get("lmstudio_api_url", "http://localhost:1234/v1")
            self.api = LMStudioAPI(api_url, model=ai_model)
            logger.info(f"LM Studio APIを使用します: {api_url} ({ai_model})")
        
        # 各処理クラスの初期化
        self.summarizer = Summarizer(self.api)
        self.classifier = Classifier(self.api)
        
        logger.info("AIプロセッサーを初期化しました")
    
    async def process_article(self, article: Dict[str, Any], feed_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        記事を処理する
        
        Args:
            article: 記事データ
            feed_info: フィード情報
            
        Returns:
            処理済み記事データ
        """
        processed = article.copy()
        
        try:
            # 要約（翻訳を兼ねる）
            if self.config.get("summarize", True):
                processed = await self._summarize_article(processed, feed_info)
            
            # ジャンル分類
            if self.config.get("classify", False):
                processed = await self._classify_article(processed)
            
            # 処理フラグを追加
            processed["ai_processed"] = True
            
            return processed
            
        except Exception as e:
            logger.error(f"記事処理中にエラーが発生しました: {article.get('title')}: {e}", exc_info=True)
            
            # エラーが発生した場合は元の記事を返す
            processed["ai_processed"] = False
            processed["ai_error"] = str(e)
            return processed
    
    async def _summarize_article(self, article: Dict[str, Any], feed_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        記事を要約する
        
        Args:
            article: 記事データ
            
        Returns:
            要約済み記事データ
        """
        try:
            # 要約対象のコンテンツ
            content = article.get("content", "")
            
            # 要約の最大文字数
            max_length = self.config.get("summary_length", 200)
            summary_type = feed_info.get("summary_type")
            if summary_type == "short":
                max_length = 100
            elif summary_type == "long":
                max_length = 400
            
            # 要約の生成
            summary = await self.summarizer.summarize(content, max_length)
            
            # 要約結果を記事に追加
            article["summary"] = summary
            article["summarized"] = True
            
            logger.info(f"記事を要約しました: {article.get('title')}")
            return article
            
        except Exception as e:
            logger.error(f"記事要約中にエラーが発生しました: {article.get('title')}: {e}", exc_info=True)
            article["summarized"] = False
            return article
    
    async def _classify_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        記事のジャンルを分類する
        
        Args:
            article: 記事データ
            
        Returns:
            分類済み記事データ
        """
        try:
            # 分類対象のコンテンツ
            title = article.get("title", "")
            content = article.get("content", "")
            
            # カテゴリリスト
            categories = self.config.get("categories", [])
            category_names = [cat.get("name") for cat in categories]
            
            # ジャンル分類
            category = await self.classifier.classify(title, content, category_names)
            
            # 分類結果を記事に追加
            article["category"] = category
            article["classified"] = True
            
            logger.info(f"記事を分類しました: {article.get('title')} -> {category}")
            return article
            
        except Exception as e:
            logger.error(f"記事分類中にエラーが発生しました: {article.get('title')}: {e}", exc_info=True)
            article["classified"] = False
            article["category"] = "other"  # デフォルトカテゴリ
            return article

