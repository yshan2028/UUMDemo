#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: logger.py
Author: yshan2028
Created: 2025-06-13 08:47:13
Description: 日志模块
"""

import logging
import os
from datetime import datetime
from config.settings import LOGS_PATH


def setup_logging():
    """配置实验系统的日志记录"""
    log_format = "[%(asctime)s] %(levelname)s: %(message)s"
    log_file = os.path.join(LOGS_PATH, f'experiment_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )

    logging.info(f"Logging initialized: {log_file}")