#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: logger.py
Author: yshan2028
Created: 2025-06-13 14:56:13
Description: 
    [请在此处添加文件描述]

Dependencies:
    [请在此处列出主要依赖]

Usage:
    [请在此处添加使用说明]
"""

import logging

def setup_logger(name: str, log_file: str, level=logging.INFO):
    """
    设置日志记录器。

    :param name: 日志记录器名称。
    :param log_file: 日志文件路径。
    :param level: 日志记录级别。
    :return: 配置好的日志记录器实例。
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

if __name__ == "__main__":
    # 测试日志功能
    logger = setup_logger("experiment_logger", "logs/experiment.log")
    logger.info("This is an info message.")
    logger.error("This is an error message.")
