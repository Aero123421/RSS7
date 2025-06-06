#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Gemini API連携

Google Gemini APIを使用してAI処理を行う
"""

import os
import logging
import json
import aiohttp
from typing import Dict, Any, List, Optional

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

        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.model = model
        self.session = None
        
        logger.info("Google Gemini APIを初期化しました")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """
        HTTPセッションを取得する
        
        Returns:
            aiohttp.ClientSession
        """
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={"Content-Type": "application/json"}
            )
        return self.session
    
    async def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
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
            # リクエストデータの作成
            data = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": temperature
                }
            }
            
            # APIリクエスト
            session = await self._get_session()
            url = f"{self.api_url}/{self.model}:generateContent?key={self.api_key}"
            
            async with session.post(url, json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"API呼び出しエラー: {response.status}, {error_text}")
                    raise Exception(f"API呼び出しエラー: {response.status}")
                
                result = await response.json()
                
                # レスポンスからテキストを抽出
                if "candidates" in result and len(result["candidates"]) > 0:
                    content = result["candidates"][0].get("content", {})
                    parts = content.get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"].strip()
                
                logger.warning(f"APIレスポンスに有効な結果がありません: {result}")
                return ""
                
        except Exception as e:
            logger.error(f"テキスト生成中にエラーが発生しました: {e}", exc_info=True)
            raise
    
    async def close(self):
        """セッションを閉じる"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("Google Gemini APIセッションを閉じました")

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

