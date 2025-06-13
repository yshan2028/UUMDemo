#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: dynamic_access.py
Author: yshan2028
Created: 2025-06-13 08:47:13
Description: 动态权限管理模块
"""

import time
import logging
from enum import Enum
from typing import List

logger = logging.getLogger(__name__)


class AccessLevel(Enum):
    DENIED = 0
    READ = 1
    WRITE = 2
    DELETE = 3
    ADMIN = 4


class AccessResult:
    """访问结果类"""

    def __init__(self, granted: bool, access_level: AccessLevel, allowed_fields: List[str], reason: str):
        self.granted = granted
        self.access_level = access_level
        self.allowed_fields = allowed_fields
        self.reason = reason


class DynamicAccessControl:
    """动态访问控制系统"""

    def __init__(self):
        self.operations = 0
        self.total_time = 0.0

        self.role_permissions = {
            "merchant": {
                "operations": ["read", "update"],
                "accessible_fields": ["order_id", "product_list", "order_status", "order_time"],
                "forbidden_fields": ["customer_address", "payment_details"]
            },
            "logistics": {
                "operations": ["read", "update"],
                "accessible_fields": ["order_id", "shipping_address", "customer_phone", "logistics_status"],
                "forbidden_fields": ["payment_details", "product_price"]
            },
            "payment": {
                "operations": ["read", "update"],
                "accessible_fields": ["order_id", "transaction_amount", "payment_method", "payment_status"],
                "forbidden_fields": ["shipping_address", "customer_phone"]
            },
            "admin": {
                "operations": ["read", "write", "delete", "admin"],
                "accessible_fields": ["*"],
                "forbidden_fields": []
            }
        }

    def verify_access(self, user_id: str, role: str, resource_type: str, operation: str) -> AccessResult:
        """验证用户访问权限"""
        start_time = time.time()

        if role not in self.role_permissions:
            return AccessResult(False, AccessLevel.DENIED, [], f"Unknown role: {role}")

        role_config = self.role_permissions[role]
        allowed_operations = role_config.get("operations", [])

        if operation not in allowed_operations and "*" not in allowed_operations:
            return AccessResult(False, AccessLevel.DENIED, [], f"Operation not allowed: {operation}")

        access_level = AccessLevel.READ
        if operation in ["write", "update"]:
            access_level = AccessLevel.WRITE
        elif operation == "delete":
            access_level = AccessLevel.DELETE
        elif operation == "admin":
            access_level = AccessLevel.ADMIN

        allowed_fields = role_config.get("accessible_fields", [])
        self._update_stats(time.time() - start_time)

        return AccessResult(True, access_level, allowed_fields, "Access granted")

    def filter_data_fields(self, data: dict, user_role: str) -> dict:
        """根据用户角色过滤数据字段"""
        if user_role not in self.role_permissions:
            return {}

        role_config = self.role_permissions[user_role]
        accessible_fields = role_config.get("accessible_fields", [])
        forbidden_fields = role_config.get("forbidden_fields", [])

        filtered_data = {}

        if "*" in accessible_fields:
            for key, value in data.items():
                if key not in forbidden_fields:
                    filtered_data[key] = value
        else:
            for field in accessible_fields:
                if field in data and field not in forbidden_fields:
                    filtered_data[field] = data[field]

        return filtered_data

    def _update_stats(self, operation_time: float):
        """更新性能统计"""
        self.operations += 1
        self.total_time += operation_time