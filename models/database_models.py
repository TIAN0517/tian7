#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jy技術團隊 獨立USDT系統 v3.0 - 數據庫模型
Author: TIAN0517
Version: 3.0.0
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Numeric, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class TransactionStatus(enum.Enum):
    """交易狀態枚舉"""
    PENDING = "pending"      # 待處理
    CONFIRMED = "confirmed"  # 已確認
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失敗
    CANCELLED = "cancelled"  # 已取消

class NetworkType(enum.Enum):
    """網絡類型枚舉"""
    TRC20 = "TRC20"
    ERC20 = "ERC20"
    BEP20 = "BEP20"

class User(Base):
    """用戶表"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    phone = Column(String(20), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    vip_level = Column(Integer, default=1)
    total_points = Column(Numeric(20, 2), default=0)
    total_deposits = Column(Numeric(20, 2), default=0)
    
    # 關聯
    transactions = relationship("Transaction", back_populates="user")
    addresses = relationship("WalletAddress", back_populates="user")
    points_history = relationship("PointsHistory", back_populates="user")

class WalletAddress(Base):
    """錢包地址表"""
    __tablename__ = 'wallet_addresses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    network = Column(Enum(NetworkType), nullable=False)
    address = Column(String(100), nullable=False)
    label = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    
    # 關聯
    user = relationship("User", back_populates="addresses")
    transactions = relationship("Transaction", back_populates="wallet_address")

class Transaction(Base):
    """交易表"""
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    wallet_address_id = Column(Integer, ForeignKey('wallet_addresses.id'), nullable=False)
    tx_hash = Column(String(100), unique=True, nullable=False)
    network = Column(Enum(NetworkType), nullable=False)
    amount = Column(Numeric(20, 6), nullable=False)  # USDT金額
    points_earned = Column(Numeric(20, 2), nullable=False)  # 獲得的積分
    bonus_points = Column(Numeric(20, 2), default=0)  # 獎勵積分
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    
    # 關聯
    user = relationship("User", back_populates="transactions")
    wallet_address = relationship("WalletAddress", back_populates="transactions")

class PointsHistory(Base):
    """積分歷史表"""
    __tablename__ = 'points_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    points = Column(Numeric(20, 2), nullable=False)
    balance = Column(Numeric(20, 2), nullable=False)  # 交易後的餘額
    description = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    user = relationship("User", back_populates="points_history")
    transaction = relationship("Transaction")

class SystemLog(Base):
    """系統日誌表"""
    __tablename__ = 'system_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR
    module = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    log_metadata = Column(Text)  # JSON格式的額外信息（原metadata）

class NetworkStatus(Base):
    """網絡狀態表"""
    __tablename__ = 'network_status'

    id = Column(Integer, primary_key=True, autoincrement=True)
    network = Column(Enum(NetworkType), nullable=False)
    is_active = Column(Boolean, default=True)
    last_block = Column(Integer)
    last_check = Column(DateTime, default=datetime.utcnow)
    error_count = Column(Integer, default=0)
    status_message = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class VIPLevel(Base):
    """VIP等級表"""
    __tablename__ = 'vip_levels'

    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(Integer, nullable=False, unique=True)
    name = Column(String(50), nullable=False)
    points_required = Column(Numeric(20, 2), nullable=False)
    multiplier = Column(Numeric(5, 2), nullable=False)  # 積分倍率
    benefits = Column(Text)  # JSON格式的權益描述
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BonusRule(Base):
    """獎勵規則表"""
    __tablename__ = 'bonus_rules'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    type = Column(String(20), nullable=False)  # first_deposit, weekend, etc.
    min_amount = Column(Numeric(20, 2))
    max_amount = Column(Numeric(20, 2))
    bonus_rate = Column(Numeric(5, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    conditions = Column(Text)  # JSON格式的條件
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 創建所有表
def create_tables(engine):
    """創建所有數據庫表"""
    Base.metadata.create_all(engine)

# 刪除所有表
def drop_tables(engine):
    """刪除所有數據庫表"""
    Base.metadata.drop_all(engine) 