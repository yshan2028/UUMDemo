#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: main.py
Author: yshan2028
Created: 2025-06-13 14:56:13
Description: 
    区块链隐私保护实验系统的主程序入口
    整合了区块链存储、隐私算法（Shamir秘密共享、Merkle树、零知识证明）
    和多种存储方案的综合实验平台，用于性能测试、隐私保护验证和对比分析

Dependencies:
    - config.settings: 实验参数配置
    - data.generate_orders: 订单数据生成器
    - blockchain: 区块链存储和交易管理模块
    - storage: MySQL和Redis存储模块
    - algorithms: 密码学算法模块（Shamir、Merkle树、零知识证明）
    - experiments: 实验测试模块

Usage:
    python main.py

    执行完整的区块链隐私保护实验流程：
    1. 生成模拟订单数据
    2. 初始化存储和算法模块
    3. 运行性能测试、隐私测试和对比测试
    4. 输出实验结果到results文件夹
"""

import logging
import sys
import traceback
from typing import Optional, Dict, Any
from datetime import datetime

from config.settings import EXPERIMENT_PARAMS
from data.generate_orders import OrderGenerator
from blockchain.blockchain_storage import BlockchainStorage
from blockchain.transaction_manager import TransactionManager
from storage.mysql_storage import MySQLStorage
from storage.redis_cache import RedisCache
from algorithms.shamir import ShamirSecretSharing
from algorithms.merkle_tree import MerkleTree
from algorithms.zk_proof import ZeroKnowledgeProof
from experiments.performance_test import run_performance_test
from experiments.privacy_test import run_privacy_test
from experiments.comparison_test import run_comparison_test


# 配置日志记录系统
def setup_logging() -> None:
    """
    配置实验系统的日志记录
    """
    log_format = "[%(asctime)s] %(levelname)s: %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(f'logs/experiment_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        ]
    )


def validate_experiment_config() -> bool:
    """
    验证实验配置参数的有效性

    Returns:
        bool: 配置是否有效
    """
    try:
        required_params = ['data_size', 'blockchain_type']
        for param in required_params:
            if param not in EXPERIMENT_PARAMS:
                logging.error(f"Missing required parameter: {param}")
                return False

        # 验证数据大小
        if EXPERIMENT_PARAMS['data_size'] <= 0:
            logging.error("Data size must be positive")
            return False

        logging.info("Experiment configuration validated successfully")
        return True

    except Exception as e:
        logging.error(f"Configuration validation failed: {str(e)}")
        return False


def initialize_storage_modules() -> Dict[str, Any]:
    """
    初始化所有存储模块

    Returns:
        Dict[str, Any]: 初始化的存储模块字典
    """
    storage_modules = {}

    try:
        # 区块链存储模块
        logging.info("Initializing blockchain storage...")
        storage_modules['blockchain'] = BlockchainStorage(EXPERIMENT_PARAMS["blockchain_type"])
        storage_modules['transaction_manager'] = TransactionManager(storage_modules['blockchain'])

        # 链下存储模块
        logging.info("Initializing off-chain storage modules...")
        storage_modules['mysql_storage'] = MySQLStorage()
        storage_modules['redis_cache'] = RedisCache()

        logging.info("All storage modules initialized successfully")
        return storage_modules

    except Exception as e:
        logging.error(f"Failed to initialize storage modules: {str(e)}")
        raise


def initialize_algorithm_modules() -> Dict[str, Any]:
    """
    初始化所有密码学算法模块

    Returns:
        Dict[str, Any]: 初始化的算法模块字典
    """
    algorithm_modules = {}

    try:
        logging.info("Initializing cryptographic algorithm modules...")

        # Shamir秘密共享算法
        algorithm_modules['shamir'] = ShamirSecretSharing()

        # Merkle树算法
        algorithm_modules['merkle_tree'] = MerkleTree()

        # 零知识证明算法
        algorithm_modules['zk_proof'] = ZeroKnowledgeProof()

        logging.info("All algorithm modules initialized successfully")
        return algorithm_modules

    except Exception as e:
        logging.error(f"Failed to initialize algorithm modules: {str(e)}")
        raise


def run_experiment_suite(orders: list, storage_modules: Dict[str, Any],
                         algorithm_modules: Dict[str, Any]) -> bool:
    """
    运行完整的实验测试套件

    Args:
        orders: 生成的订单数据
        storage_modules: 存储模块字典
        algorithm_modules: 算法模块字典

    Returns:
        bool: 实验是否成功完成
    """
    try:
        logging.info("Starting comprehensive experimental validation...")

        # 性能测试
        logging.info("Running performance tests...")
        run_performance_test(
            orders,
            storage_modules['blockchain'],
            algorithm_modules['shamir'],
            algorithm_modules['merkle_tree'],
            algorithm_modules['zk_proof']
        )

        # 隐私保护测试
        logging.info("Running privacy protection tests...")
        run_privacy_test(
            orders,
            storage_modules['blockchain'],
            storage_modules['transaction_manager'],
            storage_modules['mysql_storage'],
            storage_modules['redis_cache']
        )

        # 对比分析测试
        logging.info("Running comparative analysis tests...")
        run_comparison_test(
            orders,
            storage_modules['blockchain'],
            algorithm_modules['shamir'],
            algorithm_modules['zk_proof']
        )

        logging.info("All experimental tests completed successfully")
        return True

    except Exception as e:
        logging.error(f"Experiment suite failed: {str(e)}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        return False


def cleanup_resources(storage_modules: Optional[Dict[str, Any]] = None) -> None:
    """
    清理实验资源

    Args:
        storage_modules: 需要清理的存储模块
    """
    try:
        if storage_modules:
            logging.info("Cleaning up experiment resources...")

            # 清理数据库连接
            if 'mysql_storage' in storage_modules:
                storage_modules['mysql_storage'].close_connection()

            # 清理Redis连接
            if 'redis_cache' in storage_modules:
                storage_modules['redis_cache'].close_connection()

            logging.info("Resource cleanup completed")

    except Exception as e:
        logging.warning(f"Resource cleanup warning: {str(e)}")


def main() -> int:
    """
    区块链隐私保护实验系统主程序入口

    执行完整的实验流程：
    1. 环境初始化和配置验证
    2. 生成模拟订单数据
    3. 初始化存储和算法模块
    4. 运行实验测试套件
    5. 清理资源和生成报告

    Returns:
        int: 程序退出码 (0=成功, 1=失败)
    """
    storage_modules = None

    try:
        # 初始化日志系统
        setup_logging()

        logging.info("=" * 80)
        logging.info("BLOCKCHAIN PRIVACY PROTECTION EXPERIMENT SYSTEM")
        logging.info("=" * 80)
        logging.info("System startup initiated...")

        # 1. 验证实验配置
        logging.info("Step 1: Validating experiment configuration...")
        if not validate_experiment_config():
            logging.error("Configuration validation failed. Exiting...")
            return 1

        # 2. 生成实验数据
        logging.info("Step 2: Generating simulated order dataset...")
        orders = OrderGenerator.generate_orders(EXPERIMENT_PARAMS["data_size"])
        logging.info(f"Successfully generated {len(orders)} order records")

        # 3. 初始化系统模块
        logging.info("Step 3: Initializing system modules...")
        storage_modules = initialize_storage_modules()
        algorithm_modules = initialize_algorithm_modules()

        # 4. 执行实验测试套件
        logging.info("Step 4: Executing experiment test suite...")
        experiment_success = run_experiment_suite(orders, storage_modules, algorithm_modules)

        if not experiment_success:
            logging.error("Experiment suite execution failed")
            return 1

        # 5. 实验完成总结
        logging.info("Step 5: Experiment completion summary...")
        logging.info("=" * 80)
        logging.info("EXPERIMENT EXECUTION COMPLETED SUCCESSFULLY")
        logging.info("Results and performance metrics have been saved to the results directory")
        logging.info("Please check the generated reports for detailed analysis")
        logging.info("=" * 80)

        return 0

    except KeyboardInterrupt:
        logging.warning("Experiment interrupted by user (Ctrl+C)")
        return 1

    except Exception as e:
        logging.error(f"Fatal error in main execution: {str(e)}")
        logging.error(f"Full traceback: {traceback.format_exc()}")
        return 1

    finally:
        # 清理资源
        cleanup_resources(storage_modules)
        logging.info("System shutdown completed")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)