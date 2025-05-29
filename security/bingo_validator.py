import hmac
import hashlib
import json
import time
from typing import Dict, Optional
import logging
from datetime import datetime

class BingoSecurityValidator:
    """賓果遊戲安全驗證器"""
    
    def __init__(self, secret_key: str):
        """初始化驗證器
        
        Args:
            secret_key: 密鑰
        """
        self.secret_key = secret_key.encode()
        self.logger = logging.getLogger(__name__)
        
    def generate_hmac(self, data: Dict) -> str:
        """生成HMAC簽名
        
        Args:
            data: 要簽名的數據
            
        Returns:
            str: HMAC簽名
        """
        # 將數據轉換為JSON字符串
        data_str = json.dumps(data, sort_keys=True)
        
        # 生成HMAC
        hmac_obj = hmac.new(
            self.secret_key,
            data_str.encode(),
            hashlib.sha256
        )
        
        return hmac_obj.hexdigest()
        
    def verify_hmac(self, data: Dict, signature: str) -> bool:
        """驗證HMAC簽名
        
        Args:
            data: 原始數據
            signature: 簽名
            
        Returns:
            bool: 驗證是否通過
        """
        expected_signature = self.generate_hmac(data)
        return hmac.compare_digest(signature, expected_signature)
        
    def validate_game_start(self, user_id: str, bet_amount: float, 
                          card_count: int, timestamp: int) -> bool:
        """驗證遊戲開始請求
        
        Args:
            user_id: 用戶ID
            bet_amount: 下注金額
            card_count: 卡片數量
            timestamp: 時間戳
            
        Returns:
            bool: 驗證是否通過
        """
        # 檢查時間戳是否在合理範圍內
        current_time = int(time.time())
        if abs(current_time - timestamp) > 300:  # 5分鐘
            self.logger.warning(f"時間戳驗證失敗: {timestamp}")
            return False
            
        # 檢查下注金額是否合法
        if bet_amount <= 0 or bet_amount > 10000:
            self.logger.warning(f"下注金額不合法: {bet_amount}")
            return False
            
        # 檢查卡片數量是否合法
        if card_count <= 0 or card_count > 4:
            self.logger.warning(f"卡片數量不合法: {card_count}")
            return False
            
        return True
        
    def validate_game_result(self, result: Dict) -> bool:
        """驗證遊戲結果
        
        Args:
            result: 遊戲結果數據
            
        Returns:
            bool: 驗證是否通過
        """
        required_fields = [
            "user_id", "total_bet", "total_payout",
            "cards_data", "drawn_balls", "winning_patterns",
            "game_duration", "final_points"
        ]
        
        # 檢查必要字段
        for field in required_fields:
            if field not in result:
                self.logger.warning(f"缺少必要字段: {field}")
                return False
                
        # 檢查數據類型
        if not isinstance(result["total_bet"], (int, float)):
            self.logger.warning("下注金額類型錯誤")
            return False
            
        if not isinstance(result["total_payout"], (int, float)):
            self.logger.warning("獎金類型錯誤")
            return False
            
        if not isinstance(result["cards_data"], list):
            self.logger.warning("卡片數據類型錯誤")
            return False
            
        if not isinstance(result["drawn_balls"], list):
            self.logger.warning("抽球數據類型錯誤")
            return False
            
        if not isinstance(result["winning_patterns"], list):
            self.logger.warning("中獎模式數據類型錯誤")
            return False
            
        # 檢查卡片數據
        for card in result["cards_data"]:
            if not isinstance(card, list) or len(card) != 5:
                self.logger.warning("卡片數據格式錯誤")
                return False
                
            for row in card:
                if not isinstance(row, list) or len(row) != 5:
                    self.logger.warning("卡片行數據格式錯誤")
                    return False
                    
                for cell in row:
                    if not isinstance(cell, int):
                        self.logger.warning("卡片單元格數據類型錯誤")
                        return False
                        
        # 檢查抽球數據
        for ball in result["drawn_balls"]:
            if not isinstance(ball, int) or ball < 1 or ball > 75:
                self.logger.warning("抽球數據錯誤")
                return False
                
        # 檢查中獎模式數據
        for pattern in result["winning_patterns"]:
            if not isinstance(pattern, dict):
                self.logger.warning("中獎模式數據格式錯誤")
                return False
                
            if "card_index" not in pattern or "patterns" not in pattern:
                self.logger.warning("中獎模式數據缺少必要字段")
                return False
                
            if not isinstance(pattern["card_index"], int):
                self.logger.warning("卡片索引類型錯誤")
                return False
                
            if not isinstance(pattern["patterns"], list):
                self.logger.warning("中獎模式列表類型錯誤")
                return False
                
        return True
        
    def validate_points_update(self, user_id: str, old_points: float,
                             new_points: float, reason: str) -> bool:
        """驗證積分更新
        
        Args:
            user_id: 用戶ID
            old_points: 原積分
            new_points: 新積分
            reason: 更新原因
            
        Returns:
            bool: 驗證是否通過
        """
        # 檢查積分是否為負數
        if new_points < 0:
            self.logger.warning(f"積分不能為負數: {new_points}")
            return False
            
        # 檢查積分變動是否合理
        if abs(new_points - old_points) > 1000000:
            self.logger.warning(f"積分變動過大: {old_points} -> {new_points}")
            return False
            
        # 檢查更新原因
        valid_reasons = ["game_bet", "game_win", "admin_adjust"]
        if reason not in valid_reasons:
            self.logger.warning(f"無效的更新原因: {reason}")
            return False
            
        return True
        
    def validate_card_generation(self, card: list) -> bool:
        """驗證卡片生成
        
        Args:
            card: 卡片數據
            
        Returns:
            bool: 驗證是否通過
        """
        if not isinstance(card, list) or len(card) != 5:
            return False
            
        # 檢查每列數字範圍
        ranges = [
            (1, 15),   # B列
            (16, 30),  # I列
            (31, 45),  # N列
            (46, 60),  # G列
            (61, 75)   # O列
        ]
        
        for col, (min_val, max_val) in enumerate(ranges):
            if not isinstance(card[col], list) or len(card[col]) != 5:
                return False
                
            # 檢查數字範圍
            for num in card[col]:
                if not isinstance(num, int):
                    return False
                if num != 0 and (num < min_val or num > max_val):
                    return False
                    
        # 檢查FREE空間
        if card[2][2] != 0:
            return False
            
        return True 