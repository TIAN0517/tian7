from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta

class RankingManager:
    """排行榜管理器"""
    
    def __init__(self):
        self.rankings: Dict[str, Dict[str, List[Dict]]] = {
            "total": [],
            "roulette": [],
            "baccarat": [],
            "bingo": [],
            "keno": []
        }
        self.logger = logging.getLogger(__name__)
        
    def update_ranking(self, user_id: str, game_id: str, points: float):
        """更新排行榜"""
        try:
            # 更新總排行榜
            self._update_category_ranking("total", user_id, points)
            
            # 更新遊戲特定排行榜
            if game_id in self.rankings:
                self._update_category_ranking(game_id, user_id, points)
                
        except Exception as e:
            self.logger.error(f"更新排行榜失敗: {str(e)}")
            raise
            
    def _update_category_ranking(self, category: str, user_id: str, points: float):
        """更新特定類別的排行榜"""
        try:
            # 查找用戶是否已在排行榜中
            for entry in self.rankings[category]:
                if entry["user_id"] == user_id:
                    entry["points"] += points
                    entry["updated_at"] = datetime.now()
                    break
            else:
                # 如果用戶不在排行榜中，添加新條目
                self.rankings[category].append({
                    "user_id": user_id,
                    "points": points,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                })
                
            # 按積分排序
            self.rankings[category].sort(key=lambda x: x["points"], reverse=True)
            
        except Exception as e:
            self.logger.error(f"更新類別排行榜失敗: {str(e)}")
            raise
            
    def get_ranking(self, category: str = "total", period: str = "all") -> List[Dict]:
        """獲取排行榜"""
        try:
            if category not in self.rankings:
                raise ValueError(f"無效的類別: {category}")
                
            rankings = self.rankings[category]
            
            # 根據時間段過濾
            if period != "all":
                now = datetime.now()
                if period == "daily":
                    cutoff = now - timedelta(days=1)
                elif period == "weekly":
                    cutoff = now - timedelta(weeks=1)
                elif period == "monthly":
                    cutoff = now - timedelta(days=30)
                else:
                    raise ValueError(f"無效的時間段: {period}")
                    
                rankings = [r for r in rankings if r["updated_at"] >= cutoff]
                
            return rankings
            
        except Exception as e:
            self.logger.error(f"獲取排行榜失敗: {str(e)}")
            raise 