#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
記事ストア

処理済み記事の管理を行う
"""

import os
import logging
import sqlite3
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

class ArticleStore:
    """処理済み記事管理クラス"""
    
    def __init__(self, db_path: str = None):
        """
        初期化
        
        Args:
            db_path: データベースファイルのパス（指定がない場合はデフォルト）
        """
        self.db_path = db_path or os.path.join("data", "processed_articles.db")
        self.lock = asyncio.Lock()  # 同時アクセス防止用ロック
        
        # データベースの初期化
        self._init_db()
    
    def _init_db(self) -> None:
        """データベースを初期化する"""
        try:
            # ディレクトリが存在するか確認
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # データベース接続
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # テーブル作成
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processed_articles (
                    article_id TEXT PRIMARY KEY,
                    feed_url TEXT NOT NULL,
                    channel_id TEXT NOT NULL,
                    processed_at TEXT NOT NULL
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    message_id TEXT PRIMARY KEY,
                    channel_id TEXT NOT NULL,
                    title TEXT,
                    content TEXT,
                    feed_url TEXT,
                    created_at TEXT NOT NULL
                )
            ''')

            cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_channel ON articles (channel_id)')
            
            # インデックス作成
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_feed_url ON processed_articles (feed_url)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_processed_at ON processed_articles (processed_at)')
            
            conn.commit()
            conn.close()
            
            logger.info(f"記事データベースを初期化しました: {self.db_path}")
            
        except Exception as e:
            logger.error(f"データベース初期化中にエラーが発生しました: {e}", exc_info=True)
    
    async def add_processed_article(self, article_id: str, feed_url: str, channel_id: str) -> bool:
        """
        処理済み記事を追加する
        
        Args:
            article_id: 記事ID
            feed_url: フィードURL
            channel_id: 投稿先チャンネルID
            
        Returns:
            追加成功の場合はTrue、失敗の場合はFalse
        """
        async with self.lock:
            try:
                # 現在時刻（ISO形式）
                now = datetime.now(timezone.utc).isoformat()
                
                # データベース接続
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, lambda: self._add_article(article_id, feed_url, channel_id, now))
                
                return True
                
            except Exception as e:
                logger.error(f"記事追加中にエラーが発生しました: {article_id}: {e}", exc_info=True)
                return False
    
    def _add_article(self, article_id: str, feed_url: str, channel_id: str, processed_at: str) -> None:
        """
        処理済み記事をデータベースに追加する（同期処理）
        
        Args:
            article_id: 記事ID
            feed_url: フィードURL
            channel_id: 投稿先チャンネルID
            processed_at: 処理日時（ISO形式）
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'INSERT OR REPLACE INTO processed_articles (article_id, feed_url, channel_id, processed_at) VALUES (?, ?, ?, ?)',
                (article_id, feed_url, channel_id, processed_at)
            )
            conn.commit()
            
        finally:
            conn.close()
    
    async def is_article_processed(self, article_id: str) -> bool:
        """
        記事が処理済みかどうかを確認する
        
        Args:
            article_id: 記事ID
            
        Returns:
            処理済みの場合はTrue、未処理の場合はFalse
        """
        async with self.lock:
            try:
                # データベース接続
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, lambda: self._check_article(article_id))
                
                return result
                
            except Exception as e:
                logger.error(f"記事確認中にエラーが発生しました: {article_id}: {e}", exc_info=True)
                return False
    
    def _check_article(self, article_id: str) -> bool:
        """
        記事がデータベースに存在するか確認する（同期処理）
        
        Args:
            article_id: 記事ID
            
        Returns:
            存在する場合はTrue、存在しない場合はFalse
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT 1 FROM processed_articles WHERE article_id = ?', (article_id,))
            result = cursor.fetchone() is not None
            return result
            
        finally:
            conn.close()
    
    async def get_processed_articles(self, feed_url: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        処理済み記事のリストを取得する
        
        Args:
            feed_url: フィードURL（指定した場合はそのフィードの記事のみ）
            limit: 取得する最大件数
            
        Returns:
            処理済み記事のリスト
        """
        async with self.lock:
            try:
                # データベース接続
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, lambda: self._get_articles(feed_url, limit))
                
                return result
                
            except Exception as e:
                logger.error(f"記事リスト取得中にエラーが発生しました: {e}", exc_info=True)
                return []
    
    def _get_articles(self, feed_url: Optional[str], limit: int) -> List[Dict[str, Any]]:
        """
        処理済み記事をデータベースから取得する（同期処理）
        
        Args:
            feed_url: フィードURL（指定した場合はそのフィードの記事のみ）
            limit: 取得する最大件数
            
        Returns:
            処理済み記事のリスト
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 辞書形式で結果を取得
        cursor = conn.cursor()
        
        try:
            if feed_url:
                cursor.execute(
                    'SELECT * FROM processed_articles WHERE feed_url = ? ORDER BY processed_at DESC LIMIT ?',
                    (feed_url, limit)
                )
            else:
                cursor.execute(
                    'SELECT * FROM processed_articles ORDER BY processed_at DESC LIMIT ?',
                    (limit,)
                )
            
            # 結果を辞書のリストに変換
            result = [dict(row) for row in cursor.fetchall()]
            return result
            
        finally:
            conn.close()
    
    async def cleanup_old_articles(self, days: int = 30) -> int:
        """
        古い記事を削除する
        
        Args:
            days: 保持する日数（これより古い記事は削除）
            
        Returns:
            削除された記事数
        """
        async with self.lock:
            try:
                # 基準日時
                cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
                
                # データベース接続
                loop = asyncio.get_event_loop()
                count = await loop.run_in_executor(None, lambda: self._delete_old_articles(cutoff_date))
                
                logger.info(f"{count}件の古い記事を削除しました")
                return count
                
            except Exception as e:
                logger.error(f"古い記事の削除中にエラーが発生しました: {e}", exc_info=True)
                return 0
    
    def _delete_old_articles(self, cutoff_date: str) -> int:
        """
        古い記事をデータベースから削除する（同期処理）
        
        Args:
            cutoff_date: 基準日時（ISO形式）
            
        Returns:
            削除された記事数
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM processed_articles WHERE processed_at < ?', (cutoff_date,))
            count = cursor.rowcount
            conn.commit()
            return count
            
        finally:
            conn.close()

    async def add_full_article(self, message_id: str, channel_id: str, article: Dict[str, Any], limit: int = 1000) -> bool:
        """記事全文を保存する"""
        async with self.lock:
            try:
                now = datetime.now(timezone.utc).isoformat()
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    lambda: self._add_full_article(message_id, channel_id, article, now, limit),
                )
                return True
            except Exception as e:
                logger.error(f"記事全文の保存中にエラーが発生しました: {e}", exc_info=True)
                return False

    def _add_full_article(self, message_id: str, channel_id: str, article: Dict[str, Any], created_at: str, limit: int) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT OR REPLACE INTO articles (message_id, channel_id, title, content, feed_url, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                (
                    message_id,
                    channel_id,
                    article.get("title"),
                    article.get("content"),
                    article.get("feed_url"),
                    created_at,
                ),
            )
            conn.commit()

            cursor.execute(
                'SELECT message_id FROM articles WHERE channel_id = ? ORDER BY created_at DESC',
                (channel_id,),
            )
            rows = cursor.fetchall()
            if len(rows) > limit:
                for mid, in rows[limit:]:
                    cursor.execute('DELETE FROM articles WHERE message_id = ?', (mid,))
            conn.commit()
        finally:
            conn.close()

    async def get_full_article(self, message_id: str) -> Optional[Dict[str, Any]]:
        """保存された記事を取得する"""
        async with self.lock:
            try:
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, lambda: self._get_full_article(message_id))
            except Exception as e:
                logger.error(f"記事取得中にエラーが発生しました: {e}", exc_info=True)
                return None

    def _get_full_article(self, message_id: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM articles WHERE message_id = ?', (message_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

