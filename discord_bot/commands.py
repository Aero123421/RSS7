#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Discordコマンド

Discordのスラッシュコマンドを定義する
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from .ui_components import ConfigView, FeedListView

logger = logging.getLogger(__name__)

# グローバル変数（コマンド間で共有するマネージャーインスタンス）
feed_manager = None
config_manager = None

def set_managers(feed_mgr, conf_mgr):
    """マネージャーインスタンスを設定する"""
    global feed_manager, config_manager
    feed_manager = feed_mgr
    config_manager = conf_mgr

async def register_commands(bot: commands.Bot, config: Dict[str, Any]):
    """
    スラッシュコマンドを登録する
    
    Args:
        bot: Botインスタンス
        config: 設定辞書
    """
    # コマンドグループの作成
    rss_group = app_commands.Group(name="rss", description="RSSフィード関連のコマンド")
    
    # コマンドの定義
    @rss_group.command(name="config", description="設定パネルを表示します")
    @app_commands.checks.has_permissions(administrator=True)
    async def rss_config(interaction: discord.Interaction):
        """設定パネルを表示するコマンド"""
        try:
            # 管理者権限チェック
            admin_ids = config.get("admin_ids", [])
            if admin_ids and str(interaction.user.id) not in admin_ids:
                await interaction.response.send_message(
                    "このコマンドを実行する権限がありません。サーバー管理者に連絡してください。",
                    ephemeral=True
                )
                return
            
            # 設定パネルの作成
            embed = discord.Embed(
                title="RSS Bot 設定パネル",
                description="以下のオプションから設定を変更できます。",
                color=discord.Color(config.get("embed_color", 3447003))
            )
            
            # 現在の設定を表示
            embed.add_field(
                name="現在の設定",
                value=f"AIモデル: {config.get('ai_model', 'gemini-2.0-flash')}\n"
                      f"確認間隔: {config.get('check_interval', 15)}分\n"
                      f"要約: {'有効' if config.get('summarize', True) else '無効'}\n"
                      f"ジャンル分類: {'有効' if config.get('classify', False) else '無効'}\n"
                      f"サムネイル: {'有効' if config.get('use_thumbnails', True) else '無効'}",
                inline=False
            )
            
            # 設定パネルの送信
            view = ConfigView(config, config_manager, feed_manager, interaction.guild)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            logger.error(f"設定パネル表示中にエラーが発生しました: {e}", exc_info=True)
            await interaction.response.send_message(
                f"エラーが発生しました: {str(e)}",
                ephemeral=True
            )
    
    @rss_group.command(name="check_now", description="このチャンネルの最新記事を取得します")
    async def rss_check_now(interaction: discord.Interaction):
        """チャンネルのフィードを1件取得して投稿する"""
        try:
            channel_id = str(interaction.channel.id)
            feed = next((f for f in feed_manager.get_feeds() if f.get("channel_id") == channel_id), None)
            if not feed:
                await interaction.response.send_message(
                    "このチャンネルにはフィードが登録されていません。",
                    ephemeral=True
                )
                return
            await interaction.response.send_message("最新記事を取得しています...", ephemeral=True)
            feed_data = await feed_manager.feed_parser.parse_feed(feed.get("url"))
            if not feed_data or not feed_data.get("entries"):
                await interaction.followup.send("記事を取得できませんでした。", ephemeral=True)
                return
            entry = feed_data["entries"][0]
            entry["feed_title"] = feed_data.get("feed", {}).get("title", "")
            entry["feed_url"] = feed.get("url")
            processed = await feed_manager.ai_processor.process_article(entry, feed)
            msg_id = await feed_manager.discord_bot.post_article(processed, channel_id)
            if msg_id:
                await feed_manager.article_store.add_full_article(
                    str(msg_id),
                    channel_id,
                    entry,
                    processed.get("keywords_en", ""),
                )
            await interaction.followup.send("記事を投稿しました。", ephemeral=True)
        except Exception as e:
            logger.error(f"フィード確認中にエラーが発生しました: {e}", exc_info=True)
            await interaction.followup.send(
                f"エラーが発生しました: {str(e)}",
                ephemeral=True
            )

    
    @rss_group.command(name="list_feeds", description="登録されているフィードの一覧を表示します")
    async def rss_list_feeds(interaction: discord.Interaction):
        """フィード一覧を表示するコマンド"""
        try:
            # フィードリストの取得
            feeds = feed_manager.get_feeds()
            
            if not feeds:
                await interaction.response.send_message(
                    "登録されているフィードはありません。",
                    ephemeral=True
                )
                return
            
            # Embedの作成
            embed = discord.Embed(
                title="登録フィード一覧",
                description=f"登録されているフィード: {len(feeds)}件",
                color=discord.Color(config.get("embed_color", 3447003))
            )
            
            # フィードリストビューの作成
            view = FeedListView(feeds, config, config_manager, feed_manager)
            
            # 応答の送信
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            logger.error(f"フィード一覧表示中にエラーが発生しました: {e}", exc_info=True)
            await interaction.response.send_message(
                f"エラーが発生しました: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="addrss", description="RSSフィードを追加します")
    @app_commands.describe(
        url="RSSフィードのURL",
        channel_name="チャンネル名（省略可）",
        existing_channel="既存のチャンネル",
        summary_length="要約の長さ"
    )
    @app_commands.choices(summary_length=[
        app_commands.Choice(name="短め", value="short"),
        app_commands.Choice(name="通常", value="normal"),
        app_commands.Choice(name="長め", value="long")
    ])
    async def add_rss(
        interaction: discord.Interaction,
        url: str,
        channel_name: str = None,
        existing_channel: discord.TextChannel = None,
        summary_length: str = "normal",
    ):
        """RSSフィードを追加するコマンド"""
        try:
            # 応答を送信
            await interaction.response.send_message(
                f"フィード「{url}」を追加しています...",
                ephemeral=True
            )
            
            # フィードの追加
            success, message, feed_info = await feed_manager.add_feed(
                url,
                summary_type=summary_length,
            )
            
            if not success:
                await interaction.followup.send(
                    f"フィードの追加に失敗しました: {message}",
                    ephemeral=True
                )
                return
            
            # チャンネルの作成または指定
            if existing_channel:
                channel_id = str(existing_channel.id)
            elif channel_name:
                # 既存のチャンネルを検索
                channel = discord.utils.get(interaction.guild.text_channels, name=channel_name)
                if not channel:
                    # チャンネルが存在しない場合は作成
                    channel_id = await feed_manager.discord_bot.create_feed_channel(
                        interaction.guild.id,
                        feed_info,
                        channel_name=channel_name,
                    )
                else:
                    channel_id = str(channel.id)
            else:
                # チャンネル名が指定されていない場合は自動作成
                channel_id = await feed_manager.discord_bot.create_feed_channel(
                    interaction.guild.id,
                    feed_info
                )
            
            # チャンネルIDをフィード情報に追加
            if channel_id:
                feed_info["channel_id"] = channel_id
                
                # 設定の保存
                config_manager.save_config()
                
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

    @rss_group.command(name="status", description="ボットのステータスを表示します")
    async def rss_status(interaction: discord.Interaction):
        """ステータスを表示するコマンド"""
        try:
            # ステータス情報の取得
            feeds_count = len(feed_manager.get_feeds())
            checking = feed_manager.checking
            
            # Embedの作成
            embed = discord.Embed(
                title="RSS Bot ステータス",
                color=discord.Color(config.get("embed_color", 3447003))
            )
            
            embed.add_field(name="登録フィード数", value=str(feeds_count), inline=True)
            embed.add_field(name="確認間隔", value=f"{config.get('check_interval', 15)}分", inline=True)
            embed.add_field(name="フィード確認中", value="はい" if checking else "いいえ", inline=True)
            embed.add_field(name="AIモデル", value=config.get("ai_model", "gemini-2.0-flash"), inline=True)
            embed.add_field(name="要約", value="有効" if config.get("summarize", True) else "無効", inline=True)
            
            # 最終更新日時
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            embed.set_footer(text=f"最終更新: {now}")
            
            # 応答の送信
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"ステータス表示中にエラーが発生しました: {e}", exc_info=True)
            await interaction.response.send_message(
                f"エラーが発生しました: {str(e)}",
                ephemeral=True
            )
    
    # コマンドグループをツリーに追加
    bot.tree.add_command(rss_group)
    
    # addrssコマンドをツリーに追加
    bot.tree.add_command(add_rss)
    
    # コマンドを同期
    guild_id = config.get("guild_id")
    if guild_id:
        # 特定のサーバーにのみコマンドを登録
        guild = discord.Object(id=int(guild_id))
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        logger.info(f"コマンドをサーバー {guild_id} に同期しました")
    else:
        # グローバルコマンドとして登録
        await bot.tree.sync()
        logger.info("コマンドをグローバルに同期しました")
    
    logger.info("すべてのコマンドを登録しました")

