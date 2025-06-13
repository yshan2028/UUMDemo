#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: helpers.py
Author: yshan2028
Created: 2025-06-13 08:47:13
Description: 工具函数
"""

import hashlib
import time
import json
from typing import Any, Dict


def generate_id(prefix: str) -> str:
    """生成唯一ID"""
    timestamp = int(time.time() * 1000)
    return f"{prefix}_{timestamp}"


def hash_data(data: Any) -> str:
    """计算数据哈希"""
    if isinstance(data, dict):
        data_str = json.dumps(data, sort_keys=True)
    else:
        data_str = str(data)
    return hashlib.sha256(data_str.encode()).hexdigest()


def calculate_metrics(data_list: list) -> Dict[str, float]:
    """计算性能指标"""
    if not data_list:
        return {"avg": 0, "min": 0, "max": 0}

    return {
        "avg": sum(data_list) / len(data_list),
        "min": min(data_list),
        "max": max(data_list),
        "count": len(data_list)
    }