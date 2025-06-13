#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: transaction_manager.py
Author: yshan2028
Created: 2025-06-13 08:47:13
Description: 交易管理模块
"""

import time
import hashlib
import logging
from utils.helpers import generate_id

logger = logging.getLogger(__name__)


class Transaction:
    """交易数据结构"""

    def __init__(self, tx_type: str, from_address: str, to_address: str, data: dict):
        self.tx_id = generate_id("TX")
        self.tx_type = tx_type
        self.from_address = from_address
        self.to_address = to_address
        self.data = data
        self.timestamp = time.time()


class TransactionManager:
    """交易管理器"""

    def __init__(self, blockchain_storage):
        self.blockchain = blockchain_storage
        self.transaction_pool = []
        self.total_transactions = 0

    def create_transaction(self, tx_type: str, from_address: str, to_address: str, data: dict) -> Transaction:
        """创建新交易"""
        transaction = Transaction(tx_type, from_address, to_address, data)
        logger.debug(f"Transaction created: {transaction.tx_id}")
        return transaction

    def submit_transaction(self, transaction: Transaction) -> bool:
        """提交交易到交易池"""
        try:
            self.transaction_pool.append(transaction)
            self.total_transactions += 1
            logger.info(f"Transaction submitted: {transaction.tx_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to submit transaction: {e}")
            return False

    def process_transactions(self) -> dict:
        """处理所有待处理交易"""
        if not self.transaction_pool:
            return {"processed": 0}

        # 将交易添加到区块链
        for tx in self.transaction_pool:
            self.blockchain.add_transaction({
                "tx_id": tx.tx_id,
                "type": tx.tx_type,
                "from": tx.from_address,
                "to": tx.to_address,
                "data": tx.data,
                "timestamp": tx.timestamp
            })

        processed_count = len(self.transaction_pool)
        self.transaction_pool = []

        # 挖矿
        self.blockchain.mine_pending_transactions()

        logger.info(f"Processed {processed_count} transactions")
        return {"processed": processed_count}

    def get_stats(self) -> dict:
        """获取交易统计"""
        return {
            "total_transactions": self.total_transactions,
            "pending_transactions": len(self.transaction_pool)
        }