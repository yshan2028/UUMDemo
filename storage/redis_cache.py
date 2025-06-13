#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: redis_cache.py
Author: yshan2028
Created: 2025-06-13 14:56:13
Description: 
    [请在此处添加文件描述]

Dependencies:
    [请在此处列出主要依赖]

Usage:
    [请在此处添加使用说明]
"""

import redis
import json
from decimal import Decimal

class RedisCache:
    """
    实现链下数据的 Redis 缓存逻辑。
    """

    def __init__(self, host="localhost", port=6379, db=0):
        """
        初始化 Redis 连接。

        :param host: Redis 主机地址。
        :param port: Redis 端口。
        :param db: Redis 数据库索引。
        """
        try:
            self.client = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True)
            print("[INFO] 成功连接到 Redis 缓存。")
        except redis.ConnectionError as e:
            print(f"[ERROR] 连接 Redis 失败: {e}")
            raise

    def _convert_to_serializable(self, data):
        """
        递归转换数据中的 Decimal 为 float 或其他可序列化类型。

        :param data: 要转换的字典或列表。
        :return: 转换后的数据。
        """
        if isinstance(data, dict):
            return {key: self._convert_to_serializable(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._convert_to_serializable(item) for item in data]
        elif isinstance(data, Decimal):
            return float(data)  # 或者 str(data)
        else:
            return data

    def set_item(self, key: str, value: dict, ttl: int = 3600):
        """
        设置缓存数据，仅缓存非空值。

        :param key: 缓存键。
        :param value: 缓存值（字典）。
        :param ttl: 数据的过期时间（秒）。
        """
        if value:  # 仅缓存非空数据
            try:
                serializable_value = self._convert_to_serializable(value)
                self.client.setex(key, ttl, json.dumps(serializable_value))
                print(f"[INFO] 数据已缓存，键: {key}")
            except redis.RedisError as e:
                print(f"[ERROR] 缓存数据失败: {e}")
        else:
            print(f"[INFO] 跳过空数据的缓存，键: {key}")

    def get_item(self, key: str) -> dict:
        """
        获取缓存数据。

        :param key: 缓存键。
        :return: 缓存的值（字典）。
        """
        try:
            value = self.client.get(key)
            return json.loads(value) if value else {}
        except redis.RedisError as e:
            print(f"[ERROR] 获取缓存数据失败: {e}")
            return {}

    def delete_item(self, key: str):
        """
        删除缓存数据。

        :param key: 缓存键。
        """
        try:
            self.client.delete(key)
            print(f"[INFO] 缓存数据已删除，键: {key}")
        except redis.RedisError as e:
            print(f"[ERROR] 删除缓存数据失败: {e}")

if __name__ == "__main__":
    # 测试 Redis 缓存功能
    redis_cache = RedisCache()

    # 模拟存储包含 Decimal 的数据
    sample_data = {"sku": "SKU1234", "price": Decimal("49.99"), "quantity": 10}
    redis_cache.set_item("SKU1234", sample_data)

    # 获取缓存数据
    cached_data = redis_cache.get_item("SKU1234")
    print("缓存数据:", cached_data)

    # 删除缓存数据
    redis_cache.delete_item("SKU1234")
