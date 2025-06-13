
```bash
/project
  ├── main.py                     # 主程序入口
  ├── config/                     # 配置文件
  │   └── settings.py             # 全局配置文件
  ├── data/                       # 数据生成与预处理
  │   ├── generate_orders.py      # 模拟订单生成
  │   ├── preprocess_orders.py    # 数据预处理工具
  │   ├── sample_orders.json      # 示例订单数据
  ├── blockchain/                 # 区块链核心模块
  │   ├── blockchain_storage.py   # 实现区块链存储逻辑
  │   ├── transaction_manager.py  # 交易管理模块
  │   ├── smart_contracts/        # 智能合约模块
  │       ├── permissions.sol     # 权限管理合约
  │       └── orders.sol          # 订单处理合约
  ├── storage/                    # 链下数据存储模块
  │   ├── mysql_storage.py        # MySQL 存储实现
  │   ├── redis_cache.py          # Redis 缓存实现
  │   ├── data_validation.py      # 数据验证模块
  ├── algorithms/                 # 核心算法模块
  │   ├── shamir.py               # Shamir 秘密共享算法
  │   ├── merkle_tree.py          # Merkle 树生成与验证
  │   ├── zk_proof.py             # 零知识证明模块
  │   ├── dynamic_access.py       # 动态权限管理模块
  ├── experiments/                # 实验模块
  │   ├── performance_test.py     # 性能测试
  │   ├── privacy_test.py         # 隐私保护实验
  │   ├── attack_simulation.py    # 模拟攻击实验
  │   ├── comparison_test.py      # 性能对比实验
  │   ├── throughput_test.py      # 吞吐量测试
  │   ├── results/                # 实验结果文件夹
  │       ├── hyperledger.csv     # Hyperledger 性能结果
  │       ├── ethereum.csv        # Ethereum 性能结果
  │       ├── comparison.csv      # 对比实验结果
  ├── analysis/                   # 数据分析与可视化
  │   ├── visualize_results.py    # 数据可视化工具
  │   └── generate_report.py      # 生成实验报告
  ├── utils/                      # 通用工具
  │   ├── logger.py               # 日志模块
  │   ├── helpers.py              # 工具函数
  └── README.md                   # 项目说明

```
