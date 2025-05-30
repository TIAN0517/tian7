#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jy技術團隊 獨立USDT系統 v3.0 - 交易服務單元測試
Author: TIAN0517
Version: 3.0.0
"""

import pytest
from decimal import Decimal
from datetime import datetime
from services.transaction_service import transaction_service
from services.user_service import user_service
from models.database_models import User, Transaction, NetworkType, TransactionStatus

class TestTransactionService:
    """交易服務測試類"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """測試前準備"""
        # 清理測試數據
        with transaction_service.db_manager.get_session() as session:
            session.query(Transaction).delete()
            session.query(User).delete()
            session.commit()

        # 創建測試用戶
        user_service.register(
            username="test_user",
            password="Test123456",
            email="test@example.com",
            phone="13800138000"
        )

    def test_create_deposit(self):
        """測試創建充值交易"""
        # 測試正常充值
        success, message, data = transaction_service.create_deposit(
            user_id=1,
            network=NetworkType.TRC20,
            amount=Decimal("100.00")
        )
        assert success is True
        assert "充值交易創建成功" in message
        assert data["amount"] == Decimal("100.00")
        assert data["network"] == NetworkType.TRC20

        # 測試金額過小
        success, message, data = transaction_service.create_deposit(
            user_id=1,
            network=NetworkType.TRC20,
            amount=Decimal("0.01")
        )
        assert success is False
        assert "充值金額過小" in message

        # 測試金額過大
        success, message, data = transaction_service.create_deposit(
            user_id=1,
            network=NetworkType.TRC20,
            amount=Decimal("1000000.00")
        )
        assert success is False
        assert "充值金額過大" in message

        # 測試不存在的用戶
        success, message, data = transaction_service.create_deposit(
            user_id=999,
            network=NetworkType.TRC20,
            amount=Decimal("100.00")
        )
        assert success is False
        assert "用戶不存在" in message

    def test_verify_transaction(self):
        """測試驗證交易"""
        # 創建測試交易
        transaction_service.create_deposit(
            user_id=1,
            network=NetworkType.TRC20,
            amount=Decimal("100.00")
        )

        # 測試驗證成功
        success, message, data = transaction_service.verify_transaction(
            tx_hash="0x1234567890abcdef",
            network=NetworkType.TRC20
        )
        assert success is True
        assert "交易驗證成功" in message
        assert data["status"] == TransactionStatus.COMPLETED

        # 測試重複驗證
        success, message, data = transaction_service.verify_transaction(
            tx_hash="0x1234567890abcdef",
            network=NetworkType.TRC20
        )
        assert success is False
        assert "交易已驗證" in message

        # 測試無效交易哈希
        success, message, data = transaction_service.verify_transaction(
            tx_hash="invalid_hash",
            network=NetworkType.TRC20
        )
        assert success is False
        assert "無效的交易哈希" in message

    def test_get_transaction_history(self):
        """測試獲取交易歷史"""
        # 創建多筆測試交易
        for i in range(5):
            transaction_service.create_deposit(
                user_id=1,
                network=NetworkType.TRC20,
                amount=Decimal("100.00")
            )

        # 測試獲取所有交易
        success, message, data = transaction_service.get_transaction_history(
            user_id=1,
            page=1,
            page_size=10
        )
        assert success is True
        assert len(data["transactions"]) == 5
        assert data["total"] == 5

        # 測試分頁
        success, message, data = transaction_service.get_transaction_history(
            user_id=1,
            page=1,
            page_size=2
        )
        assert success is True
        assert len(data["transactions"]) == 2
        assert data["total"] == 5

        # 測試按狀態過濾
        success, message, data = transaction_service.get_transaction_history(
            user_id=1,
            page=1,
            page_size=10,
            status=TransactionStatus.PENDING
        )
        assert success is True
        assert len(data["transactions"]) == 5
        assert all(t["status"] == TransactionStatus.PENDING for t in data["transactions"])

    def test_get_network_status(self):
        """測試獲取網絡狀態"""
        # 測試獲取所有網絡狀態
        success, message, data = transaction_service.get_network_status()
        assert success is True
        assert "TRC20" in data
        assert "ERC20" in data
        assert "BEP20" in data

        # 驗證每個網絡的狀態格式
        for network in ["TRC20", "ERC20", "BEP20"]:
            assert "is_active" in data[network]
            assert "error_count" in data[network]
            assert "last_error" in data[network]

    def test_calculate_points(self):
        """測試計算積分"""
        # 測試TRC20小額充值
        points = transaction_service._calculate_points(
            amount=Decimal("100.00"),
            network=NetworkType.TRC20
        )
        assert points == 100

        # 測試TRC20中額充值
        points = transaction_service._calculate_points(
            amount=Decimal("1000.00"),
            network=NetworkType.TRC20
        )
        assert points == 1100

        # 測試TRC20大額充值
        points = transaction_service._calculate_points(
            amount=Decimal("10000.00"),
            network=NetworkType.TRC20
        )
        assert points == 12000

        # 測試ERC20充值
        points = transaction_service._calculate_points(
            amount=Decimal("100.00"),
            network=NetworkType.ERC20
        )
        assert points == 120

        # 測試BEP20充值
        points = transaction_service._calculate_points(
            amount=Decimal("100.00"),
            network=NetworkType.BEP20
        )
        assert points == 110

    def test_calculate_bonus(self):
        """測試計算獎勵"""
        # 測試普通會員
        bonus = transaction_service._calculate_bonus(
            points=1000,
            vip_level=1
        )
        assert bonus == 0

        # 測試白銀會員
        bonus = transaction_service._calculate_bonus(
            points=1000,
            vip_level=2
        )
        assert bonus == 100

        # 測試黃金會員
        bonus = transaction_service._calculate_bonus(
            points=1000,
            vip_level=3
        )
        assert bonus == 200

        # 測試鉑金會員
        bonus = transaction_service._calculate_bonus(
            points=1000,
            vip_level=4
        )
        assert bonus == 300

        # 測試鑽石會員
        bonus = transaction_service._calculate_bonus(
            points=1000,
            vip_level=5
        )
        assert bonus == 500 