"""
百家樂遊戲邏輯模組
實現完整的百家樂遊戲規則和邏輯
"""

import random
from typing import List, Tuple, Dict, Any
from enum import Enum

class BetType(Enum):
    """下注類型"""
    BANKER = "banker"  # 莊家
    PLAYER = "player"  # 閒家
    TIE = "tie"        # 和局

class Card:
    """撲克牌類"""
    SUITS = ["♠", "♥", "♦", "♣"]
    RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    
    def __init__(self, suit: str, rank: str):
        self.suit = suit
        self.rank = rank
    
    def get_value(self) -> int:
        """獲取牌的點數值（百家樂規則）"""
        if self.rank in ["J", "Q", "K"]:
            return 0
        elif self.rank == "A":
            return 1
        elif self.rank == "10":
            return 0
        else:
            return int(self.rank)
    
    def __str__(self) -> str:
        return f"{self.suit}{self.rank}"

class BaccaratGame:
    """百家樂遊戲邏輯類"""
    
    def __init__(self):
        self.deck: List[Card] = []
        self.player_hand: List[Card] = []
        self.banker_hand: List[Card] = []
        self.current_bets: Dict[BetType, float] = {}
        self.player_balance: float = 10000.0  # 初始餘額
        self.game_history: List[Dict] = []
        
    def create_deck(self) -> None:
        """創建一副牌"""
        self.deck = []
        for suit in Card.SUITS:
            for rank in Card.RANKS:
                self.deck.append(Card(suit, rank))
        random.shuffle(self.deck)
    
    def deal_card(self) -> Card:
        """發一張牌"""
        if not self.deck:
            self.create_deck()
        return self.deck.pop()
    
    def calculate_hand_value(self, hand: List[Card]) -> int:
        """計算手牌點數（百家樂規則：取個位數）"""
        total = sum(card.get_value() for card in hand)
        return total % 10
    
    def place_bet(self, bet_type: BetType, amount: float) -> bool:
        """下注"""
        if amount <= 0 or amount > self.player_balance:
            return False
        
        if bet_type in self.current_bets:
            self.current_bets[bet_type] += amount
        else:
            self.current_bets[bet_type] = amount
            
        self.player_balance -= amount
        return True
    
    def clear_bets(self) -> None:
        """清空所有下注"""
        # 退還下注金額
        total_bet = sum(self.current_bets.values())
        self.player_balance += total_bet
        self.current_bets.clear()
    
    def deal_initial_cards(self) -> None:
        """發初始兩張牌"""
        self.player_hand = [self.deal_card(), self.deal_card()]
        self.banker_hand = [self.deal_card(), self.deal_card()]
    
    def should_player_draw(self) -> bool:
        """判斷閒家是否需要補牌"""
        player_value = self.calculate_hand_value(self.player_hand)
        return player_value <= 5
    
    def should_banker_draw(self) -> bool:
        """判斷莊家是否需要補牌（根據複雜的百家樂規則）"""
        banker_value = self.calculate_hand_value(self.banker_hand)
        player_value = self.calculate_hand_value(self.player_hand)
        
        # 如果莊家點數是0-2，必須補牌
        if banker_value <= 2:
            return True
        
        # 如果莊家點數是7-9，不能補牌
        if banker_value >= 7:
            return False
        
        # 如果閒家沒有補牌
        if len(self.player_hand) == 2:
            return banker_value <= 5
        
        # 如果閒家有補牌，根據閒家第三張牌決定
        if len(self.player_hand) == 3:
            player_third_card_value = self.player_hand[2].get_value()
            
            if banker_value == 3:
                return player_third_card_value != 8
            elif banker_value == 4:
                return player_third_card_value in [2, 3, 4, 5, 6, 7]
            elif banker_value == 5:
                return player_third_card_value in [4, 5, 6, 7]
            elif banker_value == 6:
                return player_third_card_value in [6, 7]
        
        return False
    
    def play_round(self) -> Dict[str, Any]:
        """進行一輪遊戲"""
        if not self.current_bets:
            return {"error": "請先下注"}
        
        # 創建新牌組
        self.create_deck()
        
        # 發初始牌
        self.deal_initial_cards()
        
        # 判斷是否需要補牌
        player_initial_value = self.calculate_hand_value(self.player_hand)
        banker_initial_value = self.calculate_hand_value(self.banker_hand)
        
        # 天牌判斷（8或9點）
        is_natural = player_initial_value >= 8 or banker_initial_value >= 8
        
        if not is_natural:
            # 閒家補牌邏輯
            if self.should_player_draw():
                self.player_hand.append(self.deal_card())
            
            # 莊家補牌邏輯
            if self.should_banker_draw():
                self.banker_hand.append(self.deal_card())
        
        # 計算最終點數
        final_player_value = self.calculate_hand_value(self.player_hand)
        final_banker_value = self.calculate_hand_value(self.banker_hand)
        
        # 判斷勝負
        result = self.determine_winner(final_player_value, final_banker_value)
        
        # 計算獎金
        winnings = self.calculate_winnings(result)
        self.player_balance += winnings
        
        # 記錄遊戲歷史
        game_record = {
            "player_cards": [str(card) for card in self.player_hand],
            "banker_cards": [str(card) for card in self.banker_hand],
            "player_value": final_player_value,
            "banker_value": final_banker_value,
            "result": result,
            "bets": self.current_bets.copy(),
            "winnings": winnings,
            "balance": self.player_balance
        }
        self.game_history.append(game_record)
        
        # 清空當前下注
        self.current_bets.clear()
        
        return game_record
    
    def determine_winner(self, player_value: int, banker_value: int) -> str:
        """判斷勝負"""
        if player_value > banker_value:
            return "player"
        elif banker_value > player_value:
            return "banker"
        else:
            return "tie"
    
    def calculate_winnings(self, result: str) -> float:
        """計算獎金"""
        total_winnings = 0.0
        
        for bet_type, bet_amount in self.current_bets.items():
            if bet_type.value == result:
                if bet_type == BetType.PLAYER:
                    # 閒家勝：1:1
                    total_winnings += bet_amount * 2
                elif bet_type == BetType.BANKER:
                    # 莊家勝：1:1 (扣除5%佣金)
                    total_winnings += bet_amount * 1.95
                elif bet_type == BetType.TIE:
                    # 和局：1:8
                    total_winnings += bet_amount * 9
        
        return total_winnings
    
    def get_game_state(self) -> Dict[str, Any]:
        """獲取當前遊戲狀態"""
        return {
            "player_hand": [str(card) for card in self.player_hand],
            "banker_hand": [str(card) for card in self.banker_hand],
            "player_value": self.calculate_hand_value(self.player_hand) if self.player_hand else 0,
            "banker_value": self.calculate_hand_value(self.banker_hand) if self.banker_hand else 0,
            "current_bets": {bet_type.value: amount for bet_type, amount in self.current_bets.items()},
            "player_balance": self.player_balance,
            "total_bet": sum(self.current_bets.values())
        }
    
    def get_betting_odds(self) -> Dict[str, str]:
        """獲取下注賠率"""
        return {
            "player": "1:1",
            "banker": "1:0.95 (扣5%佣金)",
            "tie": "1:8"
        } 