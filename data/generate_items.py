#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: generate_items.py
Author: yshan2028
Created: 2025-06-13 09:10:06
Description: 商品数据生成器
"""

import random
from decimal import Decimal
from datetime import datetime, timedelta


class ItemGenerator:
    """商品数据生成器"""

    @staticmethod
    def generate_items(count: int) -> list:
        """生成商品数据"""
        items = []

        categories = ["Electronics", "Books", "Clothing", "Home & Garden", "Sports", "Toys"]
        privacy_levels = ["public", "internal", "confidential"]
        suppliers = [f"SUPPLIER_{i:03d}" for i in range(1, 21)]

        # 商品名称模板
        product_templates = {
            "Electronics": {
                "names": ["Smartphone", "Laptop", "Tablet", "Headphones", "Camera", "Speaker", "Monitor", "Keyboard"],
                "brands": ["TechMax", "DigitalPro", "SmartGear", "EliteDevice", "InnoTech"],
                "models": ["Pro", "Max", "Plus", "Standard", "Elite", "Premium", "Basic", "Advanced"]
            },
            "Books": {
                "names": ["Programming Guide", "Data Science Manual", "Security Handbook", "AI Textbook", "Blockchain Bible"],
                "brands": ["TechPublish", "EduBooks", "LearnPress", "KnowledgeHouse"],
                "models": ["2024 Edition", "Latest", "Revised", "Complete", "Essential"]
            },
            "Clothing": {
                "names": ["Business Shirt", "Casual Jeans", "Sports Jacket", "Running Shoes", "Winter Coat"],
                "brands": ["StyleMax", "ComfortWear", "FashionPlus", "ActiveGear"],
                "models": ["Classic", "Modern", "Vintage", "Sport", "Casual"]
            },
            "Home & Garden": {
                "names": ["Office Chair", "Dining Table", "Floor Lamp", "Garden Tool", "Storage Box"],
                "brands": ["HomePro", "GardenMax", "ComfortHome", "LifeStyle"],
                "models": ["Deluxe", "Standard", "Compact", "Large", "Premium"]
            },
            "Sports": {
                "names": ["Tennis Racket", "Basketball", "Running Shoes", "Fitness Equipment", "Sports Watch"],
                "brands": ["SportMax", "FitnessPro", "ActiveLife", "HealthGear"],
                "models": ["Pro", "Amateur", "Professional", "Training", "Competition"]
            },
            "Toys": {
                "names": ["Educational Puzzle", "Action Figure", "Board Game", "Building Blocks", "Remote Car"],
                "brands": ["PlayMax", "KidsFun", "LearnToy", "FamilyGame"],
                "models": ["Kids", "Family", "Educational", "Fun", "Creative"]
            }
        }

        for i in range(count):
            category = random.choice(categories)
            template = product_templates[category]

            base_name = random.choice(template["names"])
            brand = random.choice(template["brands"])
            model = random.choice(template["models"])

            # 生成价格（根据类别调整价格范围）
            price_ranges = {
                "Electronics": (50.0, 2000.0),
                "Books": (10.0, 100.0),
                "Clothing": (20.0, 300.0),
                "Home & Garden": (25.0, 800.0),
                "Sports": (15.0, 500.0),
                "Toys": (5.0, 150.0)
            }

            min_price, max_price = price_ranges[category]
            price = round(random.uniform(min_price, max_price), 2)
            cost = round(price * random.uniform(0.6, 0.8), 2)

            # 生成重量（根据类别调整）
            weight_ranges = {
                "Electronics": (0.1, 5.0),
                "Books": (0.2, 2.0),
                "Clothing": (0.1, 2.0),
                "Home & Garden": (0.5, 50.0),
                "Sports": (0.1, 10.0),
                "Toys": (0.05, 3.0)
            }

            min_weight, max_weight = weight_ranges[category]
            weight = round(random.uniform(min_weight, max_weight), 2)

            item = {
                "sku": f"SKU_{category[:3].upper()}_{i + 1:05d}",
                "name": f"{brand} {base_name} {model}",
                "category": category,
                "quantity": random.randint(10, 1000),
                "price": price,
                "cost": cost,
                "weight": weight,
                "dimensions": ItemGenerator._generate_dimensions(category),
                "description": ItemGenerator._generate_description(brand, base_name, model, category),
                "supplier_id": random.choice(suppliers),
                "privacy_level": ItemGenerator._determine_privacy_level(category, price),
                "requires_zk_proof": ItemGenerator._requires_zk_proof(category, price),
                "created_at": datetime.now() - timedelta(days=random.randint(1, 730))  # 最近2年内创建
            }
            items.append(item)

        return items

    @staticmethod
    def _generate_dimensions(category: str) -> dict:
        """根据类别生成合理的尺寸"""
        dimension_ranges = {
            "Electronics": {"length": (5, 40), "width": (3, 30), "height": (1, 15)},
            "Books": {"length": (15, 25), "width": (10, 20), "height": (1, 5)},
            "Clothing": {"length": (30, 80), "width": (25, 60), "height": (2, 10)},
            "Home & Garden": {"length": (20, 200), "width": (15, 150), "height": (5, 100)},
            "Sports": {"length": (10, 150), "width": (8, 80), "height": (3, 50)},
            "Toys": {"length": (5, 50), "width": (5, 40), "height": (2, 30)}
        }

        ranges = dimension_ranges.get(category, {"length": (10, 50), "width": (8, 40), "height": (2, 20)})

        return {
            "length": random.randint(*ranges["length"]),
            "width": random.randint(*ranges["width"]),
            "height": random.randint(*ranges["height"])
        }

    @staticmethod
    def _generate_description(brand: str, base_name: str, model: str, category: str) -> str:
        """生成商品描述"""
        descriptions = {
            "Electronics": f"High-performance {base_name.lower()} from {brand}. {model} series with advanced technology and premium build quality. Perfect for professional and personal use.",
            "Books": f"Comprehensive {base_name.lower()} published by {brand}. {model} covering essential topics with practical examples and expert insights.",
            "Clothing": f"Stylish {base_name.lower()} from {brand} {model} collection. Made with high-quality materials for comfort and durability.",
            "Home & Garden": f"Functional {base_name.lower()} designed by {brand}. {model} style perfect for modern homes and gardens.",
            "Sports": f"Professional-grade {base_name.lower()} from {brand} {model} series. Designed for optimal performance and durability.",
            "Toys": f"Educational and fun {base_name.lower()} from {brand}. {model} design promotes creativity and learning through play."
        }

        return descriptions.get(category, f"Quality {base_name.lower()} from {brand} {model} series.")

    @staticmethod
    def _determine_privacy_level(category: str, price: float) -> str:
        """根据类别和价格确定隐私级别"""
        # 高价值商品更可能需要更高的隐私保护
        if price > 1000:
            return random.choice(["confidential", "internal"])
        elif price > 100:
            return random.choice(["internal", "public", "public"])  # 更倾向于public
        else:
            return "public"

    @staticmethod
    def _requires_zk_proof(category: str, price: float) -> bool:
        """确定是否需要零知识证明"""
        # 高价值商品或敏感类别更可能需要零知识证明
        sensitive_categories = ["Electronics"]

        if category in sensitive_categories and price > 500:
            return random.choice([True, True, False])  # 67%概率
        elif price > 1000:
            return random.choice([True, False])  # 50%概率
        else:
            return random.choice([True, False, False, False])  # 25%概率


def main():
    """商品生成器测试"""
    print("=" * 50)
    print("ITEM GENERATOR TEST")
    print("=" * 50)

    items = ItemGenerator.generate_items(30)

    # 统计类别分布
    category_count = {}
    privacy_count = {}
    zk_proof_count = 0

    for item in items:
        category = item['category']
        privacy = item['privacy_level']
        category_count[category] = category_count.get(category, 0) + 1
        privacy_count[privacy] = privacy_count.get(privacy, 0) + 1
        if item['requires_zk_proof']:
            zk_proof_count += 1

    print(f"Generated {len(items)} items:")
    print("\nCategory distribution:")
    for category, count in category_count.items():
        print(f"  {category}: {count}")

    print("\nPrivacy level distribution:")
    for privacy, count in privacy_count.items():
        print(f"  {privacy}: {count}")

    print(f"\nZK proof required: {zk_proof_count}/{len(items)}")

    # 显示示例商品
    print("\nSample items:")
    for i, item in enumerate(items[:5]):
        print(f"  {i + 1}. {item['name']} - ${item['price']} ({item['privacy_level']})")

    print("Item generation test completed!")


if __name__ == "__main__":
    main()