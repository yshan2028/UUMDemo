#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: helpers.py
Author: yshan2028
Created: 2025-06-13 14:56:13
Description: 
    [请在此处添加文件描述]

Dependencies:
    [请在此处列出主要依赖]

Usage:
    [请在此处添加使用说明]
"""

from datetime import datetime

def format_timestamp(timestamp: float) -> str:
    """
    格式化时间戳为可读字符串。

    :param timestamp: 时间戳。
    :return: 格式化后的时间字符串。
    """
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

def validate_order_data(order: dict) -> bool:
    """
    验证订单数据是否完整。

    :param order: 订单数据。
    :return: 验证结果（布尔值）。
    """
    required_keys = ["order_id", "payment", "items", "shipping_address"]
    for key in required_keys:
        if key not in order:
            return False
    return True

if __name__ == "__main__":
    # 测试工具函数
    print(format_timestamp(1672531199))
    print(validate_order_data({"order_id": "ORD001", "payment": {}, "items": [], "shipping_address": {}}))
