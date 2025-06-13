#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: privacy_test.py
Author: yshan2028
Created: 2025-06-13 08:54:05
Description: 隐私保护实验
"""

import logging
from utils.helpers import generate_id

logger = logging.getLogger(__name__)


def run_privacy_test(orders, storage_modules, algorithm_modules):
    """运行隐私保护测试"""
    logger.info("Starting privacy protection test...")

    results = {
        "access_control_tests": [],
        "secret_sharing_tests": [],
        "zero_knowledge_tests": [],
        "privacy_scores": {}
    }

    roles = ["merchant", "logistics", "payment", "admin"]

    # 访问控制测试
    for i, order in enumerate(orders[:20]):
        role = roles[i % len(roles)]

        # 测试访问控制
        access_result = algorithm_modules['access_control'].verify_access(
            f"user_{i}", role, "order", "read"
        )

        # 测试数据过滤
        filtered_data = algorithm_modules['access_control'].filter_data_fields(order, role)

        results["access_control_tests"].append({
            "order_id": order["order_id"],
            "user_role": role,
            "access_granted": access_result.granted,
            "filtered_fields_count": len(filtered_data),
            "original_fields_count": len(order)
        })

    # 秘密共享测试
    for order in orders[:15]:
        secret = hash(order["order_id"]) % 1000000
        shares, _, k = algorithm_modules['shamir'].share_secret(
            secret, 5, 0.8, 0.2, 0.4
        )

        # 测试不同数量分片的重构
        for test_shares in [k - 1, k, k + 1]:
            if test_shares <= len(shares):
                recovered = algorithm_modules['shamir'].reconstruct_secret(shares[:test_shares])
                success = (recovered == secret) if test_shares >= k else (recovered != secret)

                results["secret_sharing_tests"].append({
                    "order_id": order["order_id"],
                    "threshold": k,
                    "shares_used": test_shares,
                    "reconstruction_success": success,
                    "expected_success": test_shares >= k
                })

    # 零知识证明测试
    for i, order in enumerate(orders[:10]):
        role = roles[i % len(roles)]
        permissions = ["read", "update"] if role != "admin" else ["read", "write", "delete"]

        # 生成证明
        proof = algorithm_modules['zk_proof'].generate_proof(
            f"user_{i}", role, permissions
        )

        # 验证证明
        is_valid = algorithm_modules['zk_proof'].verify_proof(proof, role)

        results["zero_knowledge_tests"].append({
            "order_id": order["order_id"],
            "user_role": role,
            "proof_valid": is_valid,
            "permissions": permissions
        })

    # 计算隐私保护评分
    access_success_rate = sum(1 for test in results["access_control_tests"] if test["access_granted"]) / len(results["access_control_tests"])
    sharing_success_rate = sum(1 for test in results["secret_sharing_tests"] if test["reconstruction_success"] == test["expected_success"]) / len(results["secret_sharing_tests"])
    zk_success_rate = sum(1 for test in results["zero_knowledge_tests"] if test["proof_valid"]) / len(results["zero_knowledge_tests"])

    results["privacy_scores"] = {
        "access_control_score": access_success_rate * 100,
        "secret_sharing_score": sharing_success_rate * 100,
        "zero_knowledge_score": zk_success_rate * 100,
        "overall_privacy_score": (access_success_rate + sharing_success_rate + zk_success_rate) / 3 * 100
    }

    # 保存结果
    experiment_result = {
        "experiment_id": generate_id("PRIV"),
        "algorithm_name": "Privacy_Protection",
        "execution_time": 0.0,  # 隐私测试关注正确性而非性能
        "throughput": 0.0,
        "results": results
    }

    storage_modules['mysql'].save_experiment_result(experiment_result)

    logger.info(f"Privacy test completed. Overall score: {results['privacy_scores']['overall_privacy_score']:.2f}%")
    return results