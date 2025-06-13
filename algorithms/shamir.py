#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: shamir.py
Author: yshan2028
Created: 2025-06-13 14:56:13
Description: 
    区块链隐私保护实验中的Shamir秘密共享算法实现
    用于将敏感数据分片存储，提供k-out-of-n的隐私保护机制
    支持秘密分片生成和重建，适用于分布式隐私数据保护场景

Dependencies:
    - random: 随机数生成，用于多项式系数
    - typing: 类型注解支持
    - logging: 算法执行日志记录

Usage:
    from algorithms.shamir import ShamirSecretSharing

    # 创建Shamir实例
    shamir = ShamirSecretSharing()

    # 生成分片
    shares = shamir.generate_shares(secret=12345, n=5, t=3)

    # 重建秘密
    reconstructed = shamir.reconstruct_secret(shares[:3], t=3)
"""

import random
import logging
from typing import List, Tuple, Optional

# 配置日志记录
logger = logging.getLogger(__name__)


class ShamirSecretSharing:
    """
    Shamir秘密共享算法实现

    基于拉格朗日插值的(t,n)门限秘密共享方案
    用于区块链隐私保护实验中的敏感数据分片存储
    """

    def __init__(self, prime: int = 2 ** 127 - 1):
        """
        初始化Shamir秘密共享系统

        Args:
            prime: 有限域的素数模数，默认使用Mersenne素数
        """
        self.prime = prime
        self.shares_generated = 0
        self.secrets_reconstructed = 0

        logger.info(f"Shamir Secret Sharing initialized with prime modulus: {prime}")

    def generate_shares(self, secret: int, n: int, t: int) -> List[Tuple[int, int]]:
        """
        生成n个秘密分片，至少需要t个分片才能重建秘密

        Args:
            secret: 要分享的秘密值
            n: 总分片数量
            t: 重建秘密所需的最小分片数（阈值）

        Returns:
            List[Tuple[int, int]]: 分片列表，每个分片为(x, y)坐标点

        Raises:
            ValueError: 当参数不合法时抛出异常
        """
        # 参数验证
        if t > n:
            raise ValueError("Threshold t cannot be greater than total shares n")
        if t < 2:
            raise ValueError("Threshold t must be at least 2")
        if n < 2:
            raise ValueError("Total shares n must be at least 2")
        if secret < 0 or secret >= self.prime:
            raise ValueError(f"Secret must be in range [0, {self.prime})")

        logger.info(f"Generating {n} shares with threshold {t} for secret")

        # 生成t-1个随机系数构建多项式 f(x) = a0 + a1*x + a2*x^2 + ... + a(t-1)*x^(t-1)
        # 其中a0 = secret，其余系数随机生成
        coefficients = [secret] + [random.randint(1, self.prime - 1) for _ in range(t - 1)]

        logger.debug(f"Generated polynomial with {len(coefficients)} coefficients")

        def evaluate_polynomial(x: int) -> int:
            """
            计算多项式在x点的值
            """
            result = 0
            x_power = 1

            for coeff in coefficients:
                result = (result + coeff * x_power) % self.prime
                x_power = (x_power * x) % self.prime

            return result

        # 计算n个分片点 (i, f(i))，i从1开始
        shares = []
        for i in range(1, n + 1):
            y_value = evaluate_polynomial(i)
            shares.append((i, y_value))

        self.shares_generated += 1
        logger.info(f"Successfully generated {n} shares")

        return shares

    def reconstruct_secret(self, shares: List[Tuple[int, int]], t: int) -> int:
        """
        使用拉格朗日插值法从t个分片重建秘密

        Args:
            shares: 用于重建的分片列表
            t: 重建所需的分片数量

        Returns:
            int: 重建的秘密值

        Raises:
            ValueError: 当分片数量不足或分片无效时抛出异常
        """
        if len(shares) < t:
            raise ValueError(f"Need at least {t} shares to reconstruct, got {len(shares)}")

        if t < 2:
            raise ValueError("Need at least 2 shares to reconstruct secret")

        logger.info(f"Reconstructing secret from {len(shares)} shares (threshold: {t})")

        # 只使用前t个分片进行重建
        selected_shares = shares[:t]

        # 验证分片的x坐标是否唯一
        x_coordinates = [x for x, y in selected_shares]
        if len(set(x_coordinates)) != len(x_coordinates):
            raise ValueError("Duplicate x coordinates found in shares")

        # 使用拉格朗日插值计算f(0)，即原始秘密
        def lagrange_interpolation(target_x: int, points: List[Tuple[int, int]]) -> int:
            """
            拉格朗日插值计算多项式在target_x处的值
            """
            total = 0

            for i, (xi, yi) in enumerate(points):
                # 计算拉格朗日基函数 Li(target_x)
                numerator = 1
                denominator = 1

                for j, (xj, _) in enumerate(points):
                    if i != j:
                        numerator = (numerator * (target_x - xj)) % self.prime
                        denominator = (denominator * (xi - xj)) % self.prime

                # 计算模逆元
                denominator_inv = pow(denominator, -1, self.prime)

                # 累加 yi * Li(target_x)
                lagrange_term = (yi * numerator * denominator_inv) % self.prime
                total = (total + lagrange_term) % self.prime

            return total

        # 计算f(0)得到原始秘密
        reconstructed_secret = lagrange_interpolation(0, selected_shares)

        self.secrets_reconstructed += 1
        logger.info(f"Successfully reconstructed secret using {t} shares")

        return reconstructed_secret

    def verify_shares(self, shares: List[Tuple[int, int]], secret: int, t: int) -> bool:
        """
        验证分片是否能正确重建指定的秘密

        Args:
            shares: 要验证的分片
            secret: 预期的秘密值
            t: 阈值

        Returns:
            bool: 验证是否成功
        """
        try:
            reconstructed = self.reconstruct_secret(shares, t)
            is_valid = reconstructed == secret

            logger.info(f"Share verification: {'PASSED' if is_valid else 'FAILED'}")
            return is_valid

        except Exception as e:
            logger.error(f"Share verification failed: {str(e)}")
            return False

    def get_statistics(self) -> dict:
        """
        获取算法执行统计信息

        Returns:
            dict: 统计信息字典
        """
        return {
            "prime_modulus": self.prime,
            "shares_generated": self.shares_generated,
            "secrets_reconstructed": self.secrets_reconstructed
        }

    def split_data(self, data: str, n: int, t: int) -> List[Tuple[int, str]]:
        """
        将字符串数据转换为整数并分片

        Args:
            data: 要分片的字符串数据
            n: 分片总数
            t: 阈值

        Returns:
            List[Tuple[int, str]]: 分片列表，格式为(x, hex_encoded_y)
        """
        # 将字符串转换为整数（使用UTF-8编码）
        data_bytes = data.encode('utf-8')
        data_int = int.from_bytes(data_bytes, byteorder='big')

        if data_int >= self.prime:
            raise ValueError(f"Data too large for current prime modulus")

        # 生成数值分片
        numerical_shares = self.generate_shares(data_int, n, t)

        # 转换为十六进制字符串格式
        string_shares = [(x, hex(y)) for x, y in numerical_shares]

        logger.info(f"Split string data into {n} shares")
        return string_shares

    def combine_data(self, shares: List[Tuple[int, str]], t: int) -> str:
        """
        从字符串分片重建原始数据

        Args:
            shares: 字符串格式的分片
            t: 阈值

        Returns:
            str: 重建的原始字符串
        """
        # 转换回数值分片
        numerical_shares = [(x, int(y, 16)) for x, y in shares]

        # 重建数值秘密
        data_int = self.reconstruct_secret(numerical_shares, t)

        # 转换回字符串
        try:
            # 计算字节长度
            byte_length = (data_int.bit_length() + 7) // 8
            data_bytes = data_int.to_bytes(byte_length, byteorder='big')
            original_data = data_bytes.decode('utf-8')

            logger.info("Successfully reconstructed string data")
            return original_data

        except Exception as e:
            logger.error(f"Failed to decode reconstructed data: {str(e)}")
            raise ValueError("Failed to decode reconstructed data")


def main():
    """
    Shamir秘密共享算法测试和演示
    """
    print("=" * 60)
    print("SHAMIR SECRET SHARING ALGORITHM TEST")
    print("=" * 60)

    # 创建Shamir实例
    shamir = ShamirSecretSharing()

    # 测试参数
    test_secret = 12345
    n_shares = 5
    threshold = 3

    print(f"\n1. Testing numerical secret sharing:")
    print("-" * 40)
    print(f"Original secret: {test_secret}")
    print(f"Total shares: {n_shares}")
    print(f"Threshold: {threshold}")

    try:
        # 生成分片
        shares = shamir.generate_shares(test_secret, n_shares, threshold)
        print(f"Generated shares: {shares}")

        # 重建秘密（使用最少数量的分片）
        reconstructed = shamir.reconstruct_secret(shares[:threshold], threshold)
        print(f"Reconstructed secret: {reconstructed}")
        print(f"Reconstruction successful: {reconstructed == test_secret}")

        # 验证分片
        is_valid = shamir.verify_shares(shares, test_secret, threshold)
        print(f"Share verification: {'PASSED' if is_valid else 'FAILED'}")

    except Exception as e:
        print(f"Error in numerical test: {str(e)}")

    # 测试字符串数据分片
    print(f"\n2. Testing string data sharing:")
    print("-" * 40)

    test_data = "sensitive_order_info_12345"
    print(f"Original data: {test_data}")

    try:
        # 分片字符串数据
        string_shares = shamir.split_data(test_data, n_shares, threshold)
        print(f"Generated {len(string_shares)} string shares")

        # 重建字符串数据
        reconstructed_data = shamir.combine_data(string_shares[:threshold], threshold)
        print(f"Reconstructed data: {reconstructed_data}")
        print(f"Data reconstruction successful: {reconstructed_data == test_data}")

    except Exception as e:
        print(f"Error in string test: {str(e)}")

    # 显示统计信息
    print(f"\n3. Algorithm statistics:")
    print("-" * 40)
    stats = shamir.get_statistics()
    print(f"Prime modulus: {stats['prime_modulus']}")
    print(f"Shares generated: {stats['shares_generated']}")
    print(f"Secrets reconstructed: {stats['secrets_reconstructed']}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()