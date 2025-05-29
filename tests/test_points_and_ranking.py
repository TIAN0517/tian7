import pytest
from datetime import datetime, timedelta
from database.bingo_db_manager import BingoDatabaseManager
from database.bingo_models import BingoStatistics

class TestPointsAndRanking:
    """積分系統和排行榜測試"""
    
    @pytest.fixture
    def db_manager(self):
        """創建數據庫管理器實例"""
        return BingoDatabaseManager("sqlite:///:memory:")
        
    def test_points_update(self, db_manager):
        """測試積分更新"""
        user_id = "test_user"
        
        # 初始積分
        initial_points = 1000.0
        
        # 下注
        bet_amount = 100.0
        card_count = 2
        total_bet = bet_amount * card_count
        
        # 獲勝
        win_amount = 500.0
        
        # 更新積分
        db_manager.update_user_points(user_id, initial_points - total_bet + win_amount)
        
        # 驗證積分
        final_points = db_manager.get_user_points(user_id)
        assert final_points == initial_points - total_bet + win_amount
        
    def test_game_history(self, db_manager):
        """測試遊戲歷史記錄"""
        user_id = "test_user"
        
        # 記錄遊戲
        game_data = {
            "user_id": user_id,
            "bet_amount": 100.0,
            "card_count": 2,
            "drawn_balls": [1, 2, 3, 4, 5],
            "winning_patterns": ["single_line"],
            "payout": 200.0,
            "duration": 60
        }
        
        db_manager.record_game_history(game_data)
        
        # 獲取歷史記錄
        history = db_manager.get_user_game_history(user_id)
        
        # 驗證記錄
        assert len(history) > 0
        assert history[0]["user_id"] == user_id
        assert history[0]["bet_amount"] == 100.0
        assert history[0]["card_count"] == 2
        assert history[0]["payout"] == 200.0
        
    def test_statistics_update(self, db_manager):
        """測試統計數據更新"""
        user_id = "test_user"
        
        # 獲取或創建統計數據
        stats = db_manager.get_or_create_statistics(user_id)
        
        # 更新統計數據
        game_result = {
            "total_bet": 100.0,
            "total_payout": 200.0,
            "winning_patterns": [
                {
                    "type": "single_line",
                    "positions": [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)]
                }
            ]
        }
        
        stats.update_statistics(game_result)
        
        # 驗證統計數據
        assert stats.total_games == 1
        assert stats.total_bet == 100.0
        assert stats.total_payout == 200.0
        assert stats.single_line_wins == 1
        
    def test_ranking_calculation(self, db_manager):
        """測試排行榜計算"""
        # 創建多個用戶的統計數據
        users = [
            ("user1", 1000.0, 500.0),  # (user_id, total_bet, total_payout)
            ("user2", 2000.0, 1000.0),
            ("user3", 1500.0, 800.0)
        ]
        
        for user_id, total_bet, total_payout in users:
            stats = db_manager.get_or_create_statistics(user_id)
            stats.total_bet = total_bet
            stats.total_payout = total_payout
            db_manager.update_statistics(user_id, {
                "total_bet": total_bet,
                "total_payout": total_payout
            })
            
        # 獲取排行榜
        ranking = db_manager.get_ranking()
        
        # 驗證排行榜順序
        assert len(ranking) == 3
        assert ranking[0]["user_id"] == "user2"  # 最高投注額
        assert ranking[1]["user_id"] == "user3"
        assert ranking[2]["user_id"] == "user1"
        
    def test_achievement_tracking(self, db_manager):
        """測試成就追蹤"""
        user_id = "test_user"
        
        # 獲取或創建統計數據
        stats = db_manager.get_or_create_statistics(user_id)
        
        # 更新統計數據以解鎖成就
        game_results = [
            {
                "total_bet": 100.0,
                "total_payout": 200.0,
                "winning_patterns": [
                    {"type": "single_line"},
                    {"type": "four_corners"}
                ]
            },
            {
                "total_bet": 200.0,
                "total_payout": 400.0,
                "winning_patterns": [
                    {"type": "double_line"},
                    {"type": "x_pattern"}
                ]
            }
        ]
        
        for result in game_results:
            stats.update_statistics(result)
            
        # 驗證成就解鎖
        assert stats.single_line_wins == 1
        assert stats.double_line_wins == 1
        assert stats.four_corners_wins == 1
        assert stats.x_pattern_wins == 1
        
    def test_points_transaction_history(self, db_manager):
        """測試積分交易歷史"""
        user_id = "test_user"
        
        # 記錄多筆交易
        transactions = [
            {"type": "bet", "amount": 100.0, "description": "下注"},
            {"type": "win", "amount": 200.0, "description": "獲勝"},
            {"type": "bet", "amount": 150.0, "description": "下注"},
            {"type": "win", "amount": 300.0, "description": "獲勝"}
        ]
        
        for trans in transactions:
            db_manager.record_transaction(user_id, trans)
            
        # 獲取交易歷史
        history = db_manager.get_user_transactions(user_id)
        
        # 驗證交易歷史
        assert len(history) == 4
        assert history[0]["type"] == "win"  # 最新的交易
        assert history[0]["amount"] == 300.0
        assert history[-1]["type"] == "bet"  # 最舊的交易
        assert history[-1]["amount"] == 100.0 