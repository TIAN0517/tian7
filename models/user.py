from typing import Dict, Optional
import logging

class UserManager:
    """用戶管理器"""
    
    def __init__(self):
        self.users: Dict[str, Dict] = {}
        self.logger = logging.getLogger(__name__)
        
    def create_user(self, username: str, initial_points: float = 0, role: str = "user") -> str:
        """創建新用戶"""
        try:
            user_id = f"user_{len(self.users) + 1}"
            self.users[user_id] = {
                "username": username,
                "points": initial_points,
                "role": role,
                "created_at": "2024-03-20"  # 這裡應該使用實際的時間戳
            }
            return user_id
        except Exception as e:
            self.logger.error(f"創建用戶失敗: {str(e)}")
            raise
            
    def get_points(self, user_id: str) -> float:
        """獲取用戶積分"""
        try:
            return self.users[user_id]["points"]
        except KeyError:
            self.logger.error(f"用戶不存在: {user_id}")
            raise
            
    def update_points(self, user_id: str, points: float) -> float:
        """更新用戶積分"""
        try:
            self.users[user_id]["points"] = points
            return points
        except KeyError:
            self.logger.error(f"用戶不存在: {user_id}")
            raise
            
    def get_role(self, user_id: str) -> str:
        """獲取用戶角色"""
        try:
            return self.users[user_id]["role"]
        except KeyError:
            self.logger.error(f"用戶不存在: {user_id}")
            raise
            
    def get_user_info(self, user_id: str) -> Dict:
        """獲取用戶信息"""
        try:
            return self.users[user_id]
        except KeyError:
            self.logger.error(f"用戶不存在: {user_id}")
            raise 