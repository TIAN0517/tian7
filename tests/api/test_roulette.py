import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from app.main import app
from app.models.roulette import RouletteSession, RouletteBet, RouletteResult
from app.schemas.roulette import BetType
from app.core.security import create_access_token

client = TestClient(app)

@pytest.fixture
def test_user(db: Session):
    """Create a test user and return their access token."""
    # Create test user in database
    user = {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "balance": 10000.0
    }
    # Add user to database...
    
    # Create access token
    access_token = create_access_token({"sub": user["email"]})
    return {"user": user, "token": access_token}

@pytest.fixture
def test_session(db: Session, test_user):
    """Create a test roulette session."""
    session = RouletteSession(
        id="test_session_001",
        user_id=test_user["user"]["id"],
        wheel_type="european",
        status="active",
        config={
            "wheel_type": "european",
            "min_bet": 1,
            "max_bet": 10000,
            "bet_time": 30
        },
        created_at=datetime.utcnow()
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def test_create_session(test_user):
    """Test creating a new roulette session."""
    response = client.post(
        "/api/v1/games/roulette/create-session",
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["game_type"] == "roulette"
    assert data["status"] == "active"
    assert "config" in data
    assert "user_balance" in data

def test_place_bet(test_user, test_session):
    """Test placing a bet in a roulette session."""
    bet_data = {
        "bet_type": "red",
        "amount": 100.0
    }
    response = client.post(
        f"/api/v1/games/roulette/{test_session.id}/bet",
        headers={"Authorization": f"Bearer {test_user['token']}"},
        json=bet_data
    )
    assert response.status_code == 200
    data = response.json()
    assert "bet_id" in data
    assert data["session_id"] == test_session.id
    assert data["bet_type"] == "red"
    assert data["amount"] == 100.0
    assert data["status"] == "pending"
    assert "new_balance" in data

def test_place_bet_insufficient_balance(test_user, test_session):
    """Test placing a bet with insufficient balance."""
    bet_data = {
        "bet_type": "red",
        "amount": 20000.0  # More than user's balance
    }
    response = client.post(
        f"/api/v1/games/roulette/{test_session.id}/bet",
        headers={"Authorization": f"Bearer {test_user['token']}"},
        json=bet_data
    )
    assert response.status_code == 400
    assert "Insufficient balance" in response.json()["detail"]

def test_spin_wheel(test_user, test_session):
    """Test spinning the roulette wheel."""
    # First place a bet
    bet_data = {
        "bet_type": "red",
        "amount": 100.0
    }
    client.post(
        f"/api/v1/games/roulette/{test_session.id}/bet",
        headers={"Authorization": f"Bearer {test_user['token']}"},
        json=bet_data
    )
    
    # Then spin the wheel
    response = client.post(
        f"/api/v1/games/roulette/{test_session.id}/spin",
        headers={"Authorization": f"Bearer {test_user['token']}"},
        json={"force_number": 1}  # Force red number for testing
    )
    assert response.status_code == 200
    data = response.json()
    assert "result_number" in data
    assert "color" in data
    assert "winners" in data
    assert "total_payout" in data
    assert data["session_id"] == test_session.id

def test_get_history(test_user):
    """Test getting roulette game history."""
    response = client.get(
        "/api/v1/games/roulette/history",
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:  # If there's any history
        assert "session_id" in data[0]
        assert "result_number" in data[0]
        assert "color" in data[0]
        assert "total_bet" in data[0]
        assert "total_win" in data[0]
        assert "bets" in data[0]

def test_get_stats(test_user):
    """Test getting roulette game statistics."""
    response = client.get(
        "/api/v1/games/roulette/stats",
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_games" in data
    assert "total_bet" in data
    assert "total_win" in data
    assert "net_profit" in data
    assert "win_rate" in data
    assert "avg_bet" in data

def test_invalid_session_id(test_user):
    """Test using an invalid session ID."""
    response = client.post(
        "/api/v1/games/roulette/invalid_session_id/bet",
        headers={"Authorization": f"Bearer {test_user['token']}"},
        json={"bet_type": "red", "amount": 100.0}
    )
    assert response.status_code == 404
    assert "Session not found" in response.json()["detail"]

def test_unauthorized_access():
    """Test accessing endpoints without authentication."""
    response = client.post("/api/v1/games/roulette/create-session")
    assert response.status_code == 401

def test_invalid_bet_type(test_user, test_session):
    """Test placing a bet with invalid bet type."""
    bet_data = {
        "bet_type": "invalid_type",
        "amount": 100.0
    }
    response = client.post(
        f"/api/v1/games/roulette/{test_session.id}/bet",
        headers={"Authorization": f"Bearer {test_user['token']}"},
        json=bet_data
    )
    assert response.status_code == 422  # Validation error

def test_spin_without_bets(test_user, test_session):
    """Test spinning the wheel without placing any bets."""
    response = client.post(
        f"/api/v1/games/roulette/{test_session.id}/spin",
        headers={"Authorization": f"Bearer {test_user['token']}"},
        json={}
    )
    assert response.status_code == 400
    assert "No pending bets found" in response.json()["detail"] 