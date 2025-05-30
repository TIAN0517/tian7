#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jy技術團隊 獨立USDT系統 v3.0 - 用戶服務單元測試
Author: TIAN0517
Version: 3.0.0
"""

import pytest
from datetime import datetime, timedelta
from services.user_service import user_service
from models.database_models import User

class TestUserService:
    """用戶服務測試類"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """測試前準備"""
        # 清理測試數據
        with user_service.db_manager.get_session() as session:
            session.query(User).delete()
            session.commit()

    def test_register_user(self):
        """測試用戶註冊"""
        # 測試正常註冊
        success, message, data = user_service.register(
            username="test_user",
            password="Test123456",
            email="test@example.com",
            phone="13800138000"
        )
        assert success is True
        assert "註冊成功" in message
        assert data["username"] == "test_user"

        # 測試重複用戶名
        success, message, data = user_service.register(
            username="test_user",
            password="Test123456",
            email="test2@example.com",
            phone="13800138001"
        )
        assert success is False
        assert "用戶名已存在" in message

        # 測試無效郵箱
        success, message, data = user_service.register(
            username="test_user2",
            password="Test123456",
            email="invalid_email",
            phone="13800138002"
        )
        assert success is False
        assert "無效的郵箱格式" in message

    def test_login_user(self):
        """測試用戶登錄"""
        # 先註冊用戶
        user_service.register(
            username="test_user",
            password="Test123456",
            email="test@example.com",
            phone="13800138000"
        )

        # 測試正確登錄
        success, message, data = user_service.login(
            username="test_user",
            password="Test123456"
        )
        assert success is True
        assert "登錄成功" in message
        assert "token" in data

        # 測試錯誤密碼
        success, message, data = user_service.login(
            username="test_user",
            password="WrongPassword"
        )
        assert success is False
        assert "密碼錯誤" in message

        # 測試不存在的用戶
        success, message, data = user_service.login(
            username="non_exist_user",
            password="Test123456"
        )
        assert success is False
        assert "用戶不存在" in message

    def test_change_password(self):
        """測試修改密碼"""
        # 先註冊用戶
        user_service.register(
            username="test_user",
            password="Test123456",
            email="test@example.com",
            phone="13800138000"
        )

        # 測試正確修改密碼
        success, message = user_service.change_password(
            user_id=1,
            old_password="Test123456",
            new_password="NewTest123456"
        )
        assert success is True
        assert "密碼修改成功" in message

        # 測試錯誤的舊密碼
        success, message = user_service.change_password(
            user_id=1,
            old_password="WrongOldPassword",
            new_password="NewTest123456"
        )
        assert success is False
        assert "舊密碼錯誤" in message

    def test_reset_password(self):
        """測試重置密碼"""
        # 先註冊用戶
        user_service.register(
            username="test_user",
            password="Test123456",
            email="test@example.com",
            phone="13800138000"
        )

        # 測試重置密碼
        success, message = user_service.reset_password(
            email="test@example.com"
        )
        assert success is True
        assert "密碼重置成功" in message

        # 測試不存在的郵箱
        success, message = user_service.reset_password(
            email="non_exist@example.com"
        )
        assert success is False
        assert "郵箱不存在" in message

    def test_get_user_info(self):
        """測試獲取用戶信息"""
        # 先註冊用戶
        user_service.register(
            username="test_user",
            password="Test123456",
            email="test@example.com",
            phone="13800138000"
        )

        # 測試獲取用戶信息
        success, message, data = user_service.get_user_info(user_id=1)
        assert success is True
        assert data["username"] == "test_user"
        assert data["email"] == "test@example.com"
        assert data["phone"] == "13800138000"

        # 測試不存在的用戶
        success, message, data = user_service.get_user_info(user_id=999)
        assert success is False
        assert "用戶不存在" in message

    def test_token_verification(self):
        """測試令牌驗證"""
        # 先註冊用戶
        user_service.register(
            username="test_user",
            password="Test123456",
            email="test@example.com",
            phone="13800138000"
        )

        # 生成令牌
        token = user_service.generate_token(user_id=1)
        assert token is not None

        # 驗證有效令牌
        user_id = user_service.verify_token(token)
        assert user_id == 1

        # 驗證無效令牌
        user_id = user_service.verify_token("invalid_token")
        assert user_id is None

        # 驗證過期令牌
        expired_token = user_service.generate_token(
            user_id=1,
            expires_delta=timedelta(seconds=1)
        )
        import time
        time.sleep(2)
        user_id = user_service.verify_token(expired_token)
        assert user_id is None 