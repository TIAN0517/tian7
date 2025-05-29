from typing import Dict, List, Optional
import logging
from datetime import datetime

class AchievementManager:
    """成就管理器"""
    
    def __init__(self):
        self.achievements: Dict[str, Dict] = {
            "first_win": {
                "id": "first_win",
                "name": "初次勝利",
                "description": "贏得第一場遊戲",
                "points": 100
            },
            "high_roller": {
                "id": "high_roller",
                "name": "高額玩家",
                "description": "單次下注超過1000點",
                "points": 500
            },
            "winning_streak": {
                "id": "winning_streak",
                "name": "連勝王",
                "description": "連續贏得5場遊戲",
                "points": 1000
            }
        }
        self.user_achievements: Dict[str, List[Dict]] = {}
        self.logger = logging.getLogger(__name__)
        
    def check_achievements(self, user_id: str, game_result: Dict) -> List[Dict]:
        """檢查並更新用戶成就"""
        try:
            if user_id not in self.user_achievements:
                self.user_achievements[user_id] = []
                
            unlocked_achievements = []
            
            # 檢查初次勝利成就
            if game_result.get("won", False):
                if not any(a["id"] == "first_win" for a in self.user_achievements[user_id]):
                    self._unlock_achievement(user_id, "first_win")
                    unlocked_achievements.append(self.achievements["first_win"])
                    
            # 檢查高額玩家成就
            if game_result.get("bet", 0) >= 1000:
                if not any(a["id"] == "high_roller" for a in self.user_achievements[user_id]):
                    self._unlock_achievement(user_id, "high_roller")
                    unlocked_achievements.append(self.achievements["high_roller"])
                    
            # 檢查連勝成就
            if game_result.get("won", False):
                # 這裡需要實現連勝邏輯
                pass
                
            return unlocked_achievements
            
        except Exception as e:
            self.logger.error(f"檢查成就失敗: {str(e)}")
            raise
            
    def _unlock_achievement(self, user_id: str, achievement_id: str):
        """解鎖成就"""
        try:
            if achievement_id not in self.achievements:
                raise ValueError(f"無效的成就ID: {achievement_id}")
                
            achievement = self.achievements[achievement_id]
            self.user_achievements[user_id].append({
                **achievement,
                "unlocked_at": datetime.now()
            })
            
        except Exception as e:
            self.logger.error(f"解鎖成就失敗: {str(e)}")
            raise
            
    def get_user_achievements(self, user_id: str) -> List[Dict]:
        """獲取用戶成就"""
        try:
            return self.user_achievements.get(user_id, [])
            
        except Exception as e:
            self.logger.error(f"獲取用戶成就失敗: {str(e)}")
            raise
            
    def get_achievement_progress(self, user_id: str, achievement_id: str) -> float:
        """獲取成就進度"""
        try:
            if achievement_id not in self.achievements:
                raise ValueError(f"無效的成就ID: {achievement_id}")
                
            # 檢查是否已解鎖
            if any(a["id"] == achievement_id for a in self.user_achievements.get(user_id, [])):
                return 1.0
                
            # 這裡需要實現具體的進度計算邏輯
            return 0.0
            
        except Exception as e:
            self.logger.error(f"獲取成就進度失敗: {str(e)}")
            raise 