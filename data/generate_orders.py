#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: generate_orders.py
Author: yshan2028
Created: 2025-06-13 14:56:13
Description: 
    [请在此处添加文件描述]

Dependencies:
    [请在此处列出主要依赖]

Usage:
    [请在此处添加使用说明]
"""

import json
import random
import uuid
from datetime import datetime

class OrderGenerator:
    """
    用于生成模拟电子商务订单数据的类。
    """

    @staticmethod
    def generate_orders(order_count: int) -> list:
        """
        生成电子商务订单数据。

        :param order_count: 需要生成的订单数量。
        :return: 包含订单数据的列表。
        """
        orders = []
        for _ in range(order_count):
            order = {
                "order_id": str(uuid.uuid4()),
                "customer": {
                    "customer_id": str(uuid.uuid4()),
                    "name": f"Customer{random.randint(1, 1000)}",
                    "email": f"customer{random.randint(1, 1000)}@example.com"
                },
                "items": OrderGenerator._generate_items(),
                "payment": {
                    "method": random.choice(["Credit Card", "PayPal", "Bank Transfer"]),
                    "amount": round(random.uniform(20.0, 500.0), 2),
                    "status": random.choice(["Paid", "Pending", "Failed"])
                },
                "shipping_address": {
                    "street": f"{random.randint(1, 999)} Main Street",
                    "city": f"City{random.randint(1, 100)}",
                    "country": "CountryA"
                },
                "order_date": datetime.utcnow().isoformat(),
                "status": random.choice(["Processing", "Shipped", "Delivered", "Cancelled"])
            }
            orders.append(order)
        return orders

    @staticmethod
    def _generate_items() -> list:
        """
        生成订单中的商品列表。

        :return: 包含商品信息的列表。
        """
        items = []
        for _ in range(random.randint(1, 5)):  # 每个订单 1-5 个商品
            item = {
                "sku": f"SKU-{random.randint(1000, 9999)}",
                "name": f"Product-{random.randint(1, 50)}",
                "quantity": random.randint(1, 3),
                "price": round(random.uniform(5.0, 100.0), 2)
            }
            items.append(item)
        return items

    @staticmethod
    def save_to_file(orders: list, filename: str = "sample_orders.json"):
        """
        将生成的订单数据保存到文件。

        :param orders: 订单数据列表。
        :param filename: 保存文件的名称。
        """
        try:
            with open(filename, "w") as f:
                json.dump(orders, f, indent=4)
            print(f"[INFO] 订单数据已保存到文件: {filename}")
        except Exception as e:
            print(f"[ERROR] 保存订单数据失败: {e}")

if __name__ == "__main__":
    # 设置生成的订单数量
    order_count = 1000
    orders = OrderGenerator.generate_orders(order_count)
    OrderGenerator.save_to_file(orders)
