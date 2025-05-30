import sqlite3
import logging

def init_database():
    """初始化 SQLite 數據庫"""
    try:
        conn = sqlite3.connect("ranuser.db")
        cursor = conn.cursor()
        # 建立必要的表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            UserID INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT UNIQUE NOT NULL,
            Password BLOB NOT NULL,
            Email TEXT UNIQUE NOT NULL,
            Points INTEGER DEFAULT 0,
            CreatedAt TEXT
        )''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS PointsTransactionHistory (
            TransactionID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID INTEGER,
            PointsChange INTEGER,
            Description TEXT,
            TransactionTime TEXT
        )''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS UserLoginHistory (
            LoginID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID INTEGER,
            LoginTime TEXT,
            IPAddress TEXT
        )''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS VirtualItems (
            ItemID INTEGER PRIMARY KEY AUTOINCREMENT,
            ItemName TEXT,
            Description TEXT
        )''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS UserVirtualItems (
            UserID INTEGER,
            ItemID INTEGER,
            Quantity INTEGER,
            PRIMARY KEY (UserID, ItemID)
        )''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS TransactionHistory (
            TransactionID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID INTEGER,
            PointsChange INTEGER,
            Reason TEXT,
            TransactionTime TEXT
        )''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS LoginHistory (
            LoginID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID INTEGER,
            LoginTime TEXT,
            IPAddress TEXT
        )''')
        conn.commit()
        conn.close()
        logging.info("SQLite 數據庫初始化完成")
    except Exception as e:
        logging.error(f"SQLite 數據庫初始化失敗: {e}")
        raise

if __name__ == "__main__":
    init_database() 