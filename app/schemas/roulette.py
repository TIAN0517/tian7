from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class BetType(str, Enum):
    STRAIGHT = "straight"      # 直注
    SPLIT = "split"           # 分注
    STREET = "street"         # 街注
    CORNER = "corner"         # 角注
    LINE = "line"             # 線注
    COLUMN = "column"         # 欄注
    DOZEN = "dozen"           # 打注
    RED = "red"               # 紅
    BLACK = "black"           # 黑
    ODD = "odd"               # 奇
    EVEN = "even"             # 偶
    HIGH = "high"             # 高
    LOW = "low"               # 低

class RouletteSessionCreate(BaseModel):
    wheel_type: str = Field(default="european", description="Type of roulette wheel (european/american)")

class RouletteSessionResponse(BaseModel):
    session_id: str
    game_type: str = "roulette"
    config: dict
    status: str
    created_at: datetime
    user_balance: float

class RouletteBetCreate(BaseModel):
    bet_type: BetType
    amount: float = Field(gt=0, description="Bet amount")
    numbers: Optional[List[int]] = Field(default=None, description="Numbers for straight/split/street/corner/line bets")

class RouletteBetResponse(BaseModel):
    bet_id: str
    session_id: str
    bet_type: BetType
    amount: float
    numbers: Optional[List[int]]
    status: str
    placed_at: datetime
    new_balance: float

class RouletteSpinRequest(BaseModel):
    force_number: Optional[int] = Field(default=None, description="Force specific number for testing")

class RouletteSpinResponse(BaseModel):
    session_id: str
    result_number: int
    color: str
    winners: List[dict]
    total_payout: float
    completed_at: datetime

class RouletteHistoryResponse(BaseModel):
    session_id: str
    result_number: int
    color: str
    total_bet: float
    total_win: float
    created_at: datetime
    bets: List[dict]

    class Config:
        orm_mode = True 