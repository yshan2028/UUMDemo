#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: privacy_test.py
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
from storage.redis_cache import RedisCache
from algorithms.dynamic_access import DynamicAccessControl

def run_privacy_test(orders, blockchain, transaction_manager, mysql_storage: MySQLStorage, redis_cache: RedisCache):
    """
    运行隐私保护测试。

    :param orders: 模拟订单列表。
    :param blockchain: 区块链存储实例。
    :param transaction_manager: 交易管理模块实例。
    :param mysql_storage: MySQL 存储实例。
    :param redis_cache: Redis 缓存实例。
    """
    access_control = DynamicAccessControl()

    print("[INFO] 开始隐私保护测试...")
    for idx, order in enumerate(orders[:50]):  # 示例测试前 50 条订单
        roles = ["merchant", "logistics", "customer", "unauthorized"]
        resources = ["items", "shipping_address", "order_status"]

        for role in roles:
            print(f"[INFO] 测试角色: {role}")
            for resource in resources:
                can_access = access_control.can_access(role, resource)

                if can_access:
                    # 模拟访问链下存储
                    if resource == "items":
                        cached_data = redis_cache.get_item(order["order_id"])
                        if not cached_data:
                            # 如果 Redis 中未命中，尝试从 MySQL 加载数据
                            sku = order["items"][0]["sku"] if order["items"] else None
                            if sku:
                                cached_data = mysql_storage.fetch_item(sku)
                                if cached_data:
                                    redis_cache.set_item(order["order_id"], cached_data)
                            else:
                                print(f"[WARNING] 订单 {order['order_id']} 无 SKU 数据，跳过缓存。")

                        print(f"[隐私测试] {role} 访问 {resource}: {cached_data}")
                    elif resource == "shipping_address":
                        print(f"[隐私测试] {role} 访问 {resource}: {order['shipping_address']}")
                else:
                    print(f"[隐私测试] {role} 无权限访问 {resource}。")

        if idx % 10 == 0:
            print(f"[INFO] 隐私测试已处理订单数: {idx + 1}/{50}")
    print("[INFO] 隐私测试完成。")
