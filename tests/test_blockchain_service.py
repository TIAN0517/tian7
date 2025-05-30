#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jy技術團隊 獨立USDT系統 v3.0 - 區塊鏈服務單元測試
Author: TIAN0517
Version: 3.0.0
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, patch
from services.blockchain_service import blockchain_service
from models.database_models import NetworkType

class TestBlockchainService:
    """區塊鏈服務測試類"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """測試前準備"""
        # 模擬Web3連接
        self.mock_trc20_w3 = Mock()
        self.mock_erc20_w3 = Mock()
        self.mock_bep20_w3 = Mock()
        
        blockchain_service.trc20_w3 = self.mock_trc20_w3
        blockchain_service.erc20_w3 = self.mock_erc20_w3
        blockchain_service.bep20_w3 = self.mock_bep20_w3

    def test_verify_trc20_transaction_success(self):
        """測試TRC20交易驗證成功"""
        # 模擬交易收據
        mock_receipt = {
            'status': 1,
            'blockNumber': 12345678,
            'gasUsed': 21000
        }
        self.mock_trc20_w3.eth.get_transaction_receipt.return_value = mock_receipt

        # 模擬交易詳情
        mock_tx = {
            'from': '0x1234567890abcdef1234567890abcdef12345678',
            'input': '0xa9059cbb0000000000000000000000001234567890abcdef1234567890abcdef12345678000000000000000000000000000000000000000000000000000000000000000064'
        }
        self.mock_trc20_w3.eth.get_transaction.return_value = mock_tx

        # 模擬合約解碼
        mock_decoded = (
            Mock(fn_name='transfer'),
            {'_to': '0x1234567890abcdef1234567890abcdef12345678', '_value': 1000000}
        )
        blockchain_service.trc20_contract.decode_function_input.return_value = mock_decoded

        # 執行測試
        success, message, data = blockchain_service.verify_transaction(
            tx_hash='0x1234567890abcdef',
            network=NetworkType.TRC20
        )

        # 驗證結果
        assert success is True
        assert message == "交易驗證成功"
        assert data['amount'] == Decimal('1.0')
        assert data['from_address'] == '0x1234567890abcdef1234567890abcdef12345678'
        assert data['block_number'] == 12345678

    def test_verify_trc20_transaction_failed(self):
        """測試TRC20交易驗證失敗"""
        # 模擬交易收據
        mock_receipt = {
            'status': 0,
            'blockNumber': 12345678,
            'gasUsed': 21000
        }
        self.mock_trc20_w3.eth.get_transaction_receipt.return_value = mock_receipt

        # 執行測試
        success, message, data = blockchain_service.verify_transaction(
            tx_hash='0x1234567890abcdef',
            network=NetworkType.TRC20
        )

        # 驗證結果
        assert success is False
        assert message == "交易失敗"
        assert data is None

    def test_verify_erc20_transaction_success(self):
        """測試ERC20交易驗證成功"""
        # 模擬交易收據
        mock_receipt = {
            'status': 1,
            'blockNumber': 12345678,
            'gasUsed': 21000
        }
        self.mock_erc20_w3.eth.get_transaction_receipt.return_value = mock_receipt

        # 模擬交易詳情
        mock_tx = {
            'from': '0x1234567890abcdef1234567890abcdef12345678',
            'input': '0xa9059cbb0000000000000000000000001234567890abcdef1234567890abcdef12345678000000000000000000000000000000000000000000000000000000000000000064'
        }
        self.mock_erc20_w3.eth.get_transaction.return_value = mock_tx

        # 模擬合約解碼
        mock_decoded = (
            Mock(fn_name='transfer'),
            {'_to': '0x1234567890abcdef1234567890abcdef12345678', '_value': 1000000}
        )
        blockchain_service.erc20_contract.decode_function_input.return_value = mock_decoded

        # 執行測試
        success, message, data = blockchain_service.verify_transaction(
            tx_hash='0x1234567890abcdef',
            network=NetworkType.ERC20
        )

        # 驗證結果
        assert success is True
        assert message == "交易驗證成功"
        assert data['amount'] == Decimal('1.0')
        assert data['from_address'] == '0x1234567890abcdef1234567890abcdef12345678'
        assert data['block_number'] == 12345678

    def test_verify_bep20_transaction_success(self):
        """測試BEP20交易驗證成功"""
        # 模擬交易收據
        mock_receipt = {
            'status': 1,
            'blockNumber': 12345678,
            'gasUsed': 21000
        }
        self.mock_bep20_w3.eth.get_transaction_receipt.return_value = mock_receipt

        # 模擬交易詳情
        mock_tx = {
            'from': '0x1234567890abcdef1234567890abcdef12345678',
            'input': '0xa9059cbb0000000000000000000000001234567890abcdef1234567890abcdef12345678000000000000000000000000000000000000000000000000000000000000000064'
        }
        self.mock_bep20_w3.eth.get_transaction.return_value = mock_tx

        # 模擬合約解碼
        mock_decoded = (
            Mock(fn_name='transfer'),
            {'_to': '0x1234567890abcdef1234567890abcdef12345678', '_value': 1000000}
        )
        blockchain_service.bep20_contract.decode_function_input.return_value = mock_decoded

        # 執行測試
        success, message, data = blockchain_service.verify_transaction(
            tx_hash='0x1234567890abcdef',
            network=NetworkType.BEP20
        )

        # 驗證結果
        assert success is True
        assert message == "交易驗證成功"
        assert data['amount'] == Decimal('1.0')
        assert data['from_address'] == '0x1234567890abcdef1234567890abcdef12345678'
        assert data['block_number'] == 12345678

    def test_verify_invalid_network(self):
        """測試無效的網絡類型"""
        success, message, data = blockchain_service.verify_transaction(
            tx_hash='0x1234567890abcdef',
            network='INVALID'
        )

        assert success is False
        assert message == "不支持的網絡類型"
        assert data is None

    def test_get_network_status(self):
        """測試獲取網絡狀態"""
        # 模擬網絡連接狀態
        self.mock_trc20_w3.is_connected.return_value = True
        self.mock_erc20_w3.is_connected.return_value = True
        self.mock_bep20_w3.is_connected.return_value = True

        # 執行測試
        status = blockchain_service.get_network_status()

        # 驗證結果
        assert status['TRC20']['is_active'] is True
        assert status['ERC20']['is_active'] is True
        assert status['BEP20']['is_active'] is True
        assert status['TRC20']['error_count'] == 0
        assert status['ERC20']['error_count'] == 0
        assert status['BEP20']['error_count'] == 0

    def test_get_network_status_with_errors(self):
        """測試獲取網絡狀態（有錯誤）"""
        # 模擬網絡連接狀態
        self.mock_trc20_w3.is_connected.return_value = False
        self.mock_erc20_w3.is_connected.return_value = True
        self.mock_bep20_w3.is_connected.return_value = False

        # 執行測試
        status = blockchain_service.get_network_status()

        # 驗證結果
        assert status['TRC20']['is_active'] is False
        assert status['ERC20']['is_active'] is True
        assert status['BEP20']['is_active'] is False
        assert status['TRC20']['error_count'] == 1
        assert status['ERC20']['error_count'] == 0
        assert status['BEP20']['error_count'] == 1
        assert status['TRC20']['last_error'] == "TRC20網絡連接失敗"
        assert status['BEP20']['last_error'] == "BEP20網絡連接失敗" 