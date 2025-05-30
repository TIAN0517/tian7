#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jy技術團隊 獨立USDT系統 v3.0 - 交易服務層
Author: TIAN0517
Version: 3.0.0
"""

from datetime import datetime
from typing import Optional, Dict, Any, Tuple, List
from decimal import Decimal
import logging
from web3 import Web3
from eth_account import Account
import requests

from config.usdt_config import config
from database.dao import (
    transaction_dao, wallet_dao, user_dao,
    points_dao, system_log_dao, network_status_dao
)
from models.database_models import (
    Transaction, WalletAddress, TransactionStatus,
    NetworkType, User
)

# 配置日誌
logger = logging.getLogger(__name__)

class TransactionService:
    """交易服務類"""
    
    @staticmethod
    def validate_amount(amount: Decimal) -> Tuple[bool, str]:
        """驗證交易金額"""
        if amount <= 0:
            return False, "交易金額必須大於0"
        if amount < config.MIN_DEPOSIT_AMOUNT:
            return False, f"最小充值金額為 {config.MIN_DEPOSIT_AMOUNT} USDT"
        if amount > config.MAX_DEPOSIT_AMOUNT:
            return False, f"最大充值金額為 {config.MAX_DEPOSIT_AMOUNT} USDT"
        return True, ""

    @staticmethod
    def calculate_points(amount: Decimal, network: NetworkType) -> Decimal:
        """計算積分獎勵"""
        base_points = amount * config.POINTS_PER_USDT
        network_multiplier = config.NETWORK_MULTIPLIERS.get(network, 1.0)
        return base_points * Decimal(str(network_multiplier))

    @staticmethod
    def calculate_bonus(amount: Decimal, user: User) -> Decimal:
        """計算額外獎勵"""
        # 根據用戶VIP等級計算獎勵倍率
        vip_multiplier = config.VIP_BONUS_MULTIPLIERS.get(user.vip_level, 0)
        return amount * Decimal(str(vip_multiplier))

    @classmethod
    def create_deposit(cls, user_id: int, network: NetworkType, amount: Decimal) -> Tuple[bool, str, Optional[Dict]]:
        """創建充值交易"""
        try:
            # 驗證用戶
            user = user_dao.get_user_by_id(user_id)
            if not user:
                return False, "用戶不存在", None

            # 驗證金額
            valid, msg = cls.validate_amount(amount)
            if not valid:
                return False, msg, None

            # 獲取用戶錢包地址
            wallet = wallet_dao.get_wallet_addresses(user_id)
            if not wallet:
                return False, "請先添加錢包地址", None

            # 計算積分和獎勵
            points = cls.calculate_points(amount, network)
            bonus = cls.calculate_bonus(amount, user)

            # 創建交易記錄
            transaction = transaction_dao.create_transaction(
                user_id=user_id,
                wallet_address_id=wallet[0].id,
                tx_hash="",  # 等待用戶轉賬後更新
                network=network,
                amount=amount,
                points_earned=points,
                bonus_points=bonus
            )

            # 記錄日誌
            system_log_dao.add_log(
                level="INFO",
                module="TransactionService",
                message=f"創建充值交易: {amount} USDT",
                metadata={
                    "user_id": user_id,
                    "transaction_id": transaction.id,
                    "network": network.value
                }
            )

            return True, "創建成功", {
                "transaction_id": transaction.id,
                "wallet_address": wallet[0].address,
                "amount": amount,
                "points": points,
                "bonus": bonus
            }

        except Exception as e:
            logger.error(f"創建充值交易失敗: {str(e)}")
            return False, "創建充值交易失敗，請稍後重試", None

    @classmethod
    def verify_transaction(cls, tx_hash: str, network: NetworkType) -> Tuple[bool, str, Optional[Dict]]:
        """驗證交易"""
        try:
            # 獲取交易記錄
            transaction = transaction_dao.get_transaction_by_hash(tx_hash)
            if not transaction:
                return False, "交易記錄不存在", None

            # 檢查交易狀態
            if transaction.status != TransactionStatus.PENDING:
                return False, "交易狀態不正確", None

            # 根據網絡類型驗證交易
            if network == NetworkType.TRC20:
                success, data = cls._verify_trc20_transaction(tx_hash)
            elif network == NetworkType.ERC20:
                success, data = cls._verify_erc20_transaction(tx_hash)
            elif network == NetworkType.BEP20:
                success, data = cls._verify_bep20_transaction(tx_hash)
            else:
                return False, "不支持的網絡類型", None

            if not success:
                return False, data, None

            # 更新交易狀態
            transaction_dao.update_transaction_status(
                transaction_id=transaction.id,
                status=TransactionStatus.CONFIRMED
            )

            # 更新用戶積分
            total_points = transaction.points_earned + transaction.bonus_points
            user_dao.update_points(
                user_id=transaction.user_id,
                points=total_points,
                description=f"充值 {transaction.amount} USDT 獲得積分"
            )

            # 記錄日誌
            system_log_dao.add_log(
                level="INFO",
                module="TransactionService",
                message=f"交易確認成功: {tx_hash}",
                metadata={
                    "transaction_id": transaction.id,
                    "user_id": transaction.user_id,
                    "amount": transaction.amount
                }
            )

            return True, "交易確認成功", {
                "transaction_id": transaction.id,
                "amount": transaction.amount,
                "points": total_points
            }

        except Exception as e:
            logger.error(f"驗證交易失敗: {str(e)}")
            return False, "驗證交易失敗，請稍後重試", None

    @staticmethod
    def _verify_trc20_transaction(tx_hash: str) -> Tuple[bool, str]:
        """驗證TRC20交易"""
        try:
            # TODO: 實現TRC20交易驗證邏輯
            return True, "驗證成功"
        except Exception as e:
            logger.error(f"TRC20交易驗證失敗: {str(e)}")
            return False, "交易驗證失敗"

    @staticmethod
    def _verify_erc20_transaction(tx_hash: str) -> Tuple[bool, str]:
        """驗證ERC20交易"""
        try:
            # TODO: 實現ERC20交易驗證邏輯
            return True, "驗證成功"
        except Exception as e:
            logger.error(f"ERC20交易驗證失敗: {str(e)}")
            return False, "交易驗證失敗"

    @staticmethod
    def _verify_bep20_transaction(tx_hash: str) -> Tuple[bool, str]:
        """驗證BEP20交易"""
        try:
            # TODO: 實現BEP20交易驗證邏輯
            return True, "驗證成功"
        except Exception as e:
            logger.error(f"BEP20交易驗證失敗: {str(e)}")
            return False, "交易驗證失敗"

    @classmethod
    def get_transaction_history(
        cls,
        user_id: int,
        page: int = 1,
        page_size: int = 10,
        status: Optional[TransactionStatus] = None
    ) -> Tuple[bool, str, Optional[Dict]]:
        """獲取交易歷史"""
        try:
            offset = (page - 1) * page_size
            transactions, total = transaction_dao.get_user_transactions(
                user_id=user_id,
                limit=page_size,
                offset=offset,
                status=status
            )

            return True, "獲取成功", {
                "transactions": [
                    {
                        "id": tx.id,
                        "amount": tx.amount,
                        "network": tx.network.value,
                        "status": tx.status.value,
                        "points_earned": tx.points_earned,
                        "bonus_points": tx.bonus_points,
                        "created_at": tx.created_at.isoformat(),
                        "confirmed_at": tx.confirmed_at.isoformat() if tx.confirmed_at else None,
                        "completed_at": tx.completed_at.isoformat() if tx.completed_at else None
                    }
                    for tx in transactions
                ],
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }

        except Exception as e:
            logger.error(f"獲取交易歷史失敗: {str(e)}")
            return False, "獲取交易歷史失敗，請稍後重試", None

    @classmethod
    def get_network_status(cls) -> Tuple[bool, str, Optional[Dict]]:
        """獲取網絡狀態"""
        try:
            status = {}
            for network in NetworkType:
                network_status = network_status_dao.get_network_status(network)
                if network_status:
                    status[network.value] = {
                        "is_active": network_status.is_active,
                        "last_block": network_status.last_block,
                        "error_count": network_status.error_count,
                        "status_message": network_status.status_message
                    }

            return True, "獲取成功", status

        except Exception as e:
            logger.error(f"獲取網絡狀態失敗: {str(e)}")
            return False, "獲取網絡狀態失敗，請稍後重試", None

# 導出服務實例
transaction_service = TransactionService() 