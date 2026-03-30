"""
Iteration 24 - MoodMeter Backend Tests
Tests for:
- POST /api/matches/{id}/mood-vote (authenticated voting)
- GET /api/matches/{id}/mood-meter (public mood meter results)
- Team name validation
- User vote tracking
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

# Known match ID from previous testing (KKR vs MI completed match)
TEST_MATCH_ID = "e06a8963-410c-4901-bb96-807a3f258fe3"


class TestAuth:
    """Authentication helper tests"""
    
    def test_login_super_admin(self):
        """Test super admin login returns token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": SUPER_ADMIN_PHONE,
            "pin": SUPER_ADMIN_PIN
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in response"
        assert "access_token" in data["token"], "No access_token in token"
        print(f"PASS: Super admin login successful")
        return data["token"]["access_token"]


class TestMoodMeterEndpoints:
    """Tests for MoodMeter backend endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": SUPER_ADMIN_PHONE,
            "pin": SUPER_ADMIN_PIN
        })
        if response.status_code == 200:
            self.token = response.json()["token"]["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Authentication failed")
    
    def test_mood_meter_get_public(self):
        """GET /api/matches/{id}/mood-meter - Public endpoint returns vote counts"""
        response = requests.get(f"{BASE_URL}/api/matches/{TEST_MATCH_ID}/mood-meter")
        assert response.status_code == 200, f"Mood meter GET failed: {response.text}"
        
        data = response.json()
        # Verify response structure
        assert "match_id" in data, "Missing match_id"
        assert "team_a" in data, "Missing team_a"
        assert "team_b" in data, "Missing team_b"
        assert "team_a_votes" in data, "Missing team_a_votes"
        assert "team_b_votes" in data, "Missing team_b_votes"
        assert "team_a_pct" in data, "Missing team_a_pct"
        assert "team_b_pct" in data, "Missing team_b_pct"
        assert "total_votes" in data, "Missing total_votes"
        
        # Verify percentages add up to 100 (or close due to rounding)
        total_pct = data["team_a_pct"] + data["team_b_pct"]
        assert 99 <= total_pct <= 101, f"Percentages don't add up: {total_pct}"
        
        print(f"PASS: Mood meter GET returns {data['team_a']} ({data['team_a_pct']}%) vs {data['team_b']} ({data['team_b_pct']}%), {data['total_votes']} votes")
    
    def test_mood_meter_get_with_auth_shows_user_vote(self):
        """GET /api/matches/{id}/mood-meter with auth shows user_vote field"""
        response = requests.get(
            f"{BASE_URL}/api/matches/{TEST_MATCH_ID}/mood-meter",
            headers=self.headers
        )
        assert response.status_code == 200, f"Mood meter GET with auth failed: {response.text}"
        
        data = response.json()
        # user_vote should be present (may be null if user hasn't voted)
        assert "user_vote" in data, "Missing user_vote field"
        print(f"PASS: Mood meter with auth shows user_vote: {data.get('user_vote')}")
    
    def test_mood_vote_requires_auth(self):
        """POST /api/matches/{id}/mood-vote requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/matches/{TEST_MATCH_ID}/mood-vote",
            json={"team": "KKR"}
        )
        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403], f"Expected auth error, got {response.status_code}"
        print(f"PASS: Mood vote requires authentication (got {response.status_code})")
    
    def test_mood_vote_validates_team_name(self):
        """POST /api/matches/{id}/mood-vote validates team name against match teams"""
        response = requests.post(
            f"{BASE_URL}/api/matches/{TEST_MATCH_ID}/mood-vote",
            json={"team": "INVALID_TEAM"},
            headers=self.headers
        )
        assert response.status_code == 400, f"Expected 400 for invalid team, got {response.status_code}"
        
        data = response.json()
        assert "detail" in data, "Missing error detail"
        assert "Invalid team" in data["detail"] or "Choose from" in data["detail"], f"Unexpected error: {data['detail']}"
        print(f"PASS: Invalid team name rejected with message: {data['detail']}")
    
    def test_mood_vote_success(self):
        """POST /api/matches/{id}/mood-vote with valid team succeeds"""
        # First get the match to know valid team names
        match_response = requests.get(f"{BASE_URL}/api/matches/{TEST_MATCH_ID}")
        assert match_response.status_code == 200
        match = match_response.json()
        
        team_a = match.get("team_a", {}).get("short_name", "KKR")
        team_b = match.get("team_b", {}).get("short_name", "MI")
        
        # Vote for team_a
        response = requests.post(
            f"{BASE_URL}/api/matches/{TEST_MATCH_ID}/mood-vote",
            json={"team": team_a},
            headers=self.headers
        )
        assert response.status_code == 200, f"Mood vote failed: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Vote not successful"
        assert data.get("your_vote") == team_a, f"Vote not recorded correctly: {data.get('your_vote')}"
        assert "team_a_votes" in data, "Missing vote counts"
        assert "team_a_pct" in data, "Missing percentages"
        assert "total_votes" in data, "Missing total_votes"
        
        print(f"PASS: Voted for {team_a}, total votes: {data['total_votes']}")
    
    def test_mood_vote_can_change_vote(self):
        """POST /api/matches/{id}/mood-vote allows changing vote (upsert)"""
        # Get valid team names
        match_response = requests.get(f"{BASE_URL}/api/matches/{TEST_MATCH_ID}")
        match = match_response.json()
        team_b = match.get("team_b", {}).get("short_name", "MI")
        
        # Vote for team_b (changing from previous vote)
        response = requests.post(
            f"{BASE_URL}/api/matches/{TEST_MATCH_ID}/mood-vote",
            json={"team": team_b},
            headers=self.headers
        )
        assert response.status_code == 200, f"Vote change failed: {response.text}"
        
        data = response.json()
        assert data.get("your_vote") == team_b, f"Vote not changed: {data.get('your_vote')}"
        print(f"PASS: Vote changed to {team_b}")
    
    def test_mood_meter_invalid_match(self):
        """GET /api/matches/{invalid_id}/mood-meter returns 404"""
        response = requests.get(f"{BASE_URL}/api/matches/invalid-match-id-12345/mood-meter")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"PASS: Invalid match returns 404")
    
    def test_mood_vote_invalid_match(self):
        """POST /api/matches/{invalid_id}/mood-vote returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/matches/invalid-match-id-12345/mood-vote",
            json={"team": "KKR"},
            headers=self.headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"PASS: Vote on invalid match returns 404")


class TestMatchEndpoints:
    """Verify existing match endpoints still work"""
    
    def test_matches_list(self):
        """GET /api/matches returns matches"""
        response = requests.get(f"{BASE_URL}/api/matches?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        print(f"PASS: Matches list returns {len(data['matches'])} matches")
    
    def test_match_detail(self):
        """GET /api/matches/{id} returns match details"""
        response = requests.get(f"{BASE_URL}/api/matches/{TEST_MATCH_ID}")
        assert response.status_code == 200
        data = response.json()
        assert "team_a" in data
        assert "team_b" in data
        assert "short_name" in data["team_a"]
        assert "short_name" in data["team_b"]
        print(f"PASS: Match detail returns {data['team_a']['short_name']} vs {data['team_b']['short_name']}")
    
    def test_match_contests(self):
        """GET /api/matches/{id}/contests returns contests"""
        response = requests.get(f"{BASE_URL}/api/matches/{TEST_MATCH_ID}/contests")
        assert response.status_code == 200
        data = response.json()
        assert "contests" in data
        print(f"PASS: Match contests returns {len(data['contests'])} contests")


class TestHealthEndpoint:
    """Basic health check"""
    
    def test_health(self):
        """GET /api/health returns OK"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print(f"PASS: Health endpoint OK")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
