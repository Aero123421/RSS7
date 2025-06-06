#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
設定モジュール

設定の管理と読み込みを行う
"""

from .config_manager import ConfigManager
from .default_config import DEFAULT_CONFIG

__all__ = ["ConfigManager", "DEFAULT_CONFIG"]

