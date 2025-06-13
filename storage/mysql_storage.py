#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: mysql_storage.py
Author: yshan2028
Created: 2025-06-13 09:25:15
Description: MySQL存储实现 - 使用数据库行锁而非Python线程锁
"""

import pymysql
import json
import logging
import time
from config.settings import MYSQL_CONFIG

logger = logging.getLogger(__name__)


class MySQLStorage:
    """MySQL数据存储类 - 使用数据库行锁"""

    def __init__(self):
        self.conn = None
        self.cursor = None
        self.operations_count = 0
        self.is_connected = False
        self.connection_retries = 3
        self.retry_delay = 1

        try:
            self._connect()
            self._initialize_tables()
            self.is_connected = True
            logger.info("MySQL storage initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MySQL storage: {str(e)}")
            self.is_connected = False

    def _connect(self):
        """建立数据库连接"""
        for attempt in range(self.connection_retries):
            try:
                # 关闭现有连接
                if self.conn:
                    try:
                        self.conn.close()
                    except:
                        pass

                temp_config = MYSQL_CONFIG.copy()
                database_name = temp_config.pop('database')

                # 连接配置 - 关闭autocommit以支持事务和行锁
                enhanced_config = {
                    **temp_config,
                    'connect_timeout': 10,
                    'read_timeout': 30,
                    'write_timeout': 30,
                    'autocommit': False,  # 关闭自动提交，支持行锁
                    'charset': 'utf8mb4',
                    'cursorclass': pymysql.cursors.DictCursor
                }

                self.conn = pymysql.connect(**enhanced_config)
                self.cursor = self.conn.cursor()

                # 创建数据库
                self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
                self.cursor.execute(f"USE {database_name}")
                self.conn.commit()

                # 设置会话参数
                self.cursor.execute("SET SESSION wait_timeout = 600")
                self.cursor.execute("SET SESSION interactive_timeout = 600")
                self.cursor.execute("SET SESSION innodb_lock_wait_timeout = 50")
                self.conn.commit()

                logger.info(f"Connected to MySQL database: {database_name}")
                return

            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.connection_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise

    def _ensure_connection(self):
        """确保数据库连接有效"""
        try:
            if not self.conn or not self.conn.open:
                logger.info("Reconnecting to MySQL...")
                self._connect()
            else:
                self.cursor.execute("SELECT 1")
                result = self.cursor.fetchone()
        except Exception as e:
            logger.warning(f"Connection test failed, reconnecting: {str(e)}")
            self._connect()

    def _initialize_tables(self):
        """初始化数据库表结构 - 保持原有完整字段"""
        if not self.cursor:
            logger.error("Cannot initialize tables: No database cursor available")
            return

        try:
            # 商品表
            self.cursor.execute("""
                                CREATE TABLE IF NOT EXISTS items
                                (
                                    id
                                    INT
                                    AUTO_INCREMENT
                                    PRIMARY
                                    KEY,
                                    sku
                                    VARCHAR
                                (
                                    50
                                ) UNIQUE NOT NULL,
                                    name VARCHAR
                                (
                                    255
                                ) NOT NULL,
                                    category VARCHAR
                                (
                                    100
                                ),
                                    quantity INT DEFAULT 0,
                                    price DECIMAL
                                (
                                    10,
                                    2
                                ) DEFAULT 0.00,
                                    cost DECIMAL
                                (
                                    10,
                                    2
                                ) DEFAULT 0.00,
                                    weight DECIMAL
                                (
                                    8,
                                    2
                                ) DEFAULT 0.00,
                                    dimensions JSON,
                                    description TEXT,
                                    supplier_id VARCHAR
                                (
                                    50
                                ),
                                    privacy_level ENUM
                                (
                                    'public',
                                    'internal',
                                    'confidential'
                                ) DEFAULT 'public',
                                    requires_zk_proof BOOLEAN DEFAULT FALSE,
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                                    INDEX idx_sku
                                (
                                    sku
                                ),
                                    INDEX idx_category
                                (
                                    category
                                ),
                                    INDEX idx_privacy_level
                                (
                                    privacy_level
                                )
                                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                                """)

            # 订单表 - 保持原有完整字段
            self.cursor.execute("""
                                CREATE TABLE IF NOT EXISTS orders
                                (
                                    id
                                    INT
                                    AUTO_INCREMENT
                                    PRIMARY
                                    KEY,
                                    order_id
                                    VARCHAR
                                (
                                    100
                                ) UNIQUE NOT NULL,
                                    customer_id VARCHAR
                                (
                                    50
                                ) NOT NULL,
                                    merchant_id VARCHAR
                                (
                                    50
                                ) NOT NULL,
                                    logistics_id VARCHAR
                                (
                                    50
                                ),
                                    order_items JSON,
                                    total_amount DECIMAL
                                (
                                    12,
                                    2
                                ) NOT NULL,
                                    currency VARCHAR
                                (
                                    10
                                ) DEFAULT 'USD',
                                    order_status ENUM
                                (
                                    'pending',
                                    'confirmed',
                                    'shipped',
                                    'delivered',
                                    'cancelled'
                                ) DEFAULT 'pending',
                                    payment_status ENUM
                                (
                                    'pending',
                                    'paid',
                                    'failed',
                                    'refunded'
                                ) DEFAULT 'pending',
                                    shipping_address JSON,
                                    privacy_requirements JSON,
                                    requires_secret_sharing BOOLEAN DEFAULT TRUE,
                                    shamir_threshold INT DEFAULT 2,
                                    shamir_shares INT DEFAULT 3,
                                    merkle_root VARCHAR
                                (
                                    64
                                ),
                                    zk_proof_hash VARCHAR
                                (
                                    64
                                ),
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                                    INDEX idx_order_id
                                (
                                    order_id
                                ),
                                    INDEX idx_customer_id
                                (
                                    customer_id
                                ),
                                    INDEX idx_merchant_id
                                (
                                    merchant_id
                                )
                                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                                """)

            # 用户表
            self.cursor.execute("""
                                CREATE TABLE IF NOT EXISTS users
                                (
                                    id
                                    INT
                                    AUTO_INCREMENT
                                    PRIMARY
                                    KEY,
                                    user_id
                                    VARCHAR
                                (
                                    50
                                ) UNIQUE NOT NULL,
                                    username VARCHAR
                                (
                                    100
                                ) NOT NULL,
                                    email VARCHAR
                                (
                                    255
                                ),
                                    role ENUM
                                (
                                    'merchant',
                                    'logistics',
                                    'customer',
                                    'admin'
                                ) NOT NULL,
                                    organization VARCHAR
                                (
                                    100
                                ),
                                    permissions JSON,
                                    privacy_preferences JSON,
                                    zk_public_key VARCHAR
                                (
                                    255
                                ),
                                    access_level ENUM
                                (
                                    'basic',
                                    'standard',
                                    'premium'
                                ) DEFAULT 'basic',
                                    last_login TIMESTAMP NULL,
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                                    INDEX idx_user_id
                                (
                                    user_id
                                ),
                                    INDEX idx_role
                                (
                                    role
                                ),
                                    INDEX idx_organization
                                (
                                    organization
                                )
                                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                                """)

            # 隐私元数据表
            self.cursor.execute("""
                                CREATE TABLE IF NOT EXISTS privacy_metadata
                                (
                                    id
                                    INT
                                    AUTO_INCREMENT
                                    PRIMARY
                                    KEY,
                                    data_id
                                    VARCHAR
                                (
                                    100
                                ) NOT NULL,
                                    data_type ENUM
                                (
                                    'item',
                                    'order',
                                    'user',
                                    'transaction'
                                ) NOT NULL,
                                    shamir_shares JSON,
                                    merkle_proof JSON,
                                    zk_proof_data JSON,
                                    access_control_rules JSON,
                                    encryption_method VARCHAR
                                (
                                    50
                                ),
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    expires_at TIMESTAMP NULL,
                                    INDEX idx_data_id
                                (
                                    data_id
                                ),
                                    INDEX idx_data_type
                                (
                                    data_type
                                )
                                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                                """)

            # 实验结果表
            self.cursor.execute("""
                                CREATE TABLE IF NOT EXISTS experiment_results
                                (
                                    id
                                    INT
                                    AUTO_INCREMENT
                                    PRIMARY
                                    KEY,
                                    experiment_id
                                    VARCHAR
                                (
                                    100
                                ) NOT NULL,
                                    experiment_type VARCHAR
                                (
                                    50
                                ) NOT NULL,
                                    algorithm_name VARCHAR
                                (
                                    50
                                ) NOT NULL,
                                    execution_time DECIMAL
                                (
                                    10,
                                    3
                                ) DEFAULT 0.000,
                                    throughput DECIMAL
                                (
                                    10,
                                    2
                                ) DEFAULT 0.00,
                                    memory_usage DECIMAL
                                (
                                    10,
                                    2
                                ),
                                    cpu_usage DECIMAL
                                (
                                    5,
                                    2
                                ),
                                    privacy_score DECIMAL
                                (
                                    5,
                                    2
                                ),
                                    parameters JSON,
                                    results JSON,
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    INDEX idx_experiment_id
                                (
                                    experiment_id
                                ),
                                    INDEX idx_algorithm_name
                                (
                                    algorithm_name
                                )
                                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                                """)

            self.conn.commit()
            logger.info("All database tables created/verified successfully")

        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to create tables: {str(e)}")
            raise

    def save_order(self, order_data: dict) -> bool:
        """保存订单数据 - 使用数据库行锁"""
        if not self.is_connected:
            logger.warning("MySQL not connected, skipping order save")
            return False

        try:
            self._ensure_connection()

            # 开始事务
            processed_data = self._prepare_order_data(order_data)

            # 使用INSERT ... ON DUPLICATE KEY UPDATE避免锁冲突
            query = """
                    INSERT INTO orders (order_id, customer_id, merchant_id, logistics_id, order_items,
                                        total_amount, currency, order_status, payment_status, shipping_address,
                                        privacy_requirements, requires_secret_sharing, shamir_threshold,
                                        shamir_shares, merkle_root, zk_proof_hash)
                    VALUES (%(order_id)s, %(customer_id)s, %(merchant_id)s, %(logistics_id)s, %(order_items)s,
                            %(total_amount)s, %(currency)s, %(order_status)s, %(payment_status)s, %(shipping_address)s,
                            %(privacy_requirements)s, %(requires_secret_sharing)s, %(shamir_threshold)s,
                            %(shamir_shares)s, %(merkle_root)s, %(zk_proof_hash)s) ON DUPLICATE KEY \
                    UPDATE \
                        order_status = \
                    VALUES (order_status), payment_status = \
                    VALUES (payment_status), total_amount = \
                    VALUES (total_amount), updated_at = CURRENT_TIMESTAMP \
                    """

            self.cursor.execute(query, processed_data)
            self.conn.commit()  # 提交事务，释放行锁
            self.operations_count += 1
            return True

        except pymysql.MySQLError as e:
            self.conn.rollback()  # 回滚事务
            logger.error(f"MySQL error saving order {order_data.get('order_id', 'Unknown')}: "
                         f"Error {e.args[0] if e.args else 'Unknown'}: {e.args[1] if len(e.args) > 1 else 'No message'}")
            return False
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Unexpected error saving order {order_data.get('order_id', 'Unknown')}: {str(e)}")
            return False

    def save_order_batch(self, orders_list: list) -> int:
        """批量保存订单 - 使用单个事务提高性能"""
        if not self.is_connected or not orders_list:
            return 0

        saved_count = 0
        try:
            self._ensure_connection()

            # 批量插入查询
            query = """
                    INSERT INTO orders (order_id, customer_id, merchant_id, logistics_id, order_items,
                                        total_amount, currency, order_status, payment_status, shipping_address,
                                        privacy_requirements, requires_secret_sharing, shamir_threshold,
                                        shamir_shares, merkle_root, zk_proof_hash)
                    VALUES (%(order_id)s, %(customer_id)s, %(merchant_id)s, %(logistics_id)s, %(order_items)s,
                            %(total_amount)s, %(currency)s, %(order_status)s, %(payment_status)s, %(shipping_address)s,
                            %(privacy_requirements)s, %(requires_secret_sharing)s, %(shamir_threshold)s,
                            %(shamir_shares)s, %(merkle_root)s, %(zk_proof_hash)s) ON DUPLICATE KEY \
                    UPDATE \
                        order_status = \
                    VALUES (order_status), total_amount = \
                    VALUES (total_amount) \
                    """

            # 分批处理，每批100个
            batch_size = 100
            for i in range(0, len(orders_list), batch_size):
                batch = orders_list[i:i + batch_size]
                processed_batch = []

                for order_data in batch:
                    try:
                        processed_data = self._prepare_order_data(order_data)
                        processed_batch.append(processed_data)
                    except Exception as e:
                        logger.warning(f"Skipping invalid order {order_data.get('order_id', 'Unknown')}: {str(e)}")
                        continue

                if processed_batch:
                    self.cursor.executemany(query, processed_batch)
                    saved_count += len(processed_batch)

            self.conn.commit()  # 一次性提交所有批次
            self.operations_count += saved_count
            logger.info(f"Batch saved {saved_count}/{len(orders_list)} orders")
            return saved_count

        except Exception as e:
            self.conn.rollback()
            logger.error(f"Batch save failed: {str(e)}")
            return saved_count

    def _prepare_order_data(self, order_data: dict) -> dict:
        """准备订单数据"""
        processed_data = {}

        # 必需字段
        required_fields = ['order_id', 'customer_id', 'merchant_id', 'total_amount']
        for field in required_fields:
            if field not in order_data:
                raise ValueError(f"Missing required field: {field}")
            processed_data[field] = order_data[field]

        # 可选字段
        processed_data['logistics_id'] = order_data.get('logistics_id', '')
        processed_data['currency'] = order_data.get('currency', 'USD')
        processed_data['order_status'] = order_data.get('order_status', 'pending')
        processed_data['payment_status'] = order_data.get('payment_status', 'pending')
        processed_data['requires_secret_sharing'] = bool(order_data.get('requires_secret_sharing', True))
        processed_data['shamir_threshold'] = int(order_data.get('shamir_threshold', 2))
        processed_data['shamir_shares'] = int(order_data.get('shamir_shares', 3))
        processed_data['merkle_root'] = order_data.get('merkle_root', '')
        processed_data['zk_proof_hash'] = order_data.get('zk_proof_hash', '')

        # JSON字段处理
        try:
            json_fields = ['order_items', 'shipping_address', 'privacy_requirements']
            for field in json_fields:
                if field in order_data:
                    if isinstance(order_data[field], (list, dict)):
                        processed_data[field] = json.dumps(order_data[field], ensure_ascii=False)
                    else:
                        processed_data[field] = str(order_data[field])
                else:
                    processed_data[field] = json.dumps({} if field != 'order_items' else [])

        except Exception as e:
            logger.error(f"Error processing JSON fields: {str(e)}")
            processed_data['order_items'] = json.dumps([])
            processed_data['shipping_address'] = json.dumps({})
            processed_data['privacy_requirements'] = json.dumps({})

        return processed_data

    def save_user(self, user_data: dict) -> bool:
        """保存用户数据"""
        if not self.is_connected:
            return False

        try:
            self._ensure_connection()

            processed_data = {
                'user_id': user_data.get('user_id'),
                'username': user_data.get('username'),
                'email': user_data.get('email', ''),
                'role': user_data.get('role'),
                'organization': user_data.get('organization', ''),
                'permissions': json.dumps(user_data.get('permissions', {}), ensure_ascii=False),
                'privacy_preferences': json.dumps(user_data.get('privacy_preferences', {}), ensure_ascii=False),
                'zk_public_key': user_data.get('zk_public_key', ''),
                'access_level': user_data.get('access_level', 'basic'),
                'last_login': user_data.get('last_login')
            }

            query = """
                    INSERT INTO users (user_id, username, email, role, organization, permissions,
                                       privacy_preferences, zk_public_key, access_level, last_login)
                    VALUES (%(user_id)s, %(username)s, %(email)s, %(role)s, %(organization)s, %(permissions)s,
                            %(privacy_preferences)s, %(zk_public_key)s, %(access_level)s, %(last_login)s) ON DUPLICATE KEY \
                    UPDATE \
                        username = \
                    VALUES (username), email = \
                    VALUES (email), role = \
                    VALUES (role), organization = \
                    VALUES (organization), updated_at = CURRENT_TIMESTAMP \
                    """

            self.cursor.execute(query, processed_data)
            self.conn.commit()
            self.operations_count += 1
            return True

        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to save user {user_data.get('user_id', 'Unknown')}: {str(e)}")
            return False

    def save_item(self, item_data: dict) -> bool:
        """保存商品数据"""
        if not self.is_connected:
            return False

        try:
            self._ensure_connection()

            processed_data = {
                'sku': item_data.get('sku'),
                'name': item_data.get('name'),
                'category': item_data.get('category', ''),
                'quantity': int(item_data.get('quantity', 0)),
                'price': float(item_data.get('price', 0.0)),
                'cost': float(item_data.get('cost', 0.0)),
                'weight': float(item_data.get('weight', 0.0)),
                'dimensions': json.dumps(item_data.get('dimensions', {}), ensure_ascii=False),
                'description': item_data.get('description', ''),
                'supplier_id': item_data.get('supplier_id', ''),
                'privacy_level': item_data.get('privacy_level', 'public'),
                'requires_zk_proof': bool(item_data.get('requires_zk_proof', False))
            }

            query = """
                    INSERT INTO items (sku, name, category, quantity, price, cost, weight, dimensions,
                                       description, supplier_id, privacy_level, requires_zk_proof)
                    VALUES (%(sku)s, %(name)s, %(category)s, %(quantity)s, %(price)s, %(cost)s, %(weight)s,
                            %(dimensions)s, %(description)s, %(supplier_id)s, %(privacy_level)s, %(requires_zk_proof)s) ON DUPLICATE KEY \
                    UPDATE \
                        name = \
                    VALUES (name), price = \
                    VALUES (price), updated_at = CURRENT_TIMESTAMP \
                    """

            self.cursor.execute(query, processed_data)
            self.conn.commit()
            self.operations_count += 1
            return True

        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to save item {item_data.get('sku', 'Unknown')}: {str(e)}")
            return False

    def save_experiment_result(self, result_data: dict) -> bool:
        """保存实验结果"""
        if not self.is_connected:
            return False

        try:
            self._ensure_connection()

            processed_data = {
                'experiment_id': result_data.get('experiment_id', 'unknown'),
                'experiment_type': result_data.get('experiment_type', 'general'),
                'algorithm_name': result_data.get('algorithm_name', 'unknown'),
                'execution_time': float(result_data.get('execution_time', 0.0)),
                'throughput': float(result_data.get('throughput', 0.0)),
                'memory_usage': float(result_data.get('memory_usage', 0.0)) if result_data.get('memory_usage') else None,
                'cpu_usage': float(result_data.get('cpu_usage', 0.0)) if result_data.get('cpu_usage') else None,
                'privacy_score': float(result_data.get('privacy_score', 0.0)) if result_data.get('privacy_score') else None,
                'parameters': json.dumps(result_data.get('parameters', {}), ensure_ascii=False),
                'results': json.dumps(result_data.get('results', {}), ensure_ascii=False)
            }

            query = """
                    INSERT INTO experiment_results (experiment_id, experiment_type, algorithm_name,
                                                    execution_time, throughput, memory_usage, cpu_usage,
                                                    privacy_score, parameters, results)
                    VALUES (%(experiment_id)s, %(experiment_type)s, %(algorithm_name)s,
                            %(execution_time)s, %(throughput)s, %(memory_usage)s, %(cpu_usage)s,
                            %(privacy_score)s, %(parameters)s, %(results)s) \
                    """

            self.cursor.execute(query, processed_data)
            self.conn.commit()
            self.operations_count += 1
            return True

        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to save experiment result: {str(e)}")
            return False

    def get_statistics(self) -> dict:
        """获取存储统计信息"""
        stats = {
            'is_connected': self.is_connected,
            'operations_count': self.operations_count
        }

        if not self.is_connected:
            return stats

        try:
            self._ensure_connection()
            tables = ['items', 'orders', 'users', 'privacy_metadata', 'experiment_results']
            for table in tables:
                try:
                    self.cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                    result = self.cursor.fetchone()
                    stats[f'{table}_count'] = result['count'] if result else 0
                except Exception as e:
                    logger.warning(f"Failed to get count for table {table}: {str(e)}")
                    stats[f'{table}_count'] = 0
        except Exception as e:
            logger.error(f"Failed to get statistics: {str(e)}")

        return stats

    def close_connection(self):
        """关闭数据库连接"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
            self.is_connected = False
            logger.info(f"MySQL connection closed, operations: {self.operations_count}")
        except Exception as e:
            logger.error(f"Error closing MySQL connection: {str(e)}")


def test_mysql_connection():
    """测试MySQL连接"""
    try:
        print("=" * 50)
        print("MYSQL CONNECTION TEST WITH ROW LOCKING")
        print("=" * 50)
        print(f"Host: {MYSQL_CONFIG['host']}")
        print(f"Port: {MYSQL_CONFIG['port']}")
        print(f"User: {MYSQL_CONFIG['user']}")
        print(f"Database: {MYSQL_CONFIG['database']}")

        storage = MySQLStorage()

        if storage.is_connected:
            print("✅ MySQL connection successful")

            # 测试单个订单保存
            test_order = {
                "order_id": f"TEST_ORDER_{int(time.time())}",
                "customer_id": "TEST_CUSTOMER",
                "merchant_id": "TEST_MERCHANT",
                "order_items": [{"item": "test", "qty": 1}],
                "total_amount": 99.99,
                "order_status": "pending"
            }

            success = storage.save_order(test_order)
            print(f"Single order save: {'SUCCESS' if success else 'FAILED'}")

            # 测试批量保存
            test_orders = []
            for i in range(5):
                order = {
                    "order_id": f"BATCH_ORDER_{int(time.time())}_{i}",
                    "customer_id": f"CUSTOMER_{i}",
                    "merchant_id": f"MERCHANT_{i}",
                    "order_items": [{"item": f"item_{i}", "qty": i + 1}],
                    "total_amount": (i + 1) * 10.0,
                    "order_status": "pending"
                }
                test_orders.append(order)

            batch_count = storage.save_order_batch(test_orders)
            print(f"Batch save: {batch_count}/{len(test_orders)} orders")

            stats = storage.get_statistics()
            print("Database statistics:")
            for k, v in stats.items():
                if k.endswith('_count'):
                    print(f"  {k}: {v}")
        else:
            print("❌ MySQL connection failed")

        storage.close_connection()
        print("Connection test completed!")

    except Exception as e:
        print(f"❌ Connection test error: {str(e)}")


if __name__ == "__main__":
    test_mysql_connection()