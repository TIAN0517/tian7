"""
RanOnline 遊戲模塊
包含所有 23 款遊戲的邏輯實現
"""

__version__ = "1.0.0"
__author__ = "Jy技術團隊"

from .game_data import ALL_GAMES_INFO
from .game_manager import GameManager

__all__ = [
    'ALL_GAMES_INFO',
    'GameManager'
]