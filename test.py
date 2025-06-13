#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: test.py
Author: yshan2028
Created: 2025-06-13 14:56:13
Description: 
    [请在此处添加文件描述]

Dependencies:
    [请在此处列出主要依赖]

Usage:
    [请在此处添加使用说明]
"""

import random
import time
from typing import List, Tuple, Union, Any
from sympy import mod_inverse

"""
在本文件中，实验主要分为三大部分：
1. DVSS-PPA 与 Traditional SSS 的对比（实验 1）
2. DVSS-PPA 与 zk-SNARKs 的对比（实验 2）
3. DVSS-PPA 与 Secure Enclave（模拟 SGX） 的对比（实验 3）
"""

class DVSS_PPA:
    def __init__(self, prime: int = 208351617316091241234326746312124448251235562226470491514186331217050270460481):
        """
        初始化动态可验证秘密共享（DVSS-PPA）系统
        :param prime: 选定的一个大素数，用于有限域上的数学运算，以确保安全性
        """
        self.prime = prime
        self.k_min = 3  # 最小阈值
        self.k_max = 10  # 最大阈值

    def _polynomial(self, x: int, coeffs: List[int]) -> int:
        """
        计算给定 x 值处的多项式结果
        """
        return sum([c * pow(x, i, self.prime) for i, c in enumerate(coeffs)]) % self.prime

    def dynamic_k_adjustment(self, sensitivity: float, load: float, frequency: float) -> int:
        """
        动态计算 k 值
        :param sensitivity: 数据敏感度 (0-1) 之间，越高则 k 值越大
        :param load: 服务器负载 (0-1) 之间，越高则 k 值越小
        :param frequency: 访问频率 (0-1) 之间，越高则 k 值越小
        :return: 动态计算的 k 值
        """
        alpha, beta, gamma = 5, 4, 3  # 权重参数
        k = self.k_min + alpha * sensitivity - beta * load - gamma * frequency
        k = max(self.k_min, min(self.k_max, int(k)))  # 限制 k 值范围
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
        生成秘密共享片段（Shamir Secret Sharing），可选地为每个分片设定过期时间
        :param secret: 需要共享的秘密（整数值）
        :param n: 生成 n 份片段（可分配的总份额数）
        :param sensitivity: 数据敏感度 (0-1)
        :param load: 服务器负载 (0-1)
        :param frequency: 访问频率 (0-1)
        :param expiration: 分片有效期（单位：秒）。若为 None，则表示不过期。
        :return: (共享片段列表, 多项式系数 commitment, 动态 k 值)
                 共享片段列表格式: (xi, yi, create_time, expire_time)
        """
        k = self.dynamic_k_adjustment(sensitivity, load, frequency)  # 计算动态 k
        coeffs = [secret] + [random.randint(1, self.prime - 1) for _ in range(k - 1)]

        create_time = time.time()
        shares = []
        for i in range(1, n + 1):
            y_val = self._polynomial(i, coeffs)
            # 如果设置了过期时长，则计算过期时间
            expire_time = (create_time + expiration) if expiration else None
            # 在元组中额外保存创建时间和过期时间
            shares.append((i, y_val, create_time, expire_time))

        return shares, coeffs, k

    # def reconstruct_secret(self,
    #                        shares: List[Tuple[int, int, float, Union[None, float]]]
    #                        ) -> Tuple[Union[int, Any], float]:
    #     """
    #     通过拉格朗日插值法恢复秘密，支持过滤过期分片。
    #     shares 的格式: (x_i, y_i, create_time, expire_time)
    #     返回 (恢复后的秘密, 恢复时长)
    #     """
    #     start_time = time.time()
    #     now_time = time.time()
    #
    #     valid_shares = []
    #     expired_shares = []
    #
    #     # 检查分片是否过期
    #     for (xj, yj, create_t, expire_t) in shares:
    #         # 若过期时间不为空，且当前时间已经超过过期时间，则认为该分片过期
    #         if expire_t is not None and now_time >= expire_t:
    #             expired_shares.append((xj, yj, create_t, expire_t))
    #         else:
    #             valid_shares.append((xj, yj))
    #
    #     # 打印出过期的分片信息
    #     for (xj, yj, c_t, e_t) in expired_shares:
    #         print(f"分片 (x={xj}, y={yj}) 已过期。 创建时间: {time.ctime(c_t)}, 过期时间: {time.ctime(e_t)}")
    #
    #     if len(valid_shares) < 2:
    #         end_time = time.time()
    #         print(f"有效分片数量不足（{len(valid_shares)} 个），无法恢复秘密。过期分片数：{len(expired_shares)}")
    #         return 0, end_time - start_time
    #
    #     # 拉格朗日插值
    #     secret = 0
    #     for j, (xj, yj) in enumerate(valid_shares):
    #         numerator, denominator = 1, 1
    #         for m, (xm, _) in enumerate(valid_shares):
    #             if m != j:
    #                 numerator = (numerator * -xm) % self.prime
    #                 denominator = (denominator * (xj - xm)) % self.prime
    #         secret = (secret + yj * numerator * mod_inverse(denominator, self.prime)) % self.prime
    #
    #     end_time = time.time()
    #     print(f"DVSS-PPA 恢复的秘密值: {secret}, 恢复时间: {end_time - start_time:.8f} 秒，"
    #           f"过期分片数: {len(expired_shares)}")
    #     return secret, end_time - start_time

    def reconstruct_secret(self,
                           shares: List[Tuple[int, int, float, Union[None, float]]]
                           ) -> Tuple[Union[int, Any], float]:
        """
        通过拉格朗日插值法恢复秘密，支持过滤过期分片
        :param shares: 用于恢复秘密的片段列表，每个片段格式为 (xi, yi, create_time, expire_time)
        :return: (恢复后的秘密, 恢复耗时)
        """
        start_time = time.time()
        now_time = time.time()

        valid_shares = []
        expired_count = 0

        # 检查分片是否过期
        for (xj, yj, create_t, expire_t) in shares:
            if expire_t is not None and now_time >= expire_t:
                # 说明该分片已过期，丢弃并统计
                expired_count += 1
                continue
            valid_shares.append((xj, yj))

        if len(valid_shares) < 2:
            # 如果有效分片数量太少，无法进行拉格朗日插值
            end_time = time.time()
            print(f"有效分片数量不足或全部过期，无法恢复秘密，共有 {expired_count} 个过期分片。")
            return 0, end_time - start_time

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
        print(f"DVSS-PPA 恢复的秘密值: {secret}, 恢复耗时: {end_time - start_time:.8f} 秒，过期分片: {expired_count} 个")
        return secret, end_time - start_time

    # def verify_shares(self,
    #                   shares: List[Tuple[int, int, float, Union[None, float]]],
    #                   commitment: List[int]) -> bool:
    #     """
    #     使用零知识证明（ZKP）思路验证秘密共享的有效性
    #     :param shares: 共享片段 (xi, yi, create_time, expire_time)
    #     :param commitment: 公开的多项式系数
    #     :return: 验证是否通过
    #     """
    #     # 校验多项式
    #     for (x, y, _, _) in shares:
    #         computed_y = sum([commitment[i] * pow(x, i, self.prime) for i in range(len(commitment))]) % self.prime
    #         if computed_y != y:
    #             return False
    #     return True

    def verify_shares(self,
                      shares: List[Tuple[int, int, float, Union[None, float]]],
                      commitment: List[int]) -> bool:
        """
        使用零知识证明思路验证秘密共享的有效性，若分片过期也视为无效
        shares: (x, y, create_time, expire_time)
        """
        now_time = time.time()
        for (x, y, create_t, expire_t) in shares:
            # 若过期，则此分片不再参与验证，可直接忽视或输出提示
            if expire_t is not None and now_time >= expire_t:
                print(f"分片 (x={x}, y={y}) 已过期, 不参与验证")
                continue

            # 校验 y 是否与 commitment 对应的多项式计算结果一致
            computed_y = sum([commitment[i] * pow(x, i, self.prime) for i in range(len(commitment))]) % self.prime
            if computed_y != y:
                print(f"分片 (x={x}, y={y}) 与承诺不符, 验证失败")
                return False
        return True


class TraditionalSSS:
    def __init__(self, prime: int = 208351617316091241234326746312124448251235562226470491514186331217050270460481):
        """
        传统 Shamir Secret Sharing (SSS)
        """
        self.prime = prime

    def _polynomial(self, x: int, coeffs: List[int]) -> int:
        return sum([c * pow(x, i, self.prime) for i, c in enumerate(coeffs)]) % self.prime

    def share_secret(self, secret: int, n: int, k: int) -> List[Tuple[int, int]]:
        coeffs = [secret] + [random.randint(1, self.prime - 1) for _ in range(k - 1)]
        shares = [(i, self._polynomial(i, coeffs)) for i in range(1, n + 1)]
        return shares

    def reconstruct_secret(self, shares: List[Tuple[int, int]]) -> Tuple[Union[int, Any], float]:
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
        print(f"传统 SSS 恢复的秘密值: {secret}, 恢复时间: {end_time - start_time:.8f} 秒")
        return secret, end_time - start_time

"""
下方为使用 DVSS-PPA 与其他方式对比的部分，不做改动。
实验 2 - DVSS-PPA 与 zk-SNARKs 对比
实验 3 - DVSS-PPA 与 Secure Enclave (macOS) 对比
可保持原样
"""
import hashlib

class ZkSnarksStorage:
    def encrypt(self, data: int) -> str:
        return hashlib.sha256(str(data).encode()).hexdigest()

    def verify(self, data: int, encrypted_data: str) -> bool:
        return hashlib.sha256(str(data).encode()).hexdigest() == encrypted_data


from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

class SecureEnclaveStorage:
    def __init__(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()

    def store_secret(self, data: bytes) -> bytes:
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
        decrypted_data = self.private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted_data



if __name__ == "__main__":
    """
    ============================
    实验 1 - DVSS-PPA 与传统 SSS 对比
    ============================
    """
    secret = 123456  # 需要共享的秘密
    n = 5  # 生成 5 份片段
    k = 3  # 固定阈值

    # 传统 SSS 测试
    print("\n===== 传统 SSS 实验 =====")
    sss = TraditionalSSS()
    sss_shares = sss.share_secret(secret, n, k)
    print(f"生成 {n} 份")
    print(f"固定计算 k 值:{k}")
    print("生成的片段:", sss_shares)
    sss_recovered_secret, sss_time = sss.reconstruct_secret(sss_shares[:k])

    # DVSS-PPA 测试
    print("\n===== DVSS-PPA 实验 =====")
    dvss = DVSS_PPA()
    sensitivity, load, frequency = 0.9, 0.2, 0.8  # 假设场景参数
    dvss_shares, commitment, dynamic_k = dvss.share_secret(secret, n, sensitivity, load, frequency)
    print(f"生成 {n} 份")
    print(f"动态计算的 k 值: {dynamic_k}")
    print("生成的片段:", dvss_shares)
    dvss_recovered_secret, dvss_time = dvss.reconstruct_secret(dvss_shares[:dynamic_k])

    # 结果对比
    print("\n===== 结果对比 =====")
    print(f"传统 SSS 恢复的秘密: {sss_recovered_secret}，恢复时间: {sss_time:.8f} 秒")
    print(f"DVSS-PPA 恢复的秘密: {dvss_recovered_secret}，恢复时间: {dvss_time:.8f} 秒")
    print(f"秘密是否一致: {'是' if sss_recovered_secret == dvss_recovered_secret else '否'}")

    # 额外做大量测试
    print("\n===== 大量测试 DVSS-PPA 与 SSS 性能对比 =====")
    test_rounds = 1000
    sss_times = []
    dvss_times = []

    for _ in range(test_rounds):
        # DVSS-PPA
        shares_dvss, _, _ = dvss.share_secret(secret, n, sensitivity, load, frequency)
        start_t = time.time()
        dvss_recovered, _ = dvss.reconstruct_secret(shares_dvss[:k])
        end_t = time.time()
        dvss_times.append(end_t - start_t)

        # SSS
        sss_shares_loop = sss.share_secret(secret, n, k)
        start_t = time.time()
        sss_recovered, _ = sss.reconstruct_secret(sss_shares_loop[:k])
        end_t = time.time()
        sss_times.append(end_t - start_t)

    print(f"SSS 平均恢复时间: {sum(sss_times) / len(sss_times):.8f} 秒 (共 {test_rounds} 次)")
    print(f"DVSS-PPA 平均恢复时间: {sum(dvss_times) / len(dvss_times):.8f} 秒 (共 {test_rounds} 次)")


    """
    ============================
    实验 2 - DVSS-PPA 与 zk-SNARKs 对比
    ============================
    使用简单哈希来模拟 zk-SNARKs 的加密和验证
    """
    print("\n===== 实验 2：zk-SNARKs 对比 =====")
    zk = ZkSnarksStorage()
    data_for_zk = 654321

    # zk-SNARKs 加密
    start_time = time.time()
    encrypted_data_zk = zk.encrypt(data_for_zk)
    end_time = time.time()
    zk_encrypt_time = end_time - start_time

    # zk-SNARKs 验证
    start_time = time.time()
    is_valid_zk = zk.verify(data_for_zk, encrypted_data_zk)
    end_time = time.time()
    zk_verify_time = end_time - start_time

    print(f"zk-SNARKs '加密' 耗时: {zk_encrypt_time:.8f} 秒")
    print(f"zk-SNARKs '验证' 耗时: {zk_verify_time:.8f} 秒")
    print(f"zk-SNARKs 验证是否成功: {'是' if is_valid_zk else '否'}")

    # DVSS-PPA 测试
    print("\n----- DVSS-PPA 测试（与 zk-SNARKs 对比）-----")
    start_time = time.time()
    dvss_shares_zk, _, k_zk = dvss.share_secret(data_for_zk, n, 0.5, 0.3, 0.2)
    end_time = time.time()
    dvss_encrypt_time_zk = end_time - start_time

    start_time = time.time()
    dvss_recovered_zk, _ = dvss.reconstruct_secret(dvss_shares_zk[:k_zk])
    end_time = time.time()
    dvss_decrypt_time_zk = end_time - start_time

    print(f"DVSS-PPA 加密耗时: {dvss_encrypt_time_zk:.8f} 秒")
    print(f"DVSS-PPA 解密耗时: {dvss_decrypt_time_zk:.8f} 秒")
    print(f"DVSS-PPA 解密后数据: {dvss_recovered_zk}")


    """
    ============================
    实验 3 - DVSS-PPA 与 Secure Enclave (macOS) 对比
    ============================
    """
    print("\n===== 实验 3：Secure Enclave 对比 =====")
    se_storage = SecureEnclaveStorage()
    data_enclave = b"Hello Secure Enclave"

    # Secure Enclave 加密存储
    start_time = time.time()
    enclave_encrypted_data = se_storage.store_secret(data_enclave)
    end_time = time.time()
    enclave_store_time = end_time - start_time

    # Secure Enclave 解密读取
    start_time = time.time()
    enclave_retrieved_data = se_storage.retrieve_secret(enclave_encrypted_data)
    end_time = time.time()
    enclave_retrieve_time = end_time - start_time

    print(f"Secure Enclave 存储时间: {enclave_store_time:.8f} 秒")
    print(f"Secure Enclave 读取时间: {enclave_retrieve_time:.8f} 秒")
    print(f"读取后数据是否正确: {'是' if enclave_retrieved_data == data_enclave else '否'}")

    # DVSS-PPA 测试
    print("\n----- DVSS-PPA 测试（与 Secure Enclave 对比）-----")
    start_time = time.time()
    dvss_shares_enclave, _, k_enclave = dvss.share_secret(999999, n, 0.7, 0.4, 0.2)
    end_time = time.time()
    dvss_store_time = end_time - start_time

    start_time = time.time()
    dvss_recovered_enclave, _ = dvss.reconstruct_secret(dvss_shares_enclave[:k_enclave])
    end_time = time.time()
    dvss_retrieve_time = end_time - start_time

    print(f"DVSS-PPA '存储' 时间: {dvss_store_time:.8f} 秒")
    print(f"DVSS-PPA '读取' 时间: {dvss_retrieve_time:.8f} 秒")
    print(f"读取后数据: {dvss_recovered_enclave}")