#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jy技術團隊 獨立USDT系統 v3.0 - 日誌系統
Author: TIAN0517
Version: 3.0.0
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from datetime import datetime

# 創建日誌目錄
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 日誌格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logger(name: str, log_file: str = None, level: int = logging.INFO) -> logging.Logger:
    """設置日誌記錄器
    
    Args:
        name: 日誌記錄器名稱
        log_file: 日誌文件名（可選）
        level: 日誌級別
        
    Returns:
        logging.Logger: 配置好的日誌記錄器
    """
    # 創建日誌記錄器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 清除現有的處理器
    logger.handlers.clear()
    
    # 創建控制台處理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 如果指定了日誌文件，創建文件處理器
    if log_file:
        # 創建按大小輪轉的文件處理器
        file_handler = RotatingFileHandler(
            filename=LOG_DIR / log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # 創建按時間輪轉的文件處理器
        time_handler = TimedRotatingFileHandler(
            filename=LOG_DIR / f"{log_file}.{datetime.now().strftime('%Y%m%d')}",
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        time_handler.setLevel(level)
        time_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
        time_handler.setFormatter(time_formatter)
        logger.addHandler(time_handler)
    
    return logger

# 創建不同模組的日誌記錄器
api_logger = setup_logger('api', 'api.log')
db_logger = setup_logger('database', 'database.log')
blockchain_logger = setup_logger('blockchain', 'blockchain.log')
user_logger = setup_logger('user', 'user.log')
transaction_logger = setup_logger('transaction', 'transaction.log')
system_logger = setup_logger('system', 'system.log')

def log_error(logger: logging.Logger, error: Exception, context: dict = None):
    """記錄錯誤日誌
    
    Args:
        logger: 日誌記錄器
        error: 異常對象
        context: 上下文信息（可選）
    """
    error_msg = f"錯誤: {str(error)}"
    if context:
        error_msg += f"\n上下文: {context}"
    logger.error(error_msg, exc_info=True)

def log_warning(logger: logging.Logger, message: str, context: dict = None):
    """記錄警告日誌
    
    Args:
        logger: 日誌記錄器
        message: 警告消息
        context: 上下文信息（可選）
    """
    warning_msg = f"警告: {message}"
    if context:
        warning_msg += f"\n上下文: {context}"
    logger.warning(warning_msg)

def log_info(logger: logging.Logger, message: str, context: dict = None):
    """記錄信息日誌
    
    Args:
        logger: 日誌記錄器
        message: 信息消息
        context: 上下文信息（可選）
    """
    info_msg = f"信息: {message}"
    if context:
        info_msg += f"\n上下文: {context}"
    logger.info(info_msg)

def log_debug(logger: logging.Logger, message: str, context: dict = None):
    """記錄調試日誌
    
    Args:
        logger: 日誌記錄器
        message: 調試消息
        context: 上下文信息（可選）
    """
    debug_msg = f"調試: {message}"
    if context:
        debug_msg += f"\n上下文: {context}"
    logger.debug(debug_msg) 