#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: initialize_items.py
Author: yshan2028
Created: 2025-06-13 14:56:13
Description: 
    [请在此处添加文件描述]

Dependencies:
    [请在此处列出主要依赖]

Usage:
    [请在此处添加使用说明]
"""

from storage.mysql_storage import MySQLStorage

def initialize_items():
    """
    初始化商品数据到 MySQL 数据库，插入足够多的 SKU 数据。
    """
    mysql_storage = MySQLStorage()
    items = [
        {"sku": f"SKU-{i:04d}", "name": f"Product-{i}", "quantity": 100, "price": round(10 + i * 0.5, 2)}
        for i in range(1, 9999)  # 生成 1000 个 SKU
    ]

    for item in items:
        mysql_storage.save_item(item)

    mysql_storage.close()
    print("[INFO] 商品数据初始化完成，共插入 1000 个商品。")

if __name__ == "__main__":
    initialize_items()
