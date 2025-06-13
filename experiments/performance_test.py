#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: performance_test.py
Author: yshan2028
Created: 2025-06-13 08:47:13
Description: 性能测试
"""

import time
import logging
from utils.helpers import calculate_metrics, generate_id

logger = logging.getLogger(__name__)


def run_performance_test(orders, storage_modules, algorithm_modules):
    """运行性能测试"""
    logger.info("Starting performance test...")

    results = {
        "algorithm_performance": {},
        "storage_performance": {},
        "overall_metrics": {}
    }

    # 测试Shamir算法性能
    shamir_times = []
    for i, order in enumerate(orders[:100]):
        start_time = time.time()

        secret = hash(order["order_id"]) % 1000000
        shares, _, k = algorithm_modules['shamir'].share_secret(
            secret, 5, 0.7, 0.3, 0.5
        )
        recovered = algorithm_modules['shamir'].reconstruct_secret(shares[:k])

        operation_time = time.time() - start_time
        shamir_times.append(operation_time * 1000)  # 转换为毫秒

    results["algorithm_performance"]["shamir"] = calculate_metrics(shamir_times)

    # 测试存储性能
    storage_times = []
    for order in orders[:50]:
        start_time = time.time()
        storage_modules['mysql'].save_order(order)
        operation_time = time.time() - start_time
        storage_times.append(operation_time * 1000)

    results["storage_performance"]["mysql"] = calculate_metrics(storage_times)

    # 整体性能指标
    results["overall_metrics"] = {
        "total_orders_processed": len(orders),
        "avg_processing_time": sum(shamir_times + storage_times) / (len(shamir_times) + len(storage_times)),
        "throughput_tps": len(orders) / sum(shamir_times + storage_times) * 1000
    }

    # 保存结果
    experiment_result = {
        "experiment_id": generate_id("PERF"),
        "algorithm_name": "Performance_Test",
        "execution_time": sum(shamir_times + storage_times),
        "throughput": results["overall_metrics"]["throughput_tps"],
        "results": results
    }

    storage_modules['mysql'].save_experiment_result(experiment_result)

    logger.info("Performance test completed")
    return results