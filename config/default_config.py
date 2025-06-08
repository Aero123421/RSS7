#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
デフォルト設定

システムのデフォルト設定値を定義する
"""

# デフォルト設定
DEFAULT_CONFIG = {
    # Discord設定
    "discord_token": "",  # Discordボットトークン
    "guild_id": None,     # サーバーID（Noneの場合はグローバルコマンド）
    "admin_ids": [],      # 管理者ユーザーID
    "category_id": None,  # RSSチャンネルを作成するカテゴリID
    
    # RSS設定
    "feeds": [],          # フィードリスト
    "check_interval": 15, # フィード確認間隔（分）
    "max_articles": 5,    # 1回の確認で処理する最大記事数
    
    # AI設定
    "ai_provider": "lmstudio",  # AIプロバイダ（lmstudio or gemini）
    "fallback_ai_provider": "gemini",  # 予備のAIプロバイダ
    "lmstudio_api_url": "http://localhost:1234/v1",  # LM Studio API URL
    "gemini_api_key": "",  # Google Gemini API Key (旧形式)
    "gemini_api_keys": [],  # Gemini API Keyのリスト
    "ai_model": "lmstudio",  # 使用するAIモデル
                              # gemini-2.0-flash, gemini-2.5-flash-preview-05-20, lmstudio
    "summarize": True,     # 要約（翻訳を兼ねる）を有効にするか
    "summary_length": 4000, # 要約の最大文字数
    "classify": False,     # ジャンル分類を有効にするか
    
    # カテゴリ設定
    "categories": [
        {"name": "technology", "jp_name": "テクノロジー", "emoji": "🖥️"},
        {"name": "business", "jp_name": "ビジネス", "emoji": "💼"},
        {"name": "science", "jp_name": "科学", "emoji": "🔬"},
        {"name": "health", "jp_name": "健康", "emoji": "🏥"},
        {"name": "entertainment", "jp_name": "エンタメ", "emoji": "🎬"},
        {"name": "sports", "jp_name": "スポーツ", "emoji": "⚽"},
        {"name": "politics", "jp_name": "政治", "emoji": "🏛️"},
        {"name": "other", "jp_name": "その他", "emoji": "📌"}
    ],
    
    # UI設定
    "embed_color": 3447003,  # Embedのカラー（青色）
    "use_thumbnails": True,  # サムネイルを使用するか
    
    # ログ設定
    "log_level": "INFO",     # ログレベル
    "log_file": "data/bot.log"  # ログファイル
}

