#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: generate_users.py
Author: yshan2028
Created: 2025-06-13 09:10:06
Description: 用户数据生成器
"""

import random
from datetime import datetime, timedelta
from utils.helpers import generate_id


class UserGenerator:
    """用户数据生成器"""

    @staticmethod
    def generate_users(count: int) -> list:
        """生成用户数据"""
        users = []
        roles = ["merchant", "logistics", "customer", "admin"]
        organizations = ["TechCorp", "LogiFlow", "RetailMax", "AdminSys", "DataSecure", "SmartChain", "CryptoLogic"]

        # 确保每种角色都有足够的用户
        role_distribution = {
            "merchant": max(1, count // 4),
            "logistics": max(1, count // 4),
            "customer": max(1, count // 2),
            "admin": max(1, count // 10)
        }

        user_index = 1

        # 按角色分配生成用户
        for role, role_count in role_distribution.items():
            for i in range(role_count):
                if user_index > count:
                    break

                user = {
                    "user_id": f"USER_{user_index:04d}",
                    "username": f"{role}_{user_index:03d}",
                    "email": f"{role}{user_index}@{random.choice(['dvss.com', 'blockchain.org', 'privacy.net'])}",
                    "role": role,
                    "organization": random.choice(organizations),
                    "permissions": UserGenerator._generate_permissions(role),
                    "privacy_preferences": {
                        "data_sharing": random.choice([True, False]),
                        "analytics": role in ["admin", "merchant"],
                        "notifications": True,
                        "encryption_required": role in ["admin", "merchant"]
                    },
                    "zk_public_key": f"zk_key_{role}_{user_index}_{random.randint(1000, 9999)}",
                    "access_level": UserGenerator._get_access_level(role),
                    "last_login": UserGenerator._generate_last_login(),
                    "created_at": datetime.now() - timedelta(days=random.randint(1, 365))
                }
                users.append(user)
                user_index += 1

        # 如果还需要更多用户，随机生成剩余的
        while len(users) < count:
            role = random.choice(roles)
            user = {
                "user_id": f"USER_{user_index:04d}",
                "username": f"{role}_{user_index:03d}",
                "email": f"{role}{user_index}@{random.choice(['dvss.com', 'blockchain.org', 'privacy.net'])}",
                "role": role,
                "organization": random.choice(organizations),
                "permissions": UserGenerator._generate_permissions(role),
                "privacy_preferences": {
                    "data_sharing": random.choice([True, False]),
                    "analytics": role in ["admin", "merchant"],
                    "notifications": True,
                    "encryption_required": role in ["admin", "merchant"]
                },
                "zk_public_key": f"zk_key_{role}_{user_index}_{random.randint(1000, 9999)}",
                "access_level": UserGenerator._get_access_level(role),
                "last_login": UserGenerator._generate_last_login(),
                "created_at": datetime.now() - timedelta(days=random.randint(1, 365))
            }
            users.append(user)
            user_index += 1

        return users

    @staticmethod
    def _generate_permissions(role: str) -> dict:
        """根据角色生成权限"""
        base_permissions = {
            "merchant": {
                "read": True,
                "write": True,
                "delete": False,
                "admin": False,
                "access_orders": True,
                "access_products": True,
                "access_customers": False
            },
            "logistics": {
                "read": True,
                "write": True,
                "delete": False,
                "admin": False,
                "access_orders": True,
                "access_shipping": True,
                "access_tracking": True
            },
            "customer": {
                "read": True,
                "write": False,
                "delete": False,
                "admin": False,
                "access_own_orders": True,
                "access_public_info": True
            },
            "admin": {
                "read": True,
                "write": True,
                "delete": True,
                "admin": True,
                "access_all": True,
                "manage_users": True,
                "system_config": True
            }
        }
        return base_permissions.get(role, base_permissions["customer"])

    @staticmethod
    def _get_access_level(role: str) -> str:
        """根据角色获取访问级别"""
        levels = {
            "admin": "premium",
            "merchant": "standard",
            "logistics": "standard",
            "customer": "basic"
        }
        return levels.get(role, "basic")

    @staticmethod
    def _generate_last_login():
        """生成最后登录时间"""
        # 70%的用户在最近7天内登录过
        if random.random() < 0.7:
            return datetime.now() - timedelta(days=random.randint(0, 7))
        # 20%的用户在最近30天内登录过
        elif random.random() < 0.9:
            return datetime.now() - timedelta(days=random.randint(8, 30))
        # 10%的用户很久没登录
        else:
            return datetime.now() - timedelta(days=random.randint(31, 180))


def main():
    """用户生成器测试"""
    print("=" * 50)
    print("USER GENERATOR TEST")
    print("=" * 50)

    users = UserGenerator.generate_users(20)

    # 统计角色分布
    role_count = {}
    for user in users:
        role = user['role']
        role_count[role] = role_count.get(role, 0) + 1

    print(f"Generated {len(users)} users:")
    for role, count in role_count.items():
        print(f"  {role}: {count}")

    # 显示示例用户
    print("\nSample users:")
    for i, user in enumerate(users[:5]):
        print(f"  {i + 1}. {user['username']} ({user['role']}) - {user['organization']}")

    print("User generation test completed!")


if __name__ == "__main__":
    main()