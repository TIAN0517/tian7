#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jy技術團隊 獨立USDT系統 v3.0 - 核心配置模組
Author: TIAN0517
Version: 3.0.0
"""

from typing import Dict, List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from dataclasses import dataclass
from decimal import Decimal
import logging
from pathlib import Path

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class NetworkStatus:
    """網絡狀態數據類"""
    network: str
    is_active: bool
    last_block: int
    last_check: float
    error_count: int = 0
    status_message: str = ""

@dataclass
class SystemMetrics:
    """系統指標數據類"""
    total_transactions: int = 0
    total_points_issued: Decimal = Decimal('0')
    active_addresses: int = 0
    last_cleanup: float = 0.0

class USDTSystemConfig(BaseSettings):
    """USDT系統配置類"""
    # 項目信息
    PROJECT_NAME: str = "RanNL Game Launcher"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    APP_NAME: str = "RanNL Game Launcher"
    APP_VERSION: str = "1.0.0"
    
    # 核心匯率
    USDT_TO_POINTS_RATE: Decimal = Decimal('30.0')
    
    # SQL Server 配置
    DB_SERVER: str = "49.158.236.36"
    DB_PORT: int = 1433
    DB_USER: str = "lstjks"
    DB_PASSWORD: str = "ji394su3@@"
    DB_NAME: str = "RanUser"
    DB_SERVER_NAME: str = "WIN-2BAJ6SC2P2P"
    
    # 區塊鏈網絡配置
    TRON_NETWORK: str = "mainnet"
    TRON_RPC_URLS: List[str] = [
        "https://api.trongrid.io",
        "https://api.shasta.trongrid.io"
    ]
    ETH_RPC_URLS: List[str] = [
        "https://mainnet.infura.io/v3/your-project-id",
        "https://eth-mainnet.alchemyapi.io/v2/your-api-key"
    ]
    BSC_RPC_URLS: List[str] = [
        "https://bsc-dataseed.binance.org",
        "https://bsc-dataseed1.defibit.io"
    ]
    
    # USDT合約地址
    USDT_CONTRACTS: Dict[str, str] = {
        "TRC20": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
        "ERC20": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "BEP20": "0x55d398326f99059fF775485246999027B3197955"
    }
    
    # 網絡參數
    NETWORK_PARAMS: Dict[str, Dict] = {
        "TRC20": {
            "decimals": 6,
            "confirmations": 19,
            "scan_url": "https://tronscan.org/#/transaction/",
            "min_amount": Decimal('1.0'),
            "max_amount": Decimal('10000.0')
        },
        "ERC20": {
            "decimals": 6,
            "confirmations": 12,
            "scan_url": "https://etherscan.io/tx/",
            "min_amount": Decimal('1.0'),
            "max_amount": Decimal('10000.0')
        },
        "BEP20": {
            "decimals": 18,
            "confirmations": 15,
            "scan_url": "https://bscscan.com/tx/",
            "min_amount": Decimal('1.0'),
            "max_amount": Decimal('10000.0')
        }
    }
    
    # 多級積分獎勵階梯
    POINTS_REWARD_TIERS: List[Dict] = [
        {"min_amount": Decimal('100.0'), "max_amount": Decimal('500.0'), "bonus_rate": Decimal('0.05')},
        {"min_amount": Decimal('500.0'), "max_amount": Decimal('1000.0'), "bonus_rate": Decimal('0.10')},
        {"min_amount": Decimal('1000.0'), "max_amount": Decimal('5000.0'), "bonus_rate": Decimal('0.15')},
        {"min_amount": Decimal('5000.0'), "max_amount": Decimal('10000.0'), "bonus_rate": Decimal('0.20')}
    ]
    
    # VIP等級倍數
    VIP_MULTIPLIERS: Dict[int, Decimal] = {
        1: Decimal('1.0'),
        2: Decimal('1.1'),
        3: Decimal('1.2'),
        4: Decimal('1.3'),
        5: Decimal('1.5')
    }
    
    # 特殊獎勵配置
    SPECIAL_REWARDS: Dict[str, Dict] = {
        "first_deposit": {
            "enabled": True,
            "bonus_rate": Decimal('0.1'),
            "max_amount": Decimal('100.0')
        },
        "weekend": {
            "enabled": True,
            "bonus_rate": Decimal('0.05'),
            "max_amount": Decimal('1000.0')
        }
    }
    
    # 安全配置
    ENCRYPTION_KEY: str = "your-encryption-key"
    JWT_SECRET: str = "your-jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 監控配置
    MONITORING_INTERVAL: int = 60  # 秒
    HEALTH_CHECK_INTERVAL: int = 300  # 秒
    MAX_RETRY_ATTEMPTS: int = 3
    RETRY_DELAY: int = 5  # 秒
    
    # 業務限制
    MAX_DAILY_DEPOSITS: int = 10
    MAX_DAILY_AMOUNT: Decimal = Decimal('50000.0')
    MIN_DEPOSIT_AMOUNT: Decimal = Decimal('1.0')
    MAX_DEPOSIT_AMOUNT: Decimal = Decimal('10000.0')
    
    # 容災配置
    BACKUP_INTERVAL: int = 3600  # 秒
    MAX_BACKUP_FILES: int = 7
    BACKUP_PATH: Path = Path("backups")
    
    # 性能配置
    DB_POOL_SIZE: int = 5  # 降低連接池大小
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800  # 30分鐘
    DB_POOL_PRE_PING: bool = True
    
    # 開發與API文檔配置
    API_PREFIX: str = "/api/v3"
    API_TITLE: str = "RanNL Game Launcher API"
    API_DESCRIPTION: str = "RanNL Game Launcher API文檔"
    API_VERSION: str = "1.0.0"
    API_DOCS_URL: str = "/docs"
    API_REDOC_URL: str = "/redoc"
    API_OPENAPI_URL: str = "/openapi.json"
    API_CORS_ORIGINS: List[str] = ["*"]
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 1
    API_RELOAD: bool = True
    API_LOG_LEVEL: str = "info"
    
    TRC20_RECEIVE_ADDRESS: str = "TDejRjcLQa92rrE6SB71LSC7J5VmHs35gq"
    ERC20_RECEIVE_ADDRESS: str = "0x732b0b53435977b03c4cef6b7bdffc45e6ec44e6"
    
    SQLITE_DB_PATH: str = "ranuser.db"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"sqlite:///{self.SQLITE_DB_PATH}"
    
    def validate_config(self) -> bool:
        """驗證配置是否有效"""
        try:
            # 驗證必要配置
            assert self.USDT_TO_POINTS_RATE > 0, "USDT兌換積分比例必須大於0"
            assert all(len(urls) > 0 for urls in [self.TRON_RPC_URLS, self.ETH_RPC_URLS, self.BSC_RPC_URLS]), "RPC URL列表不能為空"
            assert all(contract for contract in self.USDT_CONTRACTS.values()), "USDT合約地址不能為空"
            
            # 驗證獎勵配置
            assert all(tier["bonus_rate"] > 0 for tier in self.POINTS_REWARD_TIERS), "獎勵倍率必須大於0"
            assert all(multiplier > 0 for multiplier in self.VIP_MULTIPLIERS.values()), "VIP倍率必須大於0"
            
            # 驗證業務限制
            assert self.MIN_DEPOSIT_AMOUNT < self.MAX_DEPOSIT_AMOUNT, "最小充值金額必須小於最大充值金額"
            assert self.MAX_DAILY_DEPOSITS > 0, "每日最大充值次數必須大於0"
            
            return True
        except AssertionError as e:
            logger.error(f"配置驗證失敗: {str(e)}")
            return False
    
    def log_config_info(self) -> None:
        """記錄配置信息"""
        logger.info(f"項目名稱: {self.PROJECT_NAME}")
        logger.info(f"版本: {self.VERSION}")
        logger.info(f"環境: {self.ENVIRONMENT}")
        logger.info(f"USDT兌換積分比例: {self.USDT_TO_POINTS_RATE}")
        logger.info(f"數據庫服務器: {self.DB_SERVER}")
        logger.info(f"數據庫名稱: {self.DB_NAME}")
        
        # 記錄網絡配置
        for network, urls in {
            "TRON": self.TRON_RPC_URLS,
            "ETH": self.ETH_RPC_URLS,
            "BSC": self.BSC_RPC_URLS
        }.items():
            logger.info(f"{network} RPC URLs: {urls}")
        
        # 記錄合約地址
        for network, address in self.USDT_CONTRACTS.items():
            logger.info(f"{network} USDT合約地址: {address}")
    
    class Config:
        """Pydantic配置類"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"

# 創建全局配置實例
config = USDTSystemConfig()

# 驗證並記錄配置
if config.validate_config():
    config.log_config_info()
else:
    raise ValueError("配置驗證失敗，請檢查配置項") 