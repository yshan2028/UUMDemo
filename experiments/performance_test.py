#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: performance_test.py
Author: yshan2028
Created: 2025-06-13 14:56:13
Description: 
    [请在此处添加文件描述]

Dependencies:
    [请在此处列出主要依赖]

Usage:
    [请在此处添加使用说明]
"""

import csv
import os
import time
from random import randint
from config.settings import RESULTS_PATH


def run_performance_test(orders, blockchain, shamir, merkle_tree, zk_proof):
    """
    测试指定区块链与算法的性能，并保存结果到 CSV 文件。

    :param orders: 模拟订单列表。
    :param blockchain: 区块链实例。
    :param shamir: ShamirSecretSharing 实例。
    :param merkle_tree: MerkleTree 实例。
    :param zk_proof: ZeroKnowledgeProof 实例。
    """
    ethereum_output_file = os.path.join(RESULTS_PATH, "ethereum.csv")
    hyperledger_output_file = os.path.join(RESULTS_PATH, "hyperledger.csv")
    os.makedirs(RESULTS_PATH, exist_ok=True)  # 确保结果目录存在

    # 定义字段集合
    all_fieldnames = {
        "Ethereum": [
            "order_id", "shamir_time", "merkle_time", "zk_time",
            "zk_verified", "reconstructed_secret", "gas_used",
            "confirmation_time", "latency"
        ],
        "Hyperledger": [
            "order_id", "shamir_time", "merkle_time", "zk_time",
            "zk_verified", "reconstructed_secret", "cpu_usage",
            "memory_usage", "latency"
        ]
    }

    for blockchain_type, output_file in [("Ethereum", ethereum_output_file), ("Hyperledger", hyperledger_output_file)]:
        print(f"[INFO] 开始 {blockchain_type} 性能测试...")
        results = []  # 清空结果列表
        for idx, order in enumerate(orders[:100]):  # 示例前 100 条订单
            secret = randint(1000, 9999)  # 模拟订单中的敏感数据

            # Shamir Secret Sharing 测试
            shamir_start = time.time()
            shares = shamir.generate_shares(secret, 5, 3)
            reconstructed_secret = shamir.reconstruct_secret(shares[:3], 3)
            shamir_time = time.time() - shamir_start

            # Merkle Tree 测试
            merkle_tree.add_leaf(f"{order['order_id']}")
            merkle_tree_start = time.time()
            merkle_tree.build_tree()
            merkle_time = time.time() - merkle_tree_start
            merkle_root = merkle_tree.get_root()

            # Zero Knowledge Proof 测试
            zk_proof_start = time.time()
            proof = zk_proof.generate_proof(secret)
            zk_verified = zk_proof.verify_proof(proof, secret)
            zk_time = time.time() - zk_proof_start

            # 区块链性能模拟
            if blockchain_type == "Ethereum":
                gas_used = randint(21000, 50000)  # 模拟 Gas 消耗
                confirmation_time = randint(10, 20)  # 模拟确认时间（秒）
                latency = confirmation_time * 1000  # 模拟延迟（毫秒）
                additional_data = {
                    "gas_used": gas_used,
                    "confirmation_time": confirmation_time,
                    "latency": latency
                }
            elif blockchain_type == "Hyperledger":
                cpu_usage = randint(10, 20)  # 模拟 CPU 使用率（%）
                memory_usage = randint(100, 500)  # 模拟内存占用（MB）
                latency = randint(100, 200)  # 模拟延迟（毫秒）
                additional_data = {
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory_usage,
                    "latency": latency
                }

            # 记录结果
            result = {
                "order_id": order["order_id"],
                "shamir_time": shamir_time,
                "merkle_time": merkle_time,
                "zk_time": zk_time,
                "zk_verified": zk_verified,
                "reconstructed_secret": reconstructed_secret == secret
            }
            result.update(additional_data)
            results.append(result)

            if idx % 10 == 0:
                print(f"[{blockchain_type} 性能测试] 已完成订单数: {idx + 1}/{100}")

        # 保存结果到 CSV 文件
        with open(output_file, mode="w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=all_fieldnames[blockchain_type])
            writer.writeheader()
            writer.writerows(results)

        print(f"[INFO] {blockchain_type} 性能测试结果已保存到: {output_file}")
