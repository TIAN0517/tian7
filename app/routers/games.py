from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime

from ..database import get_db
from ..models.game_models import GameSession, Bet, GameResult, GameType
from ..games.game_logic import (
    GameLogic, RouletteBetType, BaccaratBetType, 
    DragonTigerBetType, Card
)
from ..schemas.game_schemas import (
    GameSessionCreate, BetCreate, GameResultResponse,
    RouletteBet, BaccaratBet, DragonTigerBet, SlotBet
)

router = APIRouter()

# WebSocket connections store
active_connections: Dict[int, WebSocket] = {}

# Game session management
@router.post("/sessions", response_model=GameSessionCreate)
async def create_game_session(
    game_type: GameType,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Create a new game session."""
    session = GameSession(
        game_type=game_type,
        user_id=user_id,
        status="active",
        created_at=datetime.utcnow()
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

# Roulette endpoints
@router.post("/roulette/bet")
async def place_roulette_bet(
    bet: RouletteBet,
    session_id: int,
    db: Session = Depends(get_db)
):
    """Place a bet in a roulette game."""
    session = db.query(GameSession).filter(GameSession.id == session_id).first()
    if not session or session.status != "active":
        raise HTTPException(status_code=400, detail="Invalid session")
    
    bet_record = Bet(
        session_id=session_id,
        user_id=session.user_id,
        bet_type=bet.bet_type.value,
        amount=bet.amount,
        odds=bet.odds,
        status="pending"
    )
    db.add(bet_record)
    db.commit()
    return {"message": "Bet placed successfully"}

@router.post("/roulette/spin")
async def spin_roulette_wheel(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Spin the roulette wheel and determine the result."""
    session = db.query(GameSession).filter(GameSession.id == session_id).first()
    if not session or session.status != "active":
        raise HTTPException(status_code=400, detail="Invalid session")
    
    number, color = GameLogic.generate_roulette_number()
    result = GameResult(
        session_id=session_id,
        result_data={"number": number, "color": color}
    )
    db.add(result)
    
    # Calculate winnings for all pending bets
    bets = db.query(Bet).filter(
        Bet.session_id == session_id,
        Bet.status == "pending"
    ).all()
    
    total_win = 0
    for bet in bets:
        win_amount = GameLogic.calculate_roulette_win(
            RouletteBetType(bet.bet_type),
            bet.amount,
            number
        )
        bet.status = "won" if win_amount > 0 else "lost"
        total_win += win_amount
    
    session.total_win = total_win
    session.status = "completed"
    session.ended_at = datetime.utcnow()
    db.commit()
    
    return {"number": number, "color": color, "total_win": total_win}

# Baccarat endpoints
@router.post("/baccarat/bet")
async def place_baccarat_bet(
    bet: BaccaratBet,
    session_id: int,
    db: Session = Depends(get_db)
):
    """Place a bet in a baccarat game."""
    session = db.query(GameSession).filter(GameSession.id == session_id).first()
    if not session or session.status != "active":
        raise HTTPException(status_code=400, detail="Invalid session")
    
    bet_record = Bet(
        session_id=session_id,
        user_id=session.user_id,
        bet_type=bet.bet_type.value,
        amount=bet.amount,
        odds=bet.odds,
        status="pending"
    )
    db.add(bet_record)
    db.commit()
    return {"message": "Bet placed successfully"}

@router.post("/baccarat/deal")
async def deal_baccarat_cards(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Deal cards and determine the result in a baccarat game."""
    session = db.query(GameSession).filter(GameSession.id == session_id).first()
    if not session or session.status != "active":
        raise HTTPException(status_code=400, detail="Invalid session")
    
    player_cards, banker_cards = GameLogic.generate_baccarat_cards()
    result = GameResult(
        session_id=session_id,
        result_data={
            "player_cards": [{"suit": c.suit, "value": c.value} for c in player_cards],
            "banker_cards": [{"suit": c.suit, "value": c.value} for c in banker_cards]
        }
    )
    db.add(result)
    
    # Calculate winnings
    bets = db.query(Bet).filter(
        Bet.session_id == session_id,
        Bet.status == "pending"
    ).all()
    
    total_win = 0
    for bet in bets:
        win_amount = GameLogic.calculate_baccarat_win(
            BaccaratBetType(bet.bet_type),
            bet.amount,
            player_cards,
            banker_cards
        )
        bet.status = "won" if win_amount > 0 else "lost"
        total_win += win_amount
    
    session.total_win = total_win
    session.status = "completed"
    session.ended_at = datetime.utcnow()
    db.commit()
    
    return {
        "player_cards": [{"suit": c.suit, "value": c.value} for c in player_cards],
        "banker_cards": [{"suit": c.suit, "value": c.value} for c in banker_cards],
        "total_win": total_win
    }

# Dragon Tiger endpoints
@router.post("/dragon-tiger/bet")
async def place_dragon_tiger_bet(
    bet: DragonTigerBet,
    session_id: int,
    db: Session = Depends(get_db)
):
    """Place a bet in a dragon tiger game."""
    session = db.query(GameSession).filter(GameSession.id == session_id).first()
    if not session or session.status != "active":
        raise HTTPException(status_code=400, detail="Invalid session")
    
    bet_record = Bet(
        session_id=session_id,
        user_id=session.user_id,
        bet_type=bet.bet_type.value,
        amount=bet.amount,
        odds=bet.odds,
        status="pending"
    )
    db.add(bet_record)
    db.commit()
    return {"message": "Bet placed successfully"}

@router.post("/dragon-tiger/deal")
async def deal_dragon_tiger_cards(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Deal cards and determine the result in a dragon tiger game."""
    session = db.query(GameSession).filter(GameSession.id == session_id).first()
    if not session or session.status != "active":
        raise HTTPException(status_code=400, detail="Invalid session")
    
    dragon_card, tiger_card = GameLogic.generate_dragon_tiger_cards()
    result = GameResult(
        session_id=session_id,
        result_data={
            "dragon_card": {"suit": dragon_card.suit, "value": dragon_card.value},
            "tiger_card": {"suit": tiger_card.suit, "value": tiger_card.value}
        }
    )
    db.add(result)
    
    # Calculate winnings
    bets = db.query(Bet).filter(
        Bet.session_id == session_id,
        Bet.status == "pending"
    ).all()
    
    total_win = 0
    for bet in bets:
        win_amount = GameLogic.calculate_dragon_tiger_win(
            DragonTigerBetType(bet.bet_type),
            bet.amount,
            dragon_card,
            tiger_card
        )
        bet.status = "won" if win_amount > 0 else "lost"
        total_win += win_amount
    
    session.total_win = total_win
    session.status = "completed"
    session.ended_at = datetime.utcnow()
    db.commit()
    
    return {
        "dragon_card": {"suit": dragon_card.suit, "value": dragon_card.value},
        "tiger_card": {"suit": tiger_card.suit, "value": tiger_card.value},
        "total_win": total_win
    }

# Slot game endpoints
@router.post("/slot/spin")
async def spin_slot_machine(
    bet: SlotBet,
    session_id: int,
    db: Session = Depends(get_db)
):
    """Spin the slot machine and determine the result."""
    session = db.query(GameSession).filter(GameSession.id == session_id).first()
    if not session or session.status != "active":
        raise HTTPException(status_code=400, detail="Invalid session")
    
    # Place bet
    bet_record = Bet(
        session_id=session_id,
        user_id=session.user_id,
        bet_type="slot",
        amount=bet.amount,
        odds=1.0,
        status="pending"
    )
    db.add(bet_record)
    
    # Generate result
    result_data = GameLogic.generate_slot_result()
    result = GameResult(
        session_id=session_id,
        result_data=result_data
    )
    db.add(result)
    
    # Update session
    session.total_win = result_data["total_win"]
    session.status = "completed"
    session.ended_at = datetime.utcnow()
    db.commit()
    
    return result_data

# WebSocket endpoint for real-time game updates
@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: int):
    await websocket.accept()
    active_connections[session_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            # Handle real-time game updates
            await websocket.send_text(f"Message received: {data}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if session_id in active_connections:
            del active_connections[session_id] 