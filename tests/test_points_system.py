import sys
import os
import pytest
from datetime import datetime
from pathlib import Path

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from models.user import UserManager
from models.points import PointsManager
from models.transaction import TransactionManager

class TestPointsSystem:
    """積分系統測試類"""
    
    @pytest.fixture
    def user_manager(self):
        """創建用戶管理器實例"""
        return UserManager()
        
    @pytest.fixture
    def points_manager(self):
        """創建積分管理器實例"""
        return PointsManager()
        
    @pytest.fixture
    def transaction_manager(self):
        """創建交易管理器實例"""
        return TransactionManager()
        
    def test_points_deposit(self, user_manager, points_manager, transaction_manager):
        """測試積分充值"""
        # 創建測試用戶
        user_id = user_manager.create_user("test_user", 0)
        initial_points = user_manager.get_user_points(user_id)
        
        # 測試充值
        deposit_amount = 1000
        transaction_id = points_manager.deposit_points(user_id, deposit_amount)
        
        # 驗證積分變動
        final_points = user_manager.get_user_points(user_id)
        assert final_points == initial_points + deposit_amount
        
        # 驗證交易記錄
        transaction = transaction_manager.get_transaction(transaction_id)
        assert transaction is not None
        assert transaction.amount == deposit_amount
        assert transaction.type == "deposit"
        
    def test_points_withdraw(self, user_manager, points_manager, transaction_manager):
        """測試積分提現"""
        # 創建測試用戶並充值
        user_id = user_manager.create_user("test_user", 1000)
        initial_points = user_manager.get_user_points(user_id)
        
        # 測試提現
        withdraw_amount = 500
        transaction_id = points_manager.withdraw_points(user_id, withdraw_amount)
        
        # 驗證積分變動
        final_points = user_manager.get_user_points(user_id)
        assert final_points == initial_points - withdraw_amount
        
        # 驗證交易記錄
        transaction = transaction_manager.get_transaction(transaction_id)
        assert transaction is not None
        assert transaction.amount == withdraw_amount
        assert transaction.type == "withdraw"
        
    def test_points_transfer(self, user_manager, points_manager, transaction_manager):
        """測試積分轉賬"""
        # 創建兩個測試用戶
        user1_id = user_manager.create_user("user1", 1000)
        user2_id = user_manager.create_user("user2", 0)
        
        # 記錄初始積分
        user1_initial = user_manager.get_user_points(user1_id)
        user2_initial = user_manager.get_user_points(user2_id)
        
        # 測試轉賬
        transfer_amount = 500
        transaction_id = points_manager.transfer_points(user1_id, user2_id, transfer_amount)
        
        # 驗證積分變動
        user1_final = user_manager.get_user_points(user1_id)
        user2_final = user_manager.get_user_points(user2_id)
        
        assert user1_final == user1_initial - transfer_amount
        assert user2_final == user2_initial + transfer_amount
        
        # 驗證交易記錄
        transaction = transaction_manager.get_transaction(transaction_id)
        assert transaction is not None
        assert transaction.amount == transfer_amount
        assert transaction.type == "transfer"
        
    def test_points_history(self, user_manager, points_manager):
        """測試積分歷史記錄"""
        # 創建測試用戶
        user_id = user_manager.create_user("test_user", 1000)
        
        # 執行多個積分操作
        operations = [
            ("deposit", 500),
            ("withdraw", 200),
            ("deposit", 300),
            ("withdraw", 100)
        ]
        
        for op_type, amount in operations:
            if op_type == "deposit":
                points_manager.deposit_points(user_id, amount)
            else:
                points_manager.withdraw_points(user_id, amount)
                
        # 驗證歷史記錄
        history = points_manager.get_points_history(user_id)
        assert len(history) == len(operations)
        
        # 驗證每條記錄
        for i, (op_type, amount) in enumerate(operations):
            assert history[i].type == op_type
            assert history[i].amount == amount
            
    def test_points_limits(self, user_manager, points_manager):
        """測試積分限制"""
        # 創建測試用戶
        user_id = user_manager.create_user("test_user", 1000)
        
        # 測試最小提現金額
        with pytest.raises(ValueError):
            points_manager.withdraw_points(user_id, 0)
            
        # 測試最大提現金額
        with pytest.raises(ValueError):
            points_manager.withdraw_points(user_id, 2000)  # 超過餘額
            
        # 測試最小充值金額
        with pytest.raises(ValueError):
            points_manager.deposit_points(user_id, 0)
            
        # 測試最大充值金額
        with pytest.raises(ValueError):
            points_manager.deposit_points(user_id, 1000000)  # 超過最大限制
            
    def test_points_freeze(self, user_manager, points_manager):
        """測試積分凍結"""
        # 創建測試用戶
        user_id = user_manager.create_user("test_user", 1000)
        
        # 凍結積分
        freeze_amount = 500
        points_manager.freeze_points(user_id, freeze_amount)
        
        # 驗證可用積分
        available_points = points_manager.get_available_points(user_id)
        assert available_points == 500  # 1000 - 500
        
        # 嘗試提現超過可用積分
        with pytest.raises(ValueError):
            points_manager.withdraw_points(user_id, 600)
            
        # 解凍積分
        points_manager.unfreeze_points(user_id, freeze_amount)
        
        # 驗證可用積分
        available_points = points_manager.get_available_points(user_id)
        assert available_points == 1000
        
    def test_points_bonus(self, user_manager, points_manager):
        """測試積分獎勵"""
        # 創建測試用戶
        user_id = user_manager.create_user("test_user", 1000)
        initial_points = user_manager.get_user_points(user_id)
        
        # 添加獎勵積分
        bonus_amount = 100
        points_manager.add_bonus_points(user_id, bonus_amount, "首充獎勵")
        
        # 驗證積分變動
        final_points = user_manager.get_user_points(user_id)
        assert final_points == initial_points + bonus_amount
        
        # 驗證獎勵記錄
        bonus_history = points_manager.get_bonus_history(user_id)
        assert len(bonus_history) > 0
        assert bonus_history[0].amount == bonus_amount
        assert bonus_history[0].description == "首充獎勵"
        
    def test_points_deduction(self, user_manager, points_manager):
        """測試積分扣除"""
        # 創建測試用戶
        user_id = user_manager.create_user("test_user", 1000)
        initial_points = user_manager.get_user_points(user_id)
        
        # 扣除積分
        deduction_amount = 100
        points_manager.deduct_points(user_id, deduction_amount, "違規扣除")
        
        # 驗證積分變動
        final_points = user_manager.get_user_points(user_id)
        assert final_points == initial_points - deduction_amount
        
        # 驗證扣除記錄
        deduction_history = points_manager.get_deduction_history(user_id)
        assert len(deduction_history) > 0
        assert deduction_history[0].amount == deduction_amount
        assert deduction_history[0].description == "違規扣除" 