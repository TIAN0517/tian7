#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jy技術團隊 獨立USDT系統 v3.0 - 區塊鏈交易驗證服務
Author: TIAN0517
Version: 3.0.0
"""

import os
import json
import logging
from decimal import Decimal
from typing import Optional, Tuple, Dict, Any
from web3 import Web3
from eth_account import Account
from eth_typing import Address
from eth_utils import to_checksum_address
from tenacity import retry, stop_after_attempt, wait_exponential
from config.usdt_config import config
from database.db_manager import db_manager
from models.database_models import NetworkType, TransactionStatus

# 配置日誌
logger = logging.getLogger(__name__)

class BlockchainService:
    """區塊鏈交易驗證服務"""

    def __init__(self):
        """初始化區塊鏈服務"""
        # 初始化Web3連接
        self.trc20_w3 = Web3(Web3.HTTPProvider(config.TRC20_RPC_URL))
        self.erc20_w3 = Web3(Web3.HTTPProvider(config.ERC20_RPC_URL))
        self.bep20_w3 = Web3(Web3.HTTPProvider(config.BEP20_RPC_URL))
        
        # 加載合約ABI
        self.contract_abi = self._load_contract_abi()
        
        # 初始化合約實例
        self.trc20_contract = self.trc20_w3.eth.contract(
            address=to_checksum_address(config.TRC20_CONTRACT_ADDRESS),
            abi=self.contract_abi
        )
        self.erc20_contract = self.erc20_w3.eth.contract(
            address=to_checksum_address(config.ERC20_CONTRACT_ADDRESS),
            abi=self.contract_abi
        )
        self.bep20_contract = self.bep20_w3.eth.contract(
            address=to_checksum_address(config.BEP20_CONTRACT_ADDRESS),
            abi=self.contract_abi
        )

    def _load_contract_abi(self) -> Dict[str, Any]:
        """加載合約ABI"""
        try:
            with open(config.CONTRACT_ABI_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加載合約ABI失敗: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def verify_transaction(self, tx_hash: str, network: NetworkType) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """驗證交易"""
        try:
            if network == NetworkType.TRC20:
                return self._verify_trc20_transaction(tx_hash)
            elif network == NetworkType.ERC20:
                return self._verify_erc20_transaction(tx_hash)
            elif network == NetworkType.BEP20:
                return self._verify_bep20_transaction(tx_hash)
            else:
                return False, "不支持的網絡類型", None
        except Exception as e:
            logger.error(f"驗證交易失敗: {str(e)}")
            return False, f"驗證交易失敗: {str(e)}", None

    def _verify_trc20_transaction(self, tx_hash: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """驗證TRC20交易"""
        try:
            # 獲取交易收據
            tx_receipt = self.trc20_w3.eth.get_transaction_receipt(tx_hash)
            if not tx_receipt:
                return False, "交易不存在", None

            # 檢查交易狀態
            if tx_receipt['status'] != 1:
                return False, "交易失敗", None

            # 獲取交易詳情
            tx = self.trc20_w3.eth.get_transaction(tx_hash)
            
            # 解析交易輸入數據
            decoded_input = self.trc20_contract.decode_function_input(tx['input'])
            function_name = decoded_input[0].fn_name
            
            if function_name != 'transfer':
                return False, "無效的交易類型", None

            # 獲取接收地址和金額
            to_address = decoded_input[1]['_to']
            amount = Decimal(decoded_input[1]['_value']) / Decimal(10 ** 6)  # USDT有6位小數

            # 驗證接收地址
            if to_address.lower() != config.TRC20_RECEIVE_ADDRESS.lower():
                return False, "無效的接收地址", None

            # 驗證金額
            if amount < config.MIN_DEPOSIT_AMOUNT:
                return False, "金額過小", None
            if amount > config.MAX_DEPOSIT_AMOUNT:
                return False, "金額過大", None

            return True, "交易驗證成功", {
                "from_address": tx['from'],
                "to_address": to_address,
                "amount": amount,
                "block_number": tx_receipt['blockNumber'],
                "gas_used": tx_receipt['gasUsed']
            }

        except Exception as e:
            logger.error(f"驗證TRC20交易失敗: {str(e)}")
            return False, f"驗證TRC20交易失敗: {str(e)}", None

    def _verify_erc20_transaction(self, tx_hash: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """驗證ERC20交易"""
        try:
            # 獲取交易收據
            tx_receipt = self.erc20_w3.eth.get_transaction_receipt(tx_hash)
            if not tx_receipt:
                return False, "交易不存在", None

            # 檢查交易狀態
            if tx_receipt['status'] != 1:
                return False, "交易失敗", None

            # 獲取交易詳情
            tx = self.erc20_w3.eth.get_transaction(tx_hash)
            
            # 解析交易輸入數據
            decoded_input = self.erc20_contract.decode_function_input(tx['input'])
            function_name = decoded_input[0].fn_name
            
            if function_name != 'transfer':
                return False, "無效的交易類型", None

            # 獲取接收地址和金額
            to_address = decoded_input[1]['_to']
            amount = Decimal(decoded_input[1]['_value']) / Decimal(10 ** 6)  # USDT有6位小數

            # 驗證接收地址
            if to_address.lower() != config.ERC20_RECEIVE_ADDRESS.lower():
                return False, "無效的接收地址", None

            # 驗證金額
            if amount < config.MIN_DEPOSIT_AMOUNT:
                return False, "金額過小", None
            if amount > config.MAX_DEPOSIT_AMOUNT:
                return False, "金額過大", None

            return True, "交易驗證成功", {
                "from_address": tx['from'],
                "to_address": to_address,
                "amount": amount,
                "block_number": tx_receipt['blockNumber'],
                "gas_used": tx_receipt['gasUsed']
            }

        except Exception as e:
            logger.error(f"驗證ERC20交易失敗: {str(e)}")
            return False, f"驗證ERC20交易失敗: {str(e)}", None

    def _verify_bep20_transaction(self, tx_hash: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """驗證BEP20交易"""
        try:
            # 獲取交易收據
            tx_receipt = self.bep20_w3.eth.get_transaction_receipt(tx_hash)
            if not tx_receipt:
                return False, "交易不存在", None

            # 檢查交易狀態
            if tx_receipt['status'] != 1:
                return False, "交易失敗", None

            # 獲取交易詳情
            tx = self.bep20_w3.eth.get_transaction(tx_hash)
            
            # 解析交易輸入數據
            decoded_input = self.bep20_contract.decode_function_input(tx['input'])
            function_name = decoded_input[0].fn_name
            
            if function_name != 'transfer':
                return False, "無效的交易類型", None

            # 獲取接收地址和金額
            to_address = decoded_input[1]['_to']
            amount = Decimal(decoded_input[1]['_value']) / Decimal(10 ** 6)  # USDT有6位小數

            # 驗證接收地址
            if to_address.lower() != config.BEP20_RECEIVE_ADDRESS.lower():
                return False, "無效的接收地址", None

            # 驗證金額
            if amount < config.MIN_DEPOSIT_AMOUNT:
                return False, "金額過小", None
            if amount > config.MAX_DEPOSIT_AMOUNT:
                return False, "金額過大", None

            return True, "交易驗證成功", {
                "from_address": tx['from'],
                "to_address": to_address,
                "amount": amount,
                "block_number": tx_receipt['blockNumber'],
                "gas_used": tx_receipt['gasUsed']
            }

        except Exception as e:
            logger.error(f"驗證BEP20交易失敗: {str(e)}")
            return False, f"驗證BEP20交易失敗: {str(e)}", None

    def get_network_status(self) -> Dict[str, Dict[str, Any]]:
        """獲取網絡狀態"""
        try:
            status = {}
            
            # 檢查TRC20網絡
            trc20_status = {
                "is_active": self.trc20_w3.is_connected(),
                "error_count": 0,
                "last_error": None
            }
            if not trc20_status["is_active"]:
                trc20_status["error_count"] += 1
                trc20_status["last_error"] = "TRC20網絡連接失敗"
            status["TRC20"] = trc20_status

            # 檢查ERC20網絡
            erc20_status = {
                "is_active": self.erc20_w3.is_connected(),
                "error_count": 0,
                "last_error": None
            }
            if not erc20_status["is_active"]:
                erc20_status["error_count"] += 1
                erc20_status["last_error"] = "ERC20網絡連接失敗"
            status["ERC20"] = erc20_status

            # 檢查BEP20網絡
            bep20_status = {
                "is_active": self.bep20_w3.is_connected(),
                "error_count": 0,
                "last_error": None
            }
            if not bep20_status["is_active"]:
                bep20_status["error_count"] += 1
                bep20_status["last_error"] = "BEP20網絡連接失敗"
            status["BEP20"] = bep20_status

            return status

        except Exception as e:
            logger.error(f"獲取網絡狀態失敗: {str(e)}")
            return {
                "TRC20": {"is_active": False, "error_count": 1, "last_error": str(e)},
                "ERC20": {"is_active": False, "error_count": 1, "last_error": str(e)},
                "BEP20": {"is_active": False, "error_count": 1, "last_error": str(e)}
            }

# 創建服務實例
blockchain_service = BlockchainService() 