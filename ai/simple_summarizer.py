#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡易要約モジュール

外部APIが利用できない場合に備えたフォールバック要約を提供する
"""

import re


def simple_summarize(text: str, max_length: int = 200) -> str:
    """テキストを簡易的に要約する

    文ごとに区切り、指定された文字数内で先頭から詰め込む単純なアルゴリズムを用いる。
    文字数が超える場合は末尾を省略記号で切り詰める。
    """
    if not text:
        return ""

    sentences = re.split(r"(?<=[。.!?])\s+", text.strip())
    summary = ""
    for sentence in sentences:
        if len(summary) + len(sentence) <= max_length:
            summary += sentence
        else:
            if not summary:
                summary = sentence[:max_length]
            break
    if len(summary) > max_length:
        summary = summary[: max_length - 3] + "..."
    return summary.strip()
