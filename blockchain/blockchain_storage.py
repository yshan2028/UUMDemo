#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: blockchain_storage.py
Author: yshan2028
Created: 2025-06-13 08:47:13
Description: 区块链存储逻辑
"""

import hashlib
import json
import time
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class Block:
    """区块数据结构"""

    def __init__(self, index: int, timestamp: float, data: dict, previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """计算区块哈希"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()


class BlockchainStorage:
    """区块链存储实现"""

    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self._create_genesis_block()

    def _create_genesis_block(self):
        """创建创世块"""
        genesis_block = Block(0, time.time(), {"message": "Genesis Block"}, "0")
        self.chain.append(genesis_block)
        logger.info("Genesis block created")

    def get_latest_block(self) -> Block:
        """获取最新区块"""
        return self.chain[-1]

    def add_transaction(self, transaction: dict):
        """添加交易到待处理池"""
        self.pending_transactions.append(transaction)

    def mine_pending_transactions(self) -> Block:
        """挖矿处理待处理交易"""
        block = Block(
            len(self.chain),
            time.time(),
            {"transactions": self.pending_transactions},
            self.get_latest_block().hash
        )

        self.chain.append(block)
        self.pending_transactions = []

        logger.info(f"Block mined: {block.hash[:16]}...")
        return block

    def get_chain_info(self) -> dict:
        """获取区块链信息"""
        return {
            "total_blocks": len(self.chain),
            "pending_transactions": len(self.pending_transactions),
            "latest_block_hash": self.get_latest_block().hash
        }