#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jy技術團隊 獨立USDT系統 v3.0 - 測試運行腳本
Author: TIAN0517
Version: 3.0.0
"""

import os
import sys
import pytest
from pathlib import Path

# 添加項目根目錄到Python路徑
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

def run_tests():
    """運行所有測試"""
    # 設置測試環境變量
    os.environ["ENV"] = "test"
    os.environ["DB_NAME"] = "RanUser_Test"
    
    # 運行測試
    pytest.main([
        "tests",
        "-v",  # 詳細輸出
        "--cov=.",  # 代碼覆蓋率
        "--cov-report=term-missing",  # 顯示未覆蓋的代碼行
        "--cov-report=html",  # 生成HTML覆蓋率報告
        "--html=reports/test_report.html",  # 生成HTML測試報告
        "--self-contained-html",  # 生成獨立的HTML報告
        "--junitxml=reports/junit.xml",  # 生成JUnit XML報告
        "--maxfail=5",  # 最多允許5個測試失敗
        "--tb=short",  # 簡短的錯誤回溯
        "--durations=10",  # 顯示最慢的10個測試
        "--randomly-seed=42",  # 固定隨機種子
        "--randomly-dont-reset-seed",  # 不重置隨機種子
        "--randomly-dont-shuffle",  # 不隨機打亂測試順序
    ])

if __name__ == "__main__":
    # 創建報告目錄
    os.makedirs("reports", exist_ok=True)
    
    # 運行測試
    run_tests() 