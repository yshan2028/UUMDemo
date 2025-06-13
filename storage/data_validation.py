#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: data_validation.py
Author: yshan2028
Created: 2025-06-13 08:47:13
Description: 数据验证模块
"""

import re


class DataValidator:
    """数据验证器"""

    def validate_order(self, order_data: dict) -> tuple:
        """验证订单数据"""
        errors = []

        # 必需字段检查
        required_fields = ['order_id', 'customer_id', 'merchant_id', 'order_items', 'total_amount']
        for field in required_fields:
            if field not in order_data:
                errors.append(f"Missing required field: {field}")

        # 金额验证
        if 'total_amount' in order_data:
            try:
                amount = float(order_data['total_amount'])
                if amount <= 0:
                    errors.append("Total amount must be positive")
            except (ValueError, TypeError):
                errors.append("Invalid total_amount format")

        return len(errors) == 0, errors

    def validate_experiment_result(self, result_data: dict) -> tuple:
        """验证实验结果数据"""
        errors = []

        required_fields = ['experiment_id', 'algorithm_name']
        for field in required_fields:
            if field not in result_data:
                errors.append(f"Missing required field: {field}")

        return len(errors) == 0, errors