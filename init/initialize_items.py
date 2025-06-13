#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: initialize_items.py
Author: yshan2028
Created: 2025-06-13 14:56:13
Description: 
    DVSS-PPA实验系统的测试数据初始化模块
    用于生成和初始化区块链隐私保护实验所需的模拟商品数据
    支持批量生成SKU商品信息，为隐私保护算法测试提供数据基础
    集成MySQL存储和Redis缓存的数据预载功能

Dependencies:
    - storage.mysql_storage: MySQL数据存储模块
    - storage.redis_cache: Redis缓存存储模块  # 修改了模块名
    - random: 随机数据生成
    - logging: 初始化过程日志记录
    - typing: 类型注解支持

Usage:
    from data.initialize_items import DVSSPPADataInitializer

    # 创建数据初始化器
    initializer = DVSSPPADataInitializer()

    # 初始化实验数据
    initializer.initialize_experiment_data()

    # 或直接运行脚本
    python initialize_items.py
"""

import random
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

# 配置日志记录
logger = logging.getLogger(__name__)


class DVSSPPADataInitializer:
    """
    DVSS-PPA实验数据初始化器

    负责生成和初始化区块链隐私保护实验所需的各类测试数据：
    - 商品SKU数据
    - 订单交易数据
    - 用户角色数据
    - 隐私保护测试场景数据
    """

    def __init__(self, item_count: int = 1000):
        """
        初始化数据生成器

        Args:
            item_count: 要生成的商品数量
        """
        self.item_count = item_count
        self.mysql_storage = None
        self.redis_cache = None  # 修改变量名以匹配模块
        self.initialized_data_count = 0

        # 商品类别配置
        self.product_categories = [
            "Electronics", "Clothing", "Books", "Home", "Sports",
            "Beauty", "Automotive", "Toys", "Food", "Health"
        ]

        # 用户角色配置
        self.user_roles = ["merchant", "logistics", "customer"]

        logger.info(f"DVSS-PPA Data Initializer created for {item_count} items")

    def _initialize_storage(self):
        """
        初始化存储连接
        """
        try:
            from storage.mysql_storage import MySQLStorage
            from storage.redis_cache import RedisCache  # 修改导入模块名

            self.mysql_storage = MySQLStorage()
            self.redis_cache = RedisCache()  # 修改变量名

            logger.info("Storage connections initialized successfully")

        except ImportError as e:
            logger.warning(f"Storage module not available: {str(e)}")
            print(f"Warning: Storage module not available, using mock storage")
        except Exception as e:
            logger.error(f"Failed to initialize storage: {str(e)}")
            print(f"Error: Failed to initialize storage: {str(e)}")

    def generate_product_items(self) -> List[Dict[str, Any]]:
        """
        生成商品SKU数据

        Returns:
            List[Dict[str, Any]]: 商品数据列表
        """
        items = []

        print(f"Generating {self.item_count} product items for DVSS-PPA experiment...")

        for i in range(1, self.item_count + 1):
            # 生成SKU编号
            sku = f"DVSS-SKU-{i:06d}"

            # 随机选择商品类别
            category = random.choice(self.product_categories)

            # 生成商品名称
            product_name = f"{category}-Product-{i:04d}"

            # 生成商品属性
            item = {
                "sku": sku,
                "name": product_name,
                "category": category,
                "quantity": random.randint(10, 500),
                "price": round(random.uniform(9.99, 999.99), 2),
                "cost": round(random.uniform(5.00, 500.00), 2),
                "weight": round(random.uniform(0.1, 50.0), 2),
                "dimensions": {
                    "length": round(random.uniform(5, 100), 1),
                    "width": round(random.uniform(5, 100), 1),
                    "height": round(random.uniform(5, 100), 1)
                },
                "description": f"High-quality {category.lower()} product for testing DVSS-PPA privacy protection",
                "supplier_id": f"SUP-{random.randint(1000, 9999)}",
                "created_at": datetime.now().isoformat(),
                "privacy_level": random.choice(["public", "internal", "confidential"]),
                "requires_zk_proof": random.choice([True, False])
            }

            items.append(item)

            # 显示进度
            if i % 100 == 0:
                progress = (i / self.item_count) * 100
                print(f"Progress: {progress:.1f}% - Generated {i} items")

        logger.info(f"Generated {len(items)} product items")
        return items

    def generate_order_data(self, order_count: int = 500) -> List[Dict[str, Any]]:
        """
        生成订单交易数据

        Args:
            order_count: 订单数量

        Returns:
            List[Dict[str, Any]]: 订单数据列表
        """
        orders = []

        print(f"Generating {order_count} order transactions...")

        for i in range(1, order_count + 1):
            # 生成订单基本信息
            order_id = f"ORDER-{datetime.now().strftime('%Y%m%d')}-{i:06d}"

            # 生成订单详情
            item_count = random.randint(1, 5)
            total_amount = 0
            order_items = []

            for j in range(item_count):
                sku = f"DVSS-SKU-{random.randint(1, self.item_count):06d}"
                quantity = random.randint(1, 10)
                unit_price = round(random.uniform(9.99, 999.99), 2)
                subtotal = quantity * unit_price
                total_amount += subtotal

                order_items.append({
                    "sku": sku,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "subtotal": subtotal
                })

            # 生成订单数据
            order = {
                "order_id": order_id,
                "customer_id": f"CUST-{random.randint(10000, 99999)}",
                "merchant_id": f"MERCH-{random.randint(1000, 9999)}",
                "logistics_id": f"LOG-{random.randint(100, 999)}",
                "order_items": order_items,
                "total_amount": round(total_amount, 2),
                "currency": "USD",
                "order_status": random.choice(["pending", "confirmed", "shipped", "delivered"]),
                "payment_status": random.choice(["pending", "paid", "failed"]),
                "shipping_address": {
                    "street": f"Test Street {random.randint(1, 999)}",
                    "city": random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]),
                    "state": random.choice(["NY", "CA", "IL", "TX", "AZ"]),
                    "zip_code": f"{random.randint(10000, 99999)}",
                    "country": "USA"
                },
                "created_at": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
                "privacy_requirements": {
                    "merchant_access": ["items", "order_amount", "customer_contact"],
                    "logistics_access": ["shipping_address", "delivery_time", "tracking_number"],
                    "customer_access": ["order_status", "payment_status", "delivery_progress"]
                },
                "requires_secret_sharing": True,
                "shamir_threshold": random.randint(2, 3),
                "shamir_shares": random.randint(3, 5),
                # 添加可能需要的字段，避免数据库插入错误
                "merkle_root": None,
                "zk_proof_hash": None
            }

            orders.append(order)

            # 显示进度
            if i % 50 == 0:
                progress = (i / order_count) * 100
                print(f"Order generation progress: {progress:.1f}% - Generated {i} orders")

        logger.info(f"Generated {len(orders)} order transactions")
        return orders

    def generate_user_data(self, user_count: int = 200) -> List[Dict[str, Any]]:
        """
        生成用户角色数据

        Args:
            user_count: 用户数量

        Returns:
            List[Dict[str, Any]]: 用户数据列表
        """
        users = []

        print(f"Generating {user_count} user accounts...")

        for i in range(1, user_count + 1):
            # 随机分配角色
            role = random.choice(self.user_roles)

            # 生成用户ID
            if role == "merchant":
                user_id = f"MERCH-{i:04d}"
                organization = random.choice(["PrivacyOrg1", "PrivacyOrg2", "PrivacyOrg3"])
            elif role == "logistics":
                user_id = f"LOG-{i:04d}"
                organization = random.choice(["PrivacyOrg2", "PrivacyOrg3"])
            else:  # customer
                user_id = f"CUST-{i:05d}"
                organization = random.choice(["PrivacyOrg1", "PrivacyOrg2", "PrivacyOrg3"])

            user = {
                "user_id": user_id,
                "username": f"user_{i:05d}",
                "email": f"user{i}@dvssppa-test.com",
                "role": role,
                "organization": organization,
                "permissions": self._get_role_permissions(role),
                "created_at": datetime.now().isoformat(),
                "last_login": (datetime.now() - timedelta(days=random.randint(0, 7))).isoformat(),
                "privacy_preferences": {
                    "data_sharing_consent": random.choice([True, False]),
                    "analytics_consent": random.choice([True, False]),
                    "marketing_consent": random.choice([True, False])
                },
                "zk_public_key": f"zk_pub_{random.randint(100000, 999999)}",
                "access_level": random.choice(["basic", "standard", "premium"])
            }

            users.append(user)

        logger.info(f"Generated {len(users)} user accounts")
        return users

    def _get_role_permissions(self, role: str) -> List[str]:
        """
        获取角色权限列表

        Args:
            role: 用户角色

        Returns:
            List[str]: 权限列表
        """
        permissions_map = {
            "merchant": ["items", "order_amount", "customer_contact", "inventory_management"],
            "logistics": ["shipping_address", "delivery_time", "tracking_number", "route_optimization"],
            "customer": ["order_status", "payment_status", "delivery_progress", "order_history"]
        }

        return permissions_map.get(role, [])

    def save_to_storage(self, data_type: str, data: List[Dict[str, Any]]) -> bool:
        """
        保存数据到存储系统

        Args:
            data_type: 数据类型 ("items", "orders", "users")
            data: 要保存的数据

        Returns:
            bool: 保存是否成功
        """
        try:
            if self.mysql_storage is None:
                print("Mock storage: Simulating data save operation")
                print(f"Would save {len(data)} {data_type} records to MySQL")
                return True

            save_count = 0

            for item in data:
                try:
                    if data_type == "items":
                        success = self.mysql_storage.save_item(item)
                    elif data_type == "orders":
                        success = self.mysql_storage.save_order(item)
                    elif data_type == "users":
                        success = self.mysql_storage.save_user(item)
                    else:
                        continue

                    if success:  # 只有成功时才计数
                        save_count += 1

                    # 显示保存进度
                    if save_count % 100 == 0:
                        progress = (save_count / len(data)) * 100
                        print(f"Saving {data_type}: {progress:.1f}% - Saved {save_count} records")

                except Exception as e:
                    logger.error(f"Failed to save {data_type} record: {str(e)}")
                    continue

            self.initialized_data_count += save_count
            logger.info(f"Successfully saved {save_count} {data_type} records")
            print(f"Successfully saved {save_count} {data_type} records to MySQL")

            return save_count > 0  # 只要有保存成功的就返回True

        except Exception as e:
            logger.error(f"Failed to save {data_type} data: {str(e)}")
            print(f"Error saving {data_type} data: {str(e)}")
            return False

    def initialize_experiment_data(self) -> bool:
        """
        初始化完整的实验数据集

        Returns:
            bool: 初始化是否成功
        """
        try:
            print("=" * 60)
            print("DVSS-PPA EXPERIMENT DATA INITIALIZATION")
            print("=" * 60)

            # 初始化存储连接
            self._initialize_storage()

            # 1. 生成并保存商品数据
            print(f"\n1. Initializing product items...")
            items = self.generate_product_items()
            items_saved = self.save_to_storage("items", items)

            # 2. 生成并保存订单数据
            print(f"\n2. Initializing order transactions...")
            orders = self.generate_order_data(500)
            orders_saved = self.save_to_storage("orders", orders)

            # 3. 生成并保存用户数据
            print(f"\n3. Initializing user accounts...")
            users = self.generate_user_data(200)
            users_saved = self.save_to_storage("users", users)

            # 4. 缓存热点数据到Redis
            if self.redis_cache:  # 修改变量名
                print(f"\n4. Caching hot data to Redis...")
                self._cache_hot_data(items[:100], orders[:50])

            # 关闭存储连接
            if self.mysql_storage:
                self.mysql_storage.close()
            if self.redis_cache:  # 修改变量名
                self.redis_cache.close()

            # 显示总结
            print(f"\n" + "=" * 60)
            print("INITIALIZATION SUMMARY")
            print("=" * 60)
            print(f"Product items: {len(items)} generated, {len(items) if items_saved else 0} saved")
            print(f"Order transactions: {len(orders)} generated, {len(orders) if orders_saved else 0} saved")
            print(f"User accounts: {len(users)} generated, {len(users) if users_saved else 0} saved")
            print(f"Total records initialized: {self.initialized_data_count}")
            print(f"Initialization status: {'SUCCESS' if all([items_saved, orders_saved, users_saved]) else 'PARTIAL'}")
            print("=" * 60)

            logger.info("DVSS-PPA experiment data initialization completed")

            return all([items_saved, orders_saved, users_saved])

        except Exception as e:
            logger.error(f"Experiment data initialization failed: {str(e)}")
            print(f"Error during initialization: {str(e)}")
            return False

    def _cache_hot_data(self, items: List[Dict], orders: List[Dict]):
        """
        缓存热点数据到Redis

        Args:
            items: 热点商品数据
            orders: 热点订单数据
        """
        try:
            # 缓存热点商品
            for item in items:
                cache_key = f"hot_item:{item['sku']}"
                self.redis_cache.set_item(cache_key, item, 3600)  # 修改方法名

            # 缓存热点订单
            for order in orders:
                cache_key = f"hot_order:{order['order_id']}"
                self.redis_cache.set_item(cache_key, order, 1800)  # 修改方法名

            print(f"Cached {len(items)} items and {len(orders)} orders to Redis")

        except Exception as e:
            logger.error(f"Failed to cache hot data: {str(e)}")
            print(f"Warning: Failed to cache hot data: {str(e)}")


def initialize_items():
    """
    初始化商品数据（向后兼容函数）
    """
    initializer = DVSSPPADataInitializer(item_count=1000)

    print("Initializing DVSS-PPA experiment items...")

    # 初始化存储连接
    initializer._initialize_storage()

    items = initializer.generate_product_items()
    success = initializer.save_to_storage("items", items)

    # 关闭连接
    if initializer.mysql_storage:
        initializer.mysql_storage.close()

    if success:
        print(f"SUCCESS: Initialized {len(items)} product items for DVSS-PPA experiment")
    else:
        print("ERROR: Failed to initialize product items")

    return success


def main():
    """
    主函数 - 运行完整的数据初始化
    """
    # 创建数据初始化器
    initializer = DVSSPPADataInitializer(item_count=1000)

    # 执行完整的数据初始化
    success = initializer.initialize_experiment_data()

    if success:
        print("\nDVSS-PPA experiment data initialization completed successfully!")
    else:
        print("\nDVSS-PPA experiment data initialization failed!")

    return success


if __name__ == "__main__":
    main()