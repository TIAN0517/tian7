import os
import pyodbc
from dotenv import load_dotenv
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

# 加載環境變量
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        """連接到數據庫"""
        try:
            conn_str = (
                f"DRIVER={{{os.getenv('DB_DRIVER')}}};"
                f"SERVER={os.getenv('DB_SERVER')};"
                f"DATABASE={os.getenv('DB_NAME')};"
                f"UID={os.getenv('DB_USER')};"
                f"PWD={os.getenv('DB_PASSWORD')};"
                "TrustServerCertificate=yes;"
            )
            self.connection = pyodbc.connect(conn_str)
            logging.info("數據庫連接成功")
        except Exception as e:
            logging.error(f"數據庫連接失敗: {str(e)}")
            raise

    def execute_query(self, query, params=None):
        """執行查詢"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor
        except Exception as e:
            logging.error(f"查詢執行失敗: {str(e)}")
            raise

    def execute_non_query(self, query, params=None):
        """執行非查詢操作（如 INSERT, UPDATE, DELETE）"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor.rowcount
        except Exception as e:
            self.connection.rollback()
            logging.error(f"非查詢操作執行失敗: {str(e)}")
            raise

    def get_user_points(self, user_id: int) -> int:
        """獲取用戶積分"""
        cursor = self.execute_query("""
            SELECT Points 
            FROM RanUser.dbo.UserInfo 
            WHERE UserID = ?
        """, (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 0
        
    def update_points(self, user_id: int, amount: int, description: str) -> bool:
        """更新用戶積分"""
        try:
            # 更新用戶積分
            cursor = self.execute_non_query("""
                UPDATE RanUser.dbo.UserInfo 
                SET Points = Points + ? 
                WHERE UserID = ?
            """, (amount, user_id))
            
            # 記錄交易
            self.record_transaction(user_id, amount, "POINTS", description)
            
            return cursor > 0
        except Exception as e:
            self.connection.rollback()
            raise e
            
    def record_transaction(self, user_id: int, amount: int, type: str, description: str) -> None:
        """記錄交易歷史"""
        self.execute_non_query("""
            INSERT INTO RanUser.dbo.PointsTransactionHistory 
            (UserID, Amount, Type, Description, TransactionTime)
            VALUES (?, ?, ?, ?, GETDATE())
        """, (user_id, amount, type, description))
        
    def record_game_history(self, user_id: int, game_type: str, bet_type: str,
                          bet_value: str, bet_amount: int, result: int,
                          win: bool, payout: int) -> None:
        """記錄遊戲歷史"""
        self.execute_non_query("""
            INSERT INTO RanGame.dbo.GameHistory 
            (UserID, GameType, BetType, BetValue, BetAmount, Result, Win, Payout, PlayTime)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
        """, (user_id, game_type, bet_type, bet_value, bet_amount, result, win, payout))
        
    def get_game_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """獲取遊戲歷史"""
        cursor = self.execute_query("""
            SELECT TOP (?) 
                GameType, BetType, BetValue, BetAmount, Result, Win, Payout, PlayTime
            FROM RanGame.dbo.GameHistory
            WHERE UserID = ?
            ORDER BY PlayTime DESC
        """, (limit, user_id))
        
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
        
    def get_transaction_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """獲取交易歷史"""
        cursor = self.execute_query("""
            SELECT TOP (?) 
                Amount, Type, Description, TransactionTime
            FROM RanUser.dbo.PointsTransactionHistory
            WHERE UserID = ?
            ORDER BY TransactionTime DESC
        """, (limit, user_id))
        
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
        
    def close(self):
        """關閉數據庫連接"""
        if self.connection:
            self.connection.close()
            logging.info("數據庫連接已關閉") 