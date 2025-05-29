import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class RouletteBetType(Enum):
    STRAIGHT = "straight"  # Single number
    RED = "red"
    BLACK = "black"
    EVEN = "even"
    ODD = "odd"
    HIGH = "high"  # 19-36
    LOW = "low"   # 1-18
    DOZEN = "dozen"  # 1-12, 13-24, 25-36
    COLUMN = "column"  # 1-34, 2-35, 3-36

class BaccaratBetType(Enum):
    PLAYER = "player"
    BANKER = "banker"
    TIE = "tie"

class DragonTigerBetType(Enum):
    DRAGON = "dragon"
    TIGER = "tiger"
    TIE = "tie"

@dataclass
class Card:
    suit: str
    value: int
    symbol: str

class GameLogic:
    @staticmethod
    def generate_roulette_number() -> Tuple[int, str]:
        """Generate a random roulette number and its color."""
        number = random.randint(0, 36)
        if number == 0:
            return number, "green"
        elif number in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]:
            return number, "red"
        else:
            return number, "black"

    @staticmethod
    def calculate_roulette_win(bet_type: RouletteBetType, bet_amount: float, 
                             winning_number: int) -> float:
        """Calculate winnings for roulette bets."""
        odds = {
            RouletteBetType.STRAIGHT: 35,
            RouletteBetType.RED: 1,
            RouletteBetType.BLACK: 1,
            RouletteBetType.EVEN: 1,
            RouletteBetType.ODD: 1,
            RouletteBetType.HIGH: 1,
            RouletteBetType.LOW: 1,
            RouletteBetType.DOZEN: 2,
            RouletteBetType.COLUMN: 2
        }
        
        if bet_type == RouletteBetType.STRAIGHT:
            return bet_amount * odds[bet_type] if winning_number == bet_amount else 0
        
        # Implement other bet type calculations
        return 0.0  # Placeholder

    @staticmethod
    def generate_baccarat_cards() -> Tuple[List[Card], List[Card]]:
        """Generate cards for a baccarat game."""
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        deck = [Card(suit, value, str(value)) for suit in suits for value in range(1, 14)]
        random.shuffle(deck)
        
        player_cards = deck[:2]
        banker_cards = deck[2:4]
        
        # Third card rules
        player_score = sum(min(card.value, 10) for card in player_cards) % 10
        banker_score = sum(min(card.value, 10) for card in banker_cards) % 10
        
        if player_score <= 5:
            player_cards.append(deck[4])
        if banker_score <= 5:
            banker_cards.append(deck[5])
            
        return player_cards, banker_cards

    @staticmethod
    def calculate_baccarat_win(bet_type: BaccaratBetType, bet_amount: float,
                             player_cards: List[Card], banker_cards: List[Card]) -> float:
        """Calculate winnings for baccarat bets."""
        player_score = sum(min(card.value, 10) for card in player_cards) % 10
        banker_score = sum(min(card.value, 10) for card in banker_cards) % 10
        
        if player_score > banker_score:
            winner = BaccaratBetType.PLAYER
        elif banker_score > player_score:
            winner = BaccaratBetType.BANKER
        else:
            winner = BaccaratBetType.TIE
            
        if bet_type == winner:
            if bet_type == BaccaratBetType.TIE:
                return bet_amount * 8
            elif bet_type == BaccaratBetType.BANKER:
                return bet_amount * 1.95  # 5% commission
            else:
                return bet_amount * 2
        return 0.0

    @staticmethod
    def generate_dragon_tiger_cards() -> Tuple[Card, Card]:
        """Generate cards for a dragon tiger game."""
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        deck = [Card(suit, value, str(value)) for suit in suits for value in range(1, 14)]
        random.shuffle(deck)
        return deck[0], deck[1]

    @staticmethod
    def calculate_dragon_tiger_win(bet_type: DragonTigerBetType, bet_amount: float,
                                 dragon_card: Card, tiger_card: Card) -> float:
        """Calculate winnings for dragon tiger bets."""
        dragon_value = min(dragon_card.value, 10)
        tiger_value = min(tiger_card.value, 10)
        
        if dragon_value > tiger_value:
            winner = DragonTigerBetType.DRAGON
        elif tiger_value > dragon_value:
            winner = DragonTigerBetType.TIGER
        else:
            winner = DragonTigerBetType.TIE
            
        if bet_type == winner:
            if bet_type == DragonTigerBetType.TIE:
                return bet_amount * 8
            else:
                return bet_amount * 2
        return 0.0

    @staticmethod
    def generate_slot_result(reels: int = 5, symbols_per_reel: int = 3) -> Dict:
        """Generate a slot machine result."""
        symbols = ['7', 'BAR', 'BELL', 'CHERRY', 'LEMON', 'ORANGE', 'PLUM', 'WATERMELON']
        result = {
            'reels': [],
            'paylines': [],
            'total_win': 0.0,
            'bonus_triggered': False,
            'bonus_type': None
        }
        
        # Generate random symbols for each reel
        for _ in range(reels):
            reel_symbols = random.choices(symbols, k=symbols_per_reel)
            result['reels'].append(reel_symbols)
            
        # Check for winning combinations
        # Implement payline checking logic here
        
        return result 