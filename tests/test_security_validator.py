import pytest
import jwt
import hmac
import hashlib
from datetime import datetime, timedelta
from security.bingo_security_validator import BingoSecurityValidator

class TestSecurityValidator:
    """安全驗證器測試"""
    
    @pytest.fixture
    def validator(self):
        """創建驗證器實例"""
        return BingoSecurityValidator("test_secret_key")
        
    def test_init(self, validator):
        """測試初始化"""
        assert validator.secret_key == "test_secret_key"
        
    def test_generate_token(self, validator):
        """測試生成令牌"""
        user_id = "test_user"
        token = validator.generate_token(user_id)
        
        # 驗證令牌
        decoded = jwt.decode(token, validator.secret_key, algorithms=["HS256"])
        assert decoded["user_id"] == user_id
        assert "exp" in decoded
        
    def test_verify_token_valid(self, validator):
        """測試驗證有效令牌"""
        user_id = "test_user"
        token = validator.generate_token(user_id)
        
        result = validator.verify_token(token)
        assert result is True
        
    def test_verify_token_invalid(self, validator):
        """測試驗證無效令牌"""
        # 使用錯誤的密鑰生成令牌
        invalid_token = jwt.encode(
            {"user_id": "test_user", "exp": datetime.utcnow() + timedelta(hours=1)},
            "wrong_secret_key",
            algorithm="HS256"
        )
        
        result = validator.verify_token(invalid_token)
        assert result is False
        
    def test_verify_token_expired(self, validator):
        """測試驗證過期令牌"""
        # 生成過期令牌
        expired_token = jwt.encode(
            {"user_id": "test_user", "exp": datetime.utcnow() - timedelta(hours=1)},
            validator.secret_key,
            algorithm="HS256"
        )
        
        result = validator.verify_token(expired_token)
        assert result is False
        
    def test_generate_hmac(self, validator):
        """測試生成HMAC"""
        data = "test_data"
        hmac_value = validator.generate_hmac(data)
        
        # 驗證HMAC
        expected_hmac = hmac.new(
            validator.secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        assert hmac_value == expected_hmac
        
    def test_verify_hmac_valid(self, validator):
        """測試驗證有效HMAC"""
        data = "test_data"
        hmac_value = validator.generate_hmac(data)
        
        result = validator.verify_hmac(data, hmac_value)
        assert result is True
        
    def test_verify_hmac_invalid(self, validator):
        """測試驗證無效HMAC"""
        data = "test_data"
        hmac_value = "invalid_hmac"
        
        result = validator.verify_hmac(data, hmac_value)
        assert result is False
        
    def test_encrypt_data(self, validator):
        """測試加密數據"""
        data = "test_data"
        encrypted = validator.encrypt_data(data)
        
        # 驗證加密結果
        assert encrypted != data
        assert isinstance(encrypted, str)
        
    def test_decrypt_data(self, validator):
        """測試解密數據"""
        data = "test_data"
        encrypted = validator.encrypt_data(data)
        
        decrypted = validator.decrypt_data(encrypted)
        assert decrypted == data
        
    def test_validate_bet_amount(self, validator):
        """測試驗證下注金額"""
        # 有效金額
        assert validator.validate_bet_amount(100.0, 1000.0, 10.0, 10000.0) is True
        
        # 金額過小
        assert validator.validate_bet_amount(5.0, 1000.0, 10.0, 10000.0) is False
        
        # 金額過大
        assert validator.validate_bet_amount(20000.0, 1000.0, 10.0, 10000.0) is False
        
        # 積分不足
        assert validator.validate_bet_amount(100.0, 50.0, 10.0, 10000.0) is False
        
    def test_validate_card_count(self, validator):
        """測試驗證卡片數量"""
        # 有效數量
        assert validator.validate_card_count(2, 4) is True
        
        # 數量過大
        assert validator.validate_card_count(5, 4) is False
        
        # 數量為0
        assert validator.validate_card_count(0, 4) is False
        
    def test_validate_game_state(self, validator):
        """測試驗證遊戲狀態"""
        # 有效狀態
        assert validator.validate_game_state(True, 1000.0, 100.0, 2) is True
        
        # 遊戲未運行
        assert validator.validate_game_state(False, 1000.0, 100.0, 2) is False
        
        # 積分不足
        assert validator.validate_game_state(True, 50.0, 100.0, 2) is False
        
        # 下注金額為0
        assert validator.validate_game_state(True, 1000.0, 0.0, 2) is False
        
        # 卡片數量為0
        assert validator.validate_game_state(True, 1000.0, 100.0, 0) is False 