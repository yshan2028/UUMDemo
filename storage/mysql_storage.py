#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: mysql_storage.py
Author: yshan2028
Created: 2025-06-13 14:56:13
Description: 
    [请在此处添加文件描述]

Dependencies:
    [请在此处列出主要依赖]

Usage:
    [请在此处添加使用说明]
"""

import pymysql
from config.settings import MYSQL_CONFIG  # 从 settings.py 导入配置

class MySQLStorage:
    """
    实现链下数据的 MySQL 存储逻辑，使用 pymysql 库。
    """

    def __init__(self):
        """
        初始化 MySQL 数据库连接。
        """
        try:
            self.conn = pymysql.connect(
                host=MYSQL_CONFIG["host"],
                user=MYSQL_CONFIG["user"],
                password=MYSQL_CONFIG["password"],
                database=MYSQL_CONFIG["database"],
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor
            )
            self.cursor = self.conn.cursor()
            print("[INFO] 成功连接到 MySQL 数据库。")
        except pymysql.MySQLError as e:
            print(f"[ERROR] 数据库连接失败: {e}")
            raise

    def save_item(self, item_data: dict):
        """
        保存商品信息到数据库。

        :param item_data: 包含商品 SKU、名称、数量和价格的字典。
        """
        try:
            query = """
                INSERT INTO items (sku, name, quantity, price) 
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                name = VALUES(name),
                quantity = VALUES(quantity),
                price = VALUES(price)
            """
            values = (item_data["sku"], item_data["name"], item_data["quantity"], item_data["price"])
            self.cursor.execute(query, values)
            self.conn.commit()
            print(f"[INFO] 商品 {item_data['sku']} 已成功保存到数据库。")
        except pymysql.MySQLError as e:
            print(f"[ERROR] 保存商品失败: {e}")

    def fetch_item(self, sku: str) -> dict:
        """
        从数据库中查询商品信息。

        :param sku: 商品 SKU。
        :return: 包含商品详情的字典，或空字典如果未找到。
        """
        try:
            query = "SELECT * FROM items WHERE sku = %s"
            self.cursor.execute(query, (sku,))
            result = self.cursor.fetchone()
            if result:
                print(f"[INFO] 查询商品成功，SKU: {sku}")
                return result
            else:
                print(f"[INFO] 未找到商品，SKU: {sku}")
                return {}
        except pymysql.MySQLError as e:
            print(f"[ERROR] 查询商品失败: {e}")
            return {}

    def delete_item(self, sku: str):
        """
        从数据库中删除商品。

        :param sku: 商品 SKU。
        """
        try:
            query = "DELETE FROM items WHERE sku = %s"
            self.cursor.execute(query, (sku,))
            self.conn.commit()
            print(f"[INFO] 商品 {sku} 已成功删除。")
        except pymysql.MySQLError as e:
            print(f"[ERROR] 删除商品失败: {e}")

    def close(self):
        """
        关闭数据库连接。
        """
        try:
            self.cursor.close()
            self.conn.close()
            print("[INFO] 已关闭 MySQL 数据库连接。")
        except pymysql.MySQLError as e:
            print(f"[ERROR] 关闭数据库连接失败: {e}")

if __name__ == "__main__":
    # 测试 MySQL 存储功能
    mysql_storage = MySQLStorage()

    # 保存商品
    item = {"sku": "SKU1234", "name": "Keyboard", "quantity": 10, "price": 49.99}
    mysql_storage.save_item(item)

    # 查询商品
    fetched_item = mysql_storage.fetch_item("SKU1234")
    print("查询结果:", fetched_item)

    # 删除商品
    mysql_storage.delete_item("SKU1234")

    # 关闭连接
    mysql_storage.close()
