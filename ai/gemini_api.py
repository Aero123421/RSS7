#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Gemini API連携

Google Gemini APIを使用してAI処理を行う
"""

import os
import logging
from typing import Optional

import google.generativeai as genai
from google.generativeai.types import GenerationConfig

logger = logging.getLogger(__name__)

class GeminiAPI:
    """Google Gemini API連携クラス"""

    def __init__(self, api_key: str = None, model: str = "gemini-1.5-pro"):
        """
        初期化

        Args:
            api_key: Google Gemini API Key（指定がない場合は環境変数から取得）
            model: 使用するモデル名
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        if not self.api_key:
            logger.warning("Gemini API Keyが設定されていません")

        genai.configure(api_key=self.api_key)

        self.model_name = model if model.startswith("models/") else f"models/{model}"
        self.model = genai.GenerativeModel(self.model_name)

        logger.info("Google Gemini APIを初期化しました")
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 0.95,
        top_k: int = 40,
        system_instruction: Optional[str] = None,
    ) -> str:
        """
        テキストを生成する
        
        Args:
            prompt: プロンプト
            max_tokens: 生成する最大トークン数
            temperature: 生成の多様性（0.0-1.0）
            
        Returns:
            生成されたテキスト
        """
        if not self.api_key:
            raise ValueError("Gemini API Keyが設定されていません")
        
        try:
            generation_config = GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                candidate_count=1,
            )

            model = self.model
            if system_instruction:
                model = genai.GenerativeModel(
                    self.model_name,
                    system_instruction=system_instruction,
                    generation_config=generation_config,
                )
                generation_config = None

            response = await model.generate_content_async(
                prompt,
                generation_config=generation_config,
            )

            if response.candidates:
                text = response.candidates[0].content.parts[0].text
                return text.strip() if text else ""

            logger.warning(f"APIレスポンスに有効な結果がありません: {response}")
            return ""
                
        except Exception as e:
            logger.error(f"テキスト生成中にエラーが発生しました: {e}", exc_info=True)
            raise
    
    async def close(self):
        """互換性のために存在するダミーメソッド"""
        logger.info("Google Gemini APIは特別なクローズ処理を必要としません")

# テスト用コード
async def test_gemini_api():
    """Google Gemini APIのテスト"""
    import asyncio
    import os
    
    # API Keyの取得
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("環境変数 GEMINI_API_KEY が設定されていません")
        return
    
    # APIインスタンスの作成
    api = GeminiAPI(api_key)
    
    try:
        # テキスト生成のテスト
        prompt = "こんにちは、私の名前は"
        print(f"プロンプト: {prompt}")
        
        response = await api.generate_text(prompt)
        print(f"応答: {response}")
        
    finally:
        # セッションを閉じる
        await api.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_gemini_api())

