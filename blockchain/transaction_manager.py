#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: transaction_manager.py
Author: yshan2028
Created: 2025-06-13 14:56:13
Description: 
    [请在此处添加文件描述]

Dependencies:
    [请在此处列出主要依赖]

Usage:
    [请在此处添加使用说明]
"""

from hashlib import sha256
import time

class TransactionManager:
    """
    管理区块链交易，包括提交、状态查询和交易日志。
    """

    def __init__(self, blockchain):
        """
        初始化交易管理器。

        :param blockchain: 区块链存储实例。
        """
        self.blockchain = blockchain
        self.transaction_log = []  # 用于存储交易的日志信息

    def submit_transaction(self, transaction_data: dict) -> str:
        """
        提交交易到区块链。

        :param transaction_data: 包含订单信息的交易数据。
        :return: 交易哈希值。
        """
        try:
            timestamp = time.time()
            transaction_data["timestamp"] = timestamp
            transaction_hash = sha256(str(transaction_data).encode()).hexdigest()
            self.blockchain.add_transaction({
                "transaction_hash": transaction_hash,
                "transaction_data": transaction_data,
                "timestamp": timestamp,
            })
            self.transaction_log.append({
                "transaction_hash": transaction_hash,
                "status": "submitted",
                "timestamp": timestamp,
            })
            print(f"[INFO] 交易已提交，哈希值: {transaction_hash}")
            return transaction_hash
        except Exception as e:
            print(f"[ERROR] 提交交易失败: {e}")
            return ""

    def query_transaction_status(self, transaction_hash: str) -> str:
        """
        查询交易的状态。

        :param transaction_hash: 要查询的交易哈希值。
        :return: 交易状态。
        """
        for log in self.transaction_log:
            if log["transaction_hash"] == transaction_hash:
                print(f"[INFO] 交易状态: {log['status']} (哈希值: {transaction_hash})")
                return log["status"]

        print(f"[ERROR] 未找到交易，哈希值: {transaction_hash}")
        return "not_found"

    def update_transaction_status(self, transaction_hash: str, new_status: str):
        """
        更新交易的状态。

        :param transaction_hash: 要更新的交易哈希值。
        :param new_status: 新的交易状态。
        """
        for log in self.transaction_log:
            if log["transaction_hash"] == transaction_hash:
                log["status"] = new_status
                print(f"[INFO] 交易状态已更新为: {new_status} (哈希值: {transaction_hash})")
                return

        print(f"[ERROR] 更新状态失败，未找到交易，哈希值: {transaction_hash}")

    def get_all_transactions(self) -> list:
        """
        获取所有交易的日志信息。

        :return: 包含交易日志的列表。
        """
        return self.transaction_log

if __name__ == "__main__":
    from blockchain.blockchain_storage import BlockchainStorage

    # 测试 TransactionManager
    blockchain = BlockchainStorage("Hyperledger")
    transaction_manager = TransactionManager(blockchain)

    # 提交交易
    transaction_data = {"order_id": "ORD12345", "amount": 150.0, "status": "Paid"}
    tx_hash = transaction_manager.submit_transaction(transaction_data)

    # 查询交易状态
    transaction_manager.query_transaction_status(tx_hash)

    # 更新交易状态
    transaction_manager.update_transaction_status(tx_hash, "confirmed")

    # 获取所有交易日志
    print("所有交易日志:", transaction_manager.get_all_transactions())
