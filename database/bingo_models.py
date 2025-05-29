from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Numeric, JSON, BigInteger
from sqlalchemy.orm import declarative_base
from datetime import datetime
from typing import Dict, List, Optional

Base = declarative_base()

class User(Base):
    """用戶表"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, unique=True)
    points = Column(Float, default=1000.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        """轉換為字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "points": self.points,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class GameHistory(Base):
    """遊戲歷史表"""
    __tablename__ = 'game_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.user_id'))
    bet_amount = Column(Float)
    card_count = Column(Integer)
    drawn_balls = Column(JSON)  # 存儲為 JSON
    winning_patterns = Column(JSON)  # 存儲為 JSON
    payout = Column(Float)
    duration = Column(Integer)  # in seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        """轉換為字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "bet_amount": self.bet_amount,
            "card_count": self.card_count,
            "drawn_balls": self.drawn_balls,
            "winning_patterns": self.winning_patterns,
            "payout": self.payout,
            "duration": self.duration,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Transaction(Base):
    """交易表"""
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.user_id'))
    type = Column(String)  # 'bet' or 'win'
    amount = Column(Float)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        """轉換為字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type,
            "amount": self.amount,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class BingoGameRecord(Base):
    """賓果遊戲記錄表"""
    __tablename__ = 'bingo_game_records'
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(String(50), nullable=False)
    session_id = Column(String(100), nullable=False)
    card_count = Column(Integer, nullable=False)
    bet_amount = Column(Numeric(10, 2), nullable=False)
    total_payout = Column(Numeric(10, 2), default=0)
    cards_data = Column(JSON)  # 卡片數據
    drawn_balls = Column(JSON)  # 抽球序列
    winning_patterns = Column(JSON)  # 中獎模式
    game_duration = Column(Integer)  # 遊戲時長(秒)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        """轉換為字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "card_count": self.card_count,
            "bet_amount": float(self.bet_amount),
            "total_payout": float(self.total_payout),
            "cards_data": self.cards_data,
            "drawn_balls": self.drawn_balls,
            "winning_patterns": self.winning_patterns,
            "game_duration": self.game_duration,
            "created_at": self.created_at.isoformat()
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'BingoGameRecord':
        """從字典創建記錄"""
        return cls(
            user_id=data["user_id"],
            session_id=data["session_id"],
            card_count=data["card_count"],
            bet_amount=data["bet_amount"],
            total_payout=data.get("total_payout", 0),
            cards_data=data["cards_data"],
            drawn_balls=data["drawn_balls"],
            winning_patterns=data["winning_patterns"],
            game_duration=data["game_duration"]
        )

class BingoCardRecord(Base):
    """賓果卡片記錄表"""
    __tablename__ = 'bingo_card_records'
    
    id = Column(BigInteger, primary_key=True)
    game_record_id = Column(BigInteger, ForeignKey('bingo_game_records.id'))
    card_index = Column(Integer, nullable=False)
    card_numbers = Column(JSON)  # 5x5卡片號碼
    marked_positions = Column(JSON)  # 標記位置
    winning_lines = Column(JSON)  # 中獎線
    payout_amount = Column(Numeric(10, 2), default=0)
    
    def to_dict(self) -> Dict:
        """轉換為字典格式"""
        return {
            "id": self.id,
            "game_record_id": self.game_record_id,
            "card_index": self.card_index,
            "card_numbers": self.card_numbers,
            "marked_positions": self.marked_positions,
            "winning_lines": self.winning_lines,
            "payout_amount": float(self.payout_amount)
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'BingoCardRecord':
        """從字典創建記錄"""
        return cls(
            game_record_id=data["game_record_id"],
            card_index=data["card_index"],
            card_numbers=data["card_numbers"],
            marked_positions=data["marked_positions"],
            winning_lines=data["winning_lines"],
            payout_amount=data.get("payout_amount", 0)
        )

class BingoStatistics(Base):
    """賓果遊戲統計表"""
    __tablename__ = 'bingo_statistics'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.user_id'), unique=True)
    total_games = Column(Integer, default=0)
    total_bet = Column(Float, default=0.0)
    total_payout = Column(Float, default=0.0)
    single_line_wins = Column(Integer, default=0)
    double_line_wins = Column(Integer, default=0)
    triple_line_wins = Column(Integer, default=0)
    quad_line_wins = Column(Integer, default=0)
    blackout_wins = Column(Integer, default=0)
    four_corners_wins = Column(Integer, default=0)
    x_pattern_wins = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def update_statistics(self, game_result: Dict) -> None:
        """更新統計數據"""
        self.total_games += 1
        self.total_bet += game_result.get("total_bet", 0.0)
        self.total_payout += game_result.get("total_payout", 0.0)
        
        # 更新獲勝模式統計
        for pattern in game_result.get("winning_patterns", []):
            pattern_type = pattern.get("type", "")
            if pattern_type == "single_line":
                self.single_line_wins += 1
            elif pattern_type == "double_line":
                self.double_line_wins += 1
            elif pattern_type == "triple_line":
                self.triple_line_wins += 1
            elif pattern_type == "quad_line":
                self.quad_line_wins += 1
            elif pattern_type == "blackout":
                self.blackout_wins += 1
            elif pattern_type == "four_corners":
                self.four_corners_wins += 1
            elif pattern_type == "x_pattern":
                self.x_pattern_wins += 1

    def to_dict(self) -> Dict:
        """轉換為字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "total_games": self.total_games,
            "total_bet": float(self.total_bet),
            "total_payout": float(self.total_payout),
            "single_line_wins": self.single_line_wins,
            "double_line_wins": self.double_line_wins,
            "triple_line_wins": self.triple_line_wins,
            "quad_line_wins": self.quad_line_wins,
            "blackout_wins": self.blackout_wins,
            "four_corners_wins": self.four_corners_wins,
            "x_pattern_wins": self.x_pattern_wins,
            "last_updated": self.last_updated.isoformat()
        } 