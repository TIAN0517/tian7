import pytest
from database.db_manager import DatabaseManager

def test_db_connection():
    """測試數據庫連接"""
    try:
        db = DatabaseManager()
        # 測試查詢
        cursor = db.execute_query("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1
        db.close()
    except Exception as e:
        pytest.fail(f"數據庫連接測試失敗: {str(e)}")

def test_user_points():
    """測試用戶積分查詢"""
    try:
        db = DatabaseManager()
        # 測試獲取用戶積分
        points = db.get_user_points(1)  # 假設用戶ID為1
        assert isinstance(points, int)
        db.close()
    except Exception as e:
        pytest.fail(f"用戶積分查詢測試失敗: {str(e)}")

def test_transaction():
    """測試交易記錄"""
    try:
        db = DatabaseManager()
        # 測試記錄交易
        db.record_transaction(1, 100, "TEST", "測試交易")
        db.close()
    except Exception as e:
        pytest.fail(f"交易記錄測試失敗: {str(e)}") 