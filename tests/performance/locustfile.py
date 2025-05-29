from locust import HttpUser, task, between
import random

class RouletteUser(HttpUser):
    host = "http://localhost:8000"
    wait_time = between(1, 3)
    
    def on_start(self):
        """Initialize user session."""
        # Login
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": f"test{random.randint(1, 1000)}@example.com",
                "password": "testpassword"
            }
        )
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Create initial session
        response = self.client.post(
            "/api/v1/games/roulette/create-session",
            headers=self.headers
        )
        self.session_id = response.json()["session_id"]
    
    @task(3)
    def place_bet(self):
        """Place a bet with random type and amount."""
        bet_types = ["red", "black", "straight", "split", "corner"]
        bet_type = random.choice(bet_types)
        amount = random.randint(10, 1000)
        
        self.client.post(
            f"/api/v1/games/roulette/{self.session_id}/bet",
            headers=self.headers,
            json={
                "bet_type": bet_type,
                "amount": amount
            }
        )
    
    @task(1)
    def spin_wheel(self):
        """Spin the wheel and check results."""
        self.client.post(
            f"/api/v1/games/roulette/{self.session_id}/spin",
            headers=self.headers,
            json={}
        )
    
    @task(2)
    def check_history(self):
        """Check game history."""
        self.client.get(
            "/api/v1/games/roulette/history",
            headers=self.headers
        )
    
    @task(1)
    def check_stats(self):
        """Check game statistics."""
        self.client.get(
            "/api/v1/games/roulette/stats",
            headers=self.headers
        )
    
    @task(1)
    def create_new_session(self):
        """Create a new game session."""
        response = self.client.post(
            "/api/v1/games/roulette/create-session",
            headers=self.headers
        )
        self.session_id = response.json()["session_id"]

class RouletteLoadTest(HttpUser):
    host = "http://localhost:8000"
    """Load test configuration for specific scenarios."""
    wait_time = between(0.1, 0.5)  # Faster wait times for load testing
    
    def on_start(self):
        """Initialize test session."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": f"loadtest{random.randint(1, 10000)}@example.com",
                "password": "testpassword"
            }
        )
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        response = self.client.post(
            "/api/v1/games/roulette/create-session",
            headers=self.headers
        )
        self.session_id = response.json()["session_id"]
    
    @task(5)
    def rapid_betting(self):
        """Simulate rapid betting behavior."""
        for _ in range(5):  # Place multiple bets quickly
            self.client.post(
                f"/api/v1/games/roulette/{self.session_id}/bet",
                headers=self.headers,
                json={
                    "bet_type": "red",
                    "amount": 100.0
                }
            )
    
    @task(1)
    def spin_and_check(self):
        """Spin wheel and immediately check results."""
        self.client.post(
            f"/api/v1/games/roulette/{self.session_id}/spin",
            headers=self.headers,
            json={}
        )
        self.client.get(
            "/api/v1/games/roulette/history",
            headers=self.headers
        ) 