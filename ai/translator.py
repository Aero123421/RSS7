#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
翻訳機能

記事の翻訳を行う
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class Translator:
    """翻訳クラス"""
    
    def __init__(self, api):
        """
        初期化
        
        Args:
            api: APIインスタンス（LMStudioAPIまたはGeminiAPI）
        """
        self.api = api
        logger.info("翻訳機能を初期化しました")
    
    async def translate(self, text: str, source_lang: str = "auto", target_lang: str = "ja") -> str:
        """
        テキストを翻訳する
        
        Args:
            text: 翻訳するテキスト
            source_lang: 元の言語（autoで自動検出）
            target_lang: 翻訳先の言語
            
        Returns:
            翻訳されたテキスト
        """
        if not text:
            return ""
        
        # 既に日本語の場合はそのまま返す（簡易判定）
        if self._is_japanese(text):
            logger.info("テキストは既に日本語のため翻訳をスキップします")
            return text
        
        try:
            # 翻訳プロンプトの作成
            prompt = f"""
以下のテキストを日本語に翻訳してください。翻訳のみを出力し、余計な説明は不要です。

テキスト:
{text}

日本語訳:
"""
            
            # APIを使用して翻訳
            translated = await self.api.generate_text(prompt, max_tokens=2000, temperature=0.1)
            
            # 余計なプレフィックスを削除
            prefixes = ["日本語訳:", "翻訳:", "翻訳結果:"]
            for prefix in prefixes:
                if translated.startswith(prefix):
                    translated = translated[len(prefix):].strip()
            
            return translated
            
        except Exception as e:
            logger.error(f"翻訳中にエラーが発生しました: {e}", exc_info=True)
            # エラーの場合は元のテキストを返す
            return text
    
    def _is_japanese(self, text: str) -> bool:
        """
        テキストが日本語かどうかを簡易判定する
        
        Args:
            text: 判定するテキスト
            
        Returns:
            日本語の場合はTrue、それ以外はFalse
        """
        # 日本語の文字コード範囲
        japanese_ranges = [
            (0x3040, 0x309F),  # ひらがな
            (0x30A0, 0x30FF),  # カタカナ
            (0x4E00, 0x9FFF),  # 漢字
            (0xFF66, 0xFF9F)   # 半角カタカナ
        ]
        
        # サンプリングして判定（長いテキストの場合は全文チェックしない）
        sample = text[:100]
        
        # 日本語文字の割合を計算
        jp_chars = 0
        for char in sample:
            code = ord(char)
            for start, end in japanese_ranges:
                if start <= code <= end:
                    jp_chars += 1
                    break
        
        # 日本語文字が30%以上あれば日本語と判定
        ratio = jp_chars / len(sample) if sample else 0
        return ratio > 0.3

# テスト用コード
async def test_translator():
    """翻訳機能のテスト"""
    import asyncio
    from lmstudio_api import LMStudioAPI
    
    # APIインスタンスの作成
    api = LMStudioAPI()
    
    # 翻訳インスタンスの作成
    translator = Translator(api)
    
    try:
        # 英語テキストの翻訳テスト
        english_text = "Hello, this is a test of the translation function. It should translate this English text to Japanese."
        print(f"英語テキスト: {english_text}")
        
        japanese_text = await translator.translate(english_text)
        print(f"翻訳結果: {japanese_text}")
        
        # 既に日本語のテキストのテスト
        japanese_original = "これは既に日本語のテキストです。翻訳せずにそのまま返されるはずです。"
        print(f"\n日本語テキスト: {japanese_original}")
        
        result = await translator.translate(japanese_original)
        print(f"翻訳結果: {result}")
        
    finally:
        # セッションを閉じる
        await api.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_translator())

