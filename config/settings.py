#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: settings.py
Author: yshan2028
Created: 2025-06-13 14:56:13
Description: 
    区块链隐私保护实验系统的配置文件
    包含实验参数、数据库配置、Hyperledger Fabric配置
    用于支持Shamir秘密共享、Merkle树、零知识证明的隐私保护实验

Dependencies:
    - os: 系统路径操作
    - typing: 类型注解支持

Usage:
    from config.settings import EXPERIMENT_PARAMS, MYSQL_CONFIG, FABRIC_CONFIG

    # 获取实验参数
    data_size = EXPERIMENT_PARAMS["data_size"]
    blockchain_type = EXPERIMENT_PARAMS["blockchain_type"]
"""

import os
from typing import Dict, Any, List, Union

# ========================================
# 实验核心参数配置
# ========================================

EXPERIMENT_PARAMS: Dict[str, Union[int, str, bool]] = {
    "data_size": 1000,  # 模拟订单数据量
    "blockchain_type": "Hyperledger",  # 区块链平台类型
    "shard_count": 5,  # Shamir秘密共享分片数量
    "threshold": 3,  # 恢复秘密所需的最小分片数
    "redis_cache_enabled": True,  # 是否启用Redis缓存
    "mysql_storage_enabled": True,  # 是否启用MySQL存储
    "test_iterations": 3,  # 实验测试迭代次数
    "batch_size": 100,  # 批处理大小
    "debug_mode": False,  # 调试模式
    "verbose_logging": True  # 详细日志记录
}

# ========================================
# 数据库配置
# ========================================

MYSQL_CONFIG: Dict[str, Union[str, int, bool]] = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "12345678",
    "database": "blockchain_privacy_experiment",
    "charset": "utf8mb4",
    "autocommit": True,
    "pool_size": 10,
    "pool_timeout": 30,
    "echo": False
}

REDIS_CONFIG: Dict[str, Union[str, int, bool, None]] = {
    "host": "localhost",
    "port": 6379,
    "password": None,
    "db": 0,
    "decode_responses": True,
    "socket_timeout": 5,
    "connection_pool_max_connections": 50
}

# ========================================
# Hyperledger Fabric配置
# ========================================

FABRIC_CONFIG: Dict[str, Any] = {
    # 网络基础配置
    "network_name": "privacy-network",
    "channel_name": "privacy-channel",
    "chaincode_name": "privacy-contract",
    "chaincode_version": "1.0",

    # 排序节点配置
    "orderer": {
        "name": "orderer.privacy.com",
        "endpoint": "localhost:7050"
    },

    # 组织配置
    "organizations": {
        "PrivacyOrg1": {
            "name": "PrivacyOrg1",
            "msp_id": "PrivacyOrg1MSP",
            "peers": [
                {
                    "name": "peer0.org1.privacy.com",
                    "endpoint": "localhost:7051",
                    "event_endpoint": "localhost:7053"
                }
            ]
        },
        "PrivacyOrg2": {
            "name": "PrivacyOrg2",
            "msp_id": "PrivacyOrg2MSP",
            "peers": [
                {
                    "name": "peer0.org2.privacy.com",
                    "endpoint": "localhost:8051",
                    "event_endpoint": "localhost:8053"
                }
            ]
        }
    },

    # 性能参数
    "timeout": 30,
    "retry_count": 3
}

# ========================================
# 算法配置
# ========================================

ALGORITHM_CONFIG: Dict[str, Dict[str, Any]] = {
    "shamir": {
        "prime_modulus": 2 ** 127 - 1,
        "polynomial_degree": EXPERIMENT_PARAMS["threshold"] - 1
    },
    "merkle_tree": {
        "hash_algorithm": "sha256",
        "leaf_encoding": "utf-8"
    },
    "zero_knowledge": {
        "proof_system": "groth16",
        "curve": "bn128"
    }
}

# ========================================
# 路径配置
# ========================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RESULTS_CONFIG: Dict[str, str] = {
    "base_path": os.path.join(BASE_DIR, "experiments", "results"),
    "performance_results": os.path.join(BASE_DIR, "experiments", "results", "performance"),
    "privacy_results": os.path.join(BASE_DIR, "experiments", "results", "privacy"),
    "comparison_results": os.path.join(BASE_DIR, "experiments", "results", "comparison"),
    "logs_path": os.path.join(BASE_DIR, "logs"),
    "data_path": os.path.join(BASE_DIR, "data", "generated")
}


def ensure_directories() -> None:
    """
    确保实验所需目录存在
    """
    for path in RESULTS_CONFIG.values():
        os.makedirs(path, exist_ok=True)


# ========================================
# 配置验证
# ========================================

def validate_configuration() -> bool:
    """
    验证实验配置参数的有效性

    Returns:
        bool: 配置是否有效
    """
    try:
        # 验证Shamir参数
        if EXPERIMENT_PARAMS["threshold"] > EXPERIMENT_PARAMS["shard_count"]:
            print("Error: Threshold cannot be greater than shard count")
            return False

        if EXPERIMENT_PARAMS["threshold"] < 2:
            print("Error: Threshold must be at least 2")
            return False

        # 验证数据大小
        if EXPERIMENT_PARAMS["data_size"] <= 0:
            print("Error: Data size must be positive")
            return False

        return True

    except Exception as e:
        print(f"Configuration validation error: {str(e)}")
        return False


# 初始化目录
ensure_directories()

# 向后兼容的导出
RESULTS_PATH = RESULTS_CONFIG["base_path"]
HYPERLEDGER_CONFIG = FABRIC_CONFIG