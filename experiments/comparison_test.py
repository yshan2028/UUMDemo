#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: comparison_test.py
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


def run_comparison_test(orders, blockchain, shamir, zk_proof, output_file="experiments/results/comparison.csv"):
    """
    运行性能对比实验。

    :param orders: 模拟订单列表。
    :param blockchain: 区块链存储实例。
    :param shamir: ShamirSecretSharing 实例。
    :param zk_proof: ZeroKnowledgeProof 实例。
    :param output_file: 实验结果保存路径。
    """
    results = []
    os.makedirs(os.path.dirname(output_file), exist_ok=True)  # 确保结果目录存在

    for idx, order in enumerate(orders[:100]):
        secret = int(order["payment"]["amount"])

        # Shamir 测试
        shamir_start = time.time()
        shares = shamir.generate_shares(secret, 5, 3)
        reconstructed_secret = shamir.reconstruct_secret(shares[:3], 3)
        shamir_time = time.time() - shamir_start

        # 零知识证明测试
        zk_start = time.time()
        proof = zk_proof.generate_proof(secret)
        zk_verified = zk_proof.verify_proof(proof, secret)
        zk_time = time.time() - zk_start

        # 区块链存储测试
        blockchain_start = time.time()
        blockchain.add_transaction({"order_id": order["order_id"], "amount": secret})
        blockchain_time = time.time() - blockchain_start

        # 记录结果
        results.append({
            "order_id": order["order_id"],
            "shamir_time": shamir_time,
            "zk_time": zk_time,
            "blockchain_time": blockchain_time,
            "zk_verified": zk_verified,
            "reconstructed_secret": reconstructed_secret == secret
        })

        if idx % 10 == 0:
            print(f"[对比实验] 已完成订单数: {idx + 1}/{100}")

    # 保存结果到 CSV 文件
    with open(output_file, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"[INFO] 对比实验结果已保存到: {output_file}")
