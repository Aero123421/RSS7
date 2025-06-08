#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Data API 連携

YouTubeの再生リストを取得するための簡易クライアント
"""

import aiohttp
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class YouTubeAPI:
    """YouTube Data API クライアント"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
        self.base_url = "https://www.googleapis.com/youtube/v3"

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def fetch_playlist(self, playlist_id: str, max_results: int = 10) -> Optional[Dict[str, Any]]:
        """プレイリストの動画情報を取得する"""
        params = {
            "part": "snippet",
            "playlistId": playlist_id,
            "maxResults": max_results,
            "key": self.api_key,
        }
        session = await self._get_session()
        async with session.get(f"{self.base_url}/playlistItems", params=params) as resp:
            if resp.status != 200:
                text = await resp.text()
                logger.error(f"YouTube API error: {resp.status} {text}")
                return None
            data = await resp.json()

        entries = []
        for item in data.get("items", []):
            sn = item.get("snippet", {})
            video_id = sn.get("resourceId", {}).get("videoId")
            if not video_id:
                continue
            entry = {
                "title": sn.get("title"),
                "link": f"https://www.youtube.com/watch?v={video_id}",
                "published": sn.get("publishedAt"),
                "author": sn.get("channelTitle"),
                "summary": sn.get("description", ""),
                "content": sn.get("description", ""),
                "media": [],
            }
            thumb = sn.get("thumbnails", {}).get("default", {})
            if thumb.get("url"):
                entry["image"] = thumb["url"]
            entries.append(entry)

        feed_title = "YouTube Playlist"
        if data.get("items"):
            feed_title = data["items"][0].get("snippet", {}).get("channelTitle", feed_title)

        return {"feed": {"title": feed_title}, "entries": entries}

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
