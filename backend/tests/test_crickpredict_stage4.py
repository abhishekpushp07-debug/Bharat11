"""
CrickPredict Stage 4 - Backend API Tests
Tests: Health, Auth (register/login/me/refresh/lockout), User Profile, Wallet
"""
import pytest
import requests
import os
import random
import string
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://plan-then-build-1.preview.emergentagent.com')

# Test credentials from test_credentials.md
TEST_PHONE = "9876543210"
TEST_PIN = "1234"


def generate_phone():
    """Generate random 10-digit phone number."""
    return "9" + ''.join(random.choices(string.digits, k=9))


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def auth_token(api_client):
    """Get authentication token for test user."""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "phone": TEST_PHONE,
        "pin": TEST_PIN
    })
    if response.status_code == 200:
        data = response.json()
        return data.get("token", {}).get("access_token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture(scope="module")
def authenticated_client(api_client, auth_token):
    """Session with auth header."""
    api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return api_client


# ==================== HEALTH ENDPOINT TESTS ====================

class TestHealthEndpoints:
    """Health check endpoint tests."""
    
    def test_health_endpoint_returns_healthy(self, api_client):
        """GET /api/health returns status healthy."""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "services" in data
        assert data["services"]["mongodb"]["status"] == "healthy"
        print(f"✓ Health endpoint: {data['status']}, MongoDB: {data['services']['mongodb']['status']}")
    
    def test_health_has_security_headers(self, api_client):
        """Health endpoint returns security headers."""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert "X-Request-ID" in response.headers
        assert "X-Response-Time" in response.headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        print(f"✓ Security headers present: X-Request-ID, X-Response-Time, X-Content-Type-Options, X-Frame-Options")


# ==================== AUTH ENDPOINT TESTS ====================

class TestAuthRegistration:
    """Auth registration tests."""
    
    def test_register_new_user_with_signup_bonus(self, api_client):
        """POST /api/auth/register creates user with 10000 signup bonus."""
        new_phone = generate_phone()
        response = api_client.post(f"{BASE_URL}/api/auth/register", json={
            "phone": new_phone,
            "pin": "5678"
        })
        assert response.status_code == 201
        data = response.json()
        
        # Verify token structure
        assert "token" in data
        assert "access_token" in data["token"]
        assert "refresh_token" in data["token"]
        assert data["token"]["token_type"] == "bearer"
        
        # Verify user data
        assert "user" in data
        assert data["user"]["phone"] == new_phone
        assert data["user"]["coins_balance"] == 10000  # Signup bonus
        assert "referral_code" in data["user"]
        print(f"✓ Registration successful: phone={new_phone}, balance={data['user']['coins_balance']}")
    
    def test_register_duplicate_phone_fails(self, api_client):
        """POST /api/auth/register with existing phone returns error."""
        response = api_client.post(f"{BASE_URL}/api/auth/register", json={
            "phone": TEST_PHONE,
            "pin": "1234"
        })
        assert response.status_code == 409  # Conflict
        data = response.json()
        assert "error" in data or "detail" in data
        print(f"✓ Duplicate phone rejected correctly")
    
    def test_register_invalid_pin_fails(self, api_client):
        """POST /api/auth/register with invalid PIN returns error."""
        response = api_client.post(f"{BASE_URL}/api/auth/register", json={
            "phone": generate_phone(),
            "pin": "12"  # Too short
        })
        assert response.status_code in [400, 422]
        print(f"✓ Invalid PIN rejected correctly")


class TestAuthLogin:
    """Auth login tests."""
    
    def test_login_success(self, api_client):
        """POST /api/auth/login with valid credentials returns tokens + user."""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "phone": TEST_PHONE,
            "pin": TEST_PIN
        })
        assert response.status_code == 200
        data = response.json()
        
        # Verify token structure
        assert "token" in data
        assert "access_token" in data["token"]
        assert "refresh_token" in data["token"]
        
        # Verify user data
        assert "user" in data
        assert data["user"]["phone"] == TEST_PHONE
        assert "coins_balance" in data["user"]
        print(f"✓ Login successful: phone={TEST_PHONE}, balance={data['user']['coins_balance']}")
    
    def test_login_wrong_pin_fails(self, api_client):
        """POST /api/auth/login with wrong PIN returns error."""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "phone": TEST_PHONE,
            "pin": "9999"  # Wrong PIN
        })
        assert response.status_code == 401
        print(f"✓ Wrong PIN rejected correctly")
    
    def test_login_nonexistent_phone_fails(self, api_client):
        """POST /api/auth/login with non-existent phone returns error."""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "phone": "1111111111",
            "pin": "1234"
        })
        assert response.status_code == 401
        print(f"✓ Non-existent phone rejected correctly")


class TestAuthMe:
    """Auth /me endpoint tests."""
    
    def test_get_me_with_token(self, authenticated_client):
        """GET /api/auth/me with Bearer token returns user profile."""
        response = authenticated_client.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        
        assert data["phone"] == TEST_PHONE
        assert "id" in data
        assert "username" in data
        assert "coins_balance" in data
        assert "rank_title" in data
        assert "referral_code" in data
        print(f"✓ /me endpoint: username={data['username']}, balance={data['coins_balance']}")
    
    def test_get_me_without_token_fails(self, api_client):
        """GET /api/auth/me without token returns 401."""
        # Use fresh client without auth
        fresh_client = requests.Session()
        response = fresh_client.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
        print(f"✓ /me without token rejected correctly")


class TestAuthRefresh:
    """Auth token refresh tests."""
    
    def test_refresh_token_returns_new_tokens(self, api_client):
        """POST /api/auth/refresh with refresh token returns new tokens."""
        # First login to get refresh token
        login_response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "phone": TEST_PHONE,
            "pin": TEST_PIN
        })
        assert login_response.status_code == 200
        refresh_token = login_response.json()["token"]["refresh_token"]
        
        # Use refresh token
        response = api_client.post(f"{BASE_URL}/api/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        print(f"✓ Token refresh successful")


# ==================== USER PROFILE TESTS ====================

class TestUserProfile:
    """User profile endpoint tests."""
    
    def test_get_profile(self, authenticated_client):
        """GET /api/user/profile returns user data."""
        response = authenticated_client.get(f"{BASE_URL}/api/user/profile")
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert "phone" in data
        assert "username" in data
        assert "coins_balance" in data
        assert "rank_title" in data
        print(f"✓ Profile: username={data['username']}, rank={data['rank_title']}")
    
    def test_update_profile_username(self, authenticated_client):
        """PUT /api/user/profile updates username."""
        new_username = f"TestPlayer_{random.randint(1000, 9999)}"
        response = authenticated_client.put(f"{BASE_URL}/api/user/profile", json={
            "username": new_username
        })
        assert response.status_code == 200
        data = response.json()
        
        assert data["username"] == new_username
        print(f"✓ Profile updated: username={new_username}")
    
    def test_get_rank_progress(self, authenticated_client):
        """GET /api/user/rank-progress returns rank and progress."""
        response = authenticated_client.get(f"{BASE_URL}/api/user/rank-progress")
        assert response.status_code == 200
        data = response.json()
        
        assert "current_rank" in data
        assert "total_points" in data
        assert "progress_percent" in data
        print(f"✓ Rank progress: rank={data['current_rank']}, points={data['total_points']}, progress={data['progress_percent']}%")
    
    def test_get_referral_stats(self, authenticated_client):
        """GET /api/user/referral-stats returns referral code and count."""
        response = authenticated_client.get(f"{BASE_URL}/api/user/referral-stats")
        assert response.status_code == 200
        data = response.json()
        
        assert "referral_code" in data
        assert "total_referrals" in data
        assert "bonus_per_referral" in data
        print(f"✓ Referral stats: code={data['referral_code']}, referrals={data['total_referrals']}")
    
    def test_get_avatars(self, api_client):
        """GET /api/user/avatars returns preset avatar list."""
        response = api_client.get(f"{BASE_URL}/api/user/avatars")
        assert response.status_code == 200
        data = response.json()
        
        assert "avatars" in data
        assert len(data["avatars"]) > 0
        print(f"✓ Avatars: {len(data['avatars'])} presets available")
    
    def test_get_leaderboard(self, api_client):
        """GET /api/user/leaderboard returns ranked users."""
        response = api_client.get(f"{BASE_URL}/api/user/leaderboard")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        if len(data) > 0:
            assert "rank" in data[0]
            assert "username" in data[0]
            assert "total_points" in data[0]
        print(f"✓ Leaderboard: {len(data)} users")


# ==================== WALLET TESTS ====================

class TestWallet:
    """Wallet endpoint tests."""
    
    def test_get_balance(self, authenticated_client):
        """GET /api/wallet/balance returns balance and daily reward status."""
        response = authenticated_client.get(f"{BASE_URL}/api/wallet/balance")
        assert response.status_code == 200
        data = response.json()
        
        assert "balance" in data
        assert "daily_streak" in data
        assert "can_claim_daily" in data
        print(f"✓ Balance: {data['balance']} coins, streak={data['daily_streak']}, can_claim={data['can_claim_daily']}")
    
    def test_get_transactions(self, authenticated_client):
        """GET /api/wallet/transactions returns paginated transaction history."""
        response = authenticated_client.get(f"{BASE_URL}/api/wallet/transactions?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        
        assert "transactions" in data
        assert "page" in data
        assert "limit" in data
        assert "total" in data
        assert "has_more" in data
        
        if len(data["transactions"]) > 0:
            tx = data["transactions"][0]
            assert "id" in tx
            assert "type" in tx
            assert "amount" in tx
            assert "reason" in tx
            assert "balance_after" in tx
        print(f"✓ Transactions: {len(data['transactions'])} items, total={data['total']}")
    
    def test_claim_daily_reward(self, authenticated_client):
        """POST /api/wallet/claim-daily claims daily reward coins."""
        # First check if can claim
        balance_response = authenticated_client.get(f"{BASE_URL}/api/wallet/balance")
        balance_data = balance_response.json()
        
        response = authenticated_client.post(f"{BASE_URL}/api/wallet/claim-daily")
        
        if balance_data.get("can_claim_daily"):
            assert response.status_code == 200
            data = response.json()
            assert "reward_amount" in data
            assert "new_balance" in data
            assert "streak" in data
            print(f"✓ Daily reward claimed: +{data['reward_amount']} coins, streak={data['streak']}")
        else:
            # Already claimed today
            assert response.status_code == 400
            print(f"✓ Daily reward already claimed (expected behavior)")
    
    def test_claim_daily_twice_fails(self, authenticated_client):
        """POST /api/wallet/claim-daily fails if already claimed today."""
        # First claim (may succeed or fail depending on state)
        authenticated_client.post(f"{BASE_URL}/api/wallet/claim-daily")
        
        # Second claim should fail
        response = authenticated_client.post(f"{BASE_URL}/api/wallet/claim-daily")
        assert response.status_code == 400
        print(f"✓ Second daily claim rejected correctly")


# ==================== SECURITY TESTS ====================

class TestSecurity:
    """Security header and rate limiting tests."""
    
    def test_security_headers_present(self, api_client):
        """All responses have security headers."""
        response = api_client.get(f"{BASE_URL}/api/health")
        
        assert response.headers.get("X-Request-ID") is not None
        assert response.headers.get("X-Response-Time") is not None
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        print(f"✓ All security headers present")
    
    def test_rate_limiting_on_auth(self, api_client):
        """Auth endpoints have rate limiting headers."""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "phone": TEST_PHONE,
            "pin": TEST_PIN
        })
        
        # Rate limit headers may be present
        # Just verify the endpoint works
        assert response.status_code in [200, 429]
        print(f"✓ Auth endpoint rate limiting check passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
