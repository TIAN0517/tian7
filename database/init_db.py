import os
import pyodbc
from dotenv import load_dotenv
import logging

# 加載環境變量
load_dotenv()

def init_database():
    """初始化數據庫"""
    try:
        # 連接數據庫
        conn_str = (
            f"DRIVER={{{os.getenv('DB_DRIVER')}}};"
            f"SERVER={os.getenv('DB_SERVER')};"
            f"DATABASE={os.getenv('DB_NAME')};"
            f"UID={os.getenv('DB_USER')};"
            f"PWD={os.getenv('DB_PASSWORD')};"
            "TrustServerCertificate=yes;"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # 創建用戶表
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'UserInfo')
        BEGIN
            CREATE TABLE UserInfo (
                UserID INT PRIMARY KEY IDENTITY(1,1),
                Username NVARCHAR(50) NOT NULL,
                Password NVARCHAR(100) NOT NULL,
                Points INT DEFAULT 0,
                CreatedAt DATETIME DEFAULT GETDATE(),
                LastLoginAt DATETIME
            )
        END
        """)

        # 創建交易歷史表
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'PointsTransactionHistory')
        BEGIN
            CREATE TABLE PointsTransactionHistory (
                TransactionID INT PRIMARY KEY IDENTITY(1,1),
                UserID INT NOT NULL,
                Amount INT NOT NULL,
                Type NVARCHAR(20) NOT NULL,
                Description NVARCHAR(200),
                TransactionTime DATETIME DEFAULT GETDATE(),
                FOREIGN KEY (UserID) REFERENCES UserInfo(UserID)
            )
        END
        """)

        # 創建遊戲歷史表
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'GameHistory')
        BEGIN
            CREATE TABLE GameHistory (
                GameID INT PRIMARY KEY IDENTITY(1,1),
                UserID INT NOT NULL,
                GameType NVARCHAR(20) NOT NULL,
                BetType NVARCHAR(20) NOT NULL,
                BetValue NVARCHAR(50) NOT NULL,
                BetAmount INT NOT NULL,
                Result NVARCHAR(50) NOT NULL,
                Win BIT NOT NULL,
                Payout INT NOT NULL,
                PlayTime DATETIME DEFAULT GETDATE(),
                FOREIGN KEY (UserID) REFERENCES UserInfo(UserID)
            )
        END
        """)

        conn.commit()
        logging.info("數據庫初始化成功")
    except Exception as e:
        logging.error(f"數據庫初始化失敗: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    init_database() 