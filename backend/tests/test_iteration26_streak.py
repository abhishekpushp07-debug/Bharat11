"""
Iteration 26 - Prediction Streak Feature Tests
Tests for:
- GET /api/contests/global/top-streak - returns top users by active prediction streak
- GET /api/contests/global/my-streak - returns current user's streak, multiplier, next milestone info
- GET /api/auth/me - should now include prediction_streak and max_prediction_streak fields
- Streak fields initialized to 0 for existing users
- Settlement engine: get_streak_multiplier and update_user_streaks functions
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
SUPER_ADMIN = {"phone": "7004186276", "pin": "5524"}
TEST_PLAYER = {"phone": "9111111111", "pin": "5678"}


class TestHealthAndAuth:
    """Basic health and auth tests"""
    
    def test_health_endpoint(self):
        """Test health endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        print("PASS: Health endpoint returns 200")
    
    def test_admin_login(self):
        """Test admin login returns token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=SUPER_ADMIN)
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in response"
        assert "access_token" in data["token"], "No access_token in token"
        print("PASS: Admin login successful")
        return data["token"]["access_token"]
    
    def test_player_login(self):
        """Test player login returns token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_PLAYER)
        assert response.status_code == 200, f"Player login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in response"
        print("PASS: Player login successful")
        return data["token"]["access_token"]


class TestStreakAPIs:
    """Tests for prediction streak endpoints"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=SUPER_ADMIN)
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json()["token"]["access_token"]
    
    @pytest.fixture
    def player_token(self):
        """Get player auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_PLAYER)
        if response.status_code != 200:
            pytest.skip("Player login failed")
        return response.json()["token"]["access_token"]
    
    def test_top_streak_endpoint_public(self):
        """Test GET /api/contests/global/top-streak is accessible (public endpoint)"""
        response = requests.get(f"{BASE_URL}/api/contests/global/top-streak")
        assert response.status_code == 200, f"Top streak endpoint failed: {response.text}"
        data = response.json()
        assert "streaks" in data, "Response missing 'streaks' field"
        assert "total" in data, "Response missing 'total' field"
        assert isinstance(data["streaks"], list), "'streaks' should be a list"
        print(f"PASS: Top streak endpoint returns {data['total']} users")
        
        # Verify structure of streak entries if any exist
        if data["streaks"]:
            streak = data["streaks"][0]
            required_fields = ["rank", "user_id", "username", "current_streak", "max_streak", "is_hot"]
            for field in required_fields:
                assert field in streak, f"Streak entry missing '{field}' field"
            print(f"PASS: Top streak entry has all required fields: {required_fields}")
    
    def test_top_streak_with_limit(self):
        """Test top-streak endpoint respects limit parameter"""
        response = requests.get(f"{BASE_URL}/api/contests/global/top-streak?limit=5")
        assert response.status_code == 200, f"Top streak with limit failed: {response.text}"
        data = response.json()
        assert len(data["streaks"]) <= 5, "Limit parameter not respected"
        print("PASS: Top streak limit parameter works")
    
    def test_my_streak_requires_auth(self):
        """Test GET /api/contests/global/my-streak requires authentication"""
        response = requests.get(f"{BASE_URL}/api/contests/global/my-streak")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: my-streak endpoint requires authentication")
    
    def test_my_streak_with_auth(self, player_token):
        """Test GET /api/contests/global/my-streak returns streak info for authenticated user"""
        headers = {"Authorization": f"Bearer {player_token}"}
        response = requests.get(f"{BASE_URL}/api/contests/global/my-streak", headers=headers)
        assert response.status_code == 200, f"my-streak failed: {response.text}"
        data = response.json()
        
        # Verify required fields
        required_fields = ["current_streak", "max_streak", "is_hot", "multiplier", "next_milestone"]
        for field in required_fields:
            assert field in data, f"my-streak response missing '{field}' field"
        
        # Verify data types
        assert isinstance(data["current_streak"], int), "current_streak should be int"
        assert isinstance(data["max_streak"], int), "max_streak should be int"
        assert isinstance(data["is_hot"], bool), "is_hot should be bool"
        assert isinstance(data["multiplier"], int), "multiplier should be int"
        
        print(f"PASS: my-streak returns: streak={data['current_streak']}, multiplier={data['multiplier']}x, is_hot={data['is_hot']}")
    
    def test_my_streak_multiplier_logic(self, player_token):
        """Test streak multiplier logic: 5+ = 2x, 10+ = 4x"""
        headers = {"Authorization": f"Bearer {player_token}"}
        response = requests.get(f"{BASE_URL}/api/contests/global/my-streak", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        streak = data["current_streak"]
        multiplier = data["multiplier"]
        is_hot = data["is_hot"]
        next_milestone = data["next_milestone"]
        
        # Verify multiplier logic
        if streak >= 10:
            assert multiplier == 4, f"Streak {streak} should have 4x multiplier, got {multiplier}x"
            assert is_hot == True, "Streak >= 10 should be hot"
            assert next_milestone is None, "Streak >= 10 should have no next milestone"
        elif streak >= 5:
            assert multiplier == 2, f"Streak {streak} should have 2x multiplier, got {multiplier}x"
            assert is_hot == True, "Streak >= 5 should be hot"
            assert next_milestone == 10, "Streak 5-9 should have next milestone 10"
        else:
            assert multiplier == 1, f"Streak {streak} should have 1x multiplier, got {multiplier}x"
            assert is_hot == False, "Streak < 5 should not be hot"
            assert next_milestone == 5, "Streak < 5 should have next milestone 5"
        
        print(f"PASS: Multiplier logic correct for streak={streak}")
    
    def test_my_streak_streak_to_next(self, player_token):
        """Test streak_to_next field calculation"""
        headers = {"Authorization": f"Bearer {player_token}"}
        response = requests.get(f"{BASE_URL}/api/contests/global/my-streak", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        streak = data["current_streak"]
        next_milestone = data["next_milestone"]
        streak_to_next = data.get("streak_to_next", 0)
        
        if next_milestone:
            expected_to_next = next_milestone - streak
            assert streak_to_next == expected_to_next, f"streak_to_next should be {expected_to_next}, got {streak_to_next}"
        else:
            assert streak_to_next == 0, "streak_to_next should be 0 when at max"
        
        print(f"PASS: streak_to_next calculation correct: {streak_to_next}")


class TestAuthMeStreakFields:
    """Test that /api/auth/me includes streak fields"""
    
    @pytest.fixture
    def player_token(self):
        """Get player auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_PLAYER)
        if response.status_code != 200:
            pytest.skip("Player login failed")
        return response.json()["token"]["access_token"]
    
    def test_auth_me_includes_streak_fields(self, player_token):
        """Test GET /api/auth/me includes prediction_streak and max_prediction_streak"""
        headers = {"Authorization": f"Bearer {player_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200, f"auth/me failed: {response.text}"
        data = response.json()
        
        # Check for streak fields
        assert "prediction_streak" in data, "auth/me missing 'prediction_streak' field"
        assert "max_prediction_streak" in data, "auth/me missing 'max_prediction_streak' field"
        
        # Verify they are integers
        assert isinstance(data["prediction_streak"], int), "prediction_streak should be int"
        assert isinstance(data["max_prediction_streak"], int), "max_prediction_streak should be int"
        
        # Verify they are >= 0
        assert data["prediction_streak"] >= 0, "prediction_streak should be >= 0"
        assert data["max_prediction_streak"] >= 0, "max_prediction_streak should be >= 0"
        
        print(f"PASS: auth/me includes streak fields: prediction_streak={data['prediction_streak']}, max_prediction_streak={data['max_prediction_streak']}")
    
    def test_auth_me_streak_fields_initialized(self, player_token):
        """Test that streak fields are initialized (not null/undefined)"""
        headers = {"Authorization": f"Bearer {player_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Fields should not be None
        assert data["prediction_streak"] is not None, "prediction_streak should not be None"
        assert data["max_prediction_streak"] is not None, "max_prediction_streak should not be None"
        
        print("PASS: Streak fields are properly initialized (not null)")


class TestSettlementEngineStreakFunctions:
    """Test settlement engine streak functions exist and work"""
    
    def test_get_streak_multiplier_function(self):
        """Test get_streak_multiplier function logic"""
        # Import the function
        import sys
        sys.path.insert(0, '/app/backend')
        from services.settlement_engine import get_streak_multiplier
        
        # Test multiplier logic
        assert get_streak_multiplier(0) == 1, "Streak 0 should return 1x"
        assert get_streak_multiplier(1) == 1, "Streak 1 should return 1x"
        assert get_streak_multiplier(4) == 1, "Streak 4 should return 1x"
        assert get_streak_multiplier(5) == 2, "Streak 5 should return 2x"
        assert get_streak_multiplier(7) == 2, "Streak 7 should return 2x"
        assert get_streak_multiplier(9) == 2, "Streak 9 should return 2x"
        assert get_streak_multiplier(10) == 4, "Streak 10 should return 4x"
        assert get_streak_multiplier(15) == 4, "Streak 15 should return 4x"
        assert get_streak_multiplier(100) == 4, "Streak 100 should return 4x"
        
        print("PASS: get_streak_multiplier function works correctly")
    
    def test_update_user_streaks_function_exists(self):
        """Test update_user_streaks function exists and is callable"""
        import sys
        sys.path.insert(0, '/app/backend')
        from services.settlement_engine import update_user_streaks
        
        assert callable(update_user_streaks), "update_user_streaks should be callable"
        print("PASS: update_user_streaks function exists and is callable")


class TestStreakKingLogic:
    """Test Streak King banner logic"""
    
    def test_top_streak_returns_is_hot_flag(self):
        """Test that top-streak returns is_hot flag for each user"""
        response = requests.get(f"{BASE_URL}/api/contests/global/top-streak?limit=10")
        assert response.status_code == 200
        data = response.json()
        
        for streak in data["streaks"]:
            assert "is_hot" in streak, "Streak entry missing 'is_hot' field"
            # is_hot should be True if current_streak >= 5
            if streak["current_streak"] >= 5:
                assert streak["is_hot"] == True, f"User with streak {streak['current_streak']} should be hot"
            else:
                assert streak["is_hot"] == False, f"User with streak {streak['current_streak']} should not be hot"
        
        print("PASS: is_hot flag correctly set based on streak >= 5")
    
    def test_top_streak_sorted_by_streak_desc(self):
        """Test that top-streak returns users sorted by current_streak descending"""
        response = requests.get(f"{BASE_URL}/api/contests/global/top-streak?limit=10")
        assert response.status_code == 200
        data = response.json()
        
        if len(data["streaks"]) > 1:
            for i in range(len(data["streaks"]) - 1):
                assert data["streaks"][i]["current_streak"] >= data["streaks"][i+1]["current_streak"], \
                    "Streaks should be sorted by current_streak descending"
        
        print("PASS: Top streaks sorted by current_streak descending")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
