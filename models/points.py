from typing import Dict, Optional
import logging
from datetime import datetime

class PointsManager:
    """积分管理器"""
    
    def __init__(self):
        self.points: Dict[str, float] = {}
        self.history: Dict[str, list] = {}
        self.logger = logging.getLogger(__name__)
        
    def add_points(self, user_id: str, points: float, reason: str = ""):
        """添加积分"""
        try:
            if user_id not in self.points:
                self.points[user_id] = 0
                self.history[user_id] = []
                
            self.points[user_id] += points
            self.history[user_id].append({
                "points": points,
                "reason": reason,
                "timestamp": datetime.now()
            })
            
        except Exception as e:
            self.logger.error(f"添加积分失败: {str(e)}")
            raise
            
    def deduct_points(self, user_id: str, points: float, reason: str = ""):
        """扣除积分"""
        try:
            if user_id not in self.points:
                raise ValueError(f"用户 {user_id} 不存在")
                
            if self.points[user_id] < points:
                raise ValueError(f"用户 {user_id} 积分不足")
                
            self.points[user_id] -= points
            self.history[user_id].append({
                "points": -points,
                "reason": reason,
                "timestamp": datetime.now()
            })
            
        except Exception as e:
            self.logger.error(f"扣除积分失败: {str(e)}")
            raise
            
    def get_points(self, user_id: str) -> float:
        """获取用户积分"""
        try:
            return self.points.get(user_id, 0)
            
        except Exception as e:
            self.logger.error(f"获取积分失败: {str(e)}")
            raise
            
    def get_history(self, user_id: str) -> list:
        """获取用户积分历史"""
        try:
            return self.history.get(user_id, [])
            
        except Exception as e:
            self.logger.error(f"获取积分历史失败: {str(e)}")
            raise 