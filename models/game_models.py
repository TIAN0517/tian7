from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class GameType(enum.Enum):
    ROULETTE = "roulette"
    BACCARAT = "baccarat"
    DRAGON_TIGER = "dragon_tiger"
    SLOT = "slot"

class GameSession(Base):
    __tablename__ = "game_sessions"
    
    id = Column(Integer, primary_key=True)
    game_type = Column(Enum(GameType))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    status = Column(String(20))  # active, completed, cancelled
    total_bet = Column(Float, default=0.0)
    total_win = Column(Float, default=0.0)
    
    # Relationships
    user = relationship("User", back_populates="game_sessions")
    bets = relationship("Bet", back_populates="session")
    results = relationship("GameResult", back_populates="session")

class Bet(Base):
    __tablename__ = "bets"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("game_sessions.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    bet_type = Column(String(50))  # specific to each game
    amount = Column(Float)
    odds = Column(Float)
    status = Column(String(20))  # pending, won, lost
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("GameSession", back_populates="bets")
    user = relationship("User", back_populates="bets")

class GameResult(Base):
    __tablename__ = "game_results"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("game_sessions.id"))
    result_data = Column(JSON)  # Store game-specific result data
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("GameSession", back_populates="results")

# Game-specific models
class RouletteGame(Base):
    __tablename__ = "roulette_games"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("game_sessions.id"))
    wheel_number = Column(Integer)  # 0-36
    color = Column(String(10))  # red, black, green
    is_zero = Column(Boolean, default=False)

class BaccaratGame(Base):
    __tablename__ = "baccarat_games"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("game_sessions.id"))
    player_cards = Column(JSON)
    banker_cards = Column(JSON)
    player_score = Column(Integer)
    banker_score = Column(Integer)
    winner = Column(String(10))  # player, banker, tie

class DragonTigerGame(Base):
    __tablename__ = "dragon_tiger_games"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("game_sessions.id"))
    dragon_card = Column(JSON)
    tiger_card = Column(JSON)
    winner = Column(String(10))  # dragon, tiger, tie

class SlotGame(Base):
    __tablename__ = "slot_games"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("game_sessions.id"))
    reels = Column(JSON)  # Store reel positions and symbols
    paylines = Column(JSON)  # Store winning paylines
    total_win = Column(Float)
    bonus_triggered = Column(Boolean, default=False)
    bonus_type = Column(String(50), nullable=True)  # free_spins, multiplier, etc. 