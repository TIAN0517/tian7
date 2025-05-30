#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jy技術團隊 獨立USDT系統 v3.0 - 數據庫初始化腳本
Author: TIAN0517
Version: 3.0.0
"""

import sys
import os
import logging
from pathlib import Path

# 添加項目根目錄到Python路徑
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from database.db_manager import db_manager
from models.database_models import Base
from config.usdt_config import config

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_database():
    """初始化數據庫"""
    try:
        # 檢查數據庫連接
        if not db_manager.check_connection():
            raise Exception("數據庫連接失敗")

        # 創建所有表
        db_manager.create_tables()
        logger.info("數據庫表創建成功")

        # 創建初始VIP等級
        from database.dao import VIPLevelDAO
        vip_dao = VIPLevelDAO()
        vip_levels = [
            {
                "level": 1,
                "name": "普通會員",
                "min_points": 0,
                "bonus_rate": 1.0,
                "description": "普通會員"
            },
            {
                "level": 2,
                "name": "白銀會員",
                "min_points": 1000,
                "bonus_rate": 1.1,
                "description": "白銀會員"
            },
            {
                "level": 3,
                "name": "黃金會員",
                "min_points": 5000,
                "bonus_rate": 1.2,
                "description": "黃金會員"
            },
            {
                "level": 4,
                "name": "鉑金會員",
                "min_points": 20000,
                "bonus_rate": 1.3,
                "description": "鉑金會員"
            },
            {
                "level": 5,
                "name": "鑽石會員",
                "min_points": 50000,
                "bonus_rate": 1.5,
                "description": "鑽石會員"
            }
        ]
        
        for level in vip_levels:
            vip_dao.create_vip_level(**level)
        logger.info("VIP等級初始化成功")

        # 創建獎勵規則
        from database.dao import BonusRuleDAO
        bonus_dao = BonusRuleDAO()
        bonus_rules = [
            {
                "network": "TRC20",
                "min_amount": 100,
                "max_amount": 1000,
                "points_rate": 1.0,
                "description": "TRC20小額充值"
            },
            {
                "network": "TRC20",
                "min_amount": 1000,
                "max_amount": 10000,
                "points_rate": 1.1,
                "description": "TRC20中額充值"
            },
            {
                "network": "TRC20",
                "min_amount": 10000,
                "max_amount": None,
                "points_rate": 1.2,
                "description": "TRC20大額充值"
            },
            {
                "network": "ERC20",
                "min_amount": 100,
                "max_amount": 1000,
                "points_rate": 1.2,
                "description": "ERC20小額充值"
            },
            {
                "network": "ERC20",
                "min_amount": 1000,
                "max_amount": 10000,
                "points_rate": 1.3,
                "description": "ERC20中額充值"
            },
            {
                "network": "ERC20",
                "min_amount": 10000,
                "max_amount": None,
                "points_rate": 1.4,
                "description": "ERC20大額充值"
            },
            {
                "network": "BEP20",
                "min_amount": 100,
                "max_amount": 1000,
                "points_rate": 1.1,
                "description": "BEP20小額充值"
            },
            {
                "network": "BEP20",
                "min_amount": 1000,
                "max_amount": 10000,
                "points_rate": 1.2,
                "description": "BEP20中額充值"
            },
            {
                "network": "BEP20",
                "min_amount": 10000,
                "max_amount": None,
                "points_rate": 1.3,
                "description": "BEP20大額充值"
            }
        ]
        
        for rule in bonus_rules:
            bonus_dao.create_bonus_rule(**rule)
        logger.info("獎勵規則初始化成功")

        logger.info("數據庫初始化完成")
        return True

    except Exception as e:
        logger.error(f"數據庫初始化失敗: {str(e)}")
        return False

def drop_database():
    """刪除所有表"""
    try:
        db_manager.drop_tables()
        logger.info("數據庫表刪除成功")
        return True
    except Exception as e:
        logger.error(f"數據庫表刪除失敗: {str(e)}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="數據庫初始化工具")
    parser.add_argument("--drop", action="store_true", help="刪除所有表")
    args = parser.parse_args()

    if args.drop:
        if input("確定要刪除所有表嗎？(y/n): ").lower() == 'y':
            drop_database()
    else:
        init_database() 