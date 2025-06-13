#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: generate_orders.py
Author: yshan2028
Created: 2025-06-13 08:47:13
Description: 模拟订单生成
"""

import random
import json
from datetime import datetime, timedelta
from utils.helpers import generate_id


class OrderGenerator:
    """订单数据生成器"""

    @staticmethod
    def generate_orders(count: int) -> list:
        """生成订单数据"""
        orders = []

        for i in range(count):
            order = {
                "order_id": generate_id("ORDER"),
                "customer_id": f"CUST_{random.randint(1000, 9999)}",
                "merchant_id": f"MERCH_{random.randint(100, 999)}",
                "logistics_id": f"LOG_{random.randint(100, 999)}",
                "order_items": [
                    {
                        "sku": f"ITEM_{random.randint(1000, 9999)}",
                        "quantity": random.randint(1, 5),
                        "price": round(random.uniform(10, 100), 2)
                    }
                ],
                "total_amount": round(random.uniform(50, 500), 2),
                "order_status": random.choice(["pending", "confirmed", "shipped", "delivered"]),
                "payment_status": random.choice(["pending", "paid"]),
                "created_at": datetime.now() - timedelta(days=random.randint(0, 30)),
                "privacy_requirements": {
                    "merchant_access": ["items", "amount"],
                    "logistics_access": ["address"],
                    "customer_access": ["status"]
                },
                "requires_secret_sharing": True,
                "shamir_threshold": random.randint(2, 4),
                "shamir_shares": random.randint(3, 6)
            }
            orders.append(order)

        return orders