import pyodbc
import bcrypt
import json
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connect()
    
    def connect(self):
        try:
            # 連接 SQL Server
            self.conn = pyodbc.connect(
                'DRIVER={SQL Server};'
                'SERVER=localhost;'
                'DATABASE=GameLauncher;'
                'Trusted_Connection=yes;'
            )
            self.cursor = self.conn.cursor()
            print("數據庫連接成功")
        except Exception as e:
            print(f"數據庫連接失敗: {e}")
            raise
    
    def close(self):
        if self.conn:
            self.conn.close()
    
    def register_user(self, username, password, email):
        try:
            # 檢查用戶名是否已存在
            self.cursor.execute(
                "SELECT COUNT(*) FROM Users WHERE Username = ?",
                (username,)
            )
            if self.cursor.fetchone()[0] > 0:
                return False, "用戶名已存在"
            
            # 檢查郵箱是否已存在
            self.cursor.execute(
                "SELECT COUNT(*) FROM Users WHERE Email = ?",
                (email,)
            )
            if self.cursor.fetchone()[0] > 0:
                return False, "郵箱已被註冊"
            
            # 密碼加密
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # 插入新用戶
            self.cursor.execute("""
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
            # 獲取用戶信息
            self.cursor.execute(
                "SELECT UserID, Password, Points FROM Users WHERE Username = ?",
                (username,)
            )
            result = self.cursor.fetchone()
            
            if not result:
                return False, "用戶名不存在"
            
            user_id, hashed_password, points = result
            
            # 驗證密碼
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                # 記錄登入歷史
                self.cursor.execute("""
                    INSERT INTO UserLoginHistory (UserID, LoginTime, IPAddress)
                    VALUES (?, ?, ?)
                """, (user_id, datetime.now(), "127.0.0.1"))  # TODO: 獲取實際IP
                
                self.conn.commit()
                return True, {"user_id": user_id, "points": points}
            else:
                return False, "密碼錯誤"
        except Exception as e:
            print(f"登入驗證失敗: {e}")
            return False, f"登入失敗: {str(e)}"
    
    def get_user_points(self, user_id):
        try:
            self.cursor.execute(
                "SELECT Points FROM Users WHERE UserID = ?",
                (user_id,)
            )
            result = self.cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            print(f"獲取用戶積分失敗: {e}")
            return 0
    
    def update_user_points(self, user_id, points_change, description):
        try:
            # 更新用戶積分
            self.cursor.execute("""
                UPDATE Users 
                SET Points = Points + ? 
                WHERE UserID = ?
            """, (points_change, user_id))
            
            # 記錄交易歷史
            self.cursor.execute("""
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
            self.cursor.execute("""
                SELECT vi.ItemName, vi.Description, uvi.Quantity
                FROM UserVirtualItems uvi
                JOIN VirtualItems vi ON uvi.ItemID = vi.ItemID
                WHERE uvi.UserID = ?
            """, (user_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"獲取用戶物品失敗: {e}")
            return []

class UserManager:
    def __init__(self):
        self.conn_str = (
            "DRIVER={SQL Server};"
            "SERVER=localhost;"
            "DATABASE=GameLauncher;"
            "Trusted_Connection=yes;"
        )
        self.credentials_file = "credentials.json"
    
    def connect(self):
        try:
            return pyodbc.connect(self.conn_str)
        except pyodbc.Error as e:
            print(f"Database connection error: {e}")
            return None
    
    def register(self, username, password, email):
        """註冊新用戶"""
        if not self._validate_username(username):
            return False, "用戶名只能包含字母、數字和下劃線"
        
        if not self._validate_password(password):
            return False, "密碼長度必須在6-20個字符之間"
        
        if not self._validate_email(email):
            return False, "請輸入有效的電子郵件地址"
        
        conn = self.connect()
        if not conn:
            return False, "數據庫連接失敗"
        
        try:
            cursor = conn.cursor()
            
            # 檢查用戶名是否已存在
            cursor.execute("SELECT COUNT(*) FROM Users WHERE Username = ?", username)
            if cursor.fetchone()[0] > 0:
                return False, "用戶名已存在"
            
            # 檢查郵箱是否已存在
            cursor.execute("SELECT COUNT(*) FROM Users WHERE Email = ?", email)
            if cursor.fetchone()[0] > 0:
                return False, "郵箱已被註冊"
            
            # 加密密碼
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # 插入新用戶
            cursor.execute("""
                INSERT INTO Users (Username, Password, Email, CreatedAt, Points)
                VALUES (?, ?, ?, ?, ?)
            """, username, hashed_password, email, datetime.now(), 0)
            
            conn.commit()
            return True, "註冊成功"
            
        except pyodbc.Error as e:
            print(f"Registration error: {e}")
            return False, "註冊失敗，請稍後重試"
        finally:
            conn.close()
    
    def login(self, username, password, remember=False):
        """用戶登入"""
        conn = self.connect()
        if not conn:
            return False, "數據庫連接失敗"
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT UserID, Username, Password, Points
                FROM Users
                WHERE Username = ?
            """, username)
            
            user = cursor.fetchone()
            if not user:
                return False, "用戶名或密碼錯誤"
            
            # 驗證密碼
            if not bcrypt.checkpw(password.encode('utf-8'), user.Password.encode('utf-8')):
                return False, "用戶名或密碼錯誤"
            
            # 如果選擇記住我，保存登入信息
            if remember:
                self._save_credentials(username, password)
            
            # 記錄登入歷史
            cursor.execute("""
                INSERT INTO LoginHistory (UserID, LoginTime, IPAddress)
                VALUES (?, ?, ?)
            """, user.UserID, datetime.now(), "127.0.0.1")  # TODO: 獲取實際IP
            
            conn.commit()
            return True, {
                "user_id": user.UserID,
                "username": user.Username,
                "points": user.Points
            }
            
        except pyodbc.Error as e:
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
        conn = self.connect()
        if not conn:
            return False, "數據庫連接失敗"
        
        try:
            cursor = conn.cursor()
            
            # 更新用戶積分
            cursor.execute("""
                UPDATE Users
                SET Points = Points + ?
                WHERE UserID = ?
            """, points_change, user_id)
            
            # 記錄交易歷史
            cursor.execute("""
                INSERT INTO TransactionHistory (UserID, PointsChange, Reason, TransactionTime)
                VALUES (?, ?, ?, ?)
            """, user_id, points_change, reason, datetime.now())
            
            conn.commit()
            return True, "積分更新成功"
            
        except pyodbc.Error as e:
            print(f"Points update error: {e}")
            return False, "積分更新失敗"
        finally:
            conn.close()
    
    def get_transaction_history(self, user_id, limit=10):
        """獲取用戶交易歷史"""
        conn = self.connect()
        if not conn:
            return False, "數據庫連接失敗"
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT TOP (?) TransactionTime, PointsChange, Reason
                FROM TransactionHistory
                WHERE UserID = ?
                ORDER BY TransactionTime DESC
            """, limit, user_id)
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    "time": row.TransactionTime,
                    "points": row.PointsChange,
                    "reason": row.Reason
                })
            
            return True, history
            
        except pyodbc.Error as e:
            print(f"Transaction history error: {e}")
            return False, "獲取交易歷史失敗"
        finally:
            conn.close() 