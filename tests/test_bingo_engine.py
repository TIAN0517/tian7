import pytest
from PyQt5.QtCore import QObject
from games.bingo_engine import BingoEngine

class TestBingoEngine:
    """賓果遊戲引擎測試"""
    
    @pytest.fixture
    def engine(self):
        """創建遊戲引擎實例"""
        return BingoEngine()
        
    def test_init(self, engine):
        """測試初始化"""
        assert isinstance(engine, QObject)
        assert not engine.is_game_running
        assert engine.current_user_id is None
        assert engine.current_points == 0
        assert engine.bet_amount == 0
        assert engine.card_count == 0
        assert engine.cards == []
        assert engine.drawn_balls == []
        assert engine.remaining_balls == list(range(1, 76))
        
    def test_start_game_success(self, engine):
        """測試成功開始遊戲"""
        user_id = "test_user"
        points = 1000.0
        bet_amount = 100.0
        card_count = 2
        
        result = engine.start_game(user_id, points, bet_amount, card_count)
        
        assert result is True
        assert engine.is_game_running
        assert engine.current_user_id == user_id
        assert engine.current_points == points
        assert engine.bet_amount == bet_amount
        assert engine.card_count == card_count
        assert len(engine.cards) == card_count
        
    def test_start_game_insufficient_points(self, engine):
        """測試積分不足"""
        user_id = "test_user"
        points = 100.0
        bet_amount = 100.0
        card_count = 2
        
        result = engine.start_game(user_id, points, bet_amount, card_count)
        
        assert result is False
        assert not engine.is_game_running
        
    def test_start_game_already_running(self, engine):
        """測試遊戲已運行"""
        # 先開始一局遊戲
        engine.start_game("test_user", 1000.0, 100.0, 1)
        
        # 嘗試開始新遊戲
        result = engine.start_game("test_user", 1000.0, 100.0, 1)
        
        assert result is False
        
    def test_generate_valid_card(self, engine):
        """測試生成有效卡片"""
        card = engine._generate_valid_card()
        
        # 檢查卡片大小
        assert len(card) == 5
        for row in card:
            assert len(row) == 5
            
        # 檢查FREE空間
        assert card[2][2] == 0
        
        # 檢查每列數字範圍
        ranges = [
            (1, 15),   # B列
            (16, 30),  # I列
            (31, 45),  # N列
            (46, 60),  # G列
            (61, 75)   # O列
        ]
        
        for col, (min_val, max_val) in enumerate(ranges):
            for num in card[col]:
                if num != 0:  # 排除FREE空間
                    assert min_val <= num <= max_val
                    
    def test_draw_ball(self, engine):
        """測試抽球"""
        # 開始遊戲
        engine.start_game("test_user", 1000.0, 100.0, 1)
        
        # 抽球
        ball = engine.draw_ball()
        
        assert ball is not None
        assert 1 <= ball <= 75
        assert ball in engine.drawn_balls
        assert ball not in engine.remaining_balls
        
    def test_draw_ball_game_not_running(self, engine):
        """測試遊戲未運行時抽球"""
        ball = engine.draw_ball()
        assert ball is None
        
    def test_draw_ball_no_balls_left(self, engine):
        """測試無球可抽"""
        # 開始遊戲
        engine.start_game("test_user", 1000.0, 100.0, 1)
        
        # 抽完所有球
        for _ in range(75):
            engine.draw_ball()
            
        # 嘗試再抽球
        ball = engine.draw_ball()
        assert ball is None
        
    def test_end_game(self, engine):
        """測試結束遊戲"""
        # 開始遊戲
        engine.start_game("test_user", 1000.0, 100.0, 1)
        
        # 抽幾個球
        for _ in range(5):
            engine.draw_ball()
            
        # 結束遊戲
        result = engine.end_game()
        
        assert result is not None
        assert not engine.is_game_running
        assert "user_id" in result
        assert "total_bet" in result
        assert "total_payout" in result
        assert "cards_data" in result
        assert "drawn_balls" in result
        assert "winning_patterns" in result
        assert "game_duration" in result
        assert "final_points" in result
        
    def test_end_game_not_running(self, engine):
        """測試遊戲未運行時結束"""
        result = engine.end_game()
        assert result is None 