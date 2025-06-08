import os
import sys
import unittest
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from discord_bot.message_builder import MessageBuilder

class TestMessageBuilder(unittest.TestCase):
    def setUp(self):
        self.config = {"use_thumbnails": True, "embed_color": 3447003, "categories": []}
        self.builder = MessageBuilder(self.config)

    def test_media_thumbnail_used(self):
        article = {
            "title": "Test",
            "link": "https://example.com",
            "content": "content",
            "media": [{"url": "https://example.com/image.jpg", "type": "image/jpeg"}]
        }
        embed = asyncio.get_event_loop().run_until_complete(
            self.builder.build_article_embed(article)
        )
        self.assertEqual(embed.thumbnail.url, "https://example.com/image.jpg")

if __name__ == "__main__":
    unittest.main()
