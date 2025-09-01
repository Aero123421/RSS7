#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AIプロセッサーのテスト"""

import asyncio
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.summarizer import Summarizer
from ai.classifier import Classifier
from ai.simple_summarizer import simple_summarize


class DummyAPI:
    async def generate_text(
        self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, **kwargs
    ):
        return simple_summarize(prompt, max_tokens)

    async def close(self) -> None:
        pass


def test_ai_functions() -> None:
    """要約と分類が動作するかを確認する"""

    async def run() -> None:
        api = DummyAPI()
        summarizer = Summarizer(api)
        summary = await summarizer.summarize("test content", 200, "normal")
        assert isinstance(summary, str)
        assert summary

        classifier = Classifier(api)
        category = await classifier.classify("title", "content", ["technology", "other"])
        assert category in {"technology", "other"}
        await api.close()

    asyncio.run(run())
