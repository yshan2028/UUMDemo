#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: run_experiment.py
Author: yshan2028
Created: 2025-06-13 08:34:56
Description: DVSS-PPA综合实验执行器 - main.py的核心依赖
"""

import json
import time
import os
from typing import Dict, List, Any
from datetime import datetime

try:
    from config.settings import EXPERIMENT_PARAMS, RESULTS_CONFIG
    from algorithms.shamir import DVSSShamirSSS
    from algorithms.merkle_tree import DVSSMerkleTree
    from algorithms.zk_proof import DVSSZKProof
    from algorithms.dynamic_access import DVSSAccessControl
    from data.generate_orders import OrderDataGenerator
    from database.connection import DatabaseManager
    from blockchain.blockchain_storage import DVSSBlockchainStorage
    from blockchain.transaction_manager import DVSSTransactionManager
except ImportError as e:
    print(f"Import error in run_experiment.py: {e}")


class DVSSExperimentRunner:
    """DVSS-PPA实验执行器 - main.py的核心依赖类"""

    def __init__(self):
        self.results = {}
        self.start_time = None
        self.end_time = None

        # 存储和算法模块引用 - main.py会设置这些
        self.storage_modules = None
        self.algorithm_modules = None

        # 初始化算法模块
        try:
            self.shamir = DVSSShamirSSS()
            self.merkle = DVSSMerkleTree()
            self.zkp = DVSSZKProof()
            self.access_control = DVSSAccessControl()

            # 初始化数据生成器
            self.data_generator = OrderDataGenerator()

            print("DVSS-PPA Experiment Runner initialized")
        except Exception as e:
            print(f"Failed to initialize experiment runner: {e}")

    def run_comprehensive_experiment(self) -> Dict[str, Any]:
        """运行综合实验 - main.py调用的核心方法"""
        print("=" * 60)
        print("DVSS-PPA COMPREHENSIVE EXPERIMENT")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Experimenter: yshan2028")

        self.start_time = time.time()

        try:
            # 生成实验数据
            print("\nGenerating experiment data...")
            orders = self.data_generator.generate_batch_orders(
                EXPERIMENT_PARAMS.get("data_size", 200)
            )

            # 运行各项实验
            experiment_results = {}

            experiment_results["shamir"] = self.run_shamir_experiment(orders)
            experiment_results["merkle"] = self.run_merkle_experiment(orders)
            experiment_results["zkp"] = self.run_zkp_experiment(orders)
            experiment_results["access_control"] = self.run_access_control_experiment(orders)

            self.end_time = time.time()

            # 生成综合结果
            comprehensive_results = {
                "experiment_info": {
                    "framework": "DVSS-PPA",
                    "experimenter": "yshan2028",
                    "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
                    "end_time": datetime.fromtimestamp(self.end_time).isoformat(),
                    "duration_seconds": round(self.end_time - self.start_time, 2),
                    "total_orders_processed": len(orders)
                },
                "algorithm_results": experiment_results,
                "summary": self._generate_experiment_summary(experiment_results)
            }

            # 保存结果
            self._save_results(comprehensive_results)

            print(f"\n" + "=" * 60)
            print("EXPERIMENT COMPLETED SUCCESSFULLY!")
            print(f"Duration: {comprehensive_results['experiment_info']['duration_seconds']}s")
            print(f"Total operations: {self._count_total_operations(experiment_results)}")
            print("=" * 60)

            return comprehensive_results

        except Exception as e:
            print(f"Experiment failed: {e}")
            return {"error": str(e)}

    def run_shamir_experiment(self, orders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """运行Shamir秘密共享实验"""
        print("\n1. Running Shamir Secret Sharing Experiment...")

        results = {
            "algorithm": "Shamir_SSS",
            "operations": [],
            "performance": {}
        }

        for i, order in enumerate(orders[:50]):  # 测试前50个订单
            # 模拟动态参数
            sensitivity = order.get("sensitivity_score", 0.5)
            load = min(i / 50, 0.8)
            frequency = min((i % 10) / 10, 0.9)

            # 生成分片
            secret = hash(order["order_id"]) % 1000000
            shares, commitment, k = self.shamir.share_secret(
                secret=secret,
                n=5,
                sensitivity=sensitivity,
                load=load,
                frequency=frequency
            )

            # 重构测试
            recovered = self.shamir.reconstruct_secret(shares[:k])

            operation_result = {
                "order_id": order["order_id"],
                "threshold": k,
                "shares_count": len(shares),
                "reconstruction_success": recovered == secret,
                "sensitivity": sensitivity
            }

            results["operations"].append(operation_result)

        # 获取性能统计
        if hasattr(self.shamir, 'get_performance_stats'):
            results["performance"] = self.shamir.get_performance_stats()
        else:
            results["performance"] = {"operations": len(results["operations"])}

        print(f"Shamir experiment completed: {len(results['operations'])} operations")
        return results

    def run_merkle_experiment(self, orders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """运行Merkle树验证实验"""
        print("\n2. Running Merkle Tree Experiment...")

        results = {
            "algorithm": "Merkle_Tree",
            "operations": [],
            "performance": {}
        }

        # 构建Merkle树
        order_data = [order["order_id"] for order in orders[:30]]
        root_hash = self.merkle.build_tree(order_data)

        # 验证测试
        verification_results = []
        for order_id in order_data[:10]:
            proof = self.merkle.generate_proof(order_id)
            is_valid = self.merkle.verify_proof(order_id, proof, root_hash)

            verification_results.append({
                "order_id": order_id,
                "proof_elements": len(proof),
                "verification_success": is_valid
            })

        results["operations"] = verification_results
        results["tree_info"] = {
            "root_hash": root_hash[:16] + "..." if root_hash else "empty",
            "leaf_count": len(order_data),
            "total_verifications": len(verification_results)
        }

        print(f"Merkle experiment completed: {len(verification_results)} verifications")
        return results

    def run_zkp_experiment(self, orders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """运行零知识证明实验"""
        print("\n3. Running Zero Knowledge Proof Experiment...")

        results = {
            "algorithm": "ZK_Proof",
            "operations": [],
            "performance": {}
        }

        roles = ["merchant", "logistics", "payment", "admin"]
        verification_results = []

        for i, order in enumerate(orders[:20]):
            role = roles[i % len(roles)]
            permissions = ["read", "update"] if role != "admin" else ["read", "write", "delete"]

            # 生成证明
            proof = self.zkp.generate_proof(
                user_id=f"user_{i}",
                role=role,
                permissions=permissions
            )

            # 验证证明
            is_valid = self.zkp.verify_proof(proof, expected_role=role)

            verification_results.append({
                "order_id": order["order_id"],
                "user_role": role,
                "permissions": permissions,
                "proof_valid": is_valid
            })

        results["operations"] = verification_results

        if hasattr(self.zkp, 'get_performance_stats'):
            results["performance"] = self.zkp.get_performance_stats()
        else:
            results["performance"] = {"operations": len(verification_results)}

        print(f"ZKP experiment completed: {len(verification_results)} proofs")
        return results

    def run_access_control_experiment(self, orders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """运行访问控制实验"""
        print("\n4. Running Access Control Experiment...")

        results = {
            "algorithm": "Access_Control",
            "operations": [],
            "performance": {}
        }

        access_results = []
        roles = ["merchant", "logistics", "payment", "admin"]

        for i, order in enumerate(orders[:30]):
            role = roles[i % len(roles)]

            # 测试访问控制
            access_result = self.access_control.verify_access(
                user_id=f"user_{i}",
                role=role,
                resource_type="order",
                operation="read"
            )

            # 测试数据过滤
            filtered_data = self.access_control.filter_data_fields(order, role)

            access_results.append({
                "order_id": order["order_id"],
                "user_role": role,
                "access_granted": access_result.granted,
                "access_level": access_result.access_level.name,
                "filtered_fields": len(filtered_data),
                "original_fields": len(order)
            })

        results["operations"] = access_results
        results["performance"] = {
            "total_operations": len(access_results),
            "granted_access": sum(1 for r in access_results if r["access_granted"]),
            "denied_access": sum(1 for r in access_results if not r["access_granted"])
        }

        print(f"Access control experiment completed: {len(access_results)} operations")
        return results

    def _generate_experiment_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成实验总结"""
        summary = {
            "algorithms_tested": len(results),
            "total_operations": self._count_total_operations(results),
            "success_rates": {}
        }

        for alg_name, alg_results in results.items():
            operations = alg_results.get("operations", [])
            if operations:
                if alg_name == "shamir":
                    success_count = sum(1 for op in operations if op.get("reconstruction_success", False))
                    summary["success_rates"][alg_name] = f"{success_count}/{len(operations)}"
                elif alg_name == "merkle":
                    success_count = sum(1 for op in operations if op.get("verification_success", False))
                    summary["success_rates"][alg_name] = f"{success_count}/{len(operations)}"
                elif alg_name == "zkp":
                    success_count = sum(1 for op in operations if op.get("proof_valid", False))
                    summary["success_rates"][alg_name] = f"{success_count}/{len(operations)}"
                elif alg_name == "access_control":
                    granted_count = sum(1 for op in operations if op.get("access_granted", False))
                    summary["success_rates"][alg_name] = f"{granted_count}/{len(operations)}"

        return summary

    def _count_total_operations(self, results: Dict[str, Any]) -> int:
        """统计总操作数"""
        total = 0
        for alg_results in results.values():
            operations = alg_results.get("operations", [])
            total += len(operations)
        return total

    def _save_results(self, results: Dict[str, Any]):
        """保存实验结果"""
        try:
            output_dir = RESULTS_CONFIG.get("base_path", "experiments/results")
            os.makedirs(output_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dvss_ppa_experiment_{timestamp}.json"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            print(f"\nResults saved to: {filepath}")

        except Exception as e:
            print(f"Failed to save results: {e}")


def main():
    """实验运行器测试"""
    print("=" * 50)
    print("DVSS-PPA EXPERIMENT RUNNER TEST")
    print("=" * 50)

    runner = DVSSExperimentRunner()
    results = runner.run_comprehensive_experiment()

    if "error" not in results:
        print("\nExperiment completed successfully!")
        summary = results.get("summary", {})
        print(f"Total algorithms tested: {summary.get('algorithms_tested', 0)}")
        print(f"Total operations: {summary.get('total_operations', 0)}")
    else:
        print(f"Experiment failed: {results['error']}")


if __name__ == "__main__":
    main()