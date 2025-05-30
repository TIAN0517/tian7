from enum import Enum
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from .config import config
from src.database.db_manager import db_manager

# 創建數據庫引擎
engine = create_engine(f"sqlite:///{config['DB_PATH']}", echo=config['DEBUG'])
Session = sessionmaker(bind=engine)
Base = declarative_base()

class TransactionType(str, Enum):
    """交易類型枚舉"""
    DEPOSIT = "deposit"  # 充值
    WITHDRAW = "withdraw"  # 提現
    BET = "bet"  # 下注
    WIN = "win"  # 贏取
    BONUS = "bonus"  # 獎勵
    REFUND = "refund"  # 退款
    ITEM_EXCHANGE = "item_exchange"  # 物品兌換

class TransactionStatus(str, Enum):
    """交易狀態枚舉"""
    PENDING = "pending"  # 待處理
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失敗
    CANCELLED = "cancelled"  # 已取消

class User(db_manager.Base):
    """用戶模型"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    credits = Column(Float, default=config['INITIAL_CREDITS'])
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # 關聯
    game_records = relationship("GameRecord", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>"

class GameRecord(db_manager.Base):
    """遊戲記錄模型"""
    __tablename__ = 'game_records'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    game_type = Column(String(50), nullable=False)  # casino 或 minigame
    game_name = Column(String(50), nullable=False)
    bet_amount = Column(Float, default=0)
    win_amount = Column(Float, default=0)
    result = Column(String(50))  # win, lose, draw
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    user = relationship("User", back_populates="game_records")
    
    def __repr__(self):
        return f"<GameRecord {self.game_name} - {self.result}>"

class Transaction(db_manager.Base):
    """交易記錄模型"""
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Float, nullable=False)
    type = Column(SQLEnum(TransactionType), nullable=False)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # 關聯
    user = relationship("User", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction {self.type} - {self.amount}>"

class GameVersion(db_manager.Base):
    """遊戲版本模型"""
    __tablename__ = 'game_versions'
    
    id = Column(Integer, primary_key=True)
    version = Column(String(20), nullable=False)
    download_url = Column(String(255), nullable=False)
    file_hash = Column(String(64), nullable=False)  # SHA-256
    is_active = Column(Boolean, default=True)
    release_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<GameVersion {self.version}>"

class ChatMessage(db_manager.Base):
    """聊天消息模型"""
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    message = Column(Text, nullable=False)
    response = Column(Text)
    is_ai = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    user = relationship("User", back_populates="chat_messages")
    
    def __repr__(self):
        return f"<ChatMessage {self.id}>"

def init_db():
    """初始化數據庫"""
    Base.metadata.create_all(engine)
    
def get_session():
    """獲取數據庫會話"""
    return Session()

# 初始化數據庫
init_db() 