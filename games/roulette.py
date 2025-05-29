import random
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal
from database.db_manager import DatabaseManager

class RouletteGame(QObject):
    # 定義信號
    game_result = pyqtSignal(dict)  # 發送遊戲結果
    points_updated = pyqtSignal(int)  # 發送積分更新
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db = db_manager
        self.red_numbers = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
        
    def place_bet(self, user_id: int, bet_type: str, bet_value: str, bet_amount: int) -> tuple[bool, str]:
        """下注邏輯"""
        try:
            # 檢查玩家積分
            points = self.db.get_user_points(user_id)
            if points < bet_amount:
                return False, "積分不足"
            
            # 扣除積分
            self.db.update_points(user_id, -bet_amount, "輪盤下注")
            
            # 記錄交易
            self.db.record_transaction(
                user_id=user_id,
                amount=-bet_amount,
                type="BET",
                description=f"輪盤下注 - {bet_type}: {bet_value}"
            )
            
            return True, "下注成功"
            
        except Exception as e:
            return False, f"下注失敗: {str(e)}"
    
    def spin(self, user_id: int, bet_type: str, bet_value: str, bet_amount: int) -> dict:
        """輪盤轉動並計算結果"""
        try:
            # 生成結果
            result = random.randint(0, 36)
            color = "red" if result in self.red_numbers else "black" if result != 0 else "green"
            odd_even = "odd" if result % 2 == 1 else "even" if result != 0 else "none"
            
            # 計算是否中獎
            win = False
            payout = 0
            
            if bet_type == "number" and int(bet_value) == result:
                win = True
                payout = bet_amount * 35
            elif bet_type == "color" and bet_value == color:
                win = True
                payout = bet_amount * 2
            elif bet_type == "odd_even" and bet_value == odd_even:
                win = True
                payout = bet_amount * 2
            
            # 更新積分
            if win:
                self.db.update_points(user_id, payout, "輪盤中獎")
                self.db.record_transaction(
                    user_id=user_id,
                    amount=payout,
                    type="WIN",
                    description=f"輪盤中獎 - {bet_type}: {bet_value}"
                )
            
            # 記錄遊戲歷史
            self.db.record_game_history(
                user_id=user_id,
                game_type="ROULETTE",
                bet_type=bet_type,
                bet_value=bet_value,
                bet_amount=bet_amount,
                result=result,
                win=win,
                payout=payout
            )
            
            # 發送結果信號
            result_data = {
                "result": result,
                "color": color,
                "odd_even": odd_even,
                "win": win,
                "payout": payout,
                "bet_type": bet_type,
                "bet_value": bet_value
            }
            self.game_result.emit(result_data)
            
            # 發送積分更新信號
            current_points = self.db.get_user_points(user_id)
            self.points_updated.emit(current_points)
            
            return result_data
            
        except Exception as e:
            QMessageBox.critical(None, "錯誤", f"遊戲執行失敗: {str(e)}")
            return None
    
    def get_bet_types(self) -> dict:
        """獲取可用的下注類型"""
        return {
            "number": {
                "name": "單個數字",
                "values": list(range(37)),  # 0-36
                "payout": 35
            },
            "color": {
                "name": "顏色",
                "values": ["red", "black"],
                "payout": 2
            },
            "odd_even": {
                "name": "單雙",
                "values": ["odd", "even"],
                "payout": 2
            }
        } 