from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import logging

from src.config.usdt_config import config

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.Session = None
        self.Base = declarative_base()
        
    def init_engine(self):
        """初始化數據庫引擎"""
        try:
            self.engine = create_engine(
                config.DATABASE_URL,
                pool_size=config.DB_POOL_SIZE,
                max_overflow=config.DB_MAX_OVERFLOW,
                pool_timeout=config.DB_POOL_TIMEOUT,
                pool_recycle=config.DB_POOL_RECYCLE,
                pool_pre_ping=config.DB_POOL_PRE_PING
            )
            self.Session = scoped_session(sessionmaker(bind=self.engine))
            logger.info("數據庫引擎初始化成功")
            return True
        except Exception as e:
            logger.error(f"數據庫引擎初始化失敗: {str(e)}")
            return False
            
    def check_connection(self):
        """檢查數據庫連接"""
        try:
            if not self.engine:
                return self.init_engine()
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"數據庫連接檢查失敗: {str(e)}")
            return False
            
    def create_tables(self):
        """創建數據表"""
        try:
            self.Base.metadata.create_all(self.engine)
            logger.info("數據表創建成功")
            return True
        except Exception as e:
            logger.error(f"數據表創建失敗: {str(e)}")
            return False

# 創建全局數據庫管理器實例
db_manager = DatabaseManager() 