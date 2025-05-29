import random
from typing import List, Dict, Set, Tuple
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal
from database.db_manager import DatabaseManager

class BingoGame(QObject):
    # 定義信號
    game_result = pyqtSignal(dict)  # 發送遊戲結果
    points_updated = pyqtSignal(int)  # 發送積分更新
    number_drawn = pyqtSignal(int)  # 發送抽出的號碼
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db = db_manager
        self.card_size = 5  # 5x5 的賓果卡
        self.max_number = 75  # 1-75的號碼
        self.numbers_per_column = 15  # 每列15個號碼
        
    def generate_card(self) -> List[List[int]]:
        """生成賓果卡"""
        card = []
        for col in range(self.card_size):
            # 計算該列的號碼範圍
            start = col * self.numbers_per_column + 1
            end = start + self.numbers_per_column - 1
            # 從範圍中隨機選擇5個不重複的號碼
            numbers = random.sample(range(start, end + 1), self.card_size)
            card.append(numbers)
        # 轉置矩陣，使每行代表一列
        return list(map(list, zip(*card)))
        
    def place_bet(self, user_id: int, bet_amount: int) -> Tuple[bool, str]:
        """下注邏輯"""
        try:
            # 檢查玩家積分
            points = self.db.get_user_points(user_id)
            if points < bet_amount:
                return False, "積分不足"
            
            # 扣除積分
            self.db.update_points(user_id, -bet_amount, "賓果下注")
            
            # 記錄交易
            self.db.record_transaction(
                user_id=user_id,
                amount=-bet_amount,
                type="BET",
                description="賓果下注"
            )
            
            return True, "下注成功"
            
        except Exception as e:
            return False, f"下注失敗: {str(e)}"
            
    def check_bingo(self, card: List[List[int]], drawn_numbers: Set[int]) -> Tuple[bool, List[List[int]]]:
        """檢查是否賓果"""
        # 創建標記矩陣
        marked = [[num in drawn_numbers for num in row] for row in card]
        
        # 檢查行
        for row in marked:
            if all(row):
                return True, marked
                
        # 檢查列
        for col in range(self.card_size):
            if all(marked[row][col] for row in range(self.card_size)):
                return True, marked
                
        # 檢查對角線
        if all(marked[i][i] for i in range(self.card_size)):
            return True, marked
        if all(marked[i][self.card_size-1-i] for i in range(self.card_size)):
            return True, marked
            
        return False, marked
        
    def play(self, user_id: int, card: List[List[int]], bet_amount: int) -> Dict:
        """開始遊戲"""
        try:
            # 生成要抽取的號碼
            drawn_numbers = set(random.sample(range(1, self.max_number + 1), 30))
            
            # 檢查是否賓果
            bingo, marked = self.check_bingo(card, drawn_numbers)
            
            # 計算賠率
            payout = 0
            if bingo:
                payout = bet_amount * 5  # 5倍賠率
                
            # 更新積分
            if bingo:
                self.db.update_points(user_id, payout, "賓果中獎")
                self.db.record_transaction(
                    user_id=user_id,
                    amount=payout,
                    type="WIN",
                    description="賓果中獎"
                )
            
            # 記錄遊戲歷史
            self.db.record_game_history(
                user_id=user_id,
                game_type="BINGO",
                bet_type="BINGO",
                bet_value=str(card),
                bet_amount=bet_amount,
                result=str(drawn_numbers),
                win=bingo,
                payout=payout
            )
            
            # 發送結果信號
            result_data = {
                "card": card,
                "marked": marked,
                "drawn_numbers": sorted(list(drawn_numbers)),
                "bingo": bingo,
                "payout": payout
            }
            self.game_result.emit(result_data)
            
            # 發送積分更新信號
            current_points = self.db.get_user_points(user_id)
            self.points_updated.emit(current_points)
            
            return result_data
            
        except Exception as e:
            QMessageBox.critical(None, "錯誤", f"遊戲執行失敗: {str(e)}")
            return None 