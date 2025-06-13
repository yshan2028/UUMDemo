#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: attack_simulation.py
Author: yshan2028
Created: 2025-06-13 08:54:05
Description: 模拟攻击实验
"""

import random
import logging
from utils.helpers import generate_id

logger = logging.getLogger(__name__)


def run_attack_simulation(orders, storage_modules, algorithm_modules):
    """运行攻击模拟实验"""
    logger.info("Starting attack simulation...")

    results = {
        "threshold_attacks": [],
        "privilege_escalation_attacks": [],
        "data_inference_attacks": [],
        "attack_resistance_scores": {}
    }

    # 阈值攻击模拟
    for order in orders[:10]:
        secret = hash(order["order_id"]) % 1000000
        shares, _, k = algorithm_modules['shamir'].share_secret(secret, 5, 0.7, 0.3, 0.5)

        # 模拟攻击者获得不足阈值的分片
        attack_shares = random.randint(1, k - 1)
        recovered = algorithm_modules['shamir'].reconstruct_secret(shares[:attack_shares])

        attack_success = (recovered == secret)  # 理论上应该失败

        results["threshold_attacks"].append({
            "order_id": order["order_id"],
            "threshold": k,
            "attacker_shares": attack_shares,
            "attack_success": attack_success,
            "resistance_level": "SECURE" if not attack_success else "VULNERABLE"
        })

    # 权限提升攻击模拟
    attack_scenarios = [
        {"role": "merchant", "attempted_operation": "delete"},
        {"role": "logistics", "attempted_operation": "admin"},
        {"role": "customer", "attempted_operation": "write"}
    ]

    for i, scenario in enumerate(attack_scenarios):
        for order in orders[i * 3:(i + 1) * 3]:
            access_result = algorithm_modules['access_control'].verify_access(
                f"attacker_{i}", scenario["role"], "order", scenario["attempted_operation"]
            )

            results["privilege_escalation_attacks"].append({
                "order_id": order["order_id"],
                "attacker_role": scenario["role"],
                "attempted_operation": scenario["attempted_operation"],
                "attack_success": access_result.granted,
                "resistance_level": "SECURE" if not access_result.granted else "VULNERABLE"
            })

    # 数据推理攻击模拟
    for order in orders[:8]:
        # 模拟攻击者尝试推理敏感数据
        filtered_merchant = algorithm_modules['access_control'].filter_data_fields(order, "merchant")
        filtered_logistics = algorithm_modules['access_control'].filter_data_fields(order, "logistics")

        # 检查是否有数据泄露
        merchant_fields = set(filtered_merchant.keys())
        logistics_fields = set(filtered_logistics.keys())
        overlap = merchant_fields.intersection(logistics_fields)

        # 检查敏感字段是否被保护
        sensitive_fields = ["customer_address", "payment_details", "customer_phone"]
        leaked_sensitive = any(field in filtered_merchant or field in filtered_logistics
                               for field in sensitive_fields if field in order)

        results["data_inference_attacks"].append({
            "order_id": order["order_id"],
            "field_overlap": len(overlap),
            "sensitive_data_leaked": leaked_sensitive,
            "resistance_level": "SECURE" if not leaked_sensitive else "VULNERABLE"
        })

    # 计算攻击抵抗性评分
    threshold_resistance = sum(1 for attack in results["threshold_attacks"]
                               if attack["resistance_level"] == "SECURE") / len(results["threshold_attacks"])

    privilege_resistance = sum(1 for attack in results["privilege_escalation_attacks"]
                               if attack["resistance_level"] == "SECURE") / len(results["privilege_escalation_attacks"])

    inference_resistance = sum(1 for attack in results["data_inference_attacks"]
                               if attack["resistance_level"] == "SECURE") / len(results["data_inference_attacks"])

    results["attack_resistance_scores"] = {
        "threshold_resistance": threshold_resistance * 100,
        "privilege_resistance": privilege_resistance * 100,
        "inference_resistance": inference_resistance * 100,
        "overall_resistance": (threshold_resistance + privilege_resistance + inference_resistance) / 3 * 100
    }

    # 保存结果
    experiment_result = {
        "experiment_id": generate_id("ATTACK"),
        "algorithm_name": "Attack_Simulation",
        "execution_time": 0.0,
        "throughput": 0.0,
        "results": results
    }

    storage_modules['mysql'].save_experiment_result(experiment_result)

    logger.info(f"Attack simulation completed. Overall resistance: {results['attack_resistance_scores']['overall_resistance']:.2f}%")
    return results