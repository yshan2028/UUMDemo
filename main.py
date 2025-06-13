#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: main.py
Author: yshan2028
Created: 2025-06-13 09:15:35
Description: 
    区块链隐私保护实验系统的主程序入口
    整合了区块链存储、隐私算法和多种存储方案的综合实验平台
    支持用户、商品、订单等完整数据集生成和实验
"""

import logging
import sys
import traceback
from datetime import datetime

from algorithms.role_based_access import demonstrate_role_access_system
# 导入配置和核心模块
from config.settings import EXPERIMENT_PARAMS, validate_configuration
from utils.logger import setup_logging
from data.generate_orders import OrderGenerator
from data.generate_users import UserGenerator
from data.generate_items import ItemGenerator
from storage.mysql_storage import MySQLStorage
from storage.redis_cache import RedisCache
from blockchain.blockchain_storage import BlockchainStorage
from blockchain.transaction_manager import TransactionManager
from algorithms.shamir import ShamirSecretSharing
from algorithms.merkle_tree import MerkleTree
from algorithms.zk_proof import ZeroKnowledgeProof
from algorithms.dynamic_access import DynamicAccessControl
from experiments.performance_test import run_performance_test
from experiments.privacy_test import run_privacy_test
from experiments.attack_simulation import run_attack_simulation
from experiments.comparison_test import run_comparison_test
from experiments.throughput_test import run_throughput_test
from analysis.generate_report import generate_comprehensive_report


def generate_complete_dataset():
    """生成完整的实验数据集"""
    logging.info("Generating comprehensive experiment dataset...")

    # 生成用户数据
    logging.info("👥 Generating user data...")
    users = UserGenerator.generate_users(1000)  # 生成100个用户
    logging.info(f"✅ Generated {len(users)} users")

    # 统计用户角色分布
    role_stats = {}
    for user in users:
        role = user['role']
        role_stats[role] = role_stats.get(role, 0) + 1

    logging.info(f"   User role distribution: {role_stats}")

    # 生成商品数据  
    logging.info("📦 Generating item data...")
    items = ItemGenerator.generate_items(2000)  # 生成200个商品
    logging.info(f"✅ Generated {len(items)} items")

    # 统计商品类别分布
    category_stats = {}
    for item in items:
        category = item['category']
        category_stats[category] = category_stats.get(category, 0) + 1

    logging.info(f"   Item category distribution: {category_stats}")

    # 生成订单数据
    logging.info("🛒 Generating order data...")
    orders = OrderGenerator.generate_orders(EXPERIMENT_PARAMS["data_size"])
    logging.info(f"✅ Generated {len(orders)} orders")

    return {
        'users': users,
        'items': items,
        'orders': orders
    }


def initialize_storage_modules():
    """初始化所有存储模块"""
    storage_modules = {}

    try:
        logging.info("Initializing storage modules...")

        # MySQL链下存储
        storage_modules['mysql'] = MySQLStorage()
        if storage_modules['mysql'].is_connected:
            logging.info("✅ MySQL storage initialized")
        else:
            logging.warning("⚠️ MySQL storage failed to initialize, continuing without it")

        # Redis缓存
        try:
            storage_modules['redis'] = RedisCache()
            logging.info("✅ Redis cache initialized")
        except Exception as e:
            logging.warning(f"⚠️ Redis cache failed to initialize: {str(e)}, continuing without it")
            storage_modules['redis'] = None

        # 区块链存储
        storage_modules['blockchain'] = BlockchainStorage()
        logging.info("✅ Blockchain storage initialized")

        # 交易管理器
        storage_modules['transaction_manager'] = TransactionManager(storage_modules['blockchain'])
        logging.info("✅ Transaction manager initialized")

        logging.info("Storage modules initialization completed")
        return storage_modules

    except Exception as e:
        logging.error(f"Failed to initialize storage modules: {str(e)}")
        raise


def initialize_algorithm_modules():
    """初始化所有算法模块"""
    algorithm_modules = {}

    try:
        logging.info("Initializing algorithm modules...")

        # Shamir秘密共享算法
        algorithm_modules['shamir'] = ShamirSecretSharing()
        logging.info("✅ Shamir secret sharing initialized")

        # Merkle树算法
        algorithm_modules['merkle'] = MerkleTree()
        logging.info("✅ Merkle tree initialized")

        # 零知识证明算法
        algorithm_modules['zk_proof'] = ZeroKnowledgeProof()
        logging.info("✅ Zero-knowledge proof initialized")

        # 动态访问控制
        algorithm_modules['access_control'] = DynamicAccessControl()
        logging.info("✅ Dynamic access control initialized")

        logging.info("All algorithm modules initialized successfully")
        return algorithm_modules

    except Exception as e:
        logging.error(f"Failed to initialize algorithm modules: {str(e)}")
        raise


def save_dataset_to_storage(dataset, storage_modules):
    """将数据集保存到存储系统"""
    logging.info("💾 Saving dataset to storage systems...")

    if 'mysql' in storage_modules and storage_modules['mysql'].is_connected:
        saved_users = 0
        saved_items = 0
        saved_orders = 0

        # 保存用户数据
        logging.info("Saving users to MySQL...")
        for user in dataset['users']:
            if storage_modules['mysql'].save_user(user):
                saved_users += 1

        # 保存商品数据  
        logging.info("Saving items to MySQL...")
        for item in dataset['items']:
            if storage_modules['mysql'].save_item(item):
                saved_items += 1

        # 保存订单数据
        logging.info("Saving orders to MySQL...")
        for order in dataset['orders']:
            if storage_modules['mysql'].save_order(order):
                saved_orders += 1

        logging.info(f"💾 Data saved to MySQL:")
        logging.info(f"   Users: {saved_users}/{len(dataset['users'])} ({saved_users / len(dataset['users']) * 100:.1f}%)")
        logging.info(f"   Items: {saved_items}/{len(dataset['items'])} ({saved_items / len(dataset['items']) * 100:.1f}%)")
        logging.info(f"   Orders: {saved_orders}/{len(dataset['orders'])} ({saved_orders / len(dataset['orders']) * 100:.1f}%)")

        # 更新存储统计
        stats = storage_modules['mysql'].get_statistics()
        logging.info(f"📊 MySQL database statistics:")
        for key, value in stats.items():
            if key.endswith('_count'):
                logging.info(f"   {key}: {value}")
    else:
        logging.warning("⚠️ MySQL not available, skipping database storage")

    # 缓存部分关键数据到Redis
    if 'redis' in storage_modules and storage_modules['redis']:
        try:
            # 缓存用户统计
            user_stats = {}
            for user in dataset['users']:
                role = user['role']
                user_stats[role] = user_stats.get(role, 0) + 1

            storage_modules['redis'].set("user_statistics", user_stats, 3600)

            # 缓存商品统计
            item_stats = {}
            for item in dataset['items']:
                category = item['category']
                item_stats[category] = item_stats.get(category, 0) + 1

            storage_modules['redis'].set("item_statistics", item_stats, 3600)

            logging.info("✅ Key statistics cached to Redis")
        except Exception as e:
            logging.warning(f"⚠️ Failed to cache data to Redis: {str(e)}")


def run_experiment_suite(dataset, storage_modules, algorithm_modules):
    """运行完整的实验测试套件"""
    try:
        logging.info("Starting comprehensive experimental validation...")
        experiment_results = {}

        # 使用处理后的订单数据进行实验
        from data.preprocess_orders import OrderPreprocessor
        preprocessor = OrderPreprocessor()
        processed_orders = preprocessor.preprocess_orders(dataset['orders'])

        logging.info(f"Using {len(processed_orders)} valid orders for experiments")

        # 1. 性能测试
        logging.info("=" * 60)
        logging.info("EXPERIMENT 1: PERFORMANCE TEST")
        logging.info("=" * 60)
        perf_results = run_performance_test(processed_orders, storage_modules, algorithm_modules)
        experiment_results['performance'] = perf_results
        logging.info("✅ Performance test completed")

        # 2. 隐私保护测试
        logging.info("=" * 60)
        logging.info("EXPERIMENT 2: PRIVACY PROTECTION TEST")
        logging.info("=" * 60)
        privacy_results = run_privacy_test(processed_orders, storage_modules, algorithm_modules)
        experiment_results['privacy'] = privacy_results
        logging.info("✅ Privacy protection test completed")

        # 3. 攻击模拟测试
        logging.info("=" * 60)
        logging.info("EXPERIMENT 3: ATTACK SIMULATION TEST")
        logging.info("=" * 60)
        attack_results = run_attack_simulation(processed_orders, storage_modules, algorithm_modules)
        experiment_results['attack_simulation'] = attack_results
        logging.info("✅ Attack simulation test completed")

        # 4. 性能对比测试
        logging.info("=" * 60)
        logging.info("EXPERIMENT 4: COMPARATIVE ANALYSIS TEST")
        logging.info("=" * 60)
        comparison_results = run_comparison_test(processed_orders, storage_modules, algorithm_modules)
        experiment_results['comparison'] = comparison_results
        logging.info("✅ Comparative analysis test completed")

        # 5. 吞吐量测试
        logging.info("=" * 60)
        logging.info("EXPERIMENT 5: THROUGHPUT SCALABILITY TEST")
        logging.info("=" * 60)
        throughput_results = run_throughput_test(processed_orders, storage_modules, algorithm_modules)
        experiment_results['throughput'] = throughput_results
        logging.info("✅ Throughput scalability test completed")

        logging.info("All experimental tests completed successfully")
        return experiment_results

    except Exception as e:
        logging.error(f"Experiment suite failed: {str(e)}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        return None


def print_experiment_summary(experiment_results, dataset):
    """打印实验结果摘要"""
    print("\n" + "=" * 80)
    print("DVSS-PPA EXPERIMENT RESULTS SUMMARY")
    print("=" * 80)
    print(f"📝 Experimenter: yshan2028")
    print(f"🕒 Completion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"🧪 Total Experiments: {len(experiment_results)}")

    # 数据集统计
    print(f"📊 Dataset Statistics:")
    print(f"   Users Generated: {len(dataset['users'])}")
    print(f"   Items Generated: {len(dataset['items'])}")
    print(f"   Orders Generated: {len(dataset['orders'])}")

    # 性能指标摘要
    if 'performance' in experiment_results:
        perf_data = experiment_results['performance']
        if 'overall_metrics' in perf_data:
            metrics = perf_data['overall_metrics']
            print(f"⚡ System Throughput: {metrics.get('throughput_tps', 0):.2f} TPS")
            print(f"📦 Orders Processed: {metrics.get('total_orders_processed', 0)}")

    # 隐私保护评分
    if 'privacy' in experiment_results:
        privacy_data = experiment_results['privacy']
        if 'privacy_scores' in privacy_data:
            scores = privacy_data['privacy_scores']
            overall_score = scores.get('overall_privacy_score', 0)
            print(f"🔒 Privacy Protection Score: {overall_score:.1f}%")

    # 攻击抵抗性
    if 'attack_simulation' in experiment_results:
        attack_data = experiment_results['attack_simulation']
        if 'attack_resistance_scores' in attack_data:
            resistance = attack_data['attack_resistance_scores']
            overall_resistance = resistance.get('overall_resistance', 0)
            print(f"🛡️  Attack Resistance: {overall_resistance:.1f}%")

    # 对比改进
    if 'comparison' in experiment_results:
        comp_data = experiment_results['comparison']
        if 'comparison_metrics' in comp_data:
            improvement = comp_data['comparison_metrics']['dvss_vs_hyperledger'].get('latency_improvement', 0)
            print(f"📈 Performance vs Hyperledger: +{improvement:.1f}%")

    # 可扩展性
    if 'throughput' in experiment_results:
        throughput_data = experiment_results['throughput']
        if 'scalability_analysis' in throughput_data:
            scalability = throughput_data['scalability_analysis']
            max_tps = scalability.get('max_throughput_tps', 0)
            print(f"🚀 Maximum Throughput: {max_tps:.2f} TPS")

    print("\n✅ All results saved to experiments/results/ directory")
    print("📊 Detailed reports and visualizations generated")
    print("💾 Complete dataset stored in MySQL database")
    print("=" * 80)


def cleanup_resources(storage_modules):
    """清理实验资源"""
    try:
        if storage_modules:
            logging.info("Cleaning up experiment resources...")

            # 获取统计信息
            if 'mysql' in storage_modules and storage_modules['mysql'].is_connected:
                stats = storage_modules['mysql'].get_statistics()
                logging.info(f"MySQL operations: {stats.get('operations_count', 0)}")
                storage_modules['mysql'].close_connection()

            if 'redis' in storage_modules and storage_modules['redis']:
                storage_modules['redis'].close_connection()

            # 区块链信息
            if 'blockchain' in storage_modules:
                chain_info = storage_modules['blockchain'].get_chain_info()
                logging.info(f"Blockchain blocks: {chain_info.get('total_blocks', 0)}")

            # 交易统计
            if 'transaction_manager' in storage_modules:
                tx_stats = storage_modules['transaction_manager'].get_stats()
                logging.info(f"Total transactions: {tx_stats.get('total_transactions', 0)}")

            logging.info("Resource cleanup completed successfully")

    except Exception as e:
        logging.warning(f"Resource cleanup warning: {str(e)}")


def main():
    """DVSS-PPA区块链隐私保护实验系统主程序入口"""
    storage_modules = None

    try:
        # 初始化日志系统
        setup_logging()

        logging.info("=" * 80)
        logging.info("DVSS-PPA BLOCKCHAIN PRIVACY PROTECTION EXPERIMENT SYSTEM")
        logging.info("=" * 80)
        logging.info(f"📝 Author: yshan2028")
        logging.info(f"🕒 Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        logging.info(f"🏷️  System: Dynamic Verifiable Secret Sharing with Privacy-Preserving Access")
        logging.info("🚀 System startup initiated...")

        # Step 1: 验证实验配置
        logging.info("\n" + "=" * 60)
        logging.info("STEP 1: VALIDATING EXPERIMENT CONFIGURATION")
        logging.info("=" * 60)

        if not validate_configuration():
            logging.error("❌ Configuration validation failed. Exiting...")
            return 1

        logging.info("✅ Experiment configuration validated successfully")
        logging.info(f"📊 Data size: {EXPERIMENT_PARAMS['data_size']}")
        logging.info(f"🔢 Shard count: {EXPERIMENT_PARAMS['shard_count']}")
        logging.info(f"🎯 Threshold: {EXPERIMENT_PARAMS['threshold']}")

        # Step 2: 生成完整实验数据集
        logging.info("\n" + "=" * 60)
        logging.info("STEP 2: GENERATING COMPLETE EXPERIMENT DATASET")
        logging.info("=" * 60)

        dataset = generate_complete_dataset()

        logging.info(f"📊 Dataset Generation Summary:")
        logging.info(f"   Users: {len(dataset['users'])}")
        logging.info(f"   Items: {len(dataset['items'])}")
        logging.info(f"   Orders: {len(dataset['orders'])}")

        # Step 3: 初始化系统模块
        logging.info("\n" + "=" * 60)
        logging.info("STEP 3: INITIALIZING SYSTEM MODULES")
        logging.info("=" * 60)

        storage_modules = initialize_storage_modules()
        algorithm_modules = initialize_algorithm_modules()

        logging.info("✅ All system modules initialized successfully")

        # Step 3.5: 演示角色权限系统
        logging.info("\n" + "=" * 60)
        logging.info("STEP 3.5: ROLE-BASED ACCESS CONTROL DEMONSTRATION")
        logging.info("=" * 60)

        # 演示权限系统
        demonstrate_role_access_system()

        # Step 4: 保存数据集到存储系统
        logging.info("\n" + "=" * 60)
        logging.info("STEP 4: SAVING DATASET TO STORAGE SYSTEMS")
        logging.info("=" * 60)

        save_dataset_to_storage(dataset, storage_modules)

        # Step 5: 执行实验测试套件
        logging.info("\n" + "=" * 60)
        logging.info("STEP 5: EXECUTING COMPREHENSIVE EXPERIMENT SUITE")
        logging.info("=" * 60)

        experiment_results = run_experiment_suite(dataset, storage_modules, algorithm_modules)

        if not experiment_results:
            logging.error("❌ Experiment suite execution failed")
            return 1

        # Step 6: 生成综合报告
        logging.info("\n" + "=" * 60)
        logging.info("STEP 6: GENERATING COMPREHENSIVE ANALYSIS REPORT")
        logging.info("=" * 60)

        report_path = generate_comprehensive_report(experiment_results)

        if report_path:
            logging.info(f"✅ Comprehensive report generated: {report_path}")
        else:
            logging.warning("⚠️ Report generation encountered issues")

        # Step 7: 显示实验摘要
        logging.info("\n" + "=" * 60)
        logging.info("STEP 7: EXPERIMENT COMPLETION SUMMARY")
        logging.info("=" * 60)

        print_experiment_summary(experiment_results, dataset)

        logging.info("=" * 80)
        logging.info("🎉 DVSS-PPA EXPERIMENT EXECUTION COMPLETED SUCCESSFULLY")
        logging.info("📋 Summary:")
        logging.info(f"   • Experiments Completed: {len(experiment_results)}")
        logging.info(f"   • Users Generated: {len(dataset['users'])}")
        logging.info(f"   • Items Generated: {len(dataset['items'])}")
        logging.info(f"   • Orders Processed: {len(dataset['orders'])}")
        logging.info(f"   • Report Generated: {report_path is not None}")
        logging.info(f"   • Total Runtime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        logging.info("📁 Results and performance metrics saved to experiments/results/ directory")
        logging.info("📊 Please check the generated reports for detailed analysis")
        logging.info("💾 Complete dataset stored in MySQL database tables")
        logging.info("=" * 80)

        return 0

    except KeyboardInterrupt:
        logging.warning("⚠️ Experiment interrupted by user (Ctrl+C)")
        print("\n🛑 Experiment interrupted by user")
        return 1

    except Exception as e:
        logging.error(f"💥 Fatal error in main execution: {str(e)}")
        logging.error(f"📋 Full traceback: {traceback.format_exc()}")
        print(f"\n❌ Fatal error: {str(e)}")
        print("📋 Check logs for detailed error information")
        return 1

    finally:
        # Step 8: 清理资源
        logging.info("\n" + "=" * 60)
        logging.info("STEP 8: CLEANING UP SYSTEM RESOURCES")
        logging.info("=" * 60)

        cleanup_resources(storage_modules)
        logging.info("🧹 System shutdown completed")
        print("🧹 System resources cleaned up successfully")


if __name__ == "__main__":
    print("🚀 Starting DVSS-PPA Blockchain Privacy Protection Experiment System...")
    print("👤 Author: yshan2028")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("🎯 System: Dynamic Verifiable Secret Sharing with Privacy-Preserving Access")
    print("=" * 80)

    exit_code = main()

    if exit_code == 0:
        print("\n🎉 Experiment completed successfully!")
        print("📊 Check the results directory for detailed reports and visualizations")
        print("💾 Complete dataset has been saved to MySQL database")
        print("📈 Performance metrics and privacy scores have been recorded")
    else:
        print("\n❌ Experiment failed!")
        print("📋 Check the logs for error details")
        print("🔧 Verify MySQL and Redis connections")

    print(f"\n👤 Experimenter: yshan2028")
    print(f"🕒 Completion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 80)

    sys.exit(exit_code)