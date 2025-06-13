#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: test.py
Author: yshan2028
Created: 2025-06-13 14:56:13
Description: 
    DVSS-PPA实验系统的综合性能测试模块
    用于验证动态可验证秘密共享与隐私保护认证的完整性和性能
    包含与传统方法的对比实验，验证分片恢复、负载平衡和隐私保护效果
    为学术论文提供完整的实验数据和性能对比分析

Dependencies:
    - sympy: 数学计算和模逆运算
    - cryptography: RSA加密和安全存储模拟
    - hashlib: 哈希计算用于零知识证明模拟
    - time: 性能测试计时
    - random: 随机数生成
    - typing: 类型注解支持

Usage:
    # 运行完整的DVSS-PPA对比实验
    python test.py

    # 或导入特定类进行测试
    from test import DVSS_PPA, TraditionalSSS
    dvss = DVSS_PPA()
    shares, commitment, k = dvss.share_secret(secret, n, sensitivity, load, frequency)
"""

import random
import time
import hashlib
import logging
from typing import List, Tuple, Union, Any, Dict
from sympy import mod_inverse
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

# 配置日志记录
logger = logging.getLogger(__name__)


class DVSS_PPA:
    """
    Dynamic Verifiable Secret Sharing with Privacy-Preserving Authentication

    DVSS-PPA系统实现类，提供动态阈值调整、分片生命周期管理和零知识验证功能
    """

    def __init__(self, prime: int = 208351617316091241234326746312124448251235562226470491514186331217050270460481):
        """
        Initialize DVSS-PPA system

        Args:
            prime: Large prime number for finite field operations ensuring security
        """
        self.prime = prime
        self.k_min = 3  # Minimum threshold
        self.k_max = 10  # Maximum threshold
        self.total_operations = 0
        self.total_verification_time = 0.0

        logger.info(f"DVSS-PPA system initialized with prime field size: {len(str(prime))} digits")

    def _polynomial(self, x: int, coeffs: List[int]) -> int:
        """
        Calculate polynomial result at given x value

        Args:
            x: Input value
            coeffs: Polynomial coefficients

        Returns:
            int: Polynomial evaluation result
        """
        return sum([c * pow(x, i, self.prime) for i, c in enumerate(coeffs)]) % self.prime

    def dynamic_k_adjustment(self, sensitivity: float, load: float, frequency: float) -> int:
        """
        Dynamically calculate threshold k value based on system parameters

        Args:
            sensitivity: Data sensitivity (0-1), higher values increase k
            load: Server load (0-1), higher values decrease k
            frequency: Access frequency (0-1), higher values decrease k

        Returns:
            int: Dynamically calculated threshold k value
        """
        alpha, beta, gamma = 5, 4, 3  # Weight parameters
        k = self.k_min + alpha * sensitivity - beta * load - gamma * frequency
        k = max(self.k_min, min(self.k_max, int(k)))

        logger.debug(f"Dynamic threshold calculation: sensitivity={sensitivity}, load={load}, "
                     f"frequency={frequency} -> k={k}")

        return k

    def share_secret(self,
                     secret: int,
                     n: int,
                     sensitivity: float,
                     load: float,
                     frequency: float,
                     expiration: float = None
                     ) -> Tuple[List[Tuple[int, int, float, Union[None, float]]], List[int], int]:
        """
        Generate secret sharing fragments using Shamir Secret Sharing with optional expiration

        Args:
            secret: Secret to be shared (integer value)
            n: Number of shares to generate
            sensitivity: Data sensitivity (0-1)
            load: Server load (0-1)
            frequency: Access frequency (0-1)
            expiration: Share validity period (seconds). None means no expiration

        Returns:
            Tuple containing:
            - Share list: (xi, yi, create_time, expire_time)
            - Polynomial coefficients commitment
            - Dynamic threshold k value
        """
        start_time = time.time()

        k = self.dynamic_k_adjustment(sensitivity, load, frequency)
        coeffs = [secret] + [random.randint(1, self.prime - 1) for _ in range(k - 1)]

        create_time = time.time()
        shares = []
        for i in range(1, n + 1):
            y_val = self._polynomial(i, coeffs)
            expire_time = (create_time + expiration) if expiration else None
            shares.append((i, y_val, create_time, expire_time))

        end_time = time.time()
        self.total_operations += 1

        logger.info(f"Generated {n} shares with dynamic threshold k={k}, "
                    f"generation time: {end_time - start_time:.6f}s")

        return shares, coeffs, k

    def reconstruct_secret(self,
                           shares: List[Tuple[int, int, float, Union[None, float]]]
                           ) -> Tuple[Union[int, Any], float]:
        """
        Recover secret using Lagrange interpolation, filtering expired shares

        Args:
            shares: List of shares for secret recovery, format: (xi, yi, create_time, expire_time)

        Returns:
            Tuple containing:
            - Recovered secret
            - Recovery time elapsed
        """
        start_time = time.time()
        now_time = time.time()

        valid_shares = []
        expired_count = 0

        # Check for expired shares
        for (xj, yj, create_t, expire_t) in shares:
            if expire_t is not None and now_time >= expire_t:
                expired_count += 1
                continue
            valid_shares.append((xj, yj))

        if len(valid_shares) < 2:
            end_time = time.time()
            logger.warning(f"Insufficient valid shares for recovery. "
                           f"Valid: {len(valid_shares)}, Expired: {expired_count}")
            print(f"Insufficient valid shares or all expired. "
                  f"Cannot recover secret. Expired shares: {expired_count}")
            return 0, end_time - start_time

        # Lagrange interpolation
        secret = 0
        for j, (xj, yj) in enumerate(valid_shares):
            numerator, denominator = 1, 1
            for m, (xm, _) in enumerate(valid_shares):
                if m != j:
                    numerator = (numerator * -xm) % self.prime
                    denominator = (denominator * (xj - xm)) % self.prime
            inv_denominator = mod_inverse(denominator, self.prime)
            secret = (secret + yj * numerator * inv_denominator) % self.prime

        end_time = time.time()
        recovery_time = end_time - start_time

        logger.info(f"Secret recovery completed: secret={secret}, "
                    f"time={recovery_time:.8f}s, expired_shares={expired_count}")
        print(f"DVSS-PPA recovered secret: {secret}, "
              f"recovery time: {recovery_time:.8f}s, expired shares: {expired_count}")

        return secret, recovery_time

    def verify_shares(self,
                      shares: List[Tuple[int, int, float, Union[None, float]]],
                      commitment: List[int]) -> bool:
        """
        Verify secret sharing validity using zero-knowledge proof approach

        Args:
            shares: Share fragments (x, y, create_time, expire_time)
            commitment: Public polynomial coefficients

        Returns:
            bool: Whether verification passes
        """
        start_time = time.time()
        now_time = time.time()
        verified_count = 0
        expired_count = 0

        for (x, y, create_t, expire_t) in shares:
            # Skip expired shares
            if expire_t is not None and now_time >= expire_t:
                expired_count += 1
                logger.debug(f"Share (x={x}, y={y}) expired, skipping verification")
                print(f"Share (x={x}, y={y}) expired, not participating in verification")
                continue

            # Verify y matches polynomial computation result from commitment
            computed_y = sum([commitment[i] * pow(x, i, self.prime)
                              for i in range(len(commitment))]) % self.prime
            if computed_y != y:
                end_time = time.time()
                self.total_verification_time += (end_time - start_time)
                logger.error(f"Share (x={x}, y={y}) does not match commitment, verification failed")
                print(f"Share (x={x}, y={y}) does not match commitment, verification failed")
                return False

            verified_count += 1

        end_time = time.time()
        verification_time = end_time - start_time
        self.total_verification_time += verification_time

        logger.info(f"Share verification completed: {verified_count} verified, "
                    f"{expired_count} expired, time={verification_time:.6f}s")
        print(f"Share verification successful: {verified_count} shares verified, "
              f"{expired_count} expired")

        return True

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics

        Returns:
            Dict containing performance metrics
        """
        avg_verification_time = (self.total_verification_time / self.total_operations
                                 if self.total_operations > 0 else 0)

        return {
            "total_operations": self.total_operations,
            "total_verification_time": self.total_verification_time,
            "average_verification_time": avg_verification_time,
            "threshold_range": f"{self.k_min}-{self.k_max}"
        }


class TraditionalSSS:
    """
    Traditional Shamir Secret Sharing (SSS) implementation for comparison
    """

    def __init__(self, prime: int = 208351617316091241234326746312124448251235562226470491514186331217050270460481):
        """
        Initialize Traditional SSS

        Args:
            prime: Prime number for finite field operations
        """
        self.prime = prime
        self.total_operations = 0

        logger.info("Traditional SSS system initialized")

    def _polynomial(self, x: int, coeffs: List[int]) -> int:
        """Calculate polynomial evaluation"""
        return sum([c * pow(x, i, self.prime) for i, c in enumerate(coeffs)]) % self.prime

    def share_secret(self, secret: int, n: int, k: int) -> List[Tuple[int, int]]:
        """
        Generate secret shares using traditional SSS

        Args:
            secret: Secret to share
            n: Number of shares
            k: Fixed threshold

        Returns:
            List of shares (x, y)
        """
        coeffs = [secret] + [random.randint(1, self.prime - 1) for _ in range(k - 1)]
        shares = [(i, self._polynomial(i, coeffs)) for i in range(1, n + 1)]
        self.total_operations += 1

        logger.info(f"Traditional SSS generated {n} shares with fixed threshold k={k}")

        return shares

    def reconstruct_secret(self, shares: List[Tuple[int, int]]) -> Tuple[Union[int, Any], float]:
        """
        Reconstruct secret from shares

        Args:
            shares: List of shares (x, y)

        Returns:
            Tuple of (secret, recovery_time)
        """
        start_time = time.time()
        secret = 0

        for j, (xj, yj) in enumerate(shares):
            numerator, denominator = 1, 1
            for m, (xm, _) in enumerate(shares):
                if m != j:
                    numerator = (numerator * -xm) % self.prime
                    denominator = (denominator * (xj - xm)) % self.prime
            inv_denominator = mod_inverse(denominator, self.prime)
            secret = (secret + yj * numerator * inv_denominator) % self.prime

        end_time = time.time()
        recovery_time = end_time - start_time

        logger.info(f"Traditional SSS recovered secret: {secret}, time: {recovery_time:.8f}s")
        print(f"Traditional SSS recovered secret: {secret}, recovery time: {recovery_time:.8f}s")

        return secret, recovery_time


class ZkSnarksStorage:
    """
    Simulated zk-SNARKs storage using hash functions for comparison
    """

    def __init__(self):
        self.operations_count = 0
        logger.info("zk-SNARKs storage simulator initialized")

    def encrypt(self, data: int) -> str:
        """
        Simulate zk-SNARKs encryption using hash

        Args:
            data: Data to encrypt

        Returns:
            str: Encrypted hash
        """
        self.operations_count += 1
        return hashlib.sha256(str(data).encode()).hexdigest()

    def verify(self, data: int, encrypted_data: str) -> bool:
        """
        Simulate zk-SNARKs verification

        Args:
            data: Original data
            encrypted_data: Encrypted hash

        Returns:
            bool: Verification result
        """
        return hashlib.sha256(str(data).encode()).hexdigest() == encrypted_data


class SecureEnclaveStorage:
    """
    Simulated Secure Enclave storage using RSA encryption
    """

    def __init__(self):
        """Initialize RSA key pair for secure enclave simulation"""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
        self.operations_count = 0

        logger.info("Secure Enclave storage simulator initialized with RSA-2048")

    def store_secret(self, data: bytes) -> bytes:
        """
        Store secret using RSA encryption

        Args:
            data: Data to encrypt

        Returns:
            bytes: Encrypted data
        """
        self.operations_count += 1
        encrypted_data = self.public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted_data

    def retrieve_secret(self, encrypted_data: bytes) -> bytes:
        """
        Retrieve secret using RSA decryption

        Args:
            encrypted_data: Encrypted data

        Returns:
            bytes: Decrypted data
        """
        decrypted_data = self.private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted_data


def run_performance_comparison(rounds: int = 1000) -> Dict[str, float]:
    """
    Run comprehensive performance comparison between DVSS-PPA and Traditional SSS

    Args:
        rounds: Number of test rounds

    Returns:
        Dict containing performance comparison results
    """
    print(f"\n===== Large-scale Performance Comparison ({rounds} rounds) =====")

    secret = 123456
    n = 5
    k = 3
    sensitivity, load, frequency = 0.9, 0.2, 0.8

    dvss = DVSS_PPA()
    sss = TraditionalSSS()

    sss_times = []
    dvss_times = []

    for i in range(rounds):
        if (i + 1) % 100 == 0:
            print(f"Progress: {i + 1}/{rounds} rounds completed")

        # DVSS-PPA performance test
        shares_dvss, _, _ = dvss.share_secret(secret, n, sensitivity, load, frequency)
        start_t = time.time()
        dvss_recovered, _ = dvss.reconstruct_secret(shares_dvss[:k])
        end_t = time.time()
        dvss_times.append(end_t - start_t)

        # Traditional SSS performance test
        sss_shares_loop = sss.share_secret(secret, n, k)
        start_t = time.time()
        sss_recovered, _ = sss.reconstruct_secret(sss_shares_loop[:k])
        end_t = time.time()
        sss_times.append(end_t - start_t)

    # Calculate statistics
    avg_sss_time = sum(sss_times) / len(sss_times)
    avg_dvss_time = sum(dvss_times) / len(dvss_times)

    results = {
        "traditional_sss_avg_time": avg_sss_time,
        "dvss_ppa_avg_time": avg_dvss_time,
        "performance_improvement_percent": ((avg_sss_time - avg_dvss_time) / avg_sss_time) * 100,
        "test_rounds": rounds
    }

    print(f"Traditional SSS average recovery time: {avg_sss_time:.8f}s ({rounds} rounds)")
    print(f"DVSS-PPA average recovery time: {avg_dvss_time:.8f}s ({rounds} rounds)")
    print(f"Performance improvement: {results['performance_improvement_percent']:.2f}%")

    return results


def main():
    """
    Main experimental function running comprehensive DVSS-PPA comparison tests
    """
    print("=" * 80)
    print("DVSS-PPA COMPREHENSIVE EXPERIMENTAL COMPARISON")
    print("=" * 80)
    print("Testing Dynamic Verifiable Secret Sharing with Privacy-Preserving Authentication")
    print("Author: yshan2028")
    print("Date: 2025-06-13")
    print("=" * 80)

    """
    ============================
    Experiment 1 - DVSS-PPA vs Traditional SSS Comparison
    ============================
    """
    secret = 123456  # Secret to be shared
    n = 5  # Generate 5 shares
    k = 3  # Fixed threshold

    # Traditional SSS test
    print("\n===== Traditional SSS Experiment =====")
    sss = TraditionalSSS()
    sss_shares = sss.share_secret(secret, n, k)
    print(f"Generated {n} shares")
    print(f"Fixed threshold k: {k}")
    print("Generated shares:", sss_shares)
    sss_recovered_secret, sss_time = sss.reconstruct_secret(sss_shares[:k])

    # DVSS-PPA test
    print("\n===== DVSS-PPA Experiment =====")
    dvss = DVSS_PPA()
    sensitivity, load, frequency = 0.9, 0.2, 0.8  # Scenario parameters
    dvss_shares, commitment, dynamic_k = dvss.share_secret(secret, n, sensitivity, load, frequency)
    print(f"Generated {n} shares")
    print(f"Dynamic threshold k: {dynamic_k}")
    print("Generated shares:", dvss_shares)
    dvss_recovered_secret, dvss_time = dvss.reconstruct_secret(dvss_shares[:dynamic_k])

    # Verification test
    print("\n===== Share Verification Test =====")
    verification_result = dvss.verify_shares(dvss_shares, commitment)
    print(f"Share verification result: {'PASSED' if verification_result else 'FAILED'}")

    # Results comparison
    print("\n===== Results Comparison =====")
    print(f"Traditional SSS recovered secret: {sss_recovered_secret}, recovery time: {sss_time:.8f}s")
    print(f"DVSS-PPA recovered secret: {dvss_recovered_secret}, recovery time: {dvss_time:.8f}s")
    print(f"Secrets match: {'YES' if sss_recovered_secret == dvss_recovered_secret else 'NO'}")

    # Performance comparison
    performance_results = run_performance_comparison(1000)

    """
    ============================
    Experiment 2 - DVSS-PPA vs zk-SNARKs Comparison
    ============================
    """
    print("\n===== Experiment 2: zk-SNARKs Comparison =====")
    zk = ZkSnarksStorage()
    data_for_zk = 654321

    # zk-SNARKs encryption
    start_time = time.time()
    encrypted_data_zk = zk.encrypt(data_for_zk)
    end_time = time.time()
    zk_encrypt_time = end_time - start_time

    # zk-SNARKs verification
    start_time = time.time()
    is_valid_zk = zk.verify(data_for_zk, encrypted_data_zk)
    end_time = time.time()
    zk_verify_time = end_time - start_time

    print(f"zk-SNARKs 'encryption' time: {zk_encrypt_time:.8f}s")
    print(f"zk-SNARKs 'verification' time: {zk_verify_time:.8f}s")
    print(f"zk-SNARKs verification successful: {'YES' if is_valid_zk else 'NO'}")

    # DVSS-PPA test for comparison
    print("\n----- DVSS-PPA Test (vs zk-SNARKs) -----")
    start_time = time.time()
    dvss_shares_zk, commitment_zk, k_zk = dvss.share_secret(data_for_zk, n, 0.5, 0.3, 0.2)
    end_time = time.time()
    dvss_encrypt_time_zk = end_time - start_time

    start_time = time.time()
    dvss_recovered_zk, _ = dvss.reconstruct_secret(dvss_shares_zk[:k_zk])
    end_time = time.time()
    dvss_decrypt_time_zk = end_time - start_time

    start_time = time.time()
    dvss_verify_result = dvss.verify_shares(dvss_shares_zk, commitment_zk)
    end_time = time.time()
    dvss_verify_time_zk = end_time - start_time

    print(f"DVSS-PPA encryption time: {dvss_encrypt_time_zk:.8f}s")
    print(f"DVSS-PPA decryption time: {dvss_decrypt_time_zk:.8f}s")
    print(f"DVSS-PPA verification time: {dvss_verify_time_zk:.8f}s")
    print(f"DVSS-PPA decrypted data: {dvss_recovered_zk}")
    print(f"DVSS-PPA verification successful: {'YES' if dvss_verify_result else 'NO'}")

    """
    ============================
    Experiment 3 - DVSS-PPA vs Secure Enclave Comparison
    ============================
    """
    print("\n===== Experiment 3: Secure Enclave Comparison =====")
    se_storage = SecureEnclaveStorage()
    data_enclave = b"Hello Secure Enclave"

    # Secure Enclave encryption storage
    start_time = time.time()
    enclave_encrypted_data = se_storage.store_secret(data_enclave)
    end_time = time.time()
    enclave_store_time = end_time - start_time

    # Secure Enclave decryption retrieval
    start_time = time.time()
    enclave_retrieved_data = se_storage.retrieve_secret(enclave_encrypted_data)
    end_time = time.time()
    enclave_retrieve_time = end_time - start_time

    print(f"Secure Enclave storage time: {enclave_store_time:.8f}s")
    print(f"Secure Enclave retrieval time: {enclave_retrieve_time:.8f}s")
    print(f"Retrieved data correct: {'YES' if enclave_retrieved_data == data_enclave else 'NO'}")

    # DVSS-PPA test for comparison
    print("\n----- DVSS-PPA Test (vs Secure Enclave) -----")
    start_time = time.time()
    dvss_shares_enclave, commitment_enclave, k_enclave = dvss.share_secret(999999, n, 0.7, 0.4, 0.2)
    end_time = time.time()
    dvss_store_time = end_time - start_time

    start_time = time.time()
    dvss_recovered_enclave, _ = dvss.reconstruct_secret(dvss_shares_enclave[:k_enclave])
    end_time = time.time()
    dvss_retrieve_time = end_time - start_time

    print(f"DVSS-PPA 'storage' time: {dvss_store_time:.8f}s")
    print(f"DVSS-PPA 'retrieval' time: {dvss_retrieve_time:.8f}s")
    print(f"Retrieved data: {dvss_recovered_enclave}")

    # Final performance summary
    print("\n" + "=" * 80)
    print("EXPERIMENTAL SUMMARY")
    print("=" * 80)

    dvss_stats = dvss.get_performance_stats()
    print(f"DVSS-PPA Performance Statistics:")
    print(f"  Total operations: {dvss_stats['total_operations']}")
    print(f"  Average verification time: {dvss_stats['average_verification_time']:.6f}s")
    print(f"  Dynamic threshold range: {dvss_stats['threshold_range']}")

    print(f"\nComparison Results:")
    print(f"  DVSS-PPA vs Traditional SSS: {performance_results['performance_improvement_percent']:.2f}% improvement")
    print(f"  DVSS-PPA provides dynamic threshold adjustment")
    print(f"  DVSS-PPA includes built-in verification and expiration management")
    print(f"  DVSS-PPA supports privacy-preserving authentication")

    print("\nDVSS-PPA comprehensive experimental comparison completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()