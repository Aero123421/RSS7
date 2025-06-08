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
            api: APIインスタンス（LMStudioAPIまたはGeminiAPI）
        """
        self.api = api
        self.system_instruction = system_instruction or (
            "あなたはプロの翻訳者兼要約者です。与えられた文章の要点を抽出し、"
            "箇条書きを使わず簡潔な文章でまとめます。日本語で分かりやすく記述してください。"
        )
        logger.info("要約機能を初期化しました")
    
    async def summarize(self, text: str, max_length: int = 200, summary_type: str = "normal") -> str:
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
            if summary_type == "short":
                prompt = (
                    "あなたはニュース編集者です。以下の文章を日本語で簡潔に一文で要約してください。"
                    f"{max_length}文字以内でまとめてください。\n\n"
                    f"テキスト:\n{text}\n\n要約:"
                )
            elif summary_type == "long":
                prompt = (
                    "あなたはニュース編集者です。以下の文章を日本語で詳しく要約してください。"
                    "箇条書きを使わず3〜5文程度の文章でまとめてください。"
                    f"必ず{max_length}文字以内で記述してください。\n\n"
                    f"テキスト:\n{text}\n\n要約:"
                )
            else:
                prompt = (
                    "あなたはニュース編集者です。以下の文章を日本語で分かりやすく要約してください。"
                    "2〜3文以内の文章で、箇条書きを使わずにまとめてください。"
                    f"{max_length}文字以内で書いてください。\n\n"
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

# テスト用コード
async def test_summarizer():
    """要約機能のテスト"""
    import asyncio
    from lmstudio_api import LMStudioAPI
    
    # APIインスタンスの作成
    api = LMStudioAPI()
    
    # 要約インスタンスの作成
    summarizer = Summarizer(api)
    
    try:
        # 長いテキストの要約テスト
        long_text = """
人工知能（AI）の発展は、社会に大きな変革をもたらしています。機械学習、深層学習、自然言語処理などの技術の進歩により、AIは様々な分野で活用されるようになりました。
医療分野では、画像診断や創薬研究に活用され、診断精度の向上や新薬開発の効率化に貢献しています。自動運転技術では、センサーデータの解析や状況判断にAIが使われ、交通事故の削減や移動の効率化が期待されています。
また、ビジネスの世界では、顧客データの分析やマーケティング戦略の最適化、業務プロセスの自動化などにAIが導入され、生産性向上やコスト削減に寄与しています。
教育分野では、個々の学習者に合わせたパーソナライズド学習や、教育コンテンツの自動生成などにAIが活用され始めています。
一方で、AIの普及に伴い、プライバシーの問題、雇用への影響、意思決定の透明性、責任の所在など、様々な倫理的・社会的課題も浮上しています。
AIの発展と社会実装を健全に進めるためには、技術開発と並行して、これらの課題に対する議論や制度設計も重要です。多様なステークホルダーが参加する対話の場を設け、AIがもたらす恩恵を最大化しつつ、リスクを最小化する取り組みが求められています。
"""
        print(f"元のテキスト（{len(long_text)}文字）:\n{long_text}\n")
        
        # 100文字で要約
        summary_100 = await summarizer.summarize(long_text, 100)
        print(f"100文字要約（{len(summary_100)}文字）:\n{summary_100}\n")
        
        # 200文字で要約
        summary_200 = await summarizer.summarize(long_text, 200)
        print(f"200文字要約（{len(summary_200)}文字）:\n{summary_200}")
        
    finally:
        # セッションを閉じる
        await api.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_summarizer())

