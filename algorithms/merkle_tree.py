#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: merkle_tree.py
Author: yshan2028
Created: 2025-06-13 08:47:13
Description: Merkle树生成与验证
"""

import hashlib
import time
import logging
from typing import List

logger = logging.getLogger(__name__)


class MerkleTree:
    """Merkle树实现"""

    def __init__(self):
        self.root_hash = None
        self.leaves = []
        self.operations = 0
        self.total_time = 0.0

    def _hash_data(self, data: str) -> str:
        """计算数据哈希"""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def build_tree(self, data_blocks: List[str]) -> str:
        """构建Merkle树"""
        start_time = time.time()

        if not data_blocks:
            return ""

        current_level = [self._hash_data(block) for block in data_blocks]
        self.leaves = current_level[:]

        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                combined = self._hash_data(left + right)
                next_level.append(combined)
            current_level = next_level

        self.root_hash = current_level[0]
        self._update_stats(time.time() - start_time)
        return self.root_hash

    def generate_proof(self, data_block: str) -> List[dict]:
        """生成Merkle证明"""
        if not self.root_hash:
            return []

        target_hash = self._hash_data(data_block)
        if target_hash not in self.leaves:
            return []

        proof = []
        index = self.leaves.index(target_hash)
        current_level = self.leaves[:]

        while len(current_level) > 1:
            if index % 2 == 0:
                sibling_index = index + 1 if index + 1 < len(current_level) else index
                direction = "right"
            else:
                sibling_index = index - 1
                direction = "left"

            if sibling_index < len(current_level):
                proof.append({
                    "hash": current_level[sibling_index],
                    "direction": direction
                })

            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                next_level.append(self._hash_data(left + right))

            current_level = next_level
            index //= 2

        return proof

    def verify_proof(self, data_block: str, proof: List[dict], root_hash: str) -> bool:
        """验证Merkle证明"""
        current_hash = self._hash_data(data_block)

        for element in proof:
            sibling_hash = element["hash"]
            direction = element["direction"]

            if direction == "left":
                current_hash = self._hash_data(sibling_hash + current_hash)
            else:
                current_hash = self._hash_data(current_hash + sibling_hash)

        return current_hash == root_hash

    def _update_stats(self, operation_time: float):
        """更新性能统计"""
        self.operations += 1
        self.total_time += operation_time