#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: blockchain_storage.py
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

class BlockchainStorage:
    """
    实现区块链存储逻辑，模拟将订单的哈希存储到区块链上。
    """

    def __init__(self, blockchain_type="Hyperledger"):
        """
        初始化区块链存储实例。

        :param blockchain_type: 区块链类型 ("Hyperledger" 或 "Ethereum")。
        """
        self.blockchain_type = blockchain_type
        self.chain = []  # 模拟区块链链条

    def add_transaction(self, transaction_data: dict) -> str:
        """
        添加交易到区块链。

        :param transaction_data: 包含订单 ID 和相关数据的交易字典。
        :return: 生成的交易哈希值。
        """
        timestamp = time.time()
        transaction_data["timestamp"] = timestamp
        transaction_hash = sha256(str(transaction_data).encode()).hexdigest()

        block = {
            "transaction_hash": transaction_hash,
            "transaction_data": transaction_data,
            "timestamp": timestamp,
        }
        self.chain.append(block)
        print(f"[INFO] 交易已添加到区块链，哈希值: {transaction_hash}")
        return transaction_hash

    def verify_transaction(self, transaction_hash: str) -> bool:
        """
        验证区块链中是否存在指定交易。

        :param transaction_hash: 要验证的交易哈希值。
        :return: 布尔值，表示交易是否存在。
        """
        for block in self.chain:
            if block["transaction_hash"] == transaction_hash:
                print(f"[INFO] 交易验证成功，哈希值: {transaction_hash}")
                return True
        print(f"[ERROR] 未找到交易，哈希值: {transaction_hash}")
        return False

    def get_chain(self) -> list:
        """
        获取整个区块链的链条。

        :return: 区块链的链条列表。
        """
        return self.chain

if __name__ == "__main__":
    # 测试区块链存储功能
    blockchain = BlockchainStorage("Hyperledger")
    transaction_data = {"order_id": "ORD12345", "amount": 100.0, "status": "Paid"}
    tx_hash = blockchain.add_transaction(transaction_data)
    blockchain.verify_transaction(tx_hash)
    print("当前区块链链条:", blockchain.get_chain())
