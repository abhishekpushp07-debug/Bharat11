"""
Iteration 25 - Global Prediction Accuracy Badge Tests
Tests for:
- GET /api/contests/global/my-badge - User's badge with rank, accuracy stats
- GET /api/contests/global/prediction-leaderboard - Global leaderboard ranked by correct answers
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
SUPER_ADMIN_PHONE = "7004186276"
SUPER_ADMIN_PIN = "5524"
TEST_PLAYER_PHONE = "9111111111"
TEST_PLAYER_PIN = "5678"


class TestAuth:
    """Authentication tests"""
    
    def test_admin_login(self):
        """Test admin login returns token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": SUPER_ADMIN_PHONE,
            "pin": SUPER_ADMIN_PIN
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in response"
        assert "access_token" in data["token"], "No access_token in token"
        print(f"PASS: Admin login successful")


class TestGlobalBadgeEndpoints:
    """Tests for Global Prediction Accuracy Badge endpoints"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": SUPER_ADMIN_PHONE,
            "pin": SUPER_ADMIN_PIN
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json()["token"]["access_token"]
    
    def test_my_badge_requires_auth(self):
        """GET /api/contests/global/my-badge requires authentication"""
        response = requests.get(f"{BASE_URL}/api/contests/global/my-badge")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"PASS: my-badge requires auth (status {response.status_code})")
    
    def test_my_badge_with_auth(self, admin_token):
        """GET /api/contests/global/my-badge returns badge data for authenticated user"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/contests/global/my-badge", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Verify response structure
        assert "rank" in data, "Missing 'rank' field"
        assert "badge" in data, "Missing 'badge' field"
        assert "total_correct" in data, "Missing 'total_correct' field"
        assert "total_attempted" in data, "Missing 'total_attempted' field"
        assert "accuracy_pct" in data, "Missing 'accuracy_pct' field"
        assert "total_points_earned" in data, "Missing 'total_points_earned' field"
        assert "contests_count" in data, "Missing 'contests_count' field"
        
        print(f"PASS: my-badge returns valid structure")
        print(f"  - Rank: {data['rank']}")
        print(f"  - Badge: {data['badge']}")
        print(f"  - Correct: {data['total_correct']}/{data['total_attempted']}")
        print(f"  - Accuracy: {data['accuracy_pct']}%")
        print(f"  - Contests: {data['contests_count']}")
    
    def test_my_badge_values(self, admin_token):
        """Verify badge values are correct types and ranges"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/contests/global/my-badge", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        
        # If user has predictions, verify badge assignment
        if data["rank"] is not None:
            assert isinstance(data["rank"], int), "rank should be int"
            assert data["rank"] >= 1, "rank should be >= 1"
            
            # Badge should match rank
            expected_badge = (
                "pink_diamond" if data["rank"] == 1 else
                "gold" if data["rank"] == 2 else
                "silver" if data["rank"] == 3 else
                "blue_crystal"
            )
            assert data["badge"] == expected_badge, f"Badge mismatch: expected {expected_badge}, got {data['badge']}"
            
            assert isinstance(data["total_correct"], int), "total_correct should be int"
            assert isinstance(data["total_attempted"], int), "total_attempted should be int"
            assert data["total_correct"] <= data["total_attempted"], "correct cannot exceed attempted"
            
            assert isinstance(data["accuracy_pct"], (int, float)), "accuracy_pct should be numeric"
            assert 0 <= data["accuracy_pct"] <= 100, "accuracy_pct should be 0-100"
            
            print(f"PASS: Badge values are valid")
            print(f"  - Badge type '{data['badge']}' matches rank #{data['rank']}")
        else:
            # User has no predictions
            assert data["badge"] is None, "badge should be null for user with no predictions"
            assert data["total_correct"] == 0, "total_correct should be 0"
            assert data["total_attempted"] == 0, "total_attempted should be 0"
            print(f"PASS: User has no predictions, badge is null")
    
    def test_global_leaderboard_public(self):
        """GET /api/contests/global/prediction-leaderboard is public (no auth required)"""
        response = requests.get(f"{BASE_URL}/api/contests/global/prediction-leaderboard")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "leaderboard" in data, "Missing 'leaderboard' field"
        assert "total_ranked" in data, "Missing 'total_ranked' field"
        assert isinstance(data["leaderboard"], list), "leaderboard should be a list"
        
        print(f"PASS: Global leaderboard is public")
        print(f"  - Total ranked users: {data['total_ranked']}")
    
    def test_global_leaderboard_structure(self):
        """Verify global leaderboard entry structure"""
        response = requests.get(f"{BASE_URL}/api/contests/global/prediction-leaderboard?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        leaderboard = data["leaderboard"]
        
        if len(leaderboard) > 0:
            entry = leaderboard[0]
            required_fields = ["rank", "user_id", "username", "total_correct", "total_attempted", 
                             "accuracy_pct", "total_points_earned", "contests_count", "badge"]
            
            for field in required_fields:
                assert field in entry, f"Missing field '{field}' in leaderboard entry"
            
            # Verify rank 1 has pink_diamond badge
            assert entry["rank"] == 1, "First entry should be rank 1"
            assert entry["badge"] == "pink_diamond", f"Rank 1 should have pink_diamond badge, got {entry['badge']}"
            
            print(f"PASS: Leaderboard entry structure is valid")
            print(f"  - Rank 1: {entry['username']} - {entry['total_correct']}/{entry['total_attempted']} ({entry['accuracy_pct']}%)")
        else:
            print(f"PASS: Leaderboard is empty (no users with predictions)")
    
    def test_global_leaderboard_ranking(self):
        """Verify leaderboard is sorted by total_correct DESC"""
        response = requests.get(f"{BASE_URL}/api/contests/global/prediction-leaderboard?limit=50")
        assert response.status_code == 200
        
        data = response.json()
        leaderboard = data["leaderboard"]
        
        if len(leaderboard) >= 2:
            for i in range(len(leaderboard) - 1):
                current = leaderboard[i]
                next_entry = leaderboard[i + 1]
                
                # Verify ranks are sequential
                assert current["rank"] == i + 1, f"Rank mismatch at position {i}"
                
                # Verify sorted by total_correct DESC
                assert current["total_correct"] >= next_entry["total_correct"], \
                    f"Leaderboard not sorted: {current['total_correct']} < {next_entry['total_correct']}"
            
            print(f"PASS: Leaderboard is correctly sorted by total_correct DESC")
        else:
            print(f"PASS: Not enough entries to verify sorting (need >= 2)")
    
    def test_global_leaderboard_badge_assignment(self):
        """Verify badge assignment: Rank 1=pink_diamond, 2=gold, 3=silver, 4+=blue_crystal"""
        response = requests.get(f"{BASE_URL}/api/contests/global/prediction-leaderboard?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        leaderboard = data["leaderboard"]
        
        badge_map = {1: "pink_diamond", 2: "gold", 3: "silver"}
        
        for entry in leaderboard:
            expected = badge_map.get(entry["rank"], "blue_crystal")
            assert entry["badge"] == expected, \
                f"Rank {entry['rank']} should have {expected} badge, got {entry['badge']}"
        
        print(f"PASS: Badge assignment is correct for all {len(leaderboard)} entries")
    
    def test_global_leaderboard_limit_param(self):
        """Verify limit parameter works"""
        response = requests.get(f"{BASE_URL}/api/contests/global/prediction-leaderboard?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["leaderboard"]) <= 5, "Limit parameter not respected"
        print(f"PASS: Limit parameter works (returned {len(data['leaderboard'])} entries)")


class TestHealthCheck:
    """Basic health check"""
    
    def test_health_endpoint(self):
        """GET /api/health returns OK"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        print(f"PASS: Health endpoint OK")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
