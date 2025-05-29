import pytest
import os
import sys
from pathlib import Path

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 設置測試環境變量
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test_secret_key"
os.environ["LOG_LEVEL"] = "DEBUG"

@pytest.fixture(scope="session")
def test_config():
    """測試配置"""
    return {
        "database_url": os.environ["DATABASE_URL"],
        "secret_key": os.environ["SECRET_KEY"],
        "log_level": os.environ["LOG_LEVEL"],
        "max_cards": 4,
        "min_bet": 10.0,
        "max_bet": 10000.0,
        "draw_interval": 2000
    }
    
@pytest.fixture(scope="session")
def test_user():
    """測試用戶數據"""
    return {
        "user_id": "test_user",
        "points": 1000.0
    }
    
@pytest.fixture(scope="session")
def test_game_data():
    """測試遊戲數據"""
    return {
        "bet_amount": 100.0,
        "card_count": 2,
        "drawn_balls": [1, 2, 3, 4, 5],
        "winning_patterns": ["single_line", "four_corners"],
        "payout": 300.0,
        "duration": 60
    }
    
@pytest.fixture(scope="session")
def test_transaction_data():
    """測試交易數據"""
    return {
        "user_id": "test_user",
        "amount": 100.0,
        "type": "bet",
        "description": "下注"
    }
    
@pytest.fixture(scope="session")
def test_card_data():
    """測試卡片數據"""
    return [
        [1, 16, 31, 46, 61],
        [2, 17, 32, 47, 62],
        [3, 18, 0, 48, 63],
        [4, 19, 33, 49, 64],
        [5, 20, 34, 50, 65]
    ]
    
@pytest.fixture(scope="session")
def test_winning_patterns():
    """測試獲勝圖案"""
    return [
        {
            "type": "single_line",
            "positions": [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)],
            "multiplier": 1.0
        },
        {
            "type": "four_corners",
            "positions": [(0, 0), (0, 4), (4, 0), (4, 4)],
            "multiplier": 2.0
        },
        {
            "type": "blackout",
            "positions": [(i, j) for i in range(5) for j in range(5)],
            "multiplier": 10.0
        }
    ]
    
@pytest.fixture(scope="session")
def test_animation_data():
    """測試動畫數據"""
    return {
        "ball_draw": {
            "start_pos": (0, 0),
            "end_pos": (100, 100),
            "duration": 1000
        },
        "card_mark": {
            "scale": 0.8,
            "duration": 200
        },
        "winning_celebration": {
            "flash_count": 5,
            "interval": 200
        },
        "points_update": {
            "steps": 10,
            "interval": 100
        }
    } 