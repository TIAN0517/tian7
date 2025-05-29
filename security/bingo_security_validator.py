import jwt
import hmac
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
from cryptography.fernet import Fernet
import re

logger = logging.getLogger(__name__)

class BingoSecurityValidator:
    """賓果遊戲安全驗證器"""
    
    def __init__(self, secret_key: str):
        """初始化安全驗證器"""
        self.secret_key = secret_key
        self.fernet = Fernet(base64.urlsafe_b64encode(hashlib.sha256(secret_key.encode()).digest()))
        self.rate_limits = {}
        self.sessions = {}
        
    def generate_token(self, user_id: str) -> str:
        """生成JWT令牌"""
        try:
            payload = {
                "user_id": user_id,
                "exp": datetime.utcnow() + timedelta(hours=1)
            }
            return jwt.encode(payload, self.secret_key, algorithm="HS256")
        except Exception as e:
            logger.error(f"生成令牌失敗: {str(e)}")
            return ""
            
    def verify_token(self, token: str) -> Optional[Dict]:
        """驗證JWT令牌"""
        try:
            return jwt.decode(token, self.secret_key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            logger.error("令牌已過期")
            return None
        except jwt.InvalidTokenError as e:
            logger.error(f"無效的令牌: {str(e)}")
            return None
            
    def generate_hmac(self, data: str) -> str:
        """生成HMAC"""
        try:
            return hmac.new(
                self.secret_key.encode(),
                data.encode(),
                hashlib.sha256
            ).hexdigest()
        except Exception as e:
            logger.error(f"生成HMAC失敗: {str(e)}")
            return ""
            
    def verify_hmac(self, data: str, hmac_value: str) -> bool:
        """驗證HMAC"""
        try:
            expected_hmac = self.generate_hmac(data)
            return hmac.compare_digest(expected_hmac, hmac_value)
        except Exception as e:
            logger.error(f"驗證HMAC失敗: {str(e)}")
            return False
            
    def encrypt_data(self, data: str) -> str:
        """加密數據"""
        try:
            return self.fernet.encrypt(data.encode()).decode()
        except Exception as e:
            logger.error(f"加密數據失敗: {str(e)}")
            return ""
            
    def decrypt_data(self, encrypted_data: str) -> str:
        """解密數據"""
        try:
            return self.fernet.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            logger.error(f"解密數據失敗: {str(e)}")
            return ""
            
    def validate_bet_amount(self, bet_amount: float, user_points: float, 
                          min_bet: float, max_bet: float) -> bool:
        """驗證下注金額"""
        try:
            if not isinstance(bet_amount, (int, float)) or bet_amount <= 0:
                return False
            if bet_amount < min_bet or bet_amount > max_bet:
                return False
            if bet_amount > user_points:
                return False
            return True
        except Exception as e:
            logger.error(f"驗證下注金額失敗: {str(e)}")
            return False
            
    def validate_card_count(self, card_count: int, max_cards: int) -> bool:
        """驗證卡片數量"""
        try:
            if not isinstance(card_count, int) or card_count <= 0:
                return False
            if card_count > max_cards:
                return False
            return True
        except Exception as e:
            logger.error(f"驗證卡片數量失敗: {str(e)}")
            return False
            
    def validate_game_state(self, is_game_running: bool, user_points: float,
                          bet_amount: float, card_count: int) -> bool:
        """驗證遊戲狀態"""
        try:
            if not isinstance(is_game_running, bool):
                return False
            if not isinstance(user_points, (int, float)) or user_points < 0:
                return False
            if not isinstance(bet_amount, (int, float)) or bet_amount <= 0:
                return False
            if not isinstance(card_count, int) or card_count <= 0:
                return False
            return True
        except Exception as e:
            logger.error(f"驗證遊戲狀態失敗: {str(e)}")
            return False
            
    def validate_win(self, win_data: Dict) -> bool:
        """驗證獲勝模式"""
        try:
            if not isinstance(win_data, dict):
                return False
                
            pattern = win_data.get("pattern")
            positions = win_data.get("positions", [])
            
            if not pattern or not positions:
                return False
                
            # 驗證位置是否連續
            if pattern == "single_line":
                # 檢查是否在同一行或同一列
                rows = [pos[0] for pos in positions]
                cols = [pos[1] for pos in positions]
                return len(set(rows)) == 1 or len(set(cols)) == 1
                
            elif pattern == "double_line":
                # 檢查是否有兩條連續線
                return len(positions) >= 8  # 至少需要8個點形成兩條線
                
            elif pattern == "triple_line":
                # 檢查是否有三條連續線
                return len(positions) >= 12  # 至少需要12個點形成三條線
                
            elif pattern == "quad_line":
                # 檢查是否有四條連續線
                return len(positions) >= 16  # 至少需要16個點形成四條線
                
            elif pattern == "blackout":
                # 檢查是否填滿整個卡片
                return len(positions) == 25  # 5x5卡片需要25個點
                
            elif pattern == "four_corners":
                # 檢查四個角落
                corners = [(0, 0), (0, 4), (4, 0), (4, 4)]
                return all(corner in positions for corner in corners)
                
            elif pattern == "x_pattern":
                # 檢查X形狀
                x_positions = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4),
                             (0, 4), (1, 3), (3, 1), (4, 0)]
                return all(pos in positions for pos in x_positions)
                
            return False
            
        except Exception as e:
            logger.error(f"驗證獲勝模式失敗: {str(e)}")
            return False
            
    def sanitize_input(self, data: Dict) -> Dict:
        """清理輸入數據"""
        try:
            sanitized = {}
            for key, value in data.items():
                if isinstance(value, str):
                    # 移除SQL注入相關字符
                    value = re.sub(r'[\'";]', '', value)
                    # 移除危險字符
                    value = re.sub(r'[<>{}[\]\\]', '', value)
                sanitized[key] = value
            return sanitized
        except Exception as e:
            logger.error(f"清理輸入數據失敗: {str(e)}")
            return {}
        
    def validate_bet(self, bet_data: Dict[str, Any], db_manager) -> bool:
        """Validate bet amount and card count
        
        Args:
            bet_data: Dictionary containing bet information
                - user_id: User ID
                - amount: Bet amount
                - card_count: Number of cards
            db_manager: Database manager instance
            
        Returns:
            bool: True if bet is valid, False otherwise
        """
        try:
            user_id = bet_data['user_id']
            amount = float(bet_data['amount'])
            card_count = int(bet_data['card_count'])
            
            # Get user's current points
            current_points = db_manager.get_user_points(user_id)
            
            # Check if user has enough points
            total_bet = amount * card_count
            if total_bet > current_points:
                return False
            
            # Validate bet amount
            if amount <= 0 or amount > 1000:  # Max bet 1000
                return False
            
            # Validate card count
            if card_count <= 0 or card_count > 4:  # Max 4 cards
                return False
            
            return True
        
        except (KeyError, ValueError, TypeError):
            return False
        
    def check_rate_limit(self, user_id: str) -> bool:
        """檢查速率限制"""
        current_time = time.time()
        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = []
            
        # 清理過期的請求記錄
        self.rate_limits[user_id] = [
            t for t in self.rate_limits[user_id]
            if current_time - t < 60  # 60秒內的請求
        ]
        
        # 檢查是否超過限制（每分鐘最多5次請求）
        if len(self.rate_limits[user_id]) >= 5:
            return False
            
        self.rate_limits[user_id].append(current_time)
        return True
        
    def reset_rate_limit(self, user_id: str):
        """重置速率限制"""
        if user_id in self.rate_limits:
            del self.rate_limits[user_id]
            
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """驗證輸入數據"""
        required_fields = ['user_id', 'bet_amount', 'card_count']
        
        # 檢查必要字段
        if not all(field in data for field in required_fields):
            return False
            
        # 檢查數據類型
        if not isinstance(data['bet_amount'], (int, float)):
            return False
        if not isinstance(data['card_count'], int):
            return False
            
        return True
        
    def create_session(self, user_id: str) -> str:
        """創建會話"""
        session_id = jwt.encode(
            {
                'user_id': user_id,
                'exp': datetime.utcnow() + timedelta(hours=1)
            },
            self.secret_key,
            algorithm='HS256'
        )
        self.sessions[session_id] = user_id
        return session_id
        
    def validate_session(self, session_id: str, user_id: str) -> bool:
        """驗證會話"""
        if session_id not in self.sessions:
            return False
        return self.sessions[session_id] == user_id
        
    def end_session(self, session_id: str):
        """結束會話"""
        if session_id in self.sessions:
            del self.sessions[session_id] 