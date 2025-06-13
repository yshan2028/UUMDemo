#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: settings.py
Author: yshan2028
Created: 2025-06-13 09:26:08
Description: 全局配置文件 - 增强版
"""

import os
import logging

# =============================================================================
# 数据库配置
# =============================================================================

# MySQL配置 - 可根据环境调整
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "12345678"),
    "database": os.getenv("MYSQL_DATABASE", "blockchain_privacy_experiment"),
    "charset": "utf8mb4",
    "autocommit": True,
    # 连接稳定性配置
    "connect_timeout": 10,
    "read_timeout": 30,
    "write_timeout": 30,
    "max_allowed_packet": 64 * 1024 * 1024  # 64MB
}

# 备用MySQL配置（如果主配置失败）
MYSQL_FALLBACK_CONFIG = {
    "host": "127.0.0.1",  # 尝试IP而不是localhost
    "port": 3306,
    "user": "root",
    "password": "12345678",
    "database": "dvss_ppa_test",  # 简化的数据库名
    "charset": "utf8mb4",
    "autocommit": True
}

# Redis配置
REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST", "localhost"),
    "port": int(os.getenv("REDIS_PORT", 6379)),
    "db": int(os.getenv("REDIS_DB", 0)),
    "decode_responses": True,
    "socket_timeout": 5,
    "socket_connect_timeout": 5
}

# =============================================================================
# 实验参数配置
# =============================================================================

EXPERIMENT_PARAMS = {
    # 数据规模配置
    "data_size": int(os.getenv("EXPERIMENT_DATA_SIZE", 10000)),  # 减少到100便于测试
    "user_count": int(os.getenv("EXPERIMENT_USER_COUNT", 50)),
    "item_count": int(os.getenv("EXPERIMENT_ITEM_COUNT", 100)),

    # 算法参数
    "shard_count": int(os.getenv("EXPERIMENT_SHARD_COUNT", 5)),
    "threshold": int(os.getenv("EXPERIMENT_THRESHOLD", 3)),
    "test_iterations": int(os.getenv("EXPERIMENT_ITERATIONS", 3)),

    # 性能目标
    "target_tps": int(os.getenv("EXPERIMENT_TARGET_TPS", 1000)),  # 降低目标
    "max_latency_ms": int(os.getenv("EXPERIMENT_MAX_LATENCY", 500)),  # 放宽延迟要求

    # 测试模式
    "enable_mysql": os.getenv("ENABLE_MYSQL", "true").lower() == "true",
    "enable_redis": os.getenv("ENABLE_REDIS", "true").lower() == "true",
    "enable_performance_test": os.getenv("ENABLE_PERF_TEST", "true").lower() == "true",
    "enable_privacy_test": os.getenv("ENABLE_PRIVACY_TEST", "true").lower() == "true",
    "batch_save": os.getenv("BATCH_SAVE", "true").lower() == "true"
}

# =============================================================================
# 算法配置
# =============================================================================

ALGORITHM_CONFIG = {
    "shamir": {
        "prime_modulus": 2 ** 127 - 1,
        "k_min": 2,
        "k_max": 10,
        "enable_time_based_shares": True
    },
    "merkle": {
        "hash_algorithm": "sha256",
        "max_tree_depth": 20
    },
    "zk_proof": {
        "proof_system": "groth16",
        "enable_simulation": True  # 在测试环境使用模拟
    },
    "access_control": {
        "enable_dynamic_rules": True,
        "default_access_level": "basic"
    }
}

# =============================================================================
# 路径配置
# =============================================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_PATH = os.path.join(BASE_DIR, "experiments", "results")
LOGS_PATH = os.path.join(BASE_DIR, "logs")
DATA_PATH = os.path.join(BASE_DIR, "data")

# =============================================================================
# 日志配置
# =============================================================================

LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "[%(asctime)s] %(levelname)s: %(message)s",
    "file_enabled": os.getenv("LOG_TO_FILE", "true").lower() == "true",
    "console_enabled": True
}

# =============================================================================
# 性能调优配置
# =============================================================================

PERFORMANCE_CONFIG = {
    "batch_size": int(os.getenv("BATCH_SIZE", 100)),
    "thread_pool_size": int(os.getenv("THREAD_POOL_SIZE", 4)),
    "memory_limit_mb": int(os.getenv("MEMORY_LIMIT_MB", 512)),
    "enable_profiling": os.getenv("ENABLE_PROFILING", "false").lower() == "true"
}


# =============================================================================
# 配置验证和初始化
# =============================================================================

def validate_configuration():
    """验证配置参数有效性"""
    try:
        # 验证实验参数
        if EXPERIMENT_PARAMS["threshold"] > EXPERIMENT_PARAMS["shard_count"]:
            print("❌ 错误: threshold 不能大于 shard_count")
            return False

        if EXPERIMENT_PARAMS["data_size"] <= 0:
            print("❌ 错误: data_size 必须大于 0")
            return False

        if EXPERIMENT_PARAMS["user_count"] <= 0:
            print("❌ 错误: user_count 必须大于 0")
            return False

        # 验证数据库配置
        required_mysql_keys = ["host", "port", "user", "password", "database"]
        for key in required_mysql_keys:
            if not MYSQL_CONFIG.get(key):
                print(f"❌ 错误: MySQL配置缺少 {key}")
                return False

        print("✅ 配置验证通过")
        return True

    except Exception as e:
        print(f"❌ 配置验证失败: {str(e)}")
        return False


def print_configuration_summary():
    """打印配置摘要"""
    print("=" * 60)
    print("DVSS-PPA 系统配置摘要")
    print("=" * 60)
    print(f"📊 数据规模:")
    print(f"   订单数量: {EXPERIMENT_PARAMS['data_size']}")
    print(f"   用户数量: {EXPERIMENT_PARAMS['user_count']}")
    print(f"   商品数量: {EXPERIMENT_PARAMS['item_count']}")

    print(f"🔢 算法参数:")
    print(f"   分片数量: {EXPERIMENT_PARAMS['shard_count']}")
    print(f"   阈值: {EXPERIMENT_PARAMS['threshold']}")

    print(f"🎯 性能目标:")
    print(f"   目标TPS: {EXPERIMENT_PARAMS['target_tps']}")
    print(f"   最大延迟: {EXPERIMENT_PARAMS['max_latency_ms']}ms")

    print(f"💾 存储配置:")
    print(f"   MySQL: {MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}")
    print(f"   数据库: {MYSQL_CONFIG['database']}")
    print(f"   Redis: {REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}")

    print(f"🧪 测试模式:")
    print(f"   MySQL启用: {EXPERIMENT_PARAMS['enable_mysql']}")
    print(f"   Redis启用: {EXPERIMENT_PARAMS['enable_redis']}")
    print(f"   批量保存: {EXPERIMENT_PARAMS['batch_save']}")

    print("=" * 60)


def get_alternative_mysql_config():
    """获取备用MySQL配置"""
    return MYSQL_FALLBACK_CONFIG.copy()


def create_test_config():
    """创建测试配置（降低数据量）"""
    test_config = EXPERIMENT_PARAMS.copy()
    test_config.update({
        "data_size": 50,
        "user_count": 20,
        "item_count": 30,
        "target_tps": 100,
        "test_iterations": 1
    })
    return test_config


def create_minimal_config():
    """创建最小配置（快速测试）"""
    minimal_config = EXPERIMENT_PARAMS.copy()
    minimal_config.update({
        "data_size": 10,
        "user_count": 5,
        "item_count": 10,
        "target_tps": 50,
        "test_iterations": 1,
        "enable_mysql": False,  # 禁用MySQL
        "enable_redis": False  # 禁用Redis
    })
    return minimal_config


# =============================================================================
# 环境检测和自动配置
# =============================================================================

def detect_and_configure_environment():
    """检测环境并自动配置"""
    print("🔍 检测运行环境...")

    # 检测MySQL
    mysql_available = test_mysql_connection()
    if not mysql_available:
        print("⚠️ MySQL不可用，将使用降级模式")
        EXPERIMENT_PARAMS["enable_mysql"] = False

    # 检测Redis
    redis_available = test_redis_connection()
    if not redis_available:
        print("⚠️ Redis不可用，将禁用缓存功能")
        EXPERIMENT_PARAMS["enable_redis"] = False

    # 根据可用资源调整参数
    if not mysql_available and not redis_available:
        print("📉 降低实验规模以适应限制环境")
        EXPERIMENT_PARAMS.update(create_test_config())


def test_mysql_connection():
    """测试MySQL连接"""
    try:
        import pymysql
        conn = pymysql.connect(
            host=MYSQL_CONFIG["host"],
            port=MYSQL_CONFIG["port"],
            user=MYSQL_CONFIG["user"],
            password=MYSQL_CONFIG["password"],
            connect_timeout=5
        )
        conn.close()
        return True
    except:
        try:
            # 尝试备用配置
            conn = pymysql.connect(
                host=MYSQL_FALLBACK_CONFIG["host"],
                port=MYSQL_FALLBACK_CONFIG["port"],
                user=MYSQL_FALLBACK_CONFIG["user"],
                password=MYSQL_FALLBACK_CONFIG["password"],
                connect_timeout=5
            )
            conn.close()
            # 更新为备用配置
            MYSQL_CONFIG.update(MYSQL_FALLBACK_CONFIG)
            return True
        except:
            return False


def test_redis_connection():
    """测试Redis连接"""
    try:
        import redis
        r = redis.Redis(
            host=REDIS_CONFIG["host"],
            port=REDIS_CONFIG["port"],
            db=REDIS_CONFIG["db"],
            socket_timeout=2
        )
        r.ping()
        return True
    except:
        return False


# =============================================================================
# 初始化
# =============================================================================

# 确保目录存在
for path in [RESULTS_PATH, LOGS_PATH, DATA_PATH]:
    os.makedirs(path, exist_ok=True)

# 如果作为主模块运行，进行配置测试
if __name__ == "__main__":
    print("=" * 60)
    print("DVSS-PPA 配置测试")
    print("=" * 60)

    # 打印配置摘要
    print_configuration_summary()

    # 验证配置
    if validate_configuration():
        print("\n✅ 基本配置验证通过")
    else:
        print("\n❌ 基本配置验证失败")
        exit(1)

    # 环境检测
    detect_and_configure_environment()

    print("\n📋 最终配置:")
    print(f"MySQL启用: {EXPERIMENT_PARAMS['enable_mysql']}")
    print(f"Redis启用: {EXPERIMENT_PARAMS['enable_redis']}")
    print(f"数据规模: {EXPERIMENT_PARAMS['data_size']}")

    # 提供配置建议
    print("\n💡 配置建议:")
    if not EXPERIMENT_PARAMS['enable_mysql']:
        print("- 启动MySQL服务: net start mysql (Windows) 或 brew services start mysql (Mac)")
        print("- 检查MySQL用户名和密码")
        print("- 尝试修改MYSQL_CONFIG中的host为'127.0.0.1'")

    if not EXPERIMENT_PARAMS['enable_redis']:
        print("- 启动Redis服务: redis-server (或安装Redis)")
        print("- Redis是可选的，不影响核心功能")

    print("\n🚀 配置测试完成！")