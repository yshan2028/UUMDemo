#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: throughput_test.py
Author: yshan2028
Created: 2025-06-13 14:56:13
Description: 
    [请在此处添加文件描述]

Dependencies:
    [请在此处列出主要依赖]

Usage:
    [请在此处添加使用说明]
"""

from concurrent.futures import ThreadPoolExecutor
import time

def process_order(order, blockchain, shamir):
    """
    单个订单的处理逻辑。

    :param order: 模拟订单。
    :param blockchain: 区块链存储实例。
    :param shamir: ShamirSecretSharing 实例。
    """
    secret = int(order["payment"]["amount"])
    shares = shamir.generate_shares(secret, 5, 3)
    blockchain.add_transaction({"order_id": order["order_id"], "shares": shares})

def run_throughput_test(orders, blockchain, shamir, max_workers=10):
    """
    运行吞吐量测试。

    :param orders: 模拟订单列表。
    :param blockchain: 区块链存储实例。
    :param shamir: ShamirSecretSharing 实例。
    :param max_workers: 并发线程数量。
    """
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(lambda order: process_order(order, blockchain, shamir), orders)

    elapsed_time = time.time() - start_time
    throughput = len(orders) / elapsed_time
    print(f"[吞吐量测试] 总耗时: {elapsed_time:.2f} 秒，吞吐量: {throughput:.2f} 订单/秒")
