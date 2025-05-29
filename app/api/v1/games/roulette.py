from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.deps import get_db, get_current_user
from app.schemas.roulette import (
    RouletteSessionCreate,
    RouletteSessionResponse,
    RouletteBetCreate,
    RouletteBetResponse,
    RouletteSpinRequest,
    RouletteSpinResponse,
    RouletteHistoryResponse
)
from app.services.roulette import RouletteService
from app.models.user import User

router = APIRouter(prefix="/roulette", tags=["roulette"])

@router.post("/create-session", response_model=RouletteSessionResponse)
async def create_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new roulette game session."""
    service = RouletteService(db)
    return await service.create_session(current_user.id)

@router.post("/{session_id}/bet", response_model=RouletteBetResponse)
async def place_bet(
    session_id: str,
    bet: RouletteBetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Place a bet in the current roulette session."""
    service = RouletteService(db)
    return await service.place_bet(session_id, current_user.id, bet)

@router.post("/{session_id}/spin", response_model=RouletteSpinResponse)
async def spin_wheel(
    session_id: str,
    request: RouletteSpinRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Spin the roulette wheel and calculate results."""
    service = RouletteService(db)
    return await service.spin_wheel(session_id, current_user.id, request)

@router.get("/history", response_model=List[RouletteHistoryResponse])
async def get_history(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get roulette game history for the current user."""
    service = RouletteService(db)
    return await service.get_history(current_user.id, skip, limit)

@router.get("/stats")
async def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get roulette game statistics for the current user."""
    service = RouletteService(db)
    return await service.get_stats(current_user.id) 