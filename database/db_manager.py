from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
import logging
from typing import Generator
from config.usdt_config import config
from models.database_models import Base

logger = logging.getLogger(__name__)

class DatabaseManager:
    _instance = None
    _engine = None
    _session_factory = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._engine is None:
            self._initialize_engine()

    def _initialize_engine(self):
        try:
            self._engine = create_engine(
                config.DATABASE_URL,
                echo=config.DEBUG
            )
            self._session_factory = scoped_session(
                sessionmaker(
                    bind=self._engine,
                    autocommit=False,
                    autoflush=False,
                    expire_on_commit=False
                )
            )
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            logger.info("SQLite 數據庫連接池初始化成功")
        except Exception as e:
            logger.error(f"SQLite 數據庫連接池初始化失敗: {str(e)}")
            raise

    @property
    def engine(self):
        return self._engine

    @property
    def session(self):
        return self._session_factory()

    @contextmanager
    def get_session(self) -> Generator:
        session = self.session
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"數據庫事務回滾: {str(e)}")
            raise
        finally:
            session.close()

    def create_tables(self):
        try:
            Base.metadata.create_all(self._engine)
            logger.info("數據表創建成功")
        except Exception as e:
            logger.error(f"創建數據表失敗: {str(e)}")
            raise

    def drop_tables(self):
        try:
            Base.metadata.drop_all(self._engine)
            logger.info("數據表刪除成功")
        except Exception as e:
            logger.error(f"刪除數據表失敗: {str(e)}")
            raise

    def check_connection(self) -> bool:
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"檢查數據庫連接失敗: {str(e)}")
            return False

    def get_connection_info(self) -> dict:
        return {
            "sqlite_path": config.SQLITE_DB_PATH
        }

    def close(self):
        if self._engine:
            self._engine.dispose()
            logger.info("數據庫連接池已關閉")

db_manager = DatabaseManager()
get_session = db_manager.get_session
check_connection = db_manager.check_connection
create_tables = db_manager.create_tables
drop_tables = db_manager.drop_tables
