import pytest
import jwt
from datetime import datetime, timedelta
from security.bingo_security_validator import BingoSecurityValidator
from database.bingo_db_manager import BingoDatabaseManager

class TestSecurity:
    """安全驗證測試"""
    
    @pytest.fixture
    def security_validator(self):
        """創建安全驗證器實例"""
        return BingoSecurityValidator("test_secret_key")
        
    @pytest.fixture
    def db_manager(self):
        """創建數據庫管理器實例"""
        return BingoDatabaseManager("sqlite:///:memory:")
        
    def test_token_generation(self, security_validator):
        """測試令牌生成"""
        user_id = "test_user"
        token = security_validator.generate_token(user_id)
        
        # 驗證令牌格式
        assert token is not None
        assert isinstance(token, str)
        
        # 驗證令牌內容
        decoded = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
        assert decoded["user_id"] == user_id
        assert "exp" in decoded
        
    def test_token_validation(self, security_validator):
        """測試令牌驗證"""
        user_id = "test_user"
        token = security_validator.generate_token(user_id)
        
        # 驗證有效令牌
        assert security_validator.validate_token(token)
        
        # 驗證無效令牌
        invalid_token = "invalid_token"
        assert not security_validator.validate_token(invalid_token)
        
        # 驗證過期令牌
        expired_token = jwt.encode(
            {
                "user_id": user_id,
                "exp": datetime.utcnow() - timedelta(hours=1)
            },
            "test_secret_key",
            algorithm="HS256"
        )
        assert not security_validator.validate_token(expired_token)
        
    def test_bet_validation(self, security_validator, db_manager):
        """測試下注驗證"""
        user_id = "test_user"
        initial_points = 1000.0
        
        # 設置用戶積分
        db_manager.update_user_points(user_id, initial_points)
        
        # 驗證有效下注
        valid_bet = {
            "user_id": user_id,
            "amount": 100.0,
            "card_count": 2
        }
        assert security_validator.validate_bet(valid_bet, db_manager)
        
        # 驗證無效下注（金額過大）
        invalid_bet = {
            "user_id": user_id,
            "amount": 2000.0,
            "card_count": 2
        }
        assert not security_validator.validate_bet(invalid_bet, db_manager)
        
        # 驗證無效下注（卡片數量過多）
        invalid_bet = {
            "user_id": user_id,
            "amount": 100.0,
            "card_count": 10
        }
        assert not security_validator.validate_bet(invalid_bet, db_manager)
        
    def test_win_validation(self, security_validator):
        """測試獲勝驗證"""
        # 驗證有效獲勝模式
        valid_win = {
            "pattern": "single_line",
            "positions": [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)]
        }
        assert security_validator.validate_win(valid_win)
        
        # 驗證無效獲勝模式（位置不連續）
        invalid_win = {
            "pattern": "single_line",
            "positions": [(0, 0), (0, 2), (0, 3), (0, 4), (0, 5)]
        }
        assert not security_validator.validate_win(invalid_win)
        
        # 驗證無效獲勝模式（位置數量不足）
        invalid_win = {
            "pattern": "single_line",
            "positions": [(0, 0), (0, 1), (0, 2), (0, 3)]
        }
        assert not security_validator.validate_win(invalid_win)
        
    def test_rate_limiting(self, security_validator):
        """測試速率限制"""
        user_id = "test_user"
        
        # 模擬多次請求
        for _ in range(5):
            assert security_validator.check_rate_limit(user_id)
            
        # 驗證超過限制
        assert not security_validator.check_rate_limit(user_id)
        
        # 等待限制重置
        security_validator.reset_rate_limit(user_id)
        assert security_validator.check_rate_limit(user_id)
        
    def test_input_validation(self, security_validator):
        """測試輸入驗證"""
        # 驗證有效輸入
        valid_input = {
            "user_id": "test_user",
            "bet_amount": 100.0,
            "card_count": 2
        }
        assert security_validator.validate_input(valid_input)
        
        # 驗證無效輸入（缺少必要字段）
        invalid_input = {
            "user_id": "test_user",
            "bet_amount": 100.0
        }
        assert not security_validator.validate_input(invalid_input)
        
        # 驗證無效輸入（類型錯誤）
        invalid_input = {
            "user_id": "test_user",
            "bet_amount": "100",
            "card_count": 2
        }
        assert not security_validator.validate_input(invalid_input)
        
    def test_sql_injection_prevention(self, security_validator, db_manager):
        """測試SQL注入防護"""
        # 嘗試SQL注入
        malicious_input = {
            "user_id": "test_user'; DROP TABLE users; --",
            "bet_amount": 100.0,
            "card_count": 2
        }
        
        # 驗證輸入被清理
        cleaned_input = security_validator.sanitize_input(malicious_input)
        assert "DROP TABLE" not in cleaned_input["user_id"]
        
        # 驗證數據庫操作安全
        db_manager.update_user_points(cleaned_input["user_id"], 1000.0)
        points = db_manager.get_user_points(cleaned_input["user_id"])
        assert points == 1000.0
        
    def test_xss_prevention(self, security_validator):
        """測試XSS防護"""
        # 嘗試XSS攻擊
        malicious_input = {
            "user_id": "test_user",
            "message": "<script>alert('XSS')</script>"
        }
        
        # 驗證輸入被清理
        cleaned_input = security_validator.sanitize_input(malicious_input)
        assert "<script>" not in cleaned_input["message"]
        assert "&lt;script&gt;" in cleaned_input["message"]
        
    def test_session_management(self, security_validator):
        """測試會話管理"""
        user_id = "test_user"
        
        # 創建會話
        session_id = security_validator.create_session(user_id)
        assert session_id is not None
        
        # 驗證會話
        assert security_validator.validate_session(session_id, user_id)
        
        # 驗證無效會話
        assert not security_validator.validate_session("invalid_session", user_id)
        
        # 結束會話
        security_validator.end_session(session_id)
        assert not security_validator.validate_session(session_id, user_id) 