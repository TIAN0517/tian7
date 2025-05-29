import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from locust import HttpUser, task, between

from app.main import app
from app.models.roulette import RouletteSession, RouletteBet
from app.core.security import create_access_token

client = TestClient(app)

class RouletteLoadTest(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Create a test user and get access token."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpassword"
            }
        )
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Create a test session
        response = self.client.post(
            "/api/v1/games/roulette/create-session",
            headers=self.headers
        )
        self.session_id = response.json()["session_id"]
    
    @task(3)
    def place_bet(self):
        """Test placing bets."""
        bet_data = {
            "bet_type": "red",
            "amount": 100.0
        }
        self.client.post(
            f"/api/v1/games/roulette/{self.session_id}/bet",
            headers=self.headers,
            json=bet_data
        )
    
    @task(1)
    def spin_wheel(self):
        """Test spinning the wheel."""
        self.client.post(
            f"/api/v1/games/roulette/{self.session_id}/spin",
            headers=self.headers,
            json={}
        )
    
    @task(2)
    def get_history(self):
        """Test getting game history."""
        self.client.get(
            "/api/v1/games/roulette/history",
            headers=self.headers
        )

@pytest.mark.benchmark
def test_create_session_performance(benchmark):
    """Benchmark session creation performance."""
    def create_session():
        response = client.post(
            "/api/v1/games/roulette/create-session",
            headers={"Authorization": f"Bearer {create_access_token({'sub': 'test@example.com'})}"}
        )
        assert response.status_code == 200
    
    benchmark(create_session)

@pytest.mark.benchmark
def test_place_bet_performance(benchmark, test_session):
    """Benchmark bet placement performance."""
    def place_bet():
        response = client.post(
            f"/api/v1/games/roulette/{test_session.id}/bet",
            headers={"Authorization": f"Bearer {create_access_token({'sub': 'test@example.com'})}"},
            json={"bet_type": "red", "amount": 100.0}
        )
        assert response.status_code == 200
    
    benchmark(place_bet)

@pytest.mark.benchmark
def test_spin_wheel_performance(benchmark, test_session):
    """Benchmark wheel spinning performance."""
    # First place a bet
    client.post(
        f"/api/v1/games/roulette/{test_session.id}/bet",
        headers={"Authorization": f"Bearer {create_access_token({'sub': 'test@example.com'})}"},
        json={"bet_type": "red", "amount": 100.0}
    )
    
    def spin_wheel():
        response = client.post(
            f"/api/v1/games/roulette/{test_session.id}/spin",
            headers={"Authorization": f"Bearer {create_access_token({'sub': 'test@example.com'})}"},
            json={}
        )
        assert response.status_code == 200
    
    benchmark(spin_wheel)

@pytest.mark.benchmark
def test_concurrent_bets_performance():
    """Test concurrent bet placement performance."""
    num_concurrent_users = 50
    num_bets_per_user = 10
    
    def place_bets(user_id):
        token = create_access_token({"sub": f"test{user_id}@example.com"})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create session
        response = client.post(
            "/api/v1/games/roulette/create-session",
            headers=headers
        )
        session_id = response.json()["session_id"]
        
        # Place bets
        for _ in range(num_bets_per_user):
            client.post(
                f"/api/v1/games/roulette/{session_id}/bet",
                headers=headers,
                json={"bet_type": "red", "amount": 100.0}
            )
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=num_concurrent_users) as executor:
        executor.map(place_bets, range(num_concurrent_users))
    
    end_time = time.time()
    total_time = end_time - start_time
    total_bets = num_concurrent_users * num_bets_per_user
    
    print(f"\nConcurrent Performance Results:")
    print(f"Total bets placed: {total_bets}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Bets per second: {total_bets/total_time:.2f}")
    print(f"Average time per bet: {total_time/total_bets*1000:.2f} ms")

@pytest.mark.benchmark
def test_database_performance(benchmark, db: Session):
    """Benchmark database operations performance."""
    def create_test_data():
        # Create test session
        session = RouletteSession(
            user_id=1,
            wheel_type="european",
            status="active"
        )
        db.add(session)
        db.commit()
        
        # Create test bets
        for _ in range(100):
            bet = RouletteBet(
                session_id=session.id,
                user_id=1,
                bet_type="red",
                amount=100.0
            )
            db.add(bet)
        db.commit()
        
        # Query test data
        bets = db.query(RouletteBet).filter(
            RouletteBet.session_id == session.id
        ).all()
        
        return len(bets)
    
    result = benchmark(create_test_data)
    assert result == 100

@pytest.mark.benchmark
def test_api_response_time():
    """Test API endpoint response times."""
    endpoints = [
        ("/api/v1/games/roulette/create-session", "POST"),
        ("/api/v1/games/roulette/history", "GET"),
        ("/api/v1/games/roulette/stats", "GET")
    ]
    
    headers = {"Authorization": f"Bearer {create_access_token({'sub': 'test@example.com'})}"}
    
    print("\nAPI Response Time Results:")
    for endpoint, method in endpoints:
        start_time = time.time()
        if method == "POST":
            response = client.post(endpoint, headers=headers)
        else:
            response = client.get(endpoint, headers=headers)
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        print(f"{method} {endpoint}: {response_time:.2f} ms")
        assert response.status_code == 200 