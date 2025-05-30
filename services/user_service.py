#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jy技術團隊 獨立USDT系統 v3.0 - 用戶服務層
Author: TIAN0517
Version: 3.0.0
"""

import re
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from decimal import Decimal
import logging
from sqlalchemy.exc import IntegrityError

from config.usdt_config import config
from database.dao import user_dao, system_log_dao
from models.database_models import User

# 配置日誌
logger = logging.getLogger(__name__)

class UserService:
    """用戶服務類"""
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """驗證用戶名"""
        if not username:
            return False, "用戶名不能為空"
        if len(username) < 3 or len(username) > 20:
            return False, "用戶名長度必須在3-20個字符之間"
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "用戶名只能包含字母、數字和下劃線"
        return True, ""

    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """驗證密碼"""
        if not password:
            return False, "密碼不能為空"
        if len(password) < 6 or len(password) > 20:
            return False, "密碼長度必須在6-20個字符之間"
        if not re.match(r'^[a-zA-Z0-9_@#$%^&*]+$', password):
            return False, "密碼只能包含字母、數字和特殊字符(@#$%^&*)"
        return True, ""

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """驗證郵箱"""
        if not email:
            return False, "郵箱不能為空"
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return False, "郵箱格式不正確"
        return True, ""

    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """驗證手機號"""
        if not phone:
            return True, ""  # 手機號為可選
        if not re.match(r'^\+?[1-9]\d{1,14}$', phone):
            return False, "手機號格式不正確"
        return True, ""

    @staticmethod
    def hash_password(password: str) -> str:
        """加密密碼"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """驗證密碼"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    @staticmethod
    def generate_token(user_id: int) -> str:
        """生成JWT令牌"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        return jwt.encode(payload, config.JWT_SECRET_KEY, algorithm='HS256')

    @staticmethod
    def verify_token(token: str) -> Optional[int]:
        """驗證JWT令牌"""
        try:
            payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=['HS256'])
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @classmethod
    def register(cls, username: str, password: str, email: str, phone: Optional[str] = None) -> Tuple[bool, str, Optional[Dict]]:
        """註冊新用戶"""
        try:
            # 驗證輸入
            valid, msg = cls.validate_username(username)
            if not valid:
                return False, msg, None

            valid, msg = cls.validate_password(password)
            if not valid:
                return False, msg, None

            valid, msg = cls.validate_email(email)
            if not valid:
                return False, msg, None

            valid, msg = cls.validate_phone(phone) if phone else (True, "")
            if not valid:
                return False, msg, None

            # 檢查用戶名是否已存在
            if user_dao.get_user_by_username(username):
                return False, "用戶名已存在", None

            # 創建用戶
            password_hash = cls.hash_password(password)
            user = user_dao.create_user(
                username=username,
                password_hash=password_hash,
                email=email,
                phone=phone
            )

            # 生成令牌
            token = cls.generate_token(user.id)

            # 記錄日誌
            system_log_dao.add_log(
                level="INFO",
                module="UserService",
                message=f"新用戶註冊成功: {username}",
                metadata={"user_id": user.id}
            )

            return True, "註冊成功", {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "token": token
            }

        except IntegrityError:
            return False, "用戶名或郵箱已存在", None
        except Exception as e:
            logger.error(f"註冊失敗: {str(e)}")
            return False, "註冊失敗，請稍後重試", None

    @classmethod
    def login(cls, username: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """用戶登錄"""
        try:
            # 獲取用戶
            user = user_dao.get_user_by_username(username)
            if not user:
                return False, "用戶名或密碼錯誤", None

            # 驗證密碼
            if not cls.verify_password(password, user.password_hash):
                return False, "用戶名或密碼錯誤", None

            # 生成令牌
            token = cls.generate_token(user.id)

            # 更新最後登錄時間
            user_dao.update_user(user.id, last_login=datetime.utcnow())

            # 記錄日誌
            system_log_dao.add_log(
                level="INFO",
                module="UserService",
                message=f"用戶登錄成功: {username}",
                metadata={"user_id": user.id}
            )

            return True, "登錄成功", {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "token": token
            }

        except Exception as e:
            logger.error(f"登錄失敗: {str(e)}")
            return False, "登錄失敗，請稍後重試", None

    @classmethod
    def change_password(cls, user_id: int, old_password: str, new_password: str) -> Tuple[bool, str]:
        """修改密碼"""
        try:
            # 獲取用戶
            user = user_dao.get_user_by_id(user_id)
            if not user:
                return False, "用戶不存在"

            # 驗證舊密碼
            if not cls.verify_password(old_password, user.password_hash):
                return False, "舊密碼錯誤"

            # 驗證新密碼
            valid, msg = cls.validate_password(new_password)
            if not valid:
                return False, msg

            # 更新密碼
            new_password_hash = cls.hash_password(new_password)
            user_dao.update_user(user_id, password_hash=new_password_hash)

            # 記錄日誌
            system_log_dao.add_log(
                level="INFO",
                module="UserService",
                message=f"用戶修改密碼: {user.username}",
                metadata={"user_id": user_id}
            )

            return True, "密碼修改成功"

        except Exception as e:
            logger.error(f"修改密碼失敗: {str(e)}")
            return False, "修改密碼失敗，請稍後重試"

    @classmethod
    def reset_password(cls, email: str) -> Tuple[bool, str]:
        """重置密碼"""
        try:
            # 獲取用戶
            user = user_dao.get_user_by_email(email)
            if not user:
                return False, "郵箱不存在"

            # 生成臨時密碼
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            password_hash = cls.hash_password(temp_password)

            # 更新密碼
            user_dao.update_user(user.id, password_hash=password_hash)

            # TODO: 發送郵件通知用戶新密碼

            # 記錄日誌
            system_log_dao.add_log(
                level="INFO",
                module="UserService",
                message=f"用戶重置密碼: {user.username}",
                metadata={"user_id": user.id}
            )

            return True, "密碼重置成功，請查收郵件"

        except Exception as e:
            logger.error(f"重置密碼失敗: {str(e)}")
            return False, "重置密碼失敗，請稍後重試"

    @classmethod
    def get_user_info(cls, user_id: int) -> Tuple[bool, str, Optional[Dict]]:
        """獲取用戶信息"""
        try:
            user = user_dao.get_user_by_id(user_id)
            if not user:
                return False, "用戶不存在", None

            return True, "獲取成功", {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "total_points": user.total_points,
                "total_deposits": user.total_deposits,
                "vip_level": user.vip_level,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None
            }

        except Exception as e:
            logger.error(f"獲取用戶信息失敗: {str(e)}")
            return False, "獲取用戶信息失敗，請稍後重試", None

# 導出服務實例
user_service = UserService() 