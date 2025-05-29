import pytest
from datetime import datetime
from database.bingo_models import User, GameHistory, Transaction

class TestUser:
    """用戶模型測試"""
    
    def test_init(self):
        """測試初始化"""
        user = User(user_id="test_user", points=1000.0)
        
        assert user.user_id == "test_user"
        assert user.points == 1000.0
        assert user.created_at is not None
        assert user.updated_at is not None
        
    def test_update_points(self):
        """測試更新積分"""
        user = User(user_id="test_user", points=1000.0)
        old_updated_at = user.updated_at
        
        # 更新積分
        user.update_points(2000.0)
        
        assert user.points == 2000.0
        assert user.updated_at > old_updated_at
        
    def test_to_dict(self):
        """測試轉換為字典"""
        user = User(user_id="test_user", points=1000.0)
        user_dict = user.to_dict()
        
        assert user_dict["user_id"] == "test_user"
        assert user_dict["points"] == 1000.0
        assert "created_at" in user_dict
        assert "updated_at" in user_dict
        
class TestGameHistory:
    """遊戲歷史模型測試"""
    
    def test_init(self):
        """測試初始化"""
        history = GameHistory(
            user_id="test_user",
            bet_amount=100.0,
            card_count=2,
            drawn_balls=[1, 2, 3],
            winning_patterns=["single_line"],
            payout=200.0,
            duration=60
        )
        
        assert history.user_id == "test_user"
        assert history.bet_amount == 100.0
        assert history.card_count == 2
        assert history.drawn_balls == [1, 2, 3]
        assert history.winning_patterns == ["single_line"]
        assert history.payout == 200.0
        assert history.duration == 60
        assert history.created_at is not None
        
    def test_to_dict(self):
        """測試轉換為字典"""
        history = GameHistory(
            user_id="test_user",
            bet_amount=100.0,
            card_count=2,
            drawn_balls=[1, 2, 3],
            winning_patterns=["single_line"],
            payout=200.0,
            duration=60
        )
        history_dict = history.to_dict()
        
        assert history_dict["user_id"] == "test_user"
        assert history_dict["bet_amount"] == 100.0
        assert history_dict["card_count"] == 2
        assert history_dict["drawn_balls"] == [1, 2, 3]
        assert history_dict["winning_patterns"] == ["single_line"]
        assert history_dict["payout"] == 200.0
        assert history_dict["duration"] == 60
        assert "created_at" in history_dict
        
class TestTransaction:
    """交易模型測試"""
    
    def test_init(self):
        """測試初始化"""
        transaction = Transaction(
            user_id="test_user",
            amount=100.0,
            type="bet",
            description="下注"
        )
        
        assert transaction.user_id == "test_user"
        assert transaction.amount == 100.0
        assert transaction.type == "bet"
        assert transaction.description == "下注"
        assert transaction.created_at is not None
        
    def test_to_dict(self):
        """測試轉換為字典"""
        transaction = Transaction(
            user_id="test_user",
            amount=100.0,
            type="bet",
            description="下注"
        )
        transaction_dict = transaction.to_dict()
        
        assert transaction_dict["user_id"] == "test_user"
        assert transaction_dict["amount"] == 100.0
        assert transaction_dict["type"] == "bet"
        assert transaction_dict["description"] == "下注"
        assert "created_at" in transaction_dict
        
    def test_transaction_types(self):
        """測試交易類型"""
        # 下注
        bet = Transaction(
            user_id="test_user",
            amount=100.0,
            type="bet",
            description="下注"
        )
        assert bet.type == "bet"
        
        # 獲勝
        win = Transaction(
            user_id="test_user",
            amount=200.0,
            type="win",
            description="獲勝"
        )
        assert win.type == "win"
        
        # 充值
        deposit = Transaction(
            user_id="test_user",
            amount=1000.0,
            type="deposit",
            description="充值"
        )
        assert deposit.type == "deposit"
        
        # 提現
        withdraw = Transaction(
            user_id="test_user",
            amount=500.0,
            type="withdraw",
            description="提現"
        )
        assert withdraw.type == "withdraw"
        
    def test_transaction_amounts(self):
        """測試交易金額"""
        # 正數金額
        positive = Transaction(
            user_id="test_user",
            amount=100.0,
            type="win",
            description="獲勝"
        )
        assert positive.amount > 0
        
        # 負數金額
        negative = Transaction(
            user_id="test_user",
            amount=-100.0,
            type="bet",
            description="下注"
        )
        assert negative.amount < 0
        
    def test_transaction_timestamps(self):
        """測試交易時間戳"""
        transaction = Transaction(
            user_id="test_user",
            amount=100.0,
            type="bet",
            description="下注"
        )
        
        # 驗證時間戳
        assert isinstance(transaction.created_at, datetime)
        assert transaction.created_at <= datetime.utcnow() 