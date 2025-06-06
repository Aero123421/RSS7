#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Discordモジュール

Discordとの連携を行う
"""

from .bot_client import DiscordBot
from .commands import register_commands, set_managers
from .message_builder import MessageBuilder
from .ui_components import (
    ConfigView, AIModelSelect, CheckIntervalSelect,
    CategorySettingsModal, FeedListView, FeedSelect,
    AddFeedModal, RemoveFeedModal, ChannelListView, ChannelSelect
)

__all__ = [
    "DiscordBot",
    "register_commands",
    "set_managers",
    "MessageBuilder",
    "ConfigView",
    "AIModelSelect",
    "CheckIntervalSelect",
    "CategorySettingsModal",
    "FeedListView",
    "FeedSelect",
    "AddFeedModal",
    "RemoveFeedModal",
    "ChannelListView",
    "ChannelSelect"
]

