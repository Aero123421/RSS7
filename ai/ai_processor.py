#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AIプロセッサー

記事のAI処理（翻訳、要約、分類）を行う
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from utils.helpers import select_gemini_api_key

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
        
        # AIモデルの設定（Google Geminiのみを利用）
        self.ai_provider = "gemini"
        self.ai_model = config.get("ai_model", "gemini-2.0-flash")

        self.api = self._create_api(self.ai_model)

        # 各処理クラスの初期化
        self.summarizer = Summarizer(self.api)
        self.classifier = Classifier(self.api)

        logger.info("AIプロセッサーを初期化しました")

    def _create_api(self, model: Optional[str] = None):
        """Google Gemini APIインスタンスを生成する"""
        api_key = self.config.get("gemini_api_key", "")
        keys = self.config.get("gemini_api_keys")
        selected_model = model or "gemini-2.0-flash"
        logger.info(f"Google Gemini APIを使用します: {selected_model}")
        return GeminiAPI(api_key, model=selected_model, api_keys=keys)

    async def extract_keywords_for_storage(self, article: Dict[str, Any]) -> str:
        """記事から検索用キーワードを抽出する"""
        title = article.get("title", "")
        content = article.get("content", "")
        prompt = (
            "You are a data indexer. Analyze the following article and extract the 5-7 most important and representative keywords in English. "
            "The keywords should be suitable for later searching. Output them as a single, comma-separated string.\n\n"
            f"Title: {title}\n\nContent:\n{content}"
        )
        try:
            text = await self.api.generate_text(prompt, max_tokens=50, temperature=0.3)
            return text.strip()
        except Exception as e:
            logger.error(f"キーワード抽出中にエラーが発生しました: {e}", exc_info=True)
            return ""
    
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
                    processed["summarized"] = False

            # ジャンル分類
            if self.config.get("classify", False):
                processed = await self._classify_article(processed)

            # 検索用キーワード抽出
            keywords_en = await self.extract_keywords_for_storage(processed)
            processed["keywords_en"] = keywords_en

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
        max_length = self.config.get("summary_length", 4000)
        summary_type = feed_info.get("summary_type")

        summarizer = self.summarizer

        # 要約の生成
        summary = await summarizer.summarize(content, max_length, summary_type or "normal")

        # タイトルの翻訳
        title = article.get("title", "")
        if title:
            translated = await summarizer.summarize(title, max_length, "title")
            if translated:
                article["title"] = translated

        # 要約結果を記事に追加
        article["summary"] = summary
        article["summarized"] = True

        logger.info(f"記事を要約しました: {article.get('title')}")

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

    async def _generate_search_keywords(
        self, original_article: Dict[str, Any], question: str
    ) -> List[str]:
        """質問と記事から検索用キーワードを生成する"""
        title = original_article.get("title", "")
        content = original_article.get("content", "")
        prompt = (
            "You are a search query expert. Extract up to 5 important English keywords from the user's question and the original article to find related information."\
            f"\n\nTitle: {title}\n\nContent:\n{content}\n\nQuestion: {question}\n\nKeywords:"
        )
        try:
            text = await self.api.generate_text(prompt, max_tokens=30, temperature=0.3)
            keywords = [k.strip() for k in text.replace("\n", "").split(",") if k.strip()]
            return keywords[:5]
        except Exception as e:
            logger.error(f"検索用キーワード生成中にエラーが発生しました: {e}", exc_info=True)
            return []

    async def answer_question(
        self,
        original_article: Dict[str, Any],
        related_articles: List[Dict[str, Any]],
        question: str,
    ) -> str:
        """元記事と関連記事を基に質問に回答する"""
        main_title = original_article.get("title", "")
        main_content = original_article.get("content", "")

        related_parts = []
        for i, art in enumerate(related_articles, 1):
            title = art.get("title", "")
            content = (art.get("content", "") or "")[:600]
            related_parts.append(f"{i}. Title: {title}\n   Content: {content}...")
        related_block = "\n".join(related_parts)

        prompt = (
            "You are an expert news commentator. Based on the following articles, please answer the user's question in Japanese.\n\n"
            f"**Main Article:**\nTitle: {main_title}\nContent: {main_content}\n\n"
            f"**Related Articles:**\n{related_block}\n\n"
            f"**User's Question:**\n{question}\n\n**Answer (in Japanese):**"
        )
        try:
            api = self._create_api("gemini-2.5-flash")
            return await api.generate_text(prompt, max_tokens=1000, temperature=0.3)
        except Exception as e:
            logger.error(f"回答生成中にエラーが発生しました: {e}", exc_info=True)
            return "回答を生成できませんでした。"

