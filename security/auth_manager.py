import os
import jwt
import logging
import datetime
import hashlib
import secrets
from functools import wraps
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class UserSession:
    """用戶會話信息"""
    user_id: str
    role: str
    token: str
    created_at: datetime.datetime
    last_activity: datetime.datetime
    ip_address: str
    user_agent: str

class AuthManager:
    """認證和授權管理器"""
    
    def __init__(self, secret_key: Optional[str] = None):
        """初始化認證管理器"""
        self.secret_key = secret_key or os.getenv('JWT_SECRET_KEY', secrets.token_hex(32))
        self.token_expiry = datetime.timedelta(hours=1)
        self.refresh_token_expiry = datetime.timedelta(days=7)
        self.active_sessions: Dict[str, UserSession] = {}
        self.failed_attempts: Dict[str, List[datetime.datetime]] = {}
        self.max_failed_attempts = 5
        self.lockout_duration = datetime.timedelta(minutes=15)
        
    def generate_token(self, user_id: str, role: str = 'user', 
                      ip_address: str = None, user_agent: str = None) -> Tuple[str, str]:
        """生成訪問令牌和刷新令牌"""
        try:
            # 生成訪問令牌
            access_payload = {
                'user_id': user_id,
                'role': role,
                'type': 'access',
                'exp': datetime.datetime.utcnow() + self.token_expiry
            }
            access_token = jwt.encode(access_payload, self.secret_key, algorithm='HS256')
            
            # 生成刷新令牌
            refresh_payload = {
                'user_id': user_id,
                'type': 'refresh',
                'exp': datetime.datetime.utcnow() + self.refresh_token_expiry
            }
            refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm='HS256')
            
            # 創建會話
            session = UserSession(
                user_id=user_id,
                role=role,
                token=access_token,
                created_at=datetime.datetime.utcnow(),
                last_activity=datetime.datetime.utcnow(),
                ip_address=ip_address or '',
                user_agent=user_agent or ''
            )
            self.active_sessions[access_token] = session
            
            logger.info(f"為用戶 {user_id} 生成令牌")
            return access_token, refresh_token
            
        except Exception as e:
            logger.error(f"生成令牌失敗：{str(e)}")
            raise
            
    def verify_token(self, token: str) -> Dict[str, Any]:
        """驗證令牌"""
        try:
            # 檢查會話是否存在
            if token not in self.active_sessions:
                raise ValueError("無效的會話")
                
            session = self.active_sessions[token]
            
            # 更新最後活動時間
            session.last_activity = datetime.datetime.utcnow()
            
            # 驗證令牌
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # 檢查令牌類型
            if payload.get('type') != 'access':
                raise ValueError("無效的令牌類型")
                
            logger.info(f"驗證令牌成功：{payload['user_id']}")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("令牌已過期")
            raise
        except jwt.InvalidTokenError as e:
            logger.error(f"無效的令牌：{str(e)}")
            raise
            
    def refresh_access_token(self, refresh_token: str) -> str:
        """使用刷新令牌獲取新的訪問令牌"""
        try:
            # 驗證刷新令牌
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=['HS256'])
            
            if payload.get('type') != 'refresh':
                raise ValueError("無效的刷新令牌")
                
            # 生成新的訪問令牌
            user_id = payload['user_id']
            role = self.get_user_role(user_id)
            access_token, _ = self.generate_token(user_id, role)
            
            return access_token
            
        except Exception as e:
            logger.error(f"刷新令牌失敗：{str(e)}")
            raise
            
    def invalidate_token(self, token: str):
        """使令牌失效"""
        if token in self.active_sessions:
            del self.active_sessions[token]
            logger.info(f"令牌已失效")
            
    def get_user_role(self, user_id: str) -> str:
        """獲取用戶角色"""
        # 這裡應該從數據庫獲取用戶角色
        # 暫時返回默認角色
        return 'user'
        
    def record_failed_attempt(self, user_id: str):
        """記錄失敗的登錄嘗試"""
        if user_id not in self.failed_attempts:
            self.failed_attempts[user_id] = []
            
        self.failed_attempts[user_id].append(datetime.datetime.utcnow())
        
        # 清理舊的失敗記錄
        cutoff = datetime.datetime.utcnow() - self.lockout_duration
        self.failed_attempts[user_id] = [
            t for t in self.failed_attempts[user_id]
            if t > cutoff
        ]
        
    def is_account_locked(self, user_id: str) -> bool:
        """檢查賬戶是否被鎖定"""
        if user_id not in self.failed_attempts:
            return False
            
        recent_attempts = [
            t for t in self.failed_attempts[user_id]
            if t > datetime.datetime.utcnow() - self.lockout_duration
        ]
        
        return len(recent_attempts) >= self.max_failed_attempts
        
    def require_auth(self, f):
        """認證裝飾器"""
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            
            # 從請求頭獲取令牌
            if 'Authorization' in kwargs:
                auth_header = kwargs['Authorization']
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
                    
            if not token:
                logger.error("未提供認證令牌")
                raise ValueError("需要認證")
                
            try:
                # 驗證令牌
                payload = self.verify_token(token)
                # 將用戶信息添加到kwargs
                kwargs['user'] = payload
                return f(*args, **kwargs)
            except Exception as e:
                logger.error(f"認證失敗：{str(e)}")
                raise
                
        return decorated
        
    def require_role(self, roles):
        """角色授權裝飾器"""
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                if 'user' not in kwargs:
                    logger.error("未認證")
                    raise ValueError("需要認證")
                    
                user_role = kwargs['user']['role']
                if user_role not in roles:
                    logger.error(f"權限不足：需要 {roles}，實際 {user_role}")
                    raise ValueError("權限不足")
                    
                return f(*args, **kwargs)
            return decorated
        return decorator
        
    def require_permission(self, permission):
        """權限授權裝飾器"""
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                if 'user' not in kwargs:
                    logger.error("未認證")
                    raise ValueError("需要認證")
                    
                user_role = kwargs['user']['role']
                if not check_permission(permission, user_role):
                    logger.error(f"權限不足：需要 {permission}")
                    raise ValueError("權限不足")
                    
                return f(*args, **kwargs)
            return decorated
        return decorator

# 創建全局認證管理器實例
auth_manager = AuthManager()

# 預定義角色
ROLES = {
    'admin': '管理員',
    'user': '普通用戶',
    'vip': 'VIP用戶',
    'moderator': '版主'
}

# 角色權限映射
ROLE_PERMISSIONS = {
    'admin': [
        'read', 'write', 'delete', 
        'manage_users', 'manage_system',
        'manage_roles', 'manage_permissions',
        'view_logs', 'manage_backups'
    ],
    'moderator': [
        'read', 'write', 'delete',
        'manage_users', 'view_logs'
    ],
    'vip': [
        'read', 'write', 'delete',
        'view_statistics'
    ],
    'user': [
        'read', 'write'
    ]
}

def check_permission(permission: str, user_role: str) -> bool:
    """檢查用戶是否有指定權限"""
    if user_role not in ROLE_PERMISSIONS:
        return False
    return permission in ROLE_PERMISSIONS[user_role]

def get_user_permissions(user_role: str) -> list:
    """獲取用戶的所有權限"""
    return ROLE_PERMISSIONS.get(user_role, [])

def hash_password(password: str) -> str:
    """哈希密碼"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((password + salt).encode())
    return f"{salt}${hash_obj.hexdigest()}"

def verify_password(password: str, hashed: str) -> bool:
    """驗證密碼"""
    salt, stored_hash = hashed.split('$')
    hash_obj = hashlib.sha256((password + salt).encode())
    return hash_obj.hexdigest() == stored_hash 