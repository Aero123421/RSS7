#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
要約機能

記事の要約を行う
"""

import logging
import re
from typing import Dict, Any, Optional

from .gemini_api import GeminiAPI

from .simple_summarizer import simple_summarize

logger = logging.getLogger(__name__)

class Summarizer:
    """要約クラス"""
    
    def __init__(self, api, system_instruction: Optional[str] = None):
        """
        初期化
        
        Args:
            api: APIインスタンス（GeminiAPI）
        """
        self.api = api
        self.system_instruction = system_instruction or (
            "あなたは熟練した日本語編集者です。文章の要点を抽出し、必ず日本語だけで簡潔にまとめます。"
            "英語は使用せず、長文の場合は適度に改行して読みやすくしてください。"
        )
        logger.info("要約機能を初期化しました")
    
    async def summarize(self, text: str, max_length: int = 4000, summary_type: str = "normal") -> str:
        """
        テキストを要約する
        
        Args:
            text: 要約するテキスト
            max_length: 要約の最大文字数
            
        Returns:
            要約されたテキスト
        """
        if not text:
            return ""
        
        try:
            # 要約および翻訳プロンプトの作成
            if summary_type == "title":
                prompt = (
                    "以下のタイトルを自然な日本語へ翻訳してください。英語は使わないでください。\n\n"
                    f"タイトル:\n{text}\n\n翻訳:"
                )
            else:
                if summary_type == "short":
                    length_inst = "2〜3文で100文字以内"
                    max_length = min(max_length, 120)
                elif summary_type == "long":
                    length_inst = "詳細に500文字以内"
                    max_length = min(max_length, 500)
                else:
                    length_inst = "200文字以内"
                    max_length = min(max_length, 200)

                prompt = (
                    "以下の文章を分かりやすく要約してください。"
                    f"{length_inst}。必ず日本語で書き、長文の場合は読みやすいように適度に改行してください。\n\n"
                    f"テキスト:\n{text}\n\n要約:"
                )
            
            # APIを使用して要約
            if isinstance(self.api, GeminiAPI):
                summary = await self.api.generate_text(
                    prompt,
                    max_tokens=1000,
                    temperature=0.3,
                    system_instruction=self.system_instruction,
                )
            else:
                summary = await self.api.generate_text(prompt, max_tokens=1000, temperature=0.3)
            
            # 余計なプレフィックスを削除
            prefixes = ["要約:", "要約結果:"]
            for prefix in prefixes:
                if summary.startswith(prefix):
                    summary = summary[len(prefix):].strip()
            
            # 最大長を超えた場合は切り詰め
            if len(summary) > max_length:
                summary = summary[:max_length - 3] + "..."
            
            return summary

        except Exception as e:
            logger.error(f"要約中にエラーが発生しました: {e}", exc_info=True)
            logger.info("外部APIが利用できないため、簡易要約にフォールバックします")
            return simple_summarize(text, max_length)
