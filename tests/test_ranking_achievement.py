import sys
import os
import pytest
from datetime import datetime
from pathlib import Path

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from models.user import UserManager
from models.game import GameManager
from models.ranking import RankingManager
from models.achievement import AchievementManager

class TestRankingAchievement:
    """排行榜和成就系統測試類"""
    
    @pytest.fixture
    def user_manager(self):
        """創建用戶管理器實例"""
        return UserManager()
        
    @pytest.fixture
    def game_manager(self):
        """創建遊戲管理器實例"""
        return GameManager()
        
    @pytest.fixture
    def ranking_manager(self):
        """創建排行榜管理器實例"""
        return RankingManager()
        
    @pytest.fixture
    def achievement_manager(self):
        """創建成就管理器實例"""
        return AchievementManager()
        
    def test_ranking_update(self, user_manager, game_manager, ranking_manager):
        """測試排行榜更新"""
        # 創建多個測試用戶
        users = []
        for i in range(5):
            user_id = user_manager.create_user(f"user{i}", 1000)
            users.append(user_id)
            
        # 模擬遊戲並更新積分
        for i, user_id in enumerate(users):
            # 每個用戶玩不同次數的遊戲
            for _ in range(i + 1):
                game_manager.play_roulette(user_id, 100, 7)
                
        # 獲取排行榜
        ranking = ranking_manager.get_ranking()
        
        # 驗證排行榜
        assert len(ranking) == len(users)
        
        # 驗證排名順序（積分從高到低）
        for i in range(len(ranking) - 1):
            assert ranking[i].points >= ranking[i + 1].points
            
    def test_ranking_categories(self, user_manager, game_manager, ranking_manager):
        """測試不同類別的排行榜"""
        # 創建測試用戶
        user_id = user_manager.create_user("test_user", 1000)
        
        # 玩不同類型的遊戲
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
                
        # 獲取不同類別的排行榜
        categories = ["total", "roulette", "baccarat", "bingo", "keno"]
        for category in categories:
            ranking = ranking_manager.get_ranking(category=category)
            assert len(ranking) > 0
            
    def test_ranking_periods(self, user_manager, game_manager, ranking_manager):
        """測試不同時期的排行榜"""
        # 創建測試用戶
        user_id = user_manager.create_user("test_user", 1000)
        
        # 模擬不同時期的遊戲
        periods = ["daily", "weekly", "monthly", "all_time"]
        for period in periods:
            # 玩遊戲
            game_manager.play_roulette(user_id, 100, 7)
            
            # 獲取該時期的排行榜
            ranking = ranking_manager.get_ranking(period=period)
            assert len(ranking) > 0
            
    def test_achievement_unlock(self, user_manager, game_manager, achievement_manager):
        """測試成就解鎖"""
        # 創建測試用戶
        user_id = user_manager.create_user("test_user", 1000)
        
        # 獲取初始成就
        initial_achievements = achievement_manager.get_user_achievements(user_id)
        
        # 玩遊戲
        game_manager.play_roulette(user_id, 100, 7)
        
        # 獲取更新後的成就
        updated_achievements = achievement_manager.get_user_achievements(user_id)
        
        # 驗證成就解鎖
        assert len(updated_achievements) >= len(initial_achievements)
        
    def test_achievement_progress(self, user_manager, game_manager, achievement_manager):
        """測試成就進度"""
        # 創建測試用戶
        user_id = user_manager.create_user("test_user", 1000)
        
        # 獲取初始進度
        initial_progress = achievement_manager.get_achievement_progress(user_id)
        
        # 玩遊戲
        game_manager.play_roulette(user_id, 100, 7)
        
        # 獲取更新後的進度
        updated_progress = achievement_manager.get_achievement_progress(user_id)
        
        # 驗證進度更新
        for achievement_id in updated_progress:
            assert updated_progress[achievement_id] >= initial_progress.get(achievement_id, 0)
            
    def test_achievement_categories(self, user_manager, game_manager, achievement_manager):
        """測試不同類別的成就"""
        # 創建測試用戶
        user_id = user_manager.create_user("test_user", 1000)
        
        # 測試不同類別的成就
        categories = ["game", "points", "streak", "special"]
        for category in categories:
            achievements = achievement_manager.get_user_achievements(user_id, category=category)
            assert len(achievements) >= 0
            
    def test_achievement_rewards(self, user_manager, game_manager, achievement_manager):
        """測試成就獎勵"""
        # 創建測試用戶
        user_id = user_manager.create_user("test_user", 1000)
        initial_points = user_manager.get_user_points(user_id)
        
        # 解鎖成就
        achievement_manager.unlock_achievement(user_id, "first_win")
        
        # 驗證獎勵發放
        final_points = user_manager.get_user_points(user_id)
        assert final_points > initial_points
        
    def test_achievement_notification(self, user_manager, game_manager, achievement_manager):
        """測試成就通知"""
        # 創建測試用戶
        user_id = user_manager.create_user("test_user", 1000)
        
        # 解鎖成就
        achievement_manager.unlock_achievement(user_id, "first_win")
        
        # 獲取通知
        notifications = achievement_manager.get_achievement_notifications(user_id)
        assert len(notifications) > 0
        assert any(n.achievement_id == "first_win" for n in notifications)
        
    def test_ranking_achievement_integration(self, user_manager, game_manager, ranking_manager, achievement_manager):
        """測試排行榜和成就系統的集成"""
        # 創建測試用戶
        user_id = user_manager.create_user("test_user", 1000)
        
        # 玩遊戲
        game_manager.play_roulette(user_id, 100, 7)
        
        # 驗證排行榜更新
        ranking = ranking_manager.get_ranking()
        assert len(ranking) > 0
        
        # 驗證成就解鎖
        achievements = achievement_manager.get_user_achievements(user_id)
        assert len(achievements) > 0
        
        # 驗證成就進度
        progress = achievement_manager.get_achievement_progress(user_id)
        assert len(progress) > 0
        
        # 驗證通知
        notifications = achievement_manager.get_achievement_notifications(user_id)
        assert len(notifications) > 0 