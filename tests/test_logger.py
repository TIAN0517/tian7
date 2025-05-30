#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jy技術團隊 獨立USDT系統 v3.0 - 日誌系統單元測試
Author: TIAN0517
Version: 3.0.0
"""

import os
import pytest
import logging
from pathlib import Path
from utils.logger import (
    setup_logger,
    log_error,
    log_warning,
    log_info,
    log_debug,
    api_logger,
    db_logger,
    blockchain_logger,
    user_logger,
    transaction_logger,
    system_logger
)

class TestLogger:
    """日誌系統測試類"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """測試前準備"""
        # 創建測試日誌目錄
        self.test_log_dir = Path(__file__).parent.parent / "logs" / "test"
        self.test_log_dir.mkdir(parents=True, exist_ok=True)
        
        # 測試日誌文件
        self.test_log_file = self.test_log_dir / "test.log"
        
        # 清理測試日誌文件
        if self.test_log_file.exists():
            self.test_log_file.unlink()

    def test_setup_logger(self):
        """測試設置日誌記錄器"""
        # 創建測試日誌記錄器
        test_logger = setup_logger(
            name="test_logger",
            log_file=str(self.test_log_file),
            level=logging.DEBUG
        )
        
        # 驗證日誌記錄器
        assert test_logger.name == "test_logger"
        assert test_logger.level == logging.DEBUG
        assert len(test_logger.handlers) == 3  # 控制台、文件、時間輪轉

    def test_log_levels(self):
        """測試不同級別的日誌記錄"""
        # 創建測試日誌記錄器
        test_logger = setup_logger(
            name="test_logger",
            log_file=str(self.test_log_file),
            level=logging.DEBUG
        )
        
        # 記錄不同級別的日誌
        log_debug(test_logger, "調試信息", {"key": "value"})
        log_info(test_logger, "一般信息", {"key": "value"})
        log_warning(test_logger, "警告信息", {"key": "value"})
        log_error(test_logger, Exception("測試錯誤"), {"key": "value"})
        
        # 驗證日誌文件
        assert self.test_log_file.exists()
        log_content = self.test_log_file.read_text()
        assert "調試" in log_content
        assert "信息" in log_content
        assert "警告" in log_content
        assert "錯誤" in log_content
        assert "key" in log_content
        assert "value" in log_content

    def test_log_rotation(self):
        """測試日誌輪轉"""
        # 創建測試日誌記錄器
        test_logger = setup_logger(
            name="test_logger",
            log_file=str(self.test_log_file),
            level=logging.INFO
        )
        
        # 寫入大量日誌以觸發輪轉
        for i in range(1000):
            log_info(test_logger, f"測試日誌 {i}")
        
        # 驗證日誌文件
        assert self.test_log_file.exists()
        assert self.test_log_file.stat().st_size > 0

    def test_module_loggers(self):
        """測試模組日誌記錄器"""
        # 驗證所有模組日誌記錄器
        assert api_logger.name == "api"
        assert db_logger.name == "database"
        assert blockchain_logger.name == "blockchain"
        assert user_logger.name == "user"
        assert transaction_logger.name == "transaction"
        assert system_logger.name == "system"
        
        # 驗證日誌級別
        assert api_logger.level == logging.INFO
        assert db_logger.level == logging.INFO
        assert blockchain_logger.level == logging.INFO
        assert user_logger.level == logging.INFO
        assert transaction_logger.level == logging.INFO
        assert system_logger.level == logging.INFO

    def test_log_context(self):
        """測試日誌上下文"""
        # 創建測試日誌記錄器
        test_logger = setup_logger(
            name="test_logger",
            log_file=str(self.test_log_file),
            level=logging.INFO
        )
        
        # 記錄帶上下文的日誌
        context = {
            "user_id": 123,
            "action": "login",
            "ip": "127.0.0.1"
        }
        log_info(test_logger, "用戶登錄", context)
        
        # 驗證日誌文件
        log_content = self.test_log_file.read_text()
        assert "用戶登錄" in log_content
        assert "user_id" in log_content
        assert "123" in log_content
        assert "action" in log_content
        assert "login" in log_content
        assert "ip" in log_content
        assert "127.0.0.1" in log_content

    def test_error_logging(self):
        """測試錯誤日誌記錄"""
        # 創建測試日誌記錄器
        test_logger = setup_logger(
            name="test_logger",
            log_file=str(self.test_log_file),
            level=logging.ERROR
        )
        
        # 記錄錯誤日誌
        try:
            raise ValueError("測試錯誤")
        except Exception as e:
            log_error(test_logger, e, {"error_type": "ValueError"})
        
        # 驗證日誌文件
        log_content = self.test_log_file.read_text()
        assert "測試錯誤" in log_content
        assert "ValueError" in log_content
        assert "error_type" in log_content
        assert "Traceback" in log_content  # 驗證堆棧跟踪 