import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from .config import config

def setup_logger(name: str = None) -> logging.Logger:
    """設置日誌記錄器
    
    Args:
        name: 日誌記錄器名稱，默認為根記錄器
        
    Returns:
        logging.Logger: 配置好的日誌記錄器
    """
    # 獲取日誌記錄器
    logger = logging.getLogger(name)
    
    # 如果已經配置過，直接返回
    if logger.handlers:
        return logger
        
    # 設置日誌級別
    log_level = getattr(logging, config['LOG_LEVEL'].upper())
    logger.setLevel(log_level)
    
    # 創建格式化器
    formatter = logging.Formatter(config['LOG_FORMAT'])
    
    # 創建控制台處理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 創建文件處理器
    log_path = Path(config['LOG_PATH'])
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# 創建默認日誌記錄器
logger = setup_logger('nl_online')

def get_logger(name: str) -> logging.Logger:
    """獲取指定名稱的日誌記錄器
    
    Args:
        name: 日誌記錄器名稱
        
    Returns:
        logging.Logger: 配置好的日誌記錄器
    """
    return setup_logger(name) 