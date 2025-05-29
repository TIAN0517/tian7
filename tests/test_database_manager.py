import pytest
from datetime import datetime
from database.db_manager import DatabaseManager
from database.bingo_models import User, GameHistory, Transaction

class TestDatabaseManager:
    """數據庫管理器測試"""
    
    @pytest.fixture
    def db_manager(self):
        """創建數據庫管理器實例"""
        return DatabaseManager("sqlite:///:memory:")
        
    def test_init(self, db_manager):
        """測試初始化"""
        assert db_manager.engine is not None
        assert db_manager.Session is not None
        
    def test_create_tables(self, db_manager):
        """測試創建表"""
        db_manager.create_tables()
        
        # 驗證表是否創建
        with db_manager.Session() as session:
            # 檢查User表
            users = session.query(User).all()
            assert users is not None
            
            # 檢查GameHistory表
            history = session.query(GameHistory).all()
            assert history is not None
            
            # 檢查Transaction表
            transactions = session.query(Transaction).all()
            assert transactions is not None
            
    def test_get_user_points(self, db_manager):
        """測試獲取用戶積分"""
        # 創建測試用戶
        with db_manager.Session() as session:
            user = User(user_id="test_user", points=1000.0)
            session.add(user)
            session.commit()
            
        # 獲取積分
        points = db_manager.get_user_points("test_user")
        assert points == 1000.0
        
    def test_update_user_points(self, db_manager):
        """測試更新用戶積分"""
        # 創建測試用戶
        with db_manager.Session() as session:
            user = User(user_id="test_user", points=1000.0)
            session.add(user)
            session.commit()
            
        # 更新積分
        db_manager.update_user_points("test_user", 2000.0)
        
        # 驗證更新
        with db_manager.Session() as session:
            user = session.query(User).filter_by(user_id="test_user").first()
            assert user.points == 2000.0
            
    def test_record_transaction(self, db_manager):
        """測試記錄交易"""
        # 創建測試用戶
        with db_manager.Session() as session:
            user = User(user_id="test_user", points=1000.0)
            session.add(user)
            session.commit()
            
        # 記錄交易
        transaction_data = {
            "user_id": "test_user",
            "amount": 100.0,
            "type": "bet",
            "description": "下注"
        }
        db_manager.record_transaction(transaction_data)
        
        # 驗證記錄
        with db_manager.Session() as session:
            transaction = session.query(Transaction).filter_by(
                user_id="test_user",
                amount=100.0,
                type="bet"
            ).first()
            assert transaction is not None
            assert transaction.description == "下注"
            
    def test_record_game_history(self, db_manager):
        """測試記錄遊戲歷史"""
        # 創建測試用戶
        with db_manager.Session() as session:
            user = User(user_id="test_user", points=1000.0)
            session.add(user)
            session.commit()
            
        # 記錄遊戲歷史
        game_data = {
            "user_id": "test_user",
            "bet_amount": 100.0,
            "card_count": 2,
            "drawn_balls": [1, 2, 3],
            "winning_patterns": ["single_line"],
            "payout": 200.0,
            "duration": 60
        }
        db_manager.record_game_history(game_data)
        
        # 驗證記錄
        with db_manager.Session() as session:
            history = session.query(GameHistory).filter_by(
                user_id="test_user",
                bet_amount=100.0,
                card_count=2
            ).first()
            assert history is not None
            assert history.drawn_balls == [1, 2, 3]
            assert history.winning_patterns == ["single_line"]
            assert history.payout == 200.0
            assert history.duration == 60
            
    def test_get_user_transactions(self, db_manager):
        """測試獲取用戶交易記錄"""
        # 創建測試用戶和交易
        with db_manager.Session() as session:
            user = User(user_id="test_user", points=1000.0)
            session.add(user)
            
            # 添加多筆交易
            transactions = [
                Transaction(user_id="test_user", amount=100.0, type="bet", description="下注1"),
                Transaction(user_id="test_user", amount=200.0, type="win", description="獲勝1"),
                Transaction(user_id="test_user", amount=300.0, type="bet", description="下注2")
            ]
            session.add_all(transactions)
            session.commit()
            
        # 獲取交易記錄
        transactions = db_manager.get_user_transactions("test_user")
        assert len(transactions) == 3
        
        # 驗證交易順序（按時間倒序）
        assert transactions[0].description == "下注2"
        assert transactions[1].description == "獲勝1"
        assert transactions[2].description == "下注1"
        
    def test_get_user_game_history(self, db_manager):
        """測試獲取用戶遊戲歷史"""
        # 創建測試用戶和遊戲歷史
        with db_manager.Session() as session:
            user = User(user_id="test_user", points=1000.0)
            session.add(user)
            
            # 添加多筆遊戲歷史
            history = [
                GameHistory(
                    user_id="test_user",
                    bet_amount=100.0,
                    card_count=1,
                    drawn_balls=[1, 2, 3],
                    winning_patterns=["single_line"],
                    payout=200.0,
                    duration=60
                ),
                GameHistory(
                    user_id="test_user",
                    bet_amount=200.0,
                    card_count=2,
                    drawn_balls=[4, 5, 6],
                    winning_patterns=["four_corners"],
                    payout=400.0,
                    duration=90
                )
            ]
            session.add_all(history)
            session.commit()
            
        # 獲取遊戲歷史
        history = db_manager.get_user_game_history("test_user")
        assert len(history) == 2
        
        # 驗證歷史順序（按時間倒序）
        assert history[0].bet_amount == 200.0
        assert history[1].bet_amount == 100.0
        
    def test_get_user_statistics(self, db_manager):
        """測試獲取用戶統計數據"""
        # 創建測試用戶和遊戲歷史
        with db_manager.Session() as session:
            user = User(user_id="test_user", points=1000.0)
            session.add(user)
            
            # 添加多筆遊戲歷史
            history = [
                GameHistory(
                    user_id="test_user",
                    bet_amount=100.0,
                    card_count=1,
                    drawn_balls=[1, 2, 3],
                    winning_patterns=["single_line"],
                    payout=200.0,
                    duration=60
                ),
                GameHistory(
                    user_id="test_user",
                    bet_amount=200.0,
                    card_count=2,
                    drawn_balls=[4, 5, 6],
                    winning_patterns=["four_corners"],
                    payout=400.0,
                    duration=90
                )
            ]
            session.add_all(history)
            session.commit()
            
        # 獲取統計數據
        stats = db_manager.get_user_statistics("test_user")
        
        assert stats["total_games"] == 2
        assert stats["total_bet"] == 300.0
        assert stats["total_payout"] == 600.0
        assert stats["win_rate"] == 1.0  # 兩局都獲勝
        assert stats["average_duration"] == 75  # (60 + 90) / 2
        assert stats["favorite_pattern"] == "single_line"  # 假設按出現次數排序 