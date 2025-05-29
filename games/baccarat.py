import random
from typing import List, Tuple, Dict
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal
from database.db_manager import DatabaseManager

class BaccaratGame(QObject):
    # 定義信號
    game_result = pyqtSignal(dict)  # 發送遊戲結果
    points_updated = pyqtSignal(int)  # 發送積分更新
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db = db_manager
        self.deck = self._create_deck()
        
    def _create_deck(self) -> List[Tuple[str, int]]:
        """創建一副撲克牌"""
        suits = ['♠', '♥', '♦', '♣']
        values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        deck = []
        for suit in suits:
            for value in values:
                # 計算點數：A=1, 2-9=面值, 10/J/Q/K=0
                points = 1 if value == 'A' else 0 if value in ['10', 'J', 'Q', 'K'] else int(value)
                deck.append((f"{value}{suit}", points))
        return deck
        
    def _shuffle_deck(self):
        """洗牌"""
        random.shuffle(self.deck)
        
    def _draw_card(self) -> Tuple[str, int]:
        """抽一張牌"""
        if not self.deck:
            self.deck = self._create_deck()
            self._shuffle_deck()
        return self.deck.pop()
        
    def _calculate_points(self, cards: List[Tuple[str, int]]) -> int:
        """計算點數"""
        total = sum(card[1] for card in cards)
        return total % 10
        
    def place_bet(self, user_id: int, bet_type: str, bet_amount: int) -> Tuple[bool, str]:
        """下注邏輯"""
        try:
            # 檢查玩家積分
            points = self.db.get_user_points(user_id)
            if points < bet_amount:
                return False, "積分不足"
            
            # 扣除積分
            self.db.update_points(user_id, -bet_amount, "百家樂下注")
            
            # 記錄交易
            self.db.record_transaction(
                user_id=user_id,
                amount=-bet_amount,
                type="BET",
                description=f"百家樂下注 - {bet_type}"
            )
            
            return True, "下注成功"
            
        except Exception as e:
            return False, f"下注失敗: {str(e)}"
            
    def play(self, user_id: int, bet_type: str, bet_amount: int) -> Dict:
        """開始遊戲"""
        try:
            # 洗牌
            self._shuffle_deck()
            
            # 發牌
            player_cards = [self._draw_card() for _ in range(2)]
            banker_cards = [self._draw_card() for _ in range(2)]
            
            # 計算點數
            player_points = self._calculate_points(player_cards)
            banker_points = self._calculate_points(banker_cards)
            
            # 補牌規則
            if player_points <= 5:
                player_cards.append(self._draw_card())
                player_points = self._calculate_points(player_cards)
                
            if banker_points <= 5:
                banker_cards.append(self._draw_card())
                banker_points = self._calculate_points(banker_cards)
            
            # 判定結果
            if player_points > banker_points:
                result = "player"
            elif banker_points > player_points:
                result = "banker"
            else:
                result = "tie"
                
            # 計算賠率
            win = (bet_type == result)
            payout = 0
            if win:
                if result == "tie":
                    payout = bet_amount * 8
                else:
                    payout = bet_amount * 2
                    
            # 更新積分
            if win:
                self.db.update_points(user_id, payout, "百家樂中獎")
                self.db.record_transaction(
                    user_id=user_id,
                    amount=payout,
                    type="WIN",
                    description=f"百家樂中獎 - {bet_type}"
                )
            
            # 記錄遊戲歷史
            self.db.record_game_history(
                user_id=user_id,
                game_type="BACCARAT",
                bet_type=bet_type,
                bet_value=bet_type,
                bet_amount=bet_amount,
                result=result,
                win=win,
                payout=payout
            )
            
            # 發送結果信號
            result_data = {
                "player_cards": [card[0] for card in player_cards],
                "banker_cards": [card[0] for card in banker_cards],
                "player_points": player_points,
                "banker_points": banker_points,
                "result": result,
                "win": win,
                "payout": payout,
                "bet_type": bet_type
            }
            self.game_result.emit(result_data)
            
            # 發送積分更新信號
            current_points = self.db.get_user_points(user_id)
            self.points_updated.emit(current_points)
            
            return result_data
            
        except Exception as e:
            QMessageBox.critical(None, "錯誤", f"遊戲執行失敗: {str(e)}")
            return None
            
    def get_bet_types(self) -> Dict:
        """獲取可用的下注類型"""
        return {
            "player": {
                "name": "閒家",
                "payout": 2
            },
            "banker": {
                "name": "莊家",
                "payout": 2
            },
            "tie": {
                "name": "和局",
                "payout": 8
            }
        } 