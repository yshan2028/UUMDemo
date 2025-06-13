#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: redis_cache.py
Author: yshan2028
Created: 2025-06-13 08:47:13
Description: Redis缓存实现
"""

import redis
import json
import logging
from config.settings import REDIS_CONFIG

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis缓存实现"""

    def __init__(self):
        self.redis_conn = None
        self._connect()

    def _connect(self):
        """连接Redis"""
        try:
            self.redis_conn = redis.Redis(**REDIS_CONFIG)
            self.redis_conn.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.error(f"Redis connection failed: {str(e)}")
            raise

    def set(self, key: str, value, expiry: int = 3600) -> bool:
        """设置缓存值"""
        try:
            serialized_value = json.dumps(value)
            self.redis_conn.setex(key, expiry, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Failed to set cache key {key}: {str(e)}")
            return False

    def get(self, key: str):
        """获取缓存值"""
        try:
            value = self.redis_conn.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Failed to get cache key {key}: {str(e)}")
            return None

    def close_connection(self):
        """关闭Redis连接"""
        try:
            if self.redis_conn:
                self.redis_conn.close()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {str(e)}")