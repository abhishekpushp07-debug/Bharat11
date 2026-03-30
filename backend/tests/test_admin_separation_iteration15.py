"""
Bharat 11 - Admin/Player Separation Tests (Iteration 15)
Tests:
- Auth flow: check-phone endpoint
- Admin separation: is_admin flag in responses
- Admin APIs: stats, questions, templates, matches, contests
- Player restrictions: 403 on admin endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
SUPER_ADMIN = {"phone": "7004186276", "pin": "5524"}
REGULAR_PLAYER = {"phone": "9111111111", "pin": "5678"}
OLD_ADMIN = {"phone": "9876543210", "pin": "1234"}


class TestAuthCheckPhone:
    """Test POST /api/auth/check-phone endpoint"""
    
    def test_check_phone_existing_user(self):
        """Existing user (super admin) should return exists: true"""
        response = requests.post(f"{BASE_URL}/api/auth/check-phone", json={"phone": SUPER_ADMIN["phone"]})
        assert response.status_code == 200
        data = response.json()
        assert data["exists"] == True
        print(f"PASS: check-phone for existing user returns exists=true")
    
    def test_check_phone_new_user(self):
        """New phone number should return exists: false"""
        response = requests.post(f"{BASE_URL}/api/auth/check-phone", json={"phone": "9999999999"})
        assert response.status_code == 200
        data = response.json()
        assert data["exists"] == False
        print(f"PASS: check-phone for new phone returns exists=false")
    
    def test_check_phone_regular_player(self):
        """Regular player should return exists: true"""
        response = requests.post(f"{BASE_URL}/api/auth/check-phone", json={"phone": REGULAR_PLAYER["phone"]})
        assert response.status_code == 200
        data = response.json()
        assert data["exists"] == True
        print(f"PASS: check-phone for regular player returns exists=true")


class TestAdminSeparation:
    """Test admin vs player separation in auth responses"""
    
    def test_super_admin_login_has_is_admin_true(self):
        """Super admin login should return is_admin: true"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=SUPER_ADMIN)
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert data["user"]["is_admin"] == True
        assert data["user"]["phone"] == SUPER_ADMIN["phone"]
        print(f"PASS: Super admin login returns is_admin=true")
    
    def test_regular_player_login_has_is_admin_false(self):
        """Regular player login should return is_admin: false"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=REGULAR_PLAYER)
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert data["user"]["is_admin"] == False
        assert data["user"]["phone"] == REGULAR_PLAYER["phone"]
        print(f"PASS: Regular player login returns is_admin=false")
    
    def test_old_admin_login_has_is_admin_true(self):
        """Old admin (9876543210) should also have is_admin: true"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=OLD_ADMIN)
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert data["user"]["is_admin"] == True
        print(f"PASS: Old admin login returns is_admin=true")


class TestAdminAPIs:
    """Test admin-only API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=SUPER_ADMIN)
        self.admin_token = response.json()["token"]["access_token"]
        self.headers = {"Authorization": f"Bearer {self.admin_token}"}
    
    def test_admin_stats_endpoint(self):
        """GET /api/admin/stats should return stats for admin"""
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "questions" in data
        assert "templates" in data
        assert "matches" in data
        assert "contests" in data
        print(f"PASS: Admin stats endpoint returns all counts: users={data['users']}, questions={data['questions']}")
    
    def test_admin_questions_list(self):
        """GET /api/admin/questions should return questions list"""
        response = requests.get(f"{BASE_URL}/api/admin/questions", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "questions" in data
        print(f"PASS: Admin questions list returns {len(data['questions'])} questions")
    
    def test_admin_templates_list(self):
        """GET /api/admin/templates should return templates list"""
        response = requests.get(f"{BASE_URL}/api/admin/templates", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        print(f"PASS: Admin templates list returns {len(data['templates'])} templates")
    
    def test_admin_matches_list(self):
        """GET /api/matches should return matches list"""
        response = requests.get(f"{BASE_URL}/api/matches", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        print(f"PASS: Matches list returns {len(data['matches'])} matches")
    
    def test_admin_contests_list(self):
        """GET /api/contests should return contests list"""
        response = requests.get(f"{BASE_URL}/api/contests", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "contests" in data
        print(f"PASS: Contests list returns {len(data['contests'])} contests")


class TestPlayerRestrictions:
    """Test that regular players cannot access admin endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get player token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=REGULAR_PLAYER)
        self.player_token = response.json()["token"]["access_token"]
        self.headers = {"Authorization": f"Bearer {self.player_token}"}
    
    def test_player_cannot_access_admin_stats(self):
        """Regular player should get 403 on admin stats"""
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=self.headers)
        assert response.status_code == 403
        print(f"PASS: Player gets 403 on admin stats")
    
    def test_player_cannot_create_match(self):
        """Regular player should get 403 on match creation"""
        response = requests.post(f"{BASE_URL}/api/matches", headers=self.headers, json={
            "team1": "IND", "team2": "AUS", "venue": "Test", "start_time": "2026-04-01T10:00:00Z"
        })
        assert response.status_code == 403
        print(f"PASS: Player gets 403 on match creation")
    
    def test_player_cannot_create_contest(self):
        """Regular player should get 403 on contest creation"""
        response = requests.post(f"{BASE_URL}/api/admin/contests", headers=self.headers, json={
            "match_id": "test", "template_id": "test", "entry_fee": 100, "prize_pool": 1000
        })
        assert response.status_code == 403
        print(f"PASS: Player gets 403 on contest creation")
    
    def test_player_can_access_public_matches(self):
        """Regular player should be able to access public matches list"""
        response = requests.get(f"{BASE_URL}/api/matches", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        print(f"PASS: Player can access public matches list")
    
    def test_player_can_access_wallet(self):
        """Regular player should be able to access wallet"""
        response = requests.get(f"{BASE_URL}/api/wallet/balance", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "balance" in data
        print(f"PASS: Player can access wallet balance: {data['balance']}")


class TestRegressionAPIs:
    """Regression tests for core functionality"""
    
    def test_health_check(self):
        """Health check should return healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"PASS: Health check returns healthy")
    
    def test_auth_me_with_admin_token(self):
        """GET /api/auth/me should return user with is_admin"""
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json=SUPER_ADMIN)
        token = login_res.json()["token"]["access_token"]
        
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["is_admin"] == True
        print(f"PASS: /auth/me returns is_admin=true for admin")
    
    def test_auth_me_with_player_token(self):
        """GET /api/auth/me should return user with is_admin=false for player"""
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json=REGULAR_PLAYER)
        token = login_res.json()["token"]["access_token"]
        
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["is_admin"] == False
        print(f"PASS: /auth/me returns is_admin=false for player")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
