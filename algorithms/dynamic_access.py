#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: dynamic_access.py
Author: yshan2028
Created: 2025-06-13 14:56:13
Description: 
    联盟链隐私保护实验中的动态访问控制模块
    实现基于角色的访问控制(RBAC)，支持商家、物流、客户三种角色
    用于验证不同角色对订单隐私数据的访问权限控制效果

Dependencies:
    - typing: 类型注解支持
    - logging: 访问控制日志记录

Usage:
    from access_control.dynamic_access import DynamicAccessControl

    # 创建访问控制实例
    access_control = DynamicAccessControl()

    # 验证权限
    can_access = access_control.can_access("merchant", "items")
"""

import logging
from typing import Dict, List, Optional

# 配置日志记录
logger = logging.getLogger(__name__)


class DynamicAccessControl:
    """
    动态访问控制系统

    实现基于角色的访问控制(RBAC)模型，用于论文实验中验证
    不同角色对订单隐私数据的访问权限控制效果
    """

    def __init__(self):
        """
        初始化动态访问控制系统
        """
        # 角色权限映射表 - 论文实验的核心配置
        self.permissions: Dict[str, List[str]] = {
            "merchant": [
                "items",  # 商品信息
                "order_amount",  # 订单金额
                "customer_contact"  # 客户联系方式
            ],
            "logistics": [
                "shipping_address",  # 配送地址
                "delivery_time",  # 配送时间
                "tracking_number"  # 快递单号
            ],
            "customer": [
                "order_status",  # 订单状态
                "payment_status",  # 支付状态
                "delivery_progress"  # 配送进度
            ]
        }

        # 访问统计 - 用于实验结果分析
        self.access_attempts: Dict[str, int] = {
            "total": 0,
            "granted": 0,
            "denied": 0
        }

        logger.info("Dynamic Access Control initialized for privacy experiment")

    def can_access(self, role: str, resource: str) -> bool:
        """
        验证角色是否有权限访问指定资源

        Args:
            role: 用户角色（merchant/logistics/customer）
            resource: 资源类型

        Returns:
            bool: 是否有访问权限
        """
        # 记录访问尝试
        self.access_attempts["total"] += 1

        # 检查角色权限
        allowed_resources = self.permissions.get(role, [])
        has_permission = resource in allowed_resources

        # 更新统计
        if has_permission:
            self.access_attempts["granted"] += 1
            logger.info(f"Access granted: {role} -> {resource}")
        else:
            self.access_attempts["denied"] += 1
            logger.warning(f"Access denied: {role} -> {resource}")

        return has_permission

    def get_role_permissions(self, role: str) -> List[str]:
        """
        获取指定角色的所有权限

        Args:
            role: 用户角色

        Returns:
            List[str]: 权限列表
        """
        return self.permissions.get(role, [])

    def get_access_statistics(self) -> Dict[str, int]:
        """
        获取访问控制统计信息

        Returns:
            Dict[str, int]: 访问统计数据
        """
        return self.access_attempts.copy()

    def reset_statistics(self) -> None:
        """
        重置访问统计数据
        """
        self.access_attempts = {
            "total": 0,
            "granted": 0,
            "denied": 0
        }
        logger.info("Access statistics reset")


def main():
    """
    动态访问控制实验演示
    """
    print("=" * 60)
    print("DYNAMIC ACCESS CONTROL EXPERIMENT")
    print("=" * 60)

    # 初始化访问控制系统
    access_control = DynamicAccessControl()

    # 实验测试用例
    print("\nTesting Role-Based Access Control:")
    print("-" * 40)

    test_cases = [
        ("merchant", "items"),
        ("merchant", "shipping_address"),  # Should be denied
        ("logistics", "shipping_address"),
        ("logistics", "items"),  # Should be denied
        ("customer", "order_status"),
        ("customer", "items")  # Should be denied
    ]

    for role, resource in test_cases:
        has_access = access_control.can_access(role, resource)
        status = "GRANTED" if has_access else "DENIED"
        print(f"{status}: {role} accessing {resource}")

    # 显示统计结果
    print(f"\nAccess Control Statistics:")
    print("-" * 40)
    stats = access_control.get_access_statistics()
    print(f"Total attempts: {stats['total']}")
    print(f"Granted: {stats['granted']}")
    print(f"Denied: {stats['denied']}")

    if stats['total'] > 0:
        success_rate = (stats['granted'] / stats['total']) * 100
        print(f"Success rate: {success_rate:.1f}%")

    print("=" * 60)


if __name__ == "__main__":
    main()