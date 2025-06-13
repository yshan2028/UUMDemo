#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: shamir.py
Author: yshan2028
Created: 2025-06-13 08:47:13
Description: Shamir秘密共享算法
"""

import random
import time
import logging
from typing import List, Tuple
from sympy import mod_inverse
from config.settings import ALGORITHM_CONFIG

logger = logging.getLogger(__name__)


class ShamirSecretSharing:
    """Shamir秘密共享算法实现"""

    def __init__(self):
        self.prime = ALGORITHM_CONFIG["shamir"]["prime_modulus"]
        self.k_min = ALGORITHM_CONFIG["shamir"]["k_min"]
        self.k_max = ALGORITHM_CONFIG["shamir"]["k_max"]
        self.operations = 0
        self.total_time = 0.0

    def calculate_dynamic_threshold(self, sensitivity: float, load: float, frequency: float) -> int:
        """动态阈值计算"""
        k = self.k_min + 5.0 * sensitivity - 4.0 * load - 3.0 * frequency
        return max(self.k_min, min(self.k_max, int(k)))

    def share_secret(self, secret: int, n: int, sensitivity: float, load: float, frequency: float) -> Tuple[List, List, int]:
        """生成秘密分片"""
        start_time = time.time()

        k = self.calculate_dynamic_threshold(sensitivity, load, frequency)
        coeffs = [secret] + [random.randint(1, self.prime - 1) for _ in range(k - 1)]

        shares = []
        create_time = time.time()
        for i in range(1, n + 1):
            y = sum(coeffs[j] * pow(i, j, self.prime) for j in range(k)) % self.prime
            shares.append((i, y, create_time, None))

        self._update_stats(time.time() - start_time)
        return shares, coeffs, k

    def reconstruct_secret(self, shares: List[Tuple]) -> int:
        """重构秘密"""
        start_time = time.time()

        valid_shares = [(x, y) for x, y, create_t, expire_t in shares
                        if expire_t is None or time.time() < expire_t]

        if len(valid_shares) < 2:
            return 0

        secret = 0
        for j, (xj, yj) in enumerate(valid_shares):
            numerator = denominator = 1
            for m, (xm, _) in enumerate(valid_shares):
                if m != j:
                    numerator = (numerator * -xm) % self.prime
                    denominator = (denominator * (xj - xm)) % self.prime
            secret = (secret + yj * numerator * mod_inverse(denominator, self.prime)) % self.prime

        self._update_stats(time.time() - start_time)
        return secret

    def _update_stats(self, operation_time: float):
        """更新性能统计"""
        self.operations += 1
        self.total_time += operation_time

    def get_performance_stats(self) -> dict:
        """获取性能统计"""
        if self.operations == 0:
            return {"operations": 0, "average_time": 0, "total_time": 0}
        return {
            "operations": self.operations,
            "average_time": self.total_time / self.operations,
            "total_time": self.total_time
        }