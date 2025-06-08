#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AIプロセッサー

記事のAI処理（翻訳、要約、分類）を行う
"""

import logging
from typing import Dict, Any, Optional, List
from utils.helpers import select_gemini_api_key

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
        
        # プライマリAIプロバイダの選択
        self.ai_provider = config.get("ai_provider", "lmstudio")
        self.ai_model = config.get("ai_model")
        if not self.ai_model:
            self.ai_model = (
                "gemini-1.5-pro" if self.ai_provider.startswith("gemini") else "lmstudio"
            )
        elif self.ai_provider.startswith("gemini") and not self.ai_model.startswith("gemini"):
            logger.warning(
                "Geminiを使用する場合、ai_model も gemini-* である必要があります。デフォルトモデルを使用します。"
            )
            self.ai_model = "gemini-1.5-pro"
        elif self.ai_provider.startswith("lmstudio") and self.ai_model.startswith("gemini"):
            logger.warning(
                "LM Studioを使用する場合、ai_model はローカルモデル名を指定してください。デフォルトモデルを使用します。"
            )
            self.ai_model = "lmstudio"

        self.api = self._create_api(self.ai_provider, self.ai_model)

        # フォールバックプロバイダ
        self.fallback_provider = config.get("fallback_ai_provider")

        # 各処理クラスの初期化
        self.summarizer = Summarizer(self.api)
        self.classifier = Classifier(self.api)

        logger.info("AIプロセッサーを初期化しました")

    def _create_api(self, provider: str, model: Optional[str] = None):
        """AIプロバイダに応じたAPIインスタンスを生成する"""
        if provider.startswith("gemini"):
            api_key = self.config.get("gemini_api_key", "")
            keys = self.config.get("gemini_api_keys")
            if keys:
                api_key = select_gemini_api_key(keys)
            selected_model = model or "gemini-1.5-pro"
            logger.info(f"Google Gemini APIを使用します: {selected_model}")
            return GeminiAPI(api_key, model=selected_model)

        api_url = self.config.get("lmstudio_api_url", "http://localhost:1234/v1")
        selected_model = model or "lmstudio"
        logger.info(f"LM Studio APIを使用します: {api_url} ({selected_model})")
        return LMStudioAPI(api_url, model=selected_model)
    
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
                try:
                    processed = await self._summarize_article(processed, feed_info)
                except Exception as e:
                    logger.warning(f"要約に失敗しました: {e}")
                    if self.fallback_provider and self.fallback_provider != self.ai_provider:
                        try:
                            processed = await self._summarize_article(
                                processed, feed_info, provider=self.fallback_provider
                            )
                        except Exception as e2:
                            logger.error(
                                f"フォールバック要約にも失敗しました: {e2}", exc_info=True
                            )
                            processed["summarized"] = False
                    else:
                        processed["summarized"] = False
            
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
    
    async def _summarize_article(
        self,
        article: Dict[str, Any],
        feed_info: Dict[str, Any],
        provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        記事を要約する
        
        Args:
            article: 記事データ
            
        Returns:
            要約済み記事データ
        """
        # 要約対象のコンテンツ
        content = article.get("content", "")

        # 要約の最大文字数
        max_length = self.config.get("summary_length", 200)
        summary_type = feed_info.get("summary_type")
        if summary_type == "short":
            max_length = 100
        elif summary_type == "long":
            max_length = 400

        # 使用するサマライザー
        summarizer = self.summarizer
        api = None
        if provider and provider != self.ai_provider:
            api = self._create_api(provider)
            summarizer = Summarizer(api)

        # 要約の生成
        summary = await summarizer.summarize(content, max_length, summary_type or "normal")

        # 要約結果を記事に追加
        article["summary"] = summary
        article["summarized"] = True

        logger.info(f"記事を要約しました: {article.get('title')}")

        if api:
            await api.close()
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

