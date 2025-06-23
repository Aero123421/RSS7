#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Gemini API連携

Google Gemini APIを使用してAI処理を行う
"""

import os
import logging
import asyncio
from typing import Optional, List

from google.api_core import exceptions as google_exceptions
import google.generativeai as genai
# from google.generativeai import types as genai_types # Old import
# For new SDK, types are often directly under genai.types or not explicitly needed for basic usage

logger = logging.getLogger(__name__)

class GeminiAPI:
    """Google Gemini API連携クラス"""

    def __init__(self, api_key: str = None, model: str = "gemini-1.5-pro", api_keys: Optional[List[str]] = None):
        """
        初期化

        Args:
            api_key: Google Gemini API Key（指定がない場合は環境変数から取得）
            model: 使用するモデル名
        """
        self.api_keys = [k for k in (api_keys or []) if k]

        if api_key:
            if api_key not in self.api_keys:
                self.api_keys.insert(0, api_key)

        env_keys = []
        # Consolidated environment variable fetching
        gemini_api_1 = os.environ.get("GEMINI_API_1")
        gemini_api_2 = os.environ.get("GEMINI_API_2")
        gemini_api_keys_env = os.environ.get("GEMINI_API_KEYS")
        gemini_api_key_env = os.environ.get("GEMINI_API_KEY")

        if gemini_api_1: env_keys.append(gemini_api_1)
        if gemini_api_2: env_keys.append(gemini_api_2)
        if not env_keys and gemini_api_keys_env: # Only if GEMINI_API_1/2 are not set
            env_keys.extend([k.strip() for k in gemini_api_keys_env.split(',') if k.strip()])
        if not env_keys and gemini_api_key_env: # Only if no other keys found yet
            env_keys.append(gemini_api_key_env)

        for key in env_keys:
            if key not in self.api_keys:
                self.api_keys.append(key)

        self.model_name = model if model.startswith("models/") else f"models/{model}"
        self.generative_model: Optional[genai.GenerativeModel] = None # Type hint for clarity

        if not self.api_keys:
            logger.warning("Gemini API Keyが設定されていません。API機能は利用できません。")
            self.api_key = ""
            self.current_key_index = 0
            logger.info(f"Google Gemini APIを初期化しました (APIキー未設定)。モデル名: {self.model_name}")
            return

        from utils.helpers import select_gemini_api_key # Ensure this helper is robust
        try:
            selected_key = select_gemini_api_key(self.api_keys)
            self.current_key_index = self.api_keys.index(selected_key)
            self.api_key = selected_key
        except (ValueError, IndexError) as e:
            logger.error(f"有効なAPIキーの選択に失敗しました: {e}. APIキーリスト: {self.api_keys}")
            self.api_key = "" # Fallback to no key
            self.current_key_index = 0
            logger.info(f"Google Gemini APIを初期化しました (有効なAPIキー選択失敗)。モデル名: {self.model_name}")
            return


        self._configure_client()
        logger.info(f"Google Gemini APIを初期化しました。モデル: {self.model_name}")


    def _configure_client(self):
        """APIキーに基づきクライアントを構成する"""
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                # Safety settings can be configured here if needed, e.g.,
                # safety_settings = [
                #     {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                #     {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                # ]
                # self.generative_model = genai.GenerativeModel(self.model_name, safety_settings=safety_settings)
                self.generative_model = genai.GenerativeModel(self.model_name)
                logger.info(f"Geminiクライアントを構成しました。APIキーindex: {self.current_key_index}")
            except Exception as e:
                logger.error(f"Geminiクライアントの構成中にエラー: {e}", exc_info=True)
                self.generative_model = None
        else:
            self.generative_model = None
            logger.warning("APIキーがないためGeminiクライアントを構成できません。")

    def _switch_api_key(self):
        """Switch to the next API key in the list"""
        if not self.api_keys or len(self.api_keys) == 0:
            logger.warning("切り替えるAPIキーがありません。")
            self.api_key = "" # Ensure api_key is cleared if no keys are available
            self._configure_client() # Attempt to configure (will likely set model to None)
            return

        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        self.api_key = self.api_keys[self.current_key_index]
        logger.info(f"APIキーを切り替えました: index={self.current_key_index}")
        self._configure_client() # Re-configure with the new key

    def _is_rate_limit_error(self, error: Exception) -> bool:
        # google_exceptions.TooManyRequests should cover most rate limit cases
        if isinstance(error, (google_exceptions.TooManyRequests, google_exceptions.ResourceExhausted)):
            return True
        # Fallback for other potential rate limit messages if any
        msg = str(error).lower()
        return "rate" in msg and "limit" in msg or "quota" in msg or "429" in msg

    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: Optional[float] = 0.95, # Made Optional as per some SDK versions
        top_k: Optional[int] = 40,   # Made Optional
        system_instruction: Optional[str] = None,
    ) -> str:
        """
        テキストを生成する
        """
        if not self.generative_model:
            raise ValueError("Gemini APIが正しく初期化されていません (モデル未設定)。APIキーを確認してください。")

        consecutive_limits = 0
        max_retries_per_key_cycle = len(self.api_keys) * 2 if self.api_keys else 1

        while True:
            try:
                generation_config_params = {
                    "max_output_tokens": max_tokens,
                    "temperature": temperature,
                }
                if top_p is not None:
                    generation_config_params["top_p"] = top_p
                if top_k is not None:
                    generation_config_params["top_k"] = top_k

                current_generation_config = genai.types.GenerationConfig(**generation_config_params)

                # Use the model instance's system_instruction if provided during its init,
                # or create a new model instance if system_instruction is provided now.
                model_to_use = self.generative_model
                if system_instruction:
                    # This creates a new model instance for this call if system_instruction is different or not set.
                    # Consider if this is desired behavior due to potential overhead.
                    # For persistent system instructions, set it when initializing GeminiAPI or its model.
                    # logger.info(f"Using dynamic system instruction for this call.")
                    model_to_use = genai.GenerativeModel(
                        self.model_name,
                        system_instruction=system_instruction,
                        generation_config=current_generation_config # Pass config here
                    )
                    # When model is created with system_instruction, pass only prompt to generate_content_async
                    response = await model_to_use.generate_content_async(contents=prompt)
                else:
                    # If no system_instruction for this call, use the existing model with new config for this call
                    response = await model_to_use.generate_content_async(
                        contents=prompt,
                        generation_config=current_generation_config
                    )

                # Accessing response text and handling potential errors/empty responses
                try:
                    # The new SDK typically provides response.text directly.
                    # It might also have response.candidates for more detailed inspection if needed.
                    if hasattr(response, 'text') and response.text:
                        return response.text.strip()
                    # Fallback to candidates if .text is not fruitful, though less common for simple success
                    elif response.candidates and response.candidates[0].content.parts:
                         all_parts = "".join(part.text for part in response.candidates[0].content.parts if hasattr(part, 'text'))
                         if all_parts:
                             return all_parts.strip()

                    # If no text, log and return empty or raise error
                    finish_reason = "N/A"
                    if response.candidates and hasattr(response.candidates[0], 'finish_reason'):
                        finish_reason = response.candidates[0].finish_reason.name
                    elif hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                         finish_reason = f"Blocked: {response.prompt_feedback.block_reason.name}"

                    logger.warning(f"APIレスポンスに有効なテキストがありません。Finish reason: {finish_reason}. Response: {response}")
                    return "" # Or raise an error depending on desired strictness

                except ValueError as ve: # Handles cases where .text might raise ValueError (e.g. blocked content)
                    logger.warning(f"テキスト取得中にValueError: {ve}. Full response: {response}", exc_info=True)
                    return ""
                except AttributeError as ae:
                     logger.warning(f"レスポンス属性エラー: {ae}. Full response: {response}", exc_info=True)
                     return ""


            except Exception as e:
                if self._is_rate_limit_error(e) and self.api_keys and len(self.api_keys) > 0:
                    consecutive_limits += 1
                    logger.warning(f"レート制限エラー。APIキーを切り替えて再試行します (試行 {consecutive_limits}/{max_retries_per_key_cycle})")

                    if consecutive_limits >= max_retries_per_key_cycle:
                        logger.error("全てのAPIキーでレート制限に達しました。30秒待機後、エラーを送出します。")
                        await asyncio.sleep(30)
                        raise # Re-raise the exception after exhausting retries

                    self._switch_api_key() # Switch key
                    if not self.api_key: # If switching results in no valid key
                        logger.error("有効なAPIキーが見つかりませんでした。エラーを送出します。")
                        raise ValueError("No valid API key available after switching.")

                    if consecutive_limits % len(self.api_keys) == 0 and len(self.api_keys) > 1: # If cycled through all keys once
                         logger.info(f"APIキーを1周しました。10秒待機します。")
                         await asyncio.sleep(10)
                    else: # Wait a bit before retrying with new key
                        await asyncio.sleep(1) # Short delay before retry
                    continue # Retry the while loop

                logger.error(f"テキスト生成中に予期せぬエラーが発生しました: {e}", exc_info=True)
                raise # Re-raise other exceptions

    async def close(self):
        """互換性のために存在するダミーメソッド"""
        # New SDK does not require explicit client closing typically
        logger.info("Google Gemini API (new SDK) は特別なクローズ処理を必要としません")

# テスト用コード
async def test_gemini_api():
    """Google Gemini APIのテスト"""
    logging.basicConfig(level=logging.INFO) # Enable logging for test

    # API Keyの取得 (環境変数から取得を推奨)
    # api_key = os.environ.get("GEMINI_API_KEY") # Single key example
    # For multiple keys as per class design:
    api_keys_str = os.environ.get("GEMINI_API_KEYS") # e.g., "key1,key2"
    api_keys_list = [k.strip() for k in api_keys_str.split(',')] if api_keys_str else []
    
    if not api_keys_list and os.environ.get("GEMINI_API_KEY"):
        api_keys_list.append(os.environ.get("GEMINI_API_KEY"))

    if not api_keys_list:
        print("環境変数 GEMINI_API_KEY または GEMINI_API_KEYS が設定されていません")
        return
    
    # APIインスタンスの作成 (最初のキーをプライマリとして渡すか、リストのみ渡す)
    # api = GeminiAPI(api_key=api_keys_list[0], api_keys=api_keys_list)
    api = GeminiAPI(api_keys=api_keys_list, model="gemini-1.5-flash") # Using flash for testing
    
    try:
        # テキスト生成のテスト
        prompt1 = "こんにちは、あなたの名前は何ですか？"
        print(f"プロンプト1: {prompt1}")
        response1 = await api.generate_text(prompt1, max_tokens=50)
        print(f"応答1: {response1}")

        print("-" * 20)

        # システムインストラクション付きのテスト
        prompt2 = "日本の首都について3つのポイントで教えてください。"
        system_instruction2 = "あなたは親切なアシスタントです。簡潔に答えてください。"
        print(f"プロンプト2: {prompt2} (System: {system_instruction2})")
        response2 = await api.generate_text(prompt2, system_instruction=system_instruction2, max_tokens=150)
        print(f"応答2: {response2}")
        
    except Exception as e:
        print(f"テスト中にエラーが発生しました: {e}")
    finally:
        await api.close() # Though it does nothing, good practice if it might in future

if __name__ == "__main__":
    # To run test:
    # export GEMINI_API_KEY="YOUR_API_KEY"
    # python -m ai.gemini_api
    asyncio.run(test_gemini_api())

