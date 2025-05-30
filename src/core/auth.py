import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from .config import config
from .models import User, get_session
from .logger import get_logger
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash
from src.database.db_manager import db_manager

logger = get_logger(__name__)

class Auth:
    """認證管理類"""
    
    _current_user = None
    _session = None
    
    @classmethod
    def init_test_account(cls):
        """初始化測試帳號"""
        session = db_manager.get_session()
        try:
            # 檢查是否已存在測試帳號
            test_user = session.query(User).filter_by(username="test").first()
            if not test_user:
                # 創建測試帳號
                test_user = User(
                    username="test",
                    password_hash=generate_password_hash("test123"),
                    email="test@example.com",
                    credits=1000.0
                )
                session.add(test_user)
                session.commit()
                logger.info("測試帳號創建成功")
            return test_user
        except Exception as e:
            logger.error(f"創建測試帳號失敗: {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()
    
    @classmethod
    def login(cls, username: str, password: str) -> bool:
        """用戶登入"""
        try:
            session = db_manager.get_session()
            user = session.query(User).filter_by(username=username).first()
            
            if user and check_password_hash(user.password_hash, password):
                user.last_login = datetime.utcnow()
                session.commit()
                cls._current_user = user
                cls._session = session
                logger.info(f"用戶 {username} 登入成功")
                return True
            else:
                logger.warning(f"用戶 {username} 登入失敗")
                return False
        except Exception as e:
            logger.error(f"登入過程發生錯誤: {str(e)}")
            if session:
                session.rollback()
            return False
    
    @classmethod
    def logout(cls):
        """用戶登出"""
        cls._current_user = None
        if cls._session:
            cls._session.close()
            cls._session = None
        logger.info("用戶登出")
    
    @classmethod
    def get_current_user(cls) -> User:
        """獲取當前登入用戶"""
        return cls._current_user
    
    @classmethod
    def get_session(cls) -> Session:
        """獲取數據庫會話"""
        return cls._session or db_manager.get_session()
    
    @classmethod
    def is_authenticated(cls) -> bool:
        """檢查是否已登入"""
        return cls._current_user is not None
    
    @staticmethod
    def hash_password(password: str) -> str:
        """對密碼進行加密
        
        Args:
            password: 原始密碼
            
        Returns:
            str: 加密後的密碼哈希
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()
        
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """驗證密碼
        
        Args:
            password: 原始密碼
            password_hash: 密碼哈希
            
        Returns:
            bool: 密碼是否正確
        """
        return bcrypt.checkpw(password.encode(), password_hash.encode())
        
    @staticmethod
    def create_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
        """創建 JWT token
        
        Args:
            user_id: 用戶ID
            expires_delta: token 過期時間
            
        Returns:
            str: JWT token
        """
        if expires_delta is None:
            expires_delta = timedelta(seconds=config['JWT_EXPIRATION'])
            
        expire = datetime.utcnow() + expires_delta
        to_encode = {
            "sub": str(user_id),
            "exp": expire
        }
        
        return jwt.encode(
            to_encode,
            config['JWT_SECRET'],
            algorithm=config['JWT_ALGORITHM']
        )
        
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """驗證 JWT token
        
        Args:
            token: JWT token
            
        Returns:
            Optional[Dict[str, Any]]: token 中的數據，如果驗證失敗則返回 None
        """
        try:
            payload = jwt.decode(
                token,
                config['JWT_SECRET'],
                algorithms=[config['JWT_ALGORITHM']]
            )
            return payload
        except jwt.PyJWTError as e:
            logger.error(f"Token verification failed: {e}")
            return None
            
    @classmethod
    def authenticate_user(cls, username: str, password: str) -> Optional[User]:
        """驗證用戶
        
        Args:
            username: 用戶名
            password: 密碼
            
        Returns:
            Optional[User]: 用戶對象，如果驗證失敗則返回 None
        """
        session = get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            if not user:
                return None
                
            if not cls.verify_password(password, user.password_hash):
                return None
                
            # 更新最後登入時間
            user.last_login = datetime.utcnow()
            session.commit()
            
            return user
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return None
        finally:
            session.close()
            
    @classmethod
    def register_user(cls, username: str, password: str, email: str) -> Optional[User]:
        """註冊新用戶
        
        Args:
            username: 用戶名
            password: 密碼
            email: 電子郵件
            
        Returns:
            Optional[User]: 新創建的用戶對象，如果註冊失敗則返回 None
        """
        session = get_session()
        try:
            # 檢查用戶名是否已存在
            if session.query(User).filter(User.username == username).first():
                logger.warning(f"Username {username} already exists")
                return None
                
            # 檢查郵箱是否已存在
            if session.query(User).filter(User.email == email).first():
                logger.warning(f"Email {email} already exists")
                return None
                
            # 創建新用戶
            user = User(
                username=username,
                password_hash=cls.hash_password(password),
                email=email
            )
            
            session.add(user)
            session.commit()
            session.refresh(user)
            
            logger.info(f"New user registered: {username}")
            return user
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            session.rollback()
            return None
        finally:
            session.close()
            
    @classmethod
    def update_password(cls, user_id: int, old_password: str, new_password: str) -> bool:
        """更新用戶密碼
        
        Args:
            user_id: 用戶ID
            old_password: 舊密碼
            new_password: 新密碼
            
        Returns:
            bool: 是否更新成功
        """
        session = get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return False
                
            if not cls.verify_password(old_password, user.password_hash):
                return False
                
            user.password_hash = cls.hash_password(new_password)
            session.commit()
            
            logger.info(f"Password updated for user: {user.username}")
            return True
        except Exception as e:
            logger.error(f"Password update failed: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    @classmethod
    def check_username_exists(cls, username: str) -> bool:
        """檢查用戶名是否已存在"""
        session = None
        try:
            session = get_session()
            user = session.query(User).filter_by(username=username).first()
            return user is not None
        except Exception as e:
            logger.error(f"檢查用戶名失敗: {str(e)}")
            return False
        finally:
            if session:
                session.close()

    @classmethod
    def register(cls, username: str, password: str, email: str) -> bool:
        """用戶註冊"""
        session = None
        try:
            if cls.check_username_exists(username):
                logger.warning(f"用戶名 {username} 已存在")
                return False
                
            session = get_session()
            user = User(
                username=username,
                password_hash=generate_password_hash(password),
                email=email,
                credits=0.0
            )
            session.add(user)
            session.commit()
            logger.info(f"用戶 {username} 註冊成功")
            return True
        except Exception as e:
            logger.error(f"註冊失敗: {str(e)}")
            if session:
                session.rollback()
            return False
        finally:
            if session:
                session.close() 