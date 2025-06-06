#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LM Studio API連携

LM Studio APIを使用してAI処理を行う
"""

import os
import logging
import json
import aiohttp
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class LMStudioAPI:
    """LM Studio API連携クラス"""

    def __init__(self, api_url: str = None, model: str = "local-model"):
        """
        初期化

        Args:
            api_url: LM Studio API URL（指定がない場合は環境変数から取得）
            model: 使用するモデル名
        """
        self.api_url = api_url or os.environ.get("LMSTUDIO_API_URL", "http://localhost:1234/v1")
        self.model = model
        self.session = None
        
        logger.info(f"LM Studio APIを初期化しました: {self.api_url}")
    
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
        try:
            # リクエストデータの作成
            data = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            # APIリクエスト
            session = await self._get_session()
            async with session.post(f"{self.api_url}/chat/completions", json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"API呼び出しエラー: {response.status}, {error_text}")
                    raise Exception(f"API呼び出しエラー: {response.status}")
                
                result = await response.json()
                
                # レスポンスからテキストを抽出
                if "choices" in result and len(result["choices"]) > 0:
                    message = result["choices"][0].get("message", {})
                    return message.get("content", "").strip()
                else:
                    logger.warning(f"APIレスポンスに有効な結果がありません: {result}")
                    return ""
                
        except Exception as e:
            logger.error(f"テキスト生成中にエラーが発生しました: {e}", exc_info=True)
            raise
    
    async def close(self):
        """セッションを閉じる"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("LM Studio APIセッションを閉じました")

# テスト用コード
async def test_lmstudio_api():
    """LM Studio APIのテスト"""
    import asyncio
    
    # APIインスタンスの作成
    api = LMStudioAPI()
    
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
    asyncio.run(test_lmstudio_api())

