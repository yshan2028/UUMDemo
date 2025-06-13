#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: preprocess_orders.py
Author: yshan2028
Created: 2025-06-13 08:47:13
Description: 数据预处理工具
"""

import json
from storage.data_validation import DataValidator


class OrderPreprocessor:
    """订单数据预处理器"""

    def __init__(self):
        self.validator = DataValidator()

    def preprocess_orders(self, orders: list) -> list:
        """预处理订单数据"""
        processed_orders = []

        for order in orders:
            # 验证数据
            is_valid, errors = self.validator.validate_order(order)

            if is_valid:
                # 标准化数据格式
                processed_order = self._normalize_order(order)
                processed_orders.append(processed_order)

        return processed_orders

    def _normalize_order(self, order: dict) -> dict:
        """标准化订单格式"""
        # 确保必要字段存在
        order.setdefault('currency', 'USD')
        order.setdefault('order_status', 'pending')
        order.setdefault('payment_status', 'pending')

        # 格式化金额
        if 'total_amount' in order:
            order['total_amount'] = round(float(order['total_amount']), 2)

        return order