#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分布式任务系统集成模块
用于现有系统与分布式任务系统的集成
创建时间: 2025-09-17
"""

from .bridge_client import (
    DistributedTaskBridge,
    distributed_bridge,
    safe_delist_products_distributed
)

__all__ = [
    'DistributedTaskBridge',
    'distributed_bridge', 
    'safe_delist_products_distributed'
]
