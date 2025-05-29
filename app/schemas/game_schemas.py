from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class GameType(str, Enum):
    ROULETTE = "roulette"
    BACCARAT = "baccarat"
    DRAGON_TIGER = "dragon_tiger"
    SLOT = "slot"

class GameSessionBase(BaseModel):
    game_type: GameType
    user_id: int
    status: str = "active"
    total_bet: float = 0.0
    total_win: float = 0.0

class GameSessionCreate(GameSessionBase):
    pass

class GameSessionResponse(GameSessionBase):
    id: int
    created_at: datetime
    ended_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class BetBase(BaseModel):
    session_id: int
    user_id: int
    bet_type: str
    amount: float
    odds: float
    status: str = "pending"

class BetCreate(BetBase):
    pass

class BetResponse(BetBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class GameResultBase(BaseModel):
    session_id: int
    result_data: Dict

class GameResultCreate(GameResultBase):
    pass

class GameResultResponse(GameResultBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Game-specific schemas
class RouletteBetType(str, Enum):
    STRAIGHT = "straight"
    RED = "red"
    BLACK = "black"
    EVEN = "even"
    ODD = "odd"
    HIGH = "high"
    LOW = "low"
    DOZEN = "dozen"
    COLUMN = "column"

class RouletteBet(BaseModel):
    bet_type: RouletteBetType
    amount: float = Field(gt=0)
    odds: float = Field(gt=0)

class BaccaratBetType(str, Enum):
    PLAYER = "player"
    BANKER = "banker"
    TIE = "tie"

class BaccaratBet(BaseModel):
    bet_type: BaccaratBetType
    amount: float = Field(gt=0)
    odds: float = Field(gt=0)

class DragonTigerBetType(str, Enum):
    DRAGON = "dragon"
    TIGER = "tiger"
    TIE = "tie"

class DragonTigerBet(BaseModel):
    bet_type: DragonTigerBetType
    amount: float = Field(gt=0)
    odds: float = Field(gt=0)

class SlotBet(BaseModel):
    amount: float = Field(gt=0)
    lines: int = Field(ge=1, le=50)
    auto_spin: bool = False
    auto_spin_count: Optional[int] = Field(None, ge=1, le=100)

# Response schemas
class RouletteResult(BaseModel):
    number: int
    color: str
    total_win: float

class BaccaratResult(BaseModel):
    player_cards: List[Dict[str, str]]
    banker_cards: List[Dict[str, str]]
    total_win: float

class DragonTigerResult(BaseModel):
    dragon_card: Dict[str, str]
    tiger_card: Dict[str, str]
    total_win: float

class SlotResult(BaseModel):
    reels: List[List[str]]
    paylines: List[Dict]
    total_win: float
    bonus_triggered: bool
    bonus_type: Optional[str] 