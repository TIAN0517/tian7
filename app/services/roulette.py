from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
import random
import hashlib
import json

from app.models.roulette import RouletteSession, RouletteBet, RouletteResult
from app.schemas.roulette import (
    RouletteSessionCreate,
    RouletteBetCreate,
    RouletteSpinRequest
)
from app.core.security import verify_balance, update_balance

class RouletteService:
    def __init__(self, db: Session):
        self.db = db
        self.ODDS = {
            "straight": 35,    # 直注
            "split": 17,       # 分注
            "street": 11,      # 街注
            "corner": 8,       # 角注
            "line": 5,         # 線注
            "column": 2,       # 欄注
            "dozen": 2,        # 打注
            "red": 1,          # 紅
            "black": 1,        # 黑
            "odd": 1,          # 奇
            "even": 1,         # 偶
            "high": 1,         # 高
            "low": 1           # 低
        }

    async def create_session(self, user_id: int) -> dict:
        """Create a new roulette game session."""
        session = RouletteSession(
            user_id=user_id,
            config={
                "wheel_type": "european",
                "min_bet": 1,
                "max_bet": 10000,
                "bet_time": 30
            }
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        return {
            "session_id": session.id,
            "game_type": "roulette",
            "config": session.config,
            "status": session.status,
            "created_at": session.created_at,
            "user_balance": await verify_balance(self.db, user_id)
        }

    async def place_bet(
        self,
        session_id: str,
        user_id: int,
        bet: RouletteBetCreate
    ) -> dict:
        """Place a bet in the current roulette session."""
        session = self.db.query(RouletteSession).filter(
            RouletteSession.id == session_id,
            RouletteSession.user_id == user_id,
            RouletteSession.status == "active"
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or not active"
            )

        # Verify user balance
        current_balance = await verify_balance(self.db, user_id)
        if current_balance < bet.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance"
            )

        # Create bet record
        new_bet = RouletteBet(
            session_id=session_id,
            user_id=user_id,
            bet_type=bet.bet_type,
            amount=bet.amount,
            numbers=bet.numbers
        )
        self.db.add(new_bet)
        
        # Update user balance
        new_balance = await update_balance(
            self.db,
            user_id,
            -bet.amount,
            f"Roulette bet {new_bet.id}"
        )
        
        self.db.commit()
        self.db.refresh(new_bet)
        
        return {
            "bet_id": new_bet.id,
            "session_id": session_id,
            "bet_type": bet.bet_type,
            "amount": bet.amount,
            "numbers": bet.numbers,
            "status": new_bet.status,
            "placed_at": new_bet.placed_at,
            "new_balance": new_balance
        }

    async def spin_wheel(
        self,
        session_id: str,
        user_id: int,
        request: RouletteSpinRequest
    ) -> dict:
        """Spin the roulette wheel and calculate results."""
        session = self.db.query(RouletteSession).filter(
            RouletteSession.id == session_id,
            RouletteSession.user_id == user_id,
            RouletteSession.status == "active"
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or not active"
            )

        # Get all pending bets
        bets = self.db.query(RouletteBet).filter(
            RouletteBet.session_id == session_id,
            RouletteBet.status == "pending"
        ).all()

        if not bets:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No pending bets found"
            )

        # Generate result
        result_number = request.force_number if request.force_number is not None else random.randint(0, 36)
        color = "green" if result_number == 0 else ("red" if result_number % 2 == 1 else "black")
        
        # Calculate winners and payouts
        winners = []
        total_payout = 0
        
        for bet in bets:
            win_amount = self._calculate_win(bet, result_number, color)
            if win_amount > 0:
                winners.append({
                    "bet_id": bet.id,
                    "bet_type": bet.bet_type,
                    "win_amount": win_amount
                })
                total_payout += win_amount
                
                # Update bet status
                bet.status = "won"
                bet.win_amount = win_amount
                bet.settled_at = datetime.utcnow()
                
                # Update user balance
                await update_balance(
                    self.db,
                    user_id,
                    win_amount,
                    f"Roulette win {bet.id}"
                )
            else:
                bet.status = "lost"
                bet.settled_at = datetime.utcnow()

        # Create result record
        result = RouletteResult(
            session_id=session_id,
            result_number=result_number,
            color=color,
            total_bet=sum(bet.amount for bet in bets),
            total_win=total_payout,
            fairness_proof=self._generate_fairness_proof(session_id, result_number)
        )
        self.db.add(result)
        
        # Update session status
        session.status = "completed"
        session.completed_at = datetime.utcnow()
        
        self.db.commit()
        
        return {
            "session_id": session_id,
            "result_number": result_number,
            "color": color,
            "winners": winners,
            "total_payout": total_payout,
            "completed_at": session.completed_at
        }

    async def get_history(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> list:
        """Get roulette game history for the user."""
        results = self.db.query(RouletteResult).join(
            RouletteSession
        ).filter(
            RouletteSession.user_id == user_id
        ).order_by(
            RouletteResult.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return [{
            "session_id": result.session_id,
            "result_number": result.result_number,
            "color": result.color,
            "total_bet": result.total_bet,
            "total_win": result.total_win,
            "created_at": result.created_at,
            "bets": [{
                "bet_type": bet.bet_type,
                "amount": bet.amount,
                "numbers": bet.numbers,
                "win_amount": bet.win_amount
            } for bet in result.session.bets]
        } for result in results]

    async def get_stats(self, user_id: int) -> dict:
        """Get roulette game statistics for the user."""
        sessions = self.db.query(RouletteSession).filter(
            RouletteSession.user_id == user_id
        ).all()
        
        total_games = len(sessions)
        total_bet = sum(
            sum(bet.amount for bet in session.bets)
            for session in sessions
        )
        total_win = sum(
            result.total_win
            for session in sessions
            for result in [session.result] if result
        )
        
        return {
            "total_games": total_games,
            "total_bet": total_bet,
            "total_win": total_win,
            "net_profit": total_win - total_bet,
            "win_rate": total_win / total_bet if total_bet > 0 else 0,
            "avg_bet": total_bet / total_games if total_games > 0 else 0
        }

    def _calculate_win(
        self,
        bet: RouletteBet,
        result_number: int,
        color: str
    ) -> float:
        """Calculate win amount for a bet."""
        if bet.bet_type == "straight":
            return bet.amount * self.ODDS["straight"] if result_number in bet.numbers else 0
        elif bet.bet_type == "red":
            return bet.amount * self.ODDS["red"] if color == "red" else 0
        elif bet.bet_type == "black":
            return bet.amount * self.ODDS["black"] if color == "black" else 0
        elif bet.bet_type == "odd":
            return bet.amount * self.ODDS["odd"] if result_number % 2 == 1 else 0
        elif bet.bet_type == "even":
            return bet.amount * self.ODDS["even"] if result_number % 2 == 0 and result_number != 0 else 0
        elif bet.bet_type == "high":
            return bet.amount * self.ODDS["high"] if 19 <= result_number <= 36 else 0
        elif bet.bet_type == "low":
            return bet.amount * self.ODDS["low"] if 1 <= result_number <= 18 else 0
        # Add more bet type calculations as needed
        return 0

    def _generate_fairness_proof(self, session_id: str, result_number: int) -> dict:
        """Generate provably fair proof for the game result."""
        # This is a simplified version. In production, you should use a more
        # sophisticated provably fair algorithm
        server_seed = hashlib.sha256(session_id.encode()).hexdigest()
        client_seed = hashlib.sha256(str(result_number).encode()).hexdigest()
        combined_seed = hashlib.sha256((server_seed + client_seed).encode()).hexdigest()
        
        return {
            "server_seed": server_seed,
            "client_seed": client_seed,
            "combined_seed": combined_seed,
            "result_number": result_number
        } 