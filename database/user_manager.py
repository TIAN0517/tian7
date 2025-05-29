from typing import Optional, Dict, Any
import bcrypt
from .db_manager import DatabaseManager

class UserManager:
    def __init__(self):
        self.db = DatabaseManager()

    def verify_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """驗證用戶登入"""
        try:
            cursor = self.db.execute_query("""
                SELECT UserID, Username, Password, Points
                FROM RanUser.dbo.UserInfo
                WHERE Username = ?
            """, (username,))
            
            user = cursor.fetchone()
            if user and bcrypt.checkpw(password.encode('utf-8'), user.Password.encode('utf-8')):
                return {
                    'user_id': user.UserID,
                    'username': user.Username,
                    'points': user.Points
                }
            return None
        except Exception as e:
            print(f"驗證用戶時發生錯誤: {str(e)}")
            return None

    def get_user_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """獲取用戶信息"""
        try:
            cursor = self.db.execute_query("""
                SELECT UserID, Username, Points
                FROM RanUser.dbo.UserInfo
                WHERE UserID = ?
            """, (user_id,))
            
            user = cursor.fetchone()
            if user:
                return {
                    'user_id': user.UserID,
                    'username': user.Username,
                    'points': user.Points
                }
            return None
        except Exception as e:
            print(f"獲取用戶信息時發生錯誤: {str(e)}")
            return None

    def update_user_points(self, user_id: int, points: int, description: str) -> bool:
        """更新用戶積分"""
        try:
            return self.db.update_points(user_id, points, description)
        except Exception as e:
            print(f"更新用戶積分時發生錯誤: {str(e)}")
            return False

    def close(self):
        """關閉數據庫連接"""
        self.db.close() 