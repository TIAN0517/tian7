import secrets
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal
from database.db_manager import DatabaseManager
from security.bingo_security_validator import BingoSecurityValidator
import random
import logging
from database.bingo_db_manager import BingoDatabaseManager

class BingoEngine(QObject):
    """賓果遊戲核心引擎 - 處理所有遊戲邏輯"""
    
    # 信號定義
    ball_drawn = pyqtSignal(int)  # 抽球信號
    card_marked = pyqtSignal(int, int, int)  # 卡片標記信號 (card_index, row, col)
    game_result = pyqtSignal(dict)  # 遊戲結果信號
    points_updated = pyqtSignal(float)  # 積分更新信號
    
    # 賠率表
    PAYOUT_TABLE = {
        "single_line": 5,      # 單線中獎概率: ~15%
        "double_line": 15,     # 雙線中獎概率: ~4%
        "triple_line": 50,     # 三線中獎概率: ~1.2%
        "quad_line": 150,      # 四線中獎概率: ~0.3%
        "blackout": 500,       # 滿卡中獎概率: ~0.08%
        "four_corners": 25,    # 四角中獎概率: ~2%
        "x_pattern": 75        # X型中獎概率: ~0.8%
    }
    
    # 房間抽成率
    HOUSE_EDGE = 0.05  # 5% 抽水
    
    def __init__(self, db_manager: BingoDatabaseManager, validator: BingoSecurityValidator):
        super().__init__()
        self.db_manager = db_manager
        self.validator = validator
        self.drawn_balls = []
        self.remaining_balls = list(range(1, 76))
        self.logger = logging.getLogger(__name__)
        self.rng = secrets.SystemRandom()
        
        # 遊戲狀態
        self.is_game_running = False
        self.current_user_id = None
        self.current_points = 0
        self.bet_amount = 0
        self.card_count = 0
        self.cards = []  # 卡片列表
        self.start_time = None
        
    def generate_valid_card(self) -> List[List]:
        """生成有效的賓果卡片"""
        card = []
        ranges = [
            (1, 15),   # B列
            (16, 30),  # I列
            (31, 45),  # N列
            (46, 60),  # G列
            (61, 75)   # O列
        ]
        
        for min_val, max_val in ranges:
            column = random.sample(range(min_val, max_val + 1), 5)
            card.append(column)
            
        # 轉置矩陣並設置FREE空間
        card = list(map(list, zip(*card)))
        card[2][2] = 'FREE'
        
        return card
        
    def validate_card_uniqueness(self, card: List[List[int]]) -> bool:
        """驗證卡片號碼唯一性"""
        numbers = set()
        for row in card:
            for num in row:
                if num != 'FREE' and num in numbers:
                    return False
                numbers.add(num)
        return True
        
    def draw_ball_sequence(self, target_balls: int = 25) -> List[int]:
        """抽球序列生成 (無重複，加權隨機)"""
        if not self.remaining_balls:
            self.remaining_balls = list(range(1, 76))
            
        drawn_balls = []
        for _ in range(target_balls):
            if not self.remaining_balls:
                break
            ball = secrets.SystemRandom().choice(self.remaining_balls)
            self.remaining_balls.remove(ball)
            drawn_balls.append(ball)
            self.ball_drawn.emit(ball)
            
        return drawn_balls
        
    def check_winning_patterns(self, card: List[List]) -> List[Dict]:
        """檢查獲勝模式"""
        patterns = []
        
        # 檢查行
        for row in range(5):
            if all(card[row][col] == 'FREE' or card[row][col] in self.drawn_balls 
                  for col in range(5)):
                patterns.append({
                    'type': 'single_line',
                    'positions': [(row, col) for col in range(5)],
                    'multiplier': 5
                })
                
        # 檢查列
        for col in range(5):
            if all(card[row][col] == 'FREE' or card[row][col] in self.drawn_balls 
                  for row in range(5)):
                patterns.append({
                    'type': 'single_line',
                    'positions': [(row, col) for row in range(5)],
                    'multiplier': 5
                })
                
        # 檢查對角線
        if all(card[i][i] == 'FREE' or card[i][i] in self.drawn_balls 
              for i in range(5)):
            patterns.append({
                'type': 'single_line',
                'positions': [(i, i) for i in range(5)],
                'multiplier': 5
            })
            
        if all(card[i][4-i] == 'FREE' or card[i][4-i] in self.drawn_balls 
              for i in range(5)):
            patterns.append({
                'type': 'single_line',
                'positions': [(i, 4-i) for i in range(5)],
                'multiplier': 5
            })
            
        # 檢查四角
        corners = [(0, 0), (0, 4), (4, 0), (4, 4)]
        if all(card[r][c] == 'FREE' or card[r][c] in self.drawn_balls 
              for r, c in corners):
            patterns.append({
                'type': 'four_corners',
                'positions': corners,
                'multiplier': 25
            })
            
        return patterns
        
    def calculate_payout(self, winning_patterns: List[Dict], bet_amount: float) -> float:
        """計算獎金"""
        total_multiplier = sum(p.get('multiplier', 0) for p in winning_patterns)
        return bet_amount * total_multiplier * (1 - self.HOUSE_EDGE)
        
    def execute_game_round(self, user_id: str, bet_amount: float, card_count: int) -> Dict[str, Any]:
        """執行一輪遊戲"""
        # 驗證下注
        bet_data = {
            'user_id': user_id,
            'amount': bet_amount,
            'card_count': card_count
        }
        
        if not self.validator.validate_bet(bet_data, self.db_manager):
            raise ValueError("Invalid bet")
            
        # 生成卡片
        cards = [self.generate_valid_card() for _ in range(card_count)]
        
        # 抽取球直到有人獲勝
        winning_patterns = []
        while len(self.drawn_balls) < 75 and not winning_patterns:
            ball = self.draw_ball()
            if ball is None:
                break
                
            # 檢查每張卡片是否有獲勝模式
            for card in cards:
                patterns = self.check_winning_patterns(card)
                if patterns:
                    winning_patterns.extend(patterns)
                    
        # 計算獎金
        total_bet = bet_amount * card_count
        total_payout = self.calculate_payout(winning_patterns, total_bet)
        
        # 更新用戶積分
        current_points = self.db_manager.get_user_points(user_id)
        new_points = current_points - total_bet + total_payout
        self.db_manager.update_user_points(user_id, new_points)
        
        # 記錄遊戲結果
        game_data = {
            'user_id': user_id,
            'bet_amount': bet_amount,
            'card_count': card_count,
            'drawn_balls': self.drawn_balls,
            'winning_patterns': winning_patterns,
            'payout': total_payout,
            'duration': len(self.drawn_balls)
        }
        self.db_manager.record_game_history(game_data)
        
        return {
            'user_id': user_id,
            'total_bet': total_bet,
            'total_payout': total_payout,
            'cards_data': cards,
            'drawn_balls': self.drawn_balls,
            'winning_patterns': winning_patterns,
            'game_duration': len(self.drawn_balls),
            'final_points': new_points
        }
        
    def start_game(self, user_id: str, points: float, bet_amount: float, card_count: int) -> bool:
        """開始遊戲
        
        Args:
            user_id: 用戶ID
            points: 當前積分
            bet_amount: 下注金額
            card_count: 卡片數量
            
        Returns:
            bool: 是否成功開始遊戲
        """
        if self.is_game_running:
            self.logger.warning("遊戲正在進行中")
            return False
            
        if points < bet_amount * card_count:
            self.logger.warning("積分不足")
            return False
            
        self.current_user_id = user_id
        self.current_points = points
        self.bet_amount = bet_amount
        self.card_count = card_count
        self.cards = []
        self.drawn_balls = []
        self.remaining_balls = list(range(1, 76))
        self.start_time = datetime.now()
        
        # 生成卡片
        for _ in range(card_count):
            card = self.generate_valid_card()
            self.cards.append(card)
            
        self.is_game_running = True
        return True
        
    def draw_ball(self) -> Optional[int]:
        """抽取一個球"""
        if not self.remaining_balls:
            return None
            
        ball = secrets.SystemRandom().choice(self.remaining_balls)
        self.remaining_balls.remove(ball)
        self.drawn_balls.append(ball)
        
        # 檢查所有卡片
        for card_index, card in enumerate(self.cards):
            for row in range(5):
                for col in range(5):
                    if card[row][col] == ball:
                        self.card_marked.emit(card_index, row, col)
                        
        self.ball_drawn.emit(ball)
        return ball
        
    def end_game(self) -> Dict:
        """結束遊戲並計算結果
        
        Returns:
            Dict: 遊戲結果數據
        """
        if not self.is_game_running:
            return None
            
        self.is_game_running = False
        game_duration = (datetime.now() - self.start_time).total_seconds()
        
        # 計算獎金
        total_payout = 0
        winning_patterns = []
        
        for card_index, card in enumerate(self.cards):
            card_patterns = self.check_winning_patterns(card)
            card_payout = self.calculate_payout(card_patterns, self.bet_amount)
            
            winning_patterns.append({
                "card_index": card_index,
                "patterns": card_patterns,
                "payout": card_payout
            })
            
            total_payout += card_payout
            
        # 更新積分
        self.current_points = self.current_points - (self.bet_amount * self.card_count) + total_payout
        self.points_updated.emit(self.current_points)
        
        # 生成結果數據
        result = {
            "user_id": self.current_user_id,
            "total_bet": self.bet_amount * self.card_count,
            "total_payout": total_payout,
            "cards_data": self.cards,
            "drawn_balls": self.drawn_balls,
            "winning_patterns": winning_patterns,
            "game_duration": game_duration,
            "final_points": self.current_points
        }
        
        self.game_result.emit(result)
        return result 