import sys
import os
import pytest
import random
from datetime import datetime
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from models.user import UserManager
from models.game import GameManager
from models.achievement import AchievementManager
from models.ranking import RankingManager
from app.main import app
from app.database import Base, get_db
from app.models.game_models import GameSession, Bet, GameResult, GameType
from app.games.game_logic import (
    GameLogic, RouletteBetType, BaccaratBetType,
    DragonTigerBetType, Card
)

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

class TestGameLogic:
    """遊戲邏輯測試類"""
    
    @pytest.fixture
    def user_manager(self):
        """創建用戶管理器實例"""
        return UserManager()
        
    @pytest.fixture
    def game_manager(self):
        """創建遊戲管理器實例"""
        return GameManager()
        
    @pytest.fixture
    def achievement_manager(self):
        """創建成就管理器實例"""
        return AchievementManager()
        
    @pytest.fixture
    def ranking_manager(self):
        """創建排行榜管理器實例"""
        return RankingManager()
        
    def test_roulette_game(self, user_manager, game_manager):
        """測試輪盤遊戲"""
        # 創建測試用戶
        user_id = user_manager.create_user("test_user", 1000)
        
        # 測試下注
        bet_amount = 100
        bet_number = 7
        result = game_manager.play_roulette(user_id, bet_amount, bet_number)
        
        # 驗證結果
        assert result is not None
        assert "開獎號碼" in result
        assert "恭喜中獎" in result or "未中獎" in result
        
        # 驗證積分變動
        user = user_manager.get_user(user_id)
        assert user is not None
        assert user.points >= 0
        
        # 驗證遊戲記錄
        history = game_manager.get_game_history(user_id)
        assert len(history) > 0
        assert history[0].game_type == "roulette"
        assert history[0].bet_amount == bet_amount
        
    def test_baccarat_game(self, user_manager, game_manager):
        """測試百家樂遊戲"""
        # 創建測試用戶
        user_id = user_manager.create_user("test_user", 1000)
        
        # 測試下注
        bet_amount = 100
        bet_on = "player"
        result = game_manager.play_baccarat(user_id, bet_amount, bet_on)
        
        # 驗證結果
        assert result is not None
        assert "閒家" in result
        assert "莊家" in result
        assert "恭喜中獎" in result or "未中獎" in result
        
        # 驗證積分變動
        user = user_manager.get_user(user_id)
        assert user is not None
        assert user.points >= 0
        
        # 驗證遊戲記錄
        history = game_manager.get_game_history(user_id)
        assert len(history) > 0
        assert history[0].game_type == "baccarat"
        assert history[0].bet_amount == bet_amount
        
    def test_bingo_game(self, user_manager, game_manager):
        """測試賓果遊戲"""
        # 創建測試用戶
        user_id = user_manager.create_user("test_user", 1000)
        
        # 測試下注
        bet_amount = 100
        user_board = [1, 2, 3, 4, 5]
        result = game_manager.play_bingo(user_id, bet_amount, user_board)
        
        # 驗證結果
        assert result is not None
        assert "開獎號碼" in result
        assert "賓果" in result or "未中獎" in result
        
        # 驗證積分變動
        user = user_manager.get_user(user_id)
        assert user is not None
        assert user.points >= 0
        
        # 驗證遊戲記錄
        history = game_manager.get_game_history(user_id)
        assert len(history) > 0
        assert history[0].game_type == "bingo"
        assert history[0].bet_amount == bet_amount
        
    def test_keno_game(self, user_manager, game_manager):
        """測試Keno遊戲"""
        # 創建測試用戶
        user_id = user_manager.create_user("test_user", 1000)
        
        # 測試下注
        bet_amount = 100
        user_numbers = [1, 2, 3, 4, 5]
        result = game_manager.play_keno(user_id, bet_amount, user_numbers)
        
        # 驗證結果
        assert result is not None
        assert "開獎號碼" in result
        assert "恭喜中獎" in result or "未中獎" in result
        
        # 驗證積分變動
        user = user_manager.get_user(user_id)
        assert user is not None
        assert user.points >= 0
        
        # 驗證遊戲記錄
        history = game_manager.get_game_history(user_id)
        assert len(history) > 0
        assert history[0].game_type == "keno"
        assert history[0].bet_amount == bet_amount
        
    def test_points_calculation(self, user_manager, game_manager):
        """測試積分計算"""
        # 創建測試用戶
        user_id = user_manager.create_user("test_user", 1000)
        initial_points = user_manager.get_user_points(user_id)
        
        # 測試遊戲
        bet_amount = 100
        result = game_manager.play_roulette(user_id, bet_amount, 7)
        
        # 驗證積分變動
        final_points = user_manager.get_user_points(user_id)
        assert final_points != initial_points
        
        # 驗證積分變動記錄
        points_history = user_manager.get_points_history(user_id)
        assert len(points_history) > 0
        assert points_history[0].amount != 0
        
    def test_achievement_system(self, user_manager, game_manager, achievement_manager):
        """測試成就系統"""
        # 創建測試用戶
        user_id = user_manager.create_user("test_user", 1000)
        
        # 測試遊戲
        bet_amount = 100
        game_manager.play_roulette(user_id, bet_amount, 7)
        
        # 驗證成就解鎖
        achievements = achievement_manager.get_user_achievements(user_id)
        assert len(achievements) > 0
        
        # 驗證成就進度
        progress = achievement_manager.get_achievement_progress(user_id)
        assert len(progress) > 0
        
    def test_ranking_system(self, user_manager, game_manager, ranking_manager):
        """測試排行榜系統"""
        # 創建測試用戶
        user_id = user_manager.create_user("test_user", 1000)
        
        # 測試遊戲
        bet_amount = 100
        game_manager.play_roulette(user_id, bet_amount, 7)
        
        # 驗證排行榜
        ranking = ranking_manager.get_ranking()
        assert len(ranking) > 0
        
        # 驗證用戶排名
        user_rank = ranking_manager.get_user_rank(user_id)
        assert user_rank is not None
        
    def test_game_history(self, user_manager, game_manager):
        """測試遊戲歷史記錄"""
        # 創建測試用戶
        user_id = user_manager.create_user("test_user", 1000)
        
        # 測試多個遊戲
        games = [
            ("roulette", 100, 7),
            ("baccarat", 100, "player"),
            ("bingo", 100, [1, 2, 3, 4, 5]),
            ("keno", 100, [1, 2, 3, 4, 5])
        ]
        
        for game_type, bet_amount, bet_data in games:
            if game_type == "roulette":
                game_manager.play_roulette(user_id, bet_amount, bet_data)
            elif game_type == "baccarat":
                game_manager.play_baccarat(user_id, bet_amount, bet_data)
            elif game_type == "bingo":
                game_manager.play_bingo(user_id, bet_amount, bet_data)
            elif game_type == "keno":
                game_manager.play_keno(user_id, bet_amount, bet_data)
                
        # 驗證遊戲歷史
        history = game_manager.get_game_history(user_id)
        assert len(history) == len(games)
        
        # 驗證每條記錄
        for i, (game_type, bet_amount, _) in enumerate(games):
            assert history[i].game_type == game_type
            assert history[i].bet_amount == bet_amount
            
    def test_error_handling(self, user_manager, game_manager):
        """測試錯誤處理"""
        # 測試無效用戶
        with pytest.raises(ValueError):
            game_manager.play_roulette("invalid_user", 100, 7)
            
        # 測試無效下注金額
        user_id = user_manager.create_user("test_user", 1000)
        with pytest.raises(ValueError):
            game_manager.play_roulette(user_id, -100, 7)
            
        # 測試無效下注號碼
        with pytest.raises(ValueError):
            game_manager.play_roulette(user_id, 100, 37)  # 輪盤號碼超出範圍
            
        # 測試餘額不足
        with pytest.raises(ValueError):
            game_manager.play_roulette(user_id, 2000, 7)  # 下注金額超過餘額 

def test_roulette_number_generation():
    """Test roulette number generation."""
    number, color = GameLogic.generate_roulette_number()
    assert 0 <= number <= 36
    assert color in ["red", "black", "green"]
    if number == 0:
        assert color == "green"
    elif number in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]:
        assert color == "red"
    else:
        assert color == "black"

def test_roulette_win_calculation():
    """Test roulette win calculations."""
    # Test straight bet
    win = GameLogic.calculate_roulette_win(RouletteBetType.STRAIGHT, 100, 7)
    assert win == 3500  # 35:1 odds
    
    # Test red bet
    win = GameLogic.calculate_roulette_win(RouletteBetType.RED, 100, 1)
    assert win == 100  # 1:1 odds
    
    # Test losing bet
    win = GameLogic.calculate_roulette_win(RouletteBetType.RED, 100, 2)
    assert win == 0

def test_baccarat_card_generation():
    """Test baccarat card generation."""
    player_cards, banker_cards = GameLogic.generate_baccarat_cards()
    assert len(player_cards) in [2, 3]
    assert len(banker_cards) in [2, 3]
    
    # Check card values
    for card in player_cards + banker_cards:
        assert 1 <= card.value <= 13
        assert card.suit in ['hearts', 'diamonds', 'clubs', 'spades']

def test_baccarat_win_calculation():
    """Test baccarat win calculations."""
    player_cards = [Card('hearts', 10, '10'), Card('diamonds', 10, '10')]  # 20 -> 0
    banker_cards = [Card('clubs', 9, '9'), Card('spades', 9, '9')]  # 18 -> 8
    
    # Test banker win
    win = GameLogic.calculate_baccarat_win(
        BaccaratBetType.BANKER,
        100,
        player_cards,
        banker_cards
    )
    assert win == 195  # 1.95:1 odds with 5% commission
    
    # Test player win
    win = GameLogic.calculate_baccarat_win(
        BaccaratBetType.PLAYER,
        100,
        banker_cards,
        player_cards
    )
    assert win == 200  # 1:1 odds

def test_dragon_tiger_card_generation():
    """Test dragon tiger card generation."""
    dragon_card, tiger_card = GameLogic.generate_dragon_tiger_cards()
    assert 1 <= dragon_card.value <= 13
    assert 1 <= tiger_card.value <= 13
    assert dragon_card.suit in ['hearts', 'diamonds', 'clubs', 'spades']
    assert tiger_card.suit in ['hearts', 'diamonds', 'clubs', 'spades']

def test_dragon_tiger_win_calculation():
    """Test dragon tiger win calculations."""
    dragon_card = Card('hearts', 10, '10')
    tiger_card = Card('diamonds', 7, '7')
    
    # Test dragon win
    win = GameLogic.calculate_dragon_tiger_win(
        DragonTigerBetType.DRAGON,
        100,
        dragon_card,
        tiger_card
    )
    assert win == 200  # 1:1 odds
    
    # Test tiger win
    win = GameLogic.calculate_dragon_tiger_win(
        DragonTigerBetType.TIGER,
        100,
        tiger_card,
        dragon_card
    )
    assert win == 200  # 1:1 odds

def test_slot_result_generation():
    """Test slot machine result generation."""
    result = GameLogic.generate_slot_result()
    assert 'reels' in result
    assert 'paylines' in result
    assert 'total_win' in result
    assert 'bonus_triggered' in result
    assert 'bonus_type' in result
    
    assert len(result['reels']) == 5  # 5 reels
    assert all(len(reel) == 3 for reel in result['reels'])  # 3 symbols per reel

# API Tests
def test_create_game_session(test_db):
    """Test creating a new game session."""
    response = client.post(
        "/sessions",
        json={
            "game_type": "roulette",
            "user_id": 1
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["game_type"] == "roulette"
    assert data["user_id"] == 1
    assert data["status"] == "active"

def test_place_roulette_bet(test_db):
    """Test placing a roulette bet."""
    # First create a session
    session_response = client.post(
        "/sessions",
        json={
            "game_type": "roulette",
            "user_id": 1
        }
    )
    session_id = session_response.json()["id"]
    
    # Place a bet
    response = client.post(
        f"/roulette/bet",
        json={
            "bet_type": "straight",
            "amount": 100,
            "odds": 35
        },
        params={"session_id": session_id}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Bet placed successfully"

def test_spin_roulette_wheel(test_db):
    """Test spinning the roulette wheel."""
    # Create session and place bet
    session_response = client.post(
        "/sessions",
        json={
            "game_type": "roulette",
            "user_id": 1
        }
    )
    session_id = session_response.json()["id"]
    
    client.post(
        f"/roulette/bet",
        json={
            "bet_type": "straight",
            "amount": 100,
            "odds": 35
        },
        params={"session_id": session_id}
    )
    
    # Spin the wheel
    response = client.post(f"/roulette/spin", params={"session_id": session_id})
    assert response.status_code == 200
    data = response.json()
    assert "number" in data
    assert "color" in data
    assert "total_win" in data
    assert 0 <= data["number"] <= 36
    assert data["color"] in ["red", "black", "green"] 