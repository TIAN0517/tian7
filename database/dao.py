#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jy技術團隊 獨立USDT系統 v3.0 - 數據庫操作層
Author: TIAN0517
Version: 3.0.0
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from decimal import Decimal
import logging
from sqlalchemy import and_, or_, desc, func
from sqlalchemy.exc import IntegrityError

from database.db_manager import db_manager, get_session
from models.database_models import (
    User, WalletAddress, Transaction, PointsHistory,
    SystemLog, NetworkStatus, VIPLevel, BonusRule,
    TransactionStatus, NetworkType
)

# 配置日誌
logger = logging.getLogger(__name__)

class UserDAO:
    """用戶數據訪問對象"""
    
    @staticmethod
    def create_user(username: str, password_hash: str, email: str, phone: Optional[str] = None) -> User:
        """創建新用戶"""
        with get_session() as session:
            user = User(
                username=username,
                password_hash=password_hash,
                email=email,
                phone=phone
            )
            session.add(user)
            session.flush()
            return user

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """根據ID獲取用戶"""
        with get_session() as session:
            return session.query(User).get(user_id)

    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """根據用戶名獲取用戶"""
        with get_session() as session:
            return session.query(User).filter_by(username=username).first()

    @staticmethod
    def update_user(user_id: int, **kwargs) -> bool:
        """更新用戶信息"""
        with get_session() as session:
            user = session.query(User).get(user_id)
            if user:
                for key, value in kwargs.items():
                    setattr(user, key, value)
                return True
            return False

    @staticmethod
    def update_points(user_id: int, points: Decimal, description: str) -> bool:
        """更新用戶積分"""
        with get_session() as session:
            user = session.query(User).get(user_id)
            if user:
                user.total_points += points
                # 記錄積分歷史
                history = PointsHistory(
                    user_id=user_id,
                    points=points,
                    balance=user.total_points,
                    description=description
                )
                session.add(history)
                return True
            return False

class WalletDAO:
    """錢包數據訪問對象"""
    
    @staticmethod
    def add_wallet_address(user_id: int, network: NetworkType, address: str, label: Optional[str] = None) -> WalletAddress:
        """添加錢包地址"""
        with get_session() as session:
            wallet = WalletAddress(
                user_id=user_id,
                network=network,
                address=address,
                label=label
            )
            session.add(wallet)
            session.flush()
            return wallet

    @staticmethod
    def get_wallet_addresses(user_id: int) -> List[WalletAddress]:
        """獲取用戶的所有錢包地址"""
        with get_session() as session:
            return session.query(WalletAddress).filter_by(user_id=user_id).all()

    @staticmethod
    def update_wallet_status(wallet_id: int, is_active: bool) -> bool:
        """更新錢包狀態"""
        with get_session() as session:
            wallet = session.query(WalletAddress).get(wallet_id)
            if wallet:
                wallet.is_active = is_active
                return True
            return False

class TransactionDAO:
    """交易數據訪問對象"""
    
    @staticmethod
    def create_transaction(
        user_id: int,
        wallet_address_id: int,
        tx_hash: str,
        network: NetworkType,
        amount: Decimal,
        points_earned: Decimal,
        bonus_points: Decimal = Decimal('0')
    ) -> Transaction:
        """創建新交易"""
        with get_session() as session:
            transaction = Transaction(
                user_id=user_id,
                wallet_address_id=wallet_address_id,
                tx_hash=tx_hash,
                network=network,
                amount=amount,
                points_earned=points_earned,
                bonus_points=bonus_points
            )
            session.add(transaction)
            session.flush()
            return transaction

    @staticmethod
    def update_transaction_status(
        transaction_id: int,
        status: TransactionStatus,
        error_message: Optional[str] = None
    ) -> bool:
        """更新交易狀態"""
        with get_session() as session:
            transaction = session.query(Transaction).get(transaction_id)
            if transaction:
                transaction.status = status
                if status == TransactionStatus.CONFIRMED:
                    transaction.confirmed_at = datetime.utcnow()
                elif status == TransactionStatus.COMPLETED:
                    transaction.completed_at = datetime.utcnow()
                if error_message:
                    transaction.error_message = error_message
                return True
            return False

    @staticmethod
    def get_user_transactions(
        user_id: int,
        limit: int = 10,
        offset: int = 0,
        status: Optional[TransactionStatus] = None
    ) -> Tuple[List[Transaction], int]:
        """獲取用戶交易歷史"""
        with get_session() as session:
            query = session.query(Transaction).filter_by(user_id=user_id)
            if status:
                query = query.filter_by(status=status)
            
            total = query.count()
            transactions = query.order_by(desc(Transaction.created_at)).offset(offset).limit(limit).all()
            return transactions, total

class PointsDAO:
    """積分數據訪問對象"""
    
    @staticmethod
    def get_points_history(
        user_id: int,
        limit: int = 10,
        offset: int = 0
    ) -> Tuple[List[PointsHistory], int]:
        """獲取積分歷史"""
        with get_session() as session:
            query = session.query(PointsHistory).filter_by(user_id=user_id)
            total = query.count()
            history = query.order_by(desc(PointsHistory.created_at)).offset(offset).limit(limit).all()
            return history, total

    @staticmethod
    def get_user_points_summary(user_id: int) -> Dict[str, Any]:
        """獲取用戶積分摘要"""
        with get_session() as session:
            user = session.query(User).get(user_id)
            if user:
                return {
                    "total_points": user.total_points,
                    "total_deposits": user.total_deposits,
                    "vip_level": user.vip_level
                }
            return {}

class SystemLogDAO:
    """系統日誌數據訪問對象"""
    
    @staticmethod
    def add_log(level: str, module: str, message: str, metadata: Optional[Dict] = None) -> SystemLog:
        """添加系統日誌"""
        with get_session() as session:
            log = SystemLog(
                level=level,
                module=module,
                message=message,
                log_metadata=str(metadata) if metadata else None
            )
            session.add(log)
            session.flush()
            return log

    @staticmethod
    def get_logs(
        level: Optional[str] = None,
        module: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[SystemLog], int]:
        """獲取系統日誌"""
        with get_session() as session:
            query = session.query(SystemLog)
            if level:
                query = query.filter_by(level=level)
            if module:
                query = query.filter_by(module=module)
            
            total = query.count()
            logs = query.order_by(desc(SystemLog.created_at)).offset(offset).limit(limit).all()
            return logs, total

class NetworkStatusDAO:
    """網絡狀態數據訪問對象"""
    
    @staticmethod
    def update_network_status(
        network: NetworkType,
        is_active: bool,
        last_block: Optional[int] = None,
        error_count: Optional[int] = None,
        status_message: Optional[str] = None
    ) -> NetworkStatus:
        """更新網絡狀態"""
        with get_session() as session:
            status = session.query(NetworkStatus).filter_by(network=network).first()
            if not status:
                status = NetworkStatus(network=network)
                session.add(status)
            
            status.is_active = is_active
            if last_block is not None:
                status.last_block = last_block
            if error_count is not None:
                status.error_count = error_count
            if status_message is not None:
                status.status_message = status_message
            
            session.flush()
            return status

    @staticmethod
    def get_network_status(network: NetworkType) -> Optional[NetworkStatus]:
        """獲取網絡狀態"""
        with get_session() as session:
            return session.query(NetworkStatus).filter_by(network=network).first()

# 導出DAO實例
user_dao = UserDAO()
wallet_dao = WalletDAO()
transaction_dao = TransactionDAO()
points_dao = PointsDAO()
system_log_dao = SystemLogDAO()
network_status_dao = NetworkStatusDAO() 