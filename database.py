import sqlite3
import bcrypt
import json
import os
from datetime import datetime
import logging
from typing import Optional, Dict, Any
import backoff

# 設置日誌
logger = logging.getLogger(__name__)

class DatabaseManager:
    """數據庫連接管理類"""
    def __init__(self):
        self.conn = sqlite3.connect("ranuser.db")
        self.conn.row_factory = sqlite3.Row
    
    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=3,
        max_time=30
    )
    def _connect(self):
        """建立數據庫連接"""
        try:
            self.conn = sqlite3.connect("ranuser.db")
            self.conn.row_factory = sqlite3.Row
            logger.info("數據庫連接成功")
        except Exception as e:
            logger.error(f"數據庫連接失敗: {str(e)}")
            raise
    
    def close(self):
        """關閉數據庫連接"""
        if self.conn:
            self.conn.close()
            logger.info("數據庫連接已關閉")
    
    def register_user(self, username, password, email):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Users WHERE Username = ?", (username,))
            if cursor.fetchone()[0] > 0:
                return False, "用戶名已存在"
            cursor.execute("SELECT COUNT(*) FROM Users WHERE Email = ?", (email,))
            if cursor.fetchone()[0] > 0:
                return False, "郵箱已被註冊"
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("""
                INSERT INTO Users (Username, Password, Email, Points, CreatedAt)
                VALUES (?, ?, ?, ?, ?)
            """, (username, hashed_password, email, 0, datetime.now()))
            self.conn.commit()
            return True, "註冊成功"
        except Exception as e:
            print(f"註冊失敗: {e}")
            return False, f"註冊失敗: {str(e)}"
    
    def verify_user(self, username, password):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT UserID, Password, Points FROM Users WHERE Username = ?", (username,))
            result = cursor.fetchone()
            if not result:
                return False, "用戶名不存在"
            user_id, hashed_password, points = result
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                cursor.execute("""
                    INSERT INTO UserLoginHistory (UserID, LoginTime, IPAddress)
                    VALUES (?, ?, ?)
                """, (user_id, datetime.now(), "127.0.0.1"))
                self.conn.commit()
                return True, {"user_id": user_id, "points": points}
            else:
                return False, "密碼錯誤"
        except Exception as e:
            print(f"登入驗證失敗: {e}")
            return False, f"登入失敗: {str(e)}"
    
    def get_user_points(self, user_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT Points FROM Users WHERE UserID = ?", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            print(f"獲取用戶積分失敗: {e}")
            return 0
    
    def update_user_points(self, user_id, points_change, description):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE Users 
                SET Points = Points + ? 
                WHERE UserID = ?
            """, (points_change, user_id))
            cursor.execute("""
                INSERT INTO PointsTransactionHistory 
                (UserID, PointsChange, Description, TransactionTime)
                VALUES (?, ?, ?, ?)
            """, (user_id, points_change, description, datetime.now()))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"更新用戶積分失敗: {e}")
            return False
    
    def get_user_items(self, user_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT vi.ItemName, vi.Description, uvi.Quantity
                FROM UserVirtualItems uvi
                JOIN VirtualItems vi ON uvi.ItemID = vi.ItemID
                WHERE uvi.UserID = ?
            """, (user_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"獲取用戶物品失敗: {e}")
            return []

    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=3,
        max_time=30
    )
    def execute_query(self, query: str, params: Optional[tuple] = None) -> Any:
        """執行查詢"""
        try:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor
        except Exception as e:
            logger.error(f"執行查詢失敗: {str(e)}")
            raise

class UserManager:
    """用戶管理類"""
    def __init__(self):
        self.db_path = "ranuser.db"
        self.credentials_file = "credentials.json"
    
    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=3,
        max_time=30
    )
    def get_connection(self):
        """獲取數據庫連接"""
        try:
            return sqlite3.connect(self.db_path)
        except Exception as e:
            logger.error(f"獲取數據庫連接失敗: {str(e)}")
            raise
    
    def register(self, username, password, email):
        """註冊新用戶"""
        if not self._validate_username(username):
            return False, "用戶名只能包含字母、數字和下劃線"
        
        if not self._validate_password(password):
            return False, "密碼長度必須在6-20個字符之間"
        
        if not self._validate_email(email):
            return False, "請輸入有效的電子郵件地址"
        
        conn = self.get_connection()
        if not conn:
            return False, "數據庫連接失敗"
        
        try:
            cursor = conn.cursor()
            
            # 檢查用戶名是否已存在
            cursor.execute("SELECT COUNT(*) FROM Users WHERE Username = ?", (username,))
            if cursor.fetchone()[0] > 0:
                return False, "用戶名已存在"
            
            # 檢查郵箱是否已存在
            cursor.execute("SELECT COUNT(*) FROM Users WHERE Email = ?", (email,))
            if cursor.fetchone()[0] > 0:
                return False, "郵箱已被註冊"
            
            # 加密密碼
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # 插入新用戶
            cursor.execute("""
                INSERT INTO Users (Username, Password, Email, CreatedAt, Points)
                VALUES (?, ?, ?, ?, ?)
            """, (username, hashed_password, email, datetime.now(), 0))
            
            conn.commit()
            return True, "註冊成功"
            
        except Exception as e:
            print(f"Registration error: {e}")
            return False, "註冊失敗，請稍後重試"
        finally:
            conn.close()
    
    def login(self, username, password, remember=False):
        """用戶登入"""
        conn = self.get_connection()
        if not conn:
            return False, "數據庫連接失敗"
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT UserID, Username, Password, Points FROM Users WHERE Username = ?", (username,))
            user = cursor.fetchone()
            if not user:
                return False, "用戶名或密碼錯誤"
            
            # 驗證密碼
            if not bcrypt.checkpw(password.encode('utf-8'), user[2]):
                return False, "用戶名或密碼錯誤"
            
            # 如果選擇記住我，保存登入信息
            if remember:
                self._save_credentials(username, password)
            
            # 記錄登入歷史
            cursor.execute("""
                INSERT INTO LoginHistory (UserID, LoginTime, IPAddress)
                VALUES (?, ?, ?)
            """, (user[0], datetime.now(), "127.0.0.1"))  # TODO: 獲取實際IP
            
            conn.commit()
            return True, {
                "user_id": user[0],
                "username": user[1],
                "points": user[3]
            }
            
        except Exception as e:
            print(f"Login error: {e}")
            return False, "登入失敗，請稍後重試"
        finally:
            conn.close()
    
    def _validate_username(self, username):
        """驗證用戶名格式"""
        import re
        return bool(re.match(r'^[a-zA-Z0-9_]{3,20}$', username))
    
    def _validate_password(self, password):
        """驗證密碼格式"""
        return 6 <= len(password) <= 20
    
    def _validate_email(self, email):
        """驗證郵箱格式"""
        import re
        return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))
    
    def _save_credentials(self, username, password):
        """保存登入信息到本地文件"""
        credentials = {
            "username": username,
            "password": password,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            with open(self.credentials_file, 'w') as f:
                json.dump(credentials, f)
        except Exception as e:
            print(f"Error saving credentials: {e}")
    
    def load_credentials(self):
        """從本地文件加載登入信息"""
        if not os.path.exists(self.credentials_file):
            return None
        
        try:
            with open(self.credentials_file, 'r') as f:
                credentials = json.load(f)
                return credentials
        except Exception as e:
            print(f"Error loading credentials: {e}")
            return None
    
    def clear_credentials(self):
        """清除保存的登入信息"""
        if os.path.exists(self.credentials_file):
            try:
                os.remove(self.credentials_file)
            except Exception as e:
                print(f"Error clearing credentials: {e}")
    
    def update_points(self, user_id, points_change, reason):
        """更新用戶積分"""
        conn = self.get_connection()
        if not conn:
            return False, "數據庫連接失敗"
        
        try:
            cursor = conn.cursor()
            
            # 更新用戶積分
            cursor.execute("""
                UPDATE Users
                SET Points = Points + ?
                WHERE UserID = ?
            """, (points_change, user_id))
            
            # 記錄交易歷史
            cursor.execute("""
                INSERT INTO TransactionHistory (UserID, PointsChange, Reason, TransactionTime)
                VALUES (?, ?, ?, ?)
            """, (user_id, points_change, reason, datetime.now()))
            
            conn.commit()
            return True, "積分更新成功"
            
        except Exception as e:
            print(f"Points update error: {e}")
            return False, "積分更新失敗"
        finally:
            conn.close()
    
    def get_transaction_history(self, user_id, limit=10):
        """獲取用戶交易歷史"""
        conn = self.get_connection()
        if not conn:
            return False, "數據庫連接失敗"
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT TransactionTime, PointsChange, Reason
                FROM TransactionHistory
                WHERE UserID = ?
                ORDER BY TransactionTime DESC
                LIMIT ?
            """, (user_id, limit))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    "time": row[0],
                    "points": row[1],
                    "reason": row[2]
                })
            
            return True, history
            
        except Exception as e:
            print(f"Transaction history error: {e}")
            return False, "獲取交易歷史失敗"
        finally:
            conn.close()

# 初始化數據庫管理器
db_manager = DatabaseManager()
user_manager = UserManager()