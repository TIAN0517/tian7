from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base_class import Base
from app.schemas.roulette import BetType

class RouletteSession(Base):
    __tablename__ = "roulette_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    wheel_type = Column(String(20), default="european")
    status = Column(String(20), default="active")
    config = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="roulette_sessions")
    bets = relationship("RouletteBet", back_populates="session")
    result = relationship("RouletteResult", back_populates="session", uselist=False)

class RouletteBet(Base):
    __tablename__ = "roulette_bets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("roulette_sessions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    bet_type = Column(SQLEnum(BetType), nullable=False)
    amount = Column(Float, nullable=False)
    numbers = Column(JSON, nullable=True)
    status = Column(String(20), default="pending")
    win_amount = Column(Float, default=0)
    placed_at = Column(DateTime, default=datetime.utcnow)
    settled_at = Column(DateTime, nullable=True)

    # Relationships
    session = relationship("RouletteSession", back_populates="bets")
    user = relationship("User", back_populates="roulette_bets")

class RouletteResult(Base):
    __tablename__ = "roulette_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("roulette_sessions.id"), nullable=False)
    result_number = Column(Integer, nullable=False)
    color = Column(String(10), nullable=False)
    total_bet = Column(Float, nullable=False)
    total_win = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    fairness_proof = Column(JSON, nullable=True)  # For provably fair gaming

    # Relationships
    session = relationship("RouletteSession", back_populates="result") 