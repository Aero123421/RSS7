#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UIコンポーネント

Discordのボタン、セレクトメニュー、モーダルなどのUIコンポーネントを定義する
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional

import discord
from discord import ui

logger = logging.getLogger(__name__)

class ConfigView(ui.View):
    """設定パネルビュー"""
    
    def __init__(self, config: Dict[str, Any], config_manager):
        """
        初期化
        
        Args:
            config: 設定辞書
            config_manager: 設定マネージャーインスタンス
        """
        super().__init__(timeout=300)  # 5分でタイムアウト
        self.config = config
        self.config_manager = config_manager
        
        # AIプロバイダ選択メニューの追加
        self.add_item(AIProviderSelect(config))
        
        # 確認間隔選択メニューの追加
        self.add_item(CheckIntervalSelect(config))
    
    @ui.button(label="翻訳設定", style=discord.ButtonStyle.primary, custom_id="translate_toggle")
    async def translate_toggle(self, interaction: discord.Interaction, button: ui.Button):
        """翻訳設定ボタン"""
        # 現在の設定を反転
        current = self.config.get("translate", True)
        self.config["translate"] = not current
        
        # 設定を保存
        self.config_manager.update_config(self.config)
        
        # ボタンのラベルを更新
        button.label = f"翻訳: {'有効' if self.config['translate'] else '無効'}"
        
        # 応答を送信
        await interaction.response.edit_message(view=self)
    
    @ui.button(label="要約設定", style=discord.ButtonStyle.primary, custom_id="summarize_toggle")
    async def summarize_toggle(self, interaction: discord.Interaction, button: ui.Button):
        """要約設定ボタン"""
        # 現在の設定を反転
        current = self.config.get("summarize", True)
        self.config["summarize"] = not current
        
        # 設定を保存
        self.config_manager.update_config(self.config)
        
        # ボタンのラベルを更新
        button.label = f"要約: {'有効' if self.config['summarize'] else '無効'}"
        
        # 応答を送信
        await interaction.response.edit_message(view=self)
    
    @ui.button(label="ジャンル分類設定", style=discord.ButtonStyle.primary, custom_id="classify_toggle")
    async def classify_toggle(self, interaction: discord.Interaction, button: ui.Button):
        """ジャンル分類設定ボタン"""
        # 現在の設定を反転
        current = self.config.get("classify", False)
        self.config["classify"] = not current
        
        # 設定を保存
        self.config_manager.update_config(self.config)
        
        # ボタンのラベルを更新
        button.label = f"ジャンル分類: {'有効' if self.config['classify'] else '無効'}"
        
        # 応答を送信
        await interaction.response.edit_message(view=self)
    
    @ui.button(label="カテゴリ設定", style=discord.ButtonStyle.secondary, custom_id="category_settings")
    async def category_settings(self, interaction: discord.Interaction, button: ui.Button):
        """カテゴリ設定ボタン"""
        # カテゴリ設定モーダルを表示
        await interaction.response.send_modal(CategorySettingsModal(self.config, self.config_manager))
    
    @ui.button(label="閉じる", style=discord.ButtonStyle.danger, custom_id="close")
    async def close_button(self, interaction: discord.Interaction, button: ui.Button):
        """閉じるボタン"""
        # メッセージを削除
        await interaction.response.edit_message(content="設定パネルを閉じました", view=None, embed=None)

class AIProviderSelect(ui.Select):
    """AIプロバイダ選択メニュー"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初期化
        
        Args:
            config: 設定辞書
        """
        self.config = config
        
        # 現在の設定を取得
        current_provider = config.get("ai_provider", "lmstudio")
        
        # オプションの作成
        options = [
            discord.SelectOption(
                label="LM Studio",
                description="ローカルで動作するLLMを使用",
                value="lmstudio",
                default=current_provider == "lmstudio"
            ),
            discord.SelectOption(
                label="Google Gemini",
                description="Google Gemini APIを使用",
                value="gemini",
                default=current_provider == "gemini"
            )
        ]
        
        super().__init__(
            placeholder="AIプロバイダを選択",
            options=options,
            custom_id="ai_provider_select"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """選択時のコールバック"""
        # 選択された値を設定に反映
        self.config["ai_provider"] = self.values[0]
        
        # 設定を保存
        from config.config_manager import ConfigManager
        config_manager = ConfigManager()
        config_manager.update_config(self.config)
        
        # 応答を送信
        await interaction.response.send_message(
            f"AIプロバイダを「{self.values[0]}」に設定しました。",
            ephemeral=True
        )

class CheckIntervalSelect(ui.Select):
    """確認間隔選択メニュー"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初期化
        
        Args:
            config: 設定辞書
        """
        self.config = config
        
        # 現在の設定を取得
        current_interval = config.get("check_interval", 15)
        
        # オプションの作成
        options = [
            discord.SelectOption(
                label="5分ごと",
                description="5分ごとにフィードを確認",
                value="5",
                default=current_interval == 5
            ),
            discord.SelectOption(
                label="15分ごと",
                description="15分ごとにフィードを確認",
                value="15",
                default=current_interval == 15
            ),
            discord.SelectOption(
                label="30分ごと",
                description="30分ごとにフィードを確認",
                value="30",
                default=current_interval == 30
            ),
            discord.SelectOption(
                label="1時間ごと",
                description="1時間ごとにフィードを確認",
                value="60",
                default=current_interval == 60
            )
        ]
        
        super().__init__(
            placeholder="確認間隔を選択",
            options=options,
            custom_id="check_interval_select"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """選択時のコールバック"""
        # 選択された値を設定に反映
        self.config["check_interval"] = int(self.values[0])
        
        # 設定を保存
        from config.config_manager import ConfigManager
        config_manager = ConfigManager()
        config_manager.update_config(self.config)
        
        # 応答を送信
        await interaction.response.send_message(
            f"確認間隔を「{self.values[0]}分」に設定しました。",
            ephemeral=True
        )

class CategorySettingsModal(ui.Modal, title="カテゴリ設定"):
    """カテゴリ設定モーダル"""
    
    def __init__(self, config: Dict[str, Any], config_manager):
        """
        初期化
        
        Args:
            config: 設定辞書
            config_manager: 設定マネージャーインスタンス
        """
        super().__init__()
        self.config = config
        self.config_manager = config_manager
        
        # 現在のカテゴリ設定を取得
        categories = config.get("categories", [])
        category_str = ""
        
        for category in categories:
            name = category.get("name", "")
            jp_name = category.get("jp_name", "")
            emoji = category.get("emoji", "")
            category_str += f"{name},{jp_name},{emoji}\n"
        
        # テキスト入力フィールドの追加
        self.categories_input = ui.TextInput(
            label="カテゴリ設定（name,jp_name,emoji）",
            style=discord.TextStyle.paragraph,
            placeholder="technology,テクノロジー,🖥️\nbusiness,ビジネス,💼\n...",
            default=category_str,
            required=True
        )
        self.add_item(self.categories_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """送信時のコールバック"""
        try:
            # 入力値を解析
            categories = []
            lines = self.categories_input.value.strip().split("\n")
            
            for line in lines:
                if not line.strip():
                    continue
                
                parts = line.split(",")
                if len(parts) >= 3:
                    category = {
                        "name": parts[0].strip(),
                        "jp_name": parts[1].strip(),
                        "emoji": parts[2].strip()
                    }
                    categories.append(category)
            
            # 設定に反映
            self.config["categories"] = categories
            
            # 設定を保存
            self.config_manager.update_config(self.config)
            
            # 応答を送信
            await interaction.response.send_message(
                f"カテゴリ設定を更新しました。{len(categories)}個のカテゴリが設定されています。",
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"カテゴリ設定更新中にエラーが発生しました: {e}", exc_info=True)
            await interaction.response.send_message(
                f"エラーが発生しました: {str(e)}",
                ephemeral=True
            )

class FeedListView(ui.View):
    """フィードリストビュー"""
    
    def __init__(self, feeds: List[Dict[str, Any]], config: Dict[str, Any], config_manager, feed_manager):
        """
        初期化
        
        Args:
            feeds: フィードリスト
            config: 設定辞書
            config_manager: 設定マネージャーインスタンス
            feed_manager: フィードマネージャーインスタンス
        """
        super().__init__(timeout=300)  # 5分でタイムアウト
        self.feeds = feeds
        self.config = config
        self.config_manager = config_manager
        self.feed_manager = feed_manager
        
        # フィード選択メニューの追加
        if feeds:
            self.add_item(FeedSelect(feeds))
    
    @ui.button(label="フィード追加", style=discord.ButtonStyle.success, custom_id="add_feed")
    async def add_feed(self, interaction: discord.Interaction, button: ui.Button):
        """フィード追加ボタン"""
        # フィード追加モーダルを表示
        await interaction.response.send_modal(AddFeedModal(self.config, self.config_manager, self.feed_manager))
    
    @ui.button(label="フィード削除", style=discord.ButtonStyle.danger, custom_id="remove_feed")
    async def remove_feed(self, interaction: discord.Interaction, button: ui.Button):
        """フィード削除ボタン"""
        # フィード削除モーダルを表示
        await interaction.response.send_modal(RemoveFeedModal(self.config, self.config_manager, self.feed_manager))
    
    @ui.button(label="閉じる", style=discord.ButtonStyle.secondary, custom_id="close")
    async def close_button(self, interaction: discord.Interaction, button: ui.Button):
        """閉じるボタン"""
        # メッセージを削除
        await interaction.response.edit_message(content="フィードリストを閉じました", view=None, embed=None)

class FeedSelect(ui.Select):
    """フィード選択メニュー"""
    
    def __init__(self, feeds: List[Dict[str, Any]]):
        """
        初期化
        
        Args:
            feeds: フィードリスト
        """
        self.feeds = feeds
        
        # オプションの作成
        options = []
        for i, feed in enumerate(feeds[:25]):  # Discordの制限で最大25個まで
            title = feed.get("title", "Unknown Feed")
            url = feed.get("url", "")
            
            # タイトルが長すぎる場合は切り詰め
            if len(title) > 100:
                title = title[:97] + "..."
            
            options.append(
                discord.SelectOption(
                    label=title,
                    description=url[:100] if len(url) <= 100 else url[:97] + "...",
                    value=str(i)
                )
            )
        
        super().__init__(
            placeholder="フィードを選択して詳細を表示",
            options=options,
            custom_id="feed_select"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """選択時のコールバック"""
        # 選択されたフィードの取得
        index = int(self.values[0])
        feed = self.feeds[index]
        
        # Embedの作成
        embed = discord.Embed(
            title=feed.get("title", "Unknown Feed"),
            description=feed.get("description", "No description"),
            url=feed.get("url", ""),
            color=discord.Color(0x3498db)
        )
        
        # フィード情報の追加
        embed.add_field(name="URL", value=feed.get("url", ""), inline=False)
        embed.add_field(name="チャンネルID", value=feed.get("channel_id", "未設定"), inline=True)
        embed.add_field(name="最終更新", value=feed.get("last_updated", "未更新"), inline=True)
        
        # 応答を送信
        await interaction.response.send_message(embed=embed, ephemeral=True)

class AddFeedModal(ui.Modal, title="フィード追加"):
    """フィード追加モーダル"""
    
    def __init__(self, config: Dict[str, Any], config_manager, feed_manager):
        """
        初期化
        
        Args:
            config: 設定辞書
            config_manager: 設定マネージャーインスタンス
            feed_manager: フィードマネージャーインスタンス
        """
        super().__init__()
        self.config = config
        self.config_manager = config_manager
        self.feed_manager = feed_manager
        
        # テキスト入力フィールドの追加
        self.url_input = ui.TextInput(
            label="フィードURL",
            placeholder="https://example.com/rss",
            required=True
        )
        self.add_item(self.url_input)
        
        self.channel_input = ui.TextInput(
            label="チャンネル名（省略可）",
            placeholder="rss-feed",
            required=False
        )
        self.add_item(self.channel_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """送信時のコールバック"""
        # 応答を送信
        await interaction.response.send_message(
            f"フィード「{self.url_input.value}」を追加しています...",
            ephemeral=True
        )
        
        try:
            # フィードの追加
            success, message, feed_info = await self.feed_manager.add_feed(self.url_input.value)
            
            if not success:
                await interaction.followup.send(
                    f"フィードの追加に失敗しました: {message}",
                    ephemeral=True
                )
                return
            
            # チャンネルの作成または指定
            channel_name = self.channel_input.value
            if channel_name:
                # 既存のチャンネルを検索
                channel = discord.utils.get(interaction.guild.text_channels, name=channel_name)
                if not channel:
                    # チャンネルが存在しない場合は作成
                    channel_id = await self.feed_manager.discord_bot.create_feed_channel(
                        interaction.guild.id,
                        feed_info
                    )
                else:
                    channel_id = str(channel.id)
            else:
                # チャンネル名が指定されていない場合は自動作成
                channel_id = await self.feed_manager.discord_bot.create_feed_channel(
                    interaction.guild.id,
                    feed_info
                )
            
            # チャンネルIDをフィード情報に追加
            if channel_id:
                feed_info["channel_id"] = channel_id
                
                # 設定の保存
                self.config_manager.save_config()
                
                # チャンネルの取得
                channel = interaction.guild.get_channel(int(channel_id))
                
                # 完了メッセージを送信
                await interaction.followup.send(
                    f"フィード「{feed_info.get('title')}」を追加し、チャンネル {channel.mention if channel else channel_id} に関連付けました。",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"フィード「{feed_info.get('title')}」を追加しましたが、チャンネルの作成に失敗しました。",
                    ephemeral=True
                )
            
        except Exception as e:
            logger.error(f"フィード追加中にエラーが発生しました: {e}", exc_info=True)
            await interaction.followup.send(
                f"エラーが発生しました: {str(e)}",
                ephemeral=True
            )

class RemoveFeedModal(ui.Modal, title="フィード削除"):
    """フィード削除モーダル"""
    
    def __init__(self, config: Dict[str, Any], config_manager, feed_manager):
        """
        初期化
        
        Args:
            config: 設定辞書
            config_manager: 設定マネージャーインスタンス
            feed_manager: フィードマネージャーインスタンス
        """
        super().__init__()
        self.config = config
        self.config_manager = config_manager
        self.feed_manager = feed_manager
        
        # テキスト入力フィールドの追加
        self.url_input = ui.TextInput(
            label="削除するフィードURL",
            placeholder="https://example.com/rss",
            required=True
        )
        self.add_item(self.url_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """送信時のコールバック"""
        try:
            # フィードの削除
            success, message = self.feed_manager.remove_feed(self.url_input.value)
            
            if success:
                # 設定の保存
                self.config_manager.save_config()
                
                # 応答を送信
                await interaction.response.send_message(
                    f"フィード「{self.url_input.value}」を削除しました。",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"フィードの削除に失敗しました: {message}",
                    ephemeral=True
                )
            
        except Exception as e:
            logger.error(f"フィード削除中にエラーが発生しました: {e}", exc_info=True)
            await interaction.response.send_message(
                f"エラーが発生しました: {str(e)}",
                ephemeral=True
            )

class ChannelListView(ui.View):
    """チャンネルリストビュー"""
    
    def __init__(self, feeds: List[Dict[str, Any]], guild):
        """
        初期化
        
        Args:
            feeds: フィードリスト
            guild: サーバーインスタンス
        """
        super().__init__(timeout=300)  # 5分でタイムアウト
        self.feeds = feeds
        self.guild = guild
        
        # チャンネル情報の収集
        self.channels = {}
        for feed in feeds:
            channel_id = feed.get("channel_id")
            if channel_id:
                if channel_id not in self.channels:
                    self.channels[channel_id] = []
                self.channels[channel_id].append(feed)
        
        # チャンネル選択メニューの追加
        if self.channels:
            self.add_item(ChannelSelect(self.channels, self.guild))
    
    @ui.button(label="閉じる", style=discord.ButtonStyle.secondary, custom_id="close")
    async def close_button(self, interaction: discord.Interaction, button: ui.Button):
        """閉じるボタン"""
        # メッセージを削除
        await interaction.response.edit_message(content="チャンネルリストを閉じました", view=None, embed=None)

class ChannelSelect(ui.Select):
    """チャンネル選択メニュー"""
    
    def __init__(self, channels: Dict[str, List[Dict[str, Any]]], guild):
        """
        初期化
        
        Args:
            channels: チャンネルとフィードの対応辞書
            guild: サーバーインスタンス
        """
        self.channels = channels
        self.guild = guild
        
        # オプションの作成
        options = []
        for i, (channel_id, feeds) in enumerate(channels.items()[:25]):  # Discordの制限で最大25個まで
            channel = guild.get_channel(int(channel_id))
            channel_name = f"#{channel.name}" if channel else f"不明なチャンネル ({channel_id})"
            
            options.append(
                discord.SelectOption(
                    label=channel_name,
                    description=f"{len(feeds)}個のフィードが登録されています",
                    value=channel_id
                )
            )
        
        super().__init__(
            placeholder="チャンネルを選択して詳細を表示",
            options=options,
            custom_id="channel_select"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """選択時のコールバック"""
        # 選択されたチャンネルの取得
        channel_id = self.values[0]
        feeds = self.channels[channel_id]
        channel = self.guild.get_channel(int(channel_id))
        
        # Embedの作成
        embed = discord.Embed(
            title=f"チャンネル: #{channel.name if channel else '不明なチャンネル'}",
            description=f"このチャンネルには{len(feeds)}個のフィードが登録されています。",
            color=discord.Color(0x3498db)
        )
        
        # フィード情報の追加
        for i, feed in enumerate(feeds[:10]):  # 最大10個まで表示
            title = feed.get("title", "Unknown Feed")
            url = feed.get("url", "")
            
            embed.add_field(
                name=f"{i+1}. {title}",
                value=url,
                inline=False
            )
        
        # 応答を送信
        await interaction.response.send_message(embed=embed, ephemeral=True)

