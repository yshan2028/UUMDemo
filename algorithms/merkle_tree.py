#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: merkle_tree.py
Author: yshan2028
Created: 2025-06-13 14:56:13
Description: 
    区块链隐私保护实验中的Merkle树实现
    用于验证数据完整性和构建密码学证明
    支持叶子节点添加、树构建、根哈希计算和路径验证

Dependencies:
    - hashlib: SHA256哈希计算
    - typing: 类型注解支持

Usage:
    from algorithms.merkle_tree import MerkleTree

    # 创建Merkle树
    tree = MerkleTree()
    tree.add_leaf("data1")
    tree.build_tree()
    root = tree.get_root()
"""

import hashlib
import logging
from typing import List, Optional

# 配置日志记录
logger = logging.getLogger(__name__)


class MerkleTree:
    """
    Merkle树实现类

    用于区块链隐私保护实验中的数据完整性验证
    支持构建二叉Merkle树和生成验证路径
    """

    def __init__(self):
        """
        初始化Merkle树
        """
        self.leaves: List[str] = []  # 叶子节点哈希列表
        self.tree: List[List[str]] = []  # 树的各层节点
        self.is_built: bool = False  # 树是否已构建标志

        logger.info("Merkle tree initialized")

    def add_leaf(self, data: str) -> None:
        """
        添加叶子节点数据

        Args:
            data: 要添加的数据字符串
        """
        if self.is_built:
            logger.warning("Tree already built, clearing existing tree")
            self._reset_tree()

        leaf_hash = self._hash(data)
        self.leaves.append(leaf_hash)
        logger.debug(f"Added leaf: {data} -> {leaf_hash[:16]}...")

    def add_multiple_leaves(self, data_list: List[str]) -> None:
        """
        批量添加叶子节点

        Args:
            data_list: 数据字符串列表
        """
        for data in data_list:
            self.add_leaf(data)
        logger.info(f"Added {len(data_list)} leaves to Merkle tree")

    def build_tree(self) -> None:
        """
        构建Merkle树
        """
        if not self.leaves:
            raise ValueError("No leaves available to build Merkle tree")

        if self.is_built:
            logger.info("Tree already built, rebuilding...")

        # 初始化树的第一层（叶子层）
        current_level = self.leaves.copy()
        self.tree = [current_level]

        logger.info(f"Building Merkle tree with {len(current_level)} leaves")

        # 逐层构建树
        while len(current_level) > 1:
            next_level = []

            # 两两配对计算父节点哈希
            for i in range(0, len(current_level), 2):
                left_hash = current_level[i]

                # 如果是奇数个节点，最后一个节点与自己配对
                if i + 1 < len(current_level):
                    right_hash = current_level[i + 1]
                else:
                    right_hash = left_hash

                parent_hash = self._hash(left_hash + right_hash)
                next_level.append(parent_hash)

            self.tree.append(next_level)
            current_level = next_level

            logger.debug(f"Built tree level with {len(next_level)} nodes")

        self.is_built = True
        logger.info(f"Merkle tree built successfully with {len(self.tree)} levels")

    def get_root(self) -> str:
        """
        获取Merkle树根哈希

        Returns:
            str: 根节点哈希值
        """
        if not self.is_built or not self.tree:
            raise ValueError("Tree not built yet, cannot get root")

        root_hash = self.tree[-1][0]
        logger.debug(f"Root hash: {root_hash}")
        return root_hash

    def get_proof(self, data: str) -> List[str]:
        """
        获取指定数据的Merkle证明路径

        Args:
            data: 要证明的数据

        Returns:
            List[str]: 证明路径中的兄弟节点哈希列表
        """
        if not self.is_built:
            raise ValueError("Tree not built yet, cannot generate proof")

        # 查找叶子节点索引
        target_hash = self._hash(data)
        try:
            leaf_index = self.leaves.index(target_hash)
        except ValueError:
            raise ValueError(f"Data not found in tree: {data}")

        proof = []
        current_index = leaf_index

        # 从叶子层向上构建证明路径
        for level in range(len(self.tree) - 1):
            # 计算兄弟节点索引
            if current_index % 2 == 0:  # 当前节点是左子节点
                sibling_index = current_index + 1
            else:  # 当前节点是右子节点
                sibling_index = current_index - 1

            # 添加兄弟节点到证明路径
            if sibling_index < len(self.tree[level]):
                proof.append(self.tree[level][sibling_index])
            else:
                # 如果没有兄弟节点，使用自己
                proof.append(self.tree[level][current_index])

            # 移动到父节点
            current_index = current_index // 2

        logger.debug(f"Generated proof for {data}: {len(proof)} elements")
        return proof

    def verify_proof(self, data: str, proof: List[str], root_hash: str) -> bool:
        """
        验证Merkle证明

        Args:
            data: 要验证的数据
            proof: 证明路径
            root_hash: 预期的根哈希

        Returns:
            bool: 验证是否成功
        """
        current_hash = self._hash(data)

        # 沿着证明路径向上计算
        for sibling_hash in proof:
            # 按字典序决定左右顺序
            if current_hash <= sibling_hash:
                current_hash = self._hash(current_hash + sibling_hash)
            else:
                current_hash = self._hash(sibling_hash + current_hash)

        is_valid = current_hash == root_hash
        logger.debug(f"Proof verification for {data}: {'VALID' if is_valid else 'INVALID'}")
        return is_valid

    def verify_leaf(self, data: str, proof: List[str], root: str) -> bool:
        """
        验证叶子节点（兼容原有接口）

        Args:
            data: 要验证的叶子数据
            proof: 验证路径
            root: Merkle树的根哈希

        Returns:
            bool: 验证结果
        """
        return self.verify_proof(data, proof, root)

    def get_tree_info(self) -> dict:
        """
        获取树的统计信息

        Returns:
            dict: 树的统计信息
        """
        if not self.is_built:
            return {
                "built": False,
                "leaf_count": len(self.leaves),
                "tree_height": 0,
                "total_nodes": 0
            }

        total_nodes = sum(len(level) for level in self.tree)

        return {
            "built": True,
            "leaf_count": len(self.leaves),
            "tree_height": len(self.tree),
            "total_nodes": total_nodes,
            "root_hash": self.get_root()
        }

    def _reset_tree(self) -> None:
        """
        重置树状态
        """
        self.leaves.clear()
        self.tree.clear()
        self.is_built = False

    def _hash(self, data: str) -> str:
        """
        计算SHA256哈希值

        Args:
            data: 输入数据字符串

        Returns:
            str: 十六进制哈希值
        """
        return hashlib.sha256(data.encode('utf-8')).hexdigest()


def main():
    """
    Merkle树功能测试和演示
    """
    print("=" * 60)
    print("MERKLE TREE IMPLEMENTATION TEST")
    print("=" * 60)

    # 创建Merkle树实例
    tree = MerkleTree()

    # 测试数据
    test_data = ["order1", "order2", "order3", "order4", "order5"]

    print(f"\n1. Adding {len(test_data)} data items:")
    print("-" * 40)
    for data in test_data:
        tree.add_leaf(data)
        print(f"Added: {data}")

    # 构建树
    print(f"\n2. Building Merkle tree:")
    print("-" * 40)
    tree.build_tree()

    # 获取树信息
    tree_info = tree.get_tree_info()
    print(f"Tree height: {tree_info['tree_height']}")
    print(f"Total nodes: {tree_info['total_nodes']}")
    print(f"Leaf count: {tree_info['leaf_count']}")

    # 获取根哈希
    root_hash = tree.get_root()
    print(f"Root hash: {root_hash}")

    # 测试证明生成和验证
    print(f"\n3. Testing proof generation and verification:")
    print("-" * 40)

    test_item = "order3"
    try:
        # 生成证明
        proof = tree.get_proof(test_item)
        print(f"Generated proof for '{test_item}': {len(proof)} elements")

        # 验证证明
        is_valid = tree.verify_proof(test_item, proof, root_hash)
        print(f"Proof verification: {'VALID' if is_valid else 'INVALID'}")

        # 测试无效数据
        invalid_item = "invalid_order"
        fake_proof = proof  # 使用相同的证明路径
        is_valid_fake = tree.verify_proof(invalid_item, fake_proof, root_hash)
        print(f"Invalid data verification: {'VALID' if is_valid_fake else 'INVALID'}")

    except Exception as e:
        print(f"Error during proof testing: {str(e)}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()