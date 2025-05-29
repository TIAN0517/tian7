import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from .config import config
from .models import User, get_session
from .logger import get_logger

logger = get_logger(__name__)

class Auth:
    """認證管理類"""
    
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
    def get_current_user(cls, token: str) -> Optional[User]:
        """獲取當前用戶
        
        Args:
            token: JWT token
            
        Returns:
            Optional[User]: 用戶對象，如果驗證失敗則返回 None
        """
        payload = cls.verify_token(token)
        if not payload:
            return None
            
        session = get_session()
        try:
            user = session.query(User).filter(User.id == int(payload['sub'])).first()
            return user
        except Exception as e:
            logger.error(f"Failed to get current user: {e}")
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