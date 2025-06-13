#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: preprocess_orders.py
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

class OrderPreprocessor:
    """
    对订单数据进行清洗和预处理的类。
    """

    @staticmethod
    def load_from_file(filename: str) -> list:
        """
        从文件加载订单数据。

        :param filename: 文件名。
        :return: 订单数据列表。
        """
        try:
            with open(filename, "r") as f:
                orders = json.load(f)
            return orders
        except Exception as e:
            print(f"[ERROR] 加载订单数据失败: {e}")
            return []

    @staticmethod
    def remove_duplicates(orders: list) -> list:
        """
        去重订单数据。

        :param orders: 订单数据列表。
        :return: 去重后的订单数据。
        """
        unique_orders = {order["order_id"]: order for order in orders}
        return list(unique_orders.values())

    @staticmethod
    def fill_missing_data(orders: list) -> list:
        """
        填补订单数据中的缺失字段。

        :param orders: 订单数据列表。
        :return: 填补后的订单数据。
        """
        for order in orders:
            if "status" not in order:
                order["status"] = "Unknown"
            if "payment" not in order or "amount" not in order["payment"]:
                order["payment"] = {"amount": 0.0, "method": "Unknown", "status": "Pending"}
        return orders

    @staticmethod
    def preprocess_orders(orders: list) -> list:
        """
        对订单数据进行完整的预处理，包括去重和填补缺失数据。

        :param orders: 订单数据列表。
        :return: 预处理后的订单数据。
        """
        orders = OrderPreprocessor.remove_duplicates(orders)
        orders = OrderPreprocessor.fill_missing_data(orders)
        return orders

    @staticmethod
    def save_to_file(orders: list, filename: str = "processed_orders.json"):
        """
        将预处理后的订单数据保存到文件。

        :param orders: 订单数据列表。
        :param filename: 保存文件的名称。
        """
        try:
            with open(filename, "w") as f:
                json.dump(orders, f, indent=4)
            print(f"[INFO] 预处理订单数据已保存到文件: {filename}")
        except Exception as e:
            print(f"[ERROR] 保存预处理订单数据失败: {e}")

if __name__ == "__main__":
    # 加载订单数据并预处理
    raw_orders_file = "sample_orders.json"
    processed_orders_file = "processed_orders.json"

    raw_orders = OrderPreprocessor.load_from_file(raw_orders_file)
    processed_orders = OrderPreprocessor.preprocess_orders(raw_orders)
    OrderPreprocessor.save_to_file(processed_orders, processed_orders_file)
