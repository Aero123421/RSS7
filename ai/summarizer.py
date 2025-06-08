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
            "あなたは日本語編集者です。要点を抽出し、日本語のみで短くまとめます。"
            "長文は読みやすいように適度に改行してください。"
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
                    "次のタイトルを日本語に翻訳してください。\n\n"
                    f"{text}\n\n翻訳:"
                )
            else:
                if summary_type == "short":
                    prompt = (
                        "次の文章を日本語で2〜3文、100文字以内で要約してください。\n\n"
                        f"{text}\n\n要約:"
                    )
                elif summary_type == "long":
                    prompt = (
                        "次の文章を日本語で詳細に500文字以内で要約してください。読みやすいように適度に改行してください。\n\n"
                        f"{text}\n\n要約:"
                    )
                else:
                    prompt = (
                        "次の文章を日本語で200文字以内で要約してください。読みやすいように適度に改行してください。\n\n"
                        f"{text}\n\n要約:"
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
            prefixes = ["要約:", "要約結果:", "翻訳:", "翻訳結果:"]
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
