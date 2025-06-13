#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: throughput_test.py
Author: yshan2028
Created: 2025-06-13 08:54:05
Description: 吞吐量测试
"""

import time
import threading
import logging
from concurrent.futures import ThreadPoolExecutor
from utils.helpers import calculate_metrics, generate_id

logger = logging.getLogger(__name__)


def run_throughput_test(orders, storage_modules, algorithm_modules):
    """运行吞吐量测试"""
    logger.info("Starting throughput test...")

    results = {
        "single_thread_results": {},
        "multi_thread_results": {},
        "scalability_analysis": {}
    }

    # 单线程吞吐量测试
    single_thread_tps = _test_single_thread_throughput(orders[:100], storage_modules, algorithm_modules)
    results["single_thread_results"] = {
        "transactions_per_second": single_thread_tps,
        "test_duration_seconds": 100 / single_thread_tps if single_thread_tps > 0 else 0,
        "total_transactions": 100
    }

    # 多线程吞吐量测试
    thread_counts = [2, 4, 8, 16]
    multi_thread_results = {}

    for thread_count in thread_counts:
        if len(orders) >= thread_count * 20:
            tps = _test_multi_thread_throughput(
                orders[:thread_count * 20],
                storage_modules,
                algorithm_modules,
                thread_count
            )
            multi_thread_results[f"{thread_count}_threads"] = {
                "transactions_per_second": tps,
                "thread_count": thread_count,
                "scalability_factor": tps / single_thread_tps if single_thread_tps > 0 else 0
            }

    results["multi_thread_results"] = multi_thread_results

    # 可扩展性分析
    max_tps = max([result["transactions_per_second"] for result in multi_thread_results.values()])
    optimal_threads = None
    for threads, result in multi_thread_results.items():
        if result["transactions_per_second"] == max_tps:
            optimal_threads = result["thread_count"]
            break

    results["scalability_analysis"] = {
        "max_throughput_tps": max_tps,
        "optimal_thread_count": optimal_threads,
        "linear_scalability_score": _calculate_scalability_score(multi_thread_results),
        "bottleneck_analysis": _analyze_bottlenecks(multi_thread_results)
    }

    # 保存结果
    experiment_result = {
        "experiment_id": generate_id("THROUGH"),
        "algorithm_name": "Throughput_Test",
        "execution_time": 0.0,
        "throughput": max_tps,
        "results": results
    }

    storage_modules['mysql'].save_experiment_result(experiment_result)

    logger.info(f"Throughput test completed. Max TPS: {max_tps:.2f}")
    return results


def _test_single_thread_throughput(orders, storage_modules, algorithm_modules):
    """测试单线程吞吐量"""
    start_time = time.time()

    for order in orders:
        # 执行完整的DVSS-PPA操作
        secret = hash(order["order_id"]) % 1000000
        shares, _, k = algorithm_modules['shamir'].share_secret(secret, 5, 0.7, 0.3, 0.5)
        recovered = algorithm_modules['shamir'].reconstruct_secret(shares[:k])
        storage_modules['mysql'].save_order(order)

    end_time = time.time()
    duration = end_time - start_time

    return len(orders) / duration if duration > 0 else 0


def _test_multi_thread_throughput(orders, storage_modules, algorithm_modules, thread_count):
    """测试多线程吞吐量"""
    start_time = time.time()

    def process_order_batch(order_batch):
        for order in order_batch:
            secret = hash(order["order_id"]) % 1000000
            shares, _, k = algorithm_modules['shamir'].share_secret(secret, 5, 0.7, 0.3, 0.5)
            recovered = algorithm_modules['shamir'].reconstruct_secret(shares[:k])
            storage_modules['mysql'].save_order(order)

    # 分批处理订单
    batch_size = len(orders) // thread_count
    order_batches = [orders[i:i + batch_size] for i in range(0, len(orders), batch_size)]

    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        executor.map(process_order_batch, order_batches)

    end_time = time.time()
    duration = end_time - start_time

    return len(orders) / duration if duration > 0 else 0


def _calculate_scalability_score(multi_thread_results):
    """计算线性可扩展性评分"""
    if len(multi_thread_results) < 2:
        return 0.0

    scalability_factors = [result["scalability_factor"] for result in multi_thread_results.values()]
    thread_counts = [result["thread_count"] for result in multi_thread_results.values()]

    # 理想情况下，可扩展性因子应该等于线程数
    ideal_factors = thread_counts
    actual_factors = scalability_factors

    # 计算与理想情况的偏差
    deviations = [abs(ideal - actual) / ideal for ideal, actual in zip(ideal_factors, actual_factors)]
    avg_deviation = sum(deviations) / len(deviations)

    # 可扩展性评分（100分为满分）
    return max(0, (1 - avg_deviation) * 100)


def _analyze_bottlenecks(multi_thread_results):
    """分析性能瓶颈"""
    bottlenecks = []

    # 检查吞吐量是否随线程数增加而下降
    thread_counts = sorted([result["thread_count"] for result in multi_thread_results.values()])
    tps_values = [multi_thread_results[f"{tc}_threads"]["transactions_per_second"] for tc in thread_counts]

    for i in range(1, len(tps_values)):
        if tps_values[i] < tps_values[i - 1]:
            bottlenecks.append(f"Performance degradation detected at {thread_counts[i]} threads")

    # 检查可扩展性因子是否过低
    for threads, result in multi_thread_results.items():
        if result["scalability_factor"] < result["thread_count"] * 0.5:
            bottlenecks.append(f"Poor scalability at {result['thread_count']} threads (factor: {result['scalability_factor']:.2f})")

    return bottlenecks if bottlenecks else ["No significant bottlenecks detected"]