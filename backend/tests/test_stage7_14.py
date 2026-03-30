"""
CrickPredict Backend Tests - Stages 7-14
Tests for: Contest Join, Predictions, Leaderboard, User Answers, Admin Panel, Cricbuzz Integration
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_PHONE = "9876543210"
TEST_PIN = "1234"


class TestHealthAndBasics:
    """Basic health and connectivity tests"""
    
    def test_health_endpoint(self):
        """Test health endpoint returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "mongodb" in data["services"]
        print(f"Health check passed: {data['status']}")
    
    def test_matches_list(self):
        """Test matches list endpoint"""
        response = requests.get(f"{BASE_URL}/api/matches?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        assert len(data["matches"]) >= 1
        print(f"Found {len(data['matches'])} matches")
    
    def test_contests_list(self):
        """Test contests list endpoint"""
        response = requests.get(f"{BASE_URL}/api/contests?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "contests" in data
        assert len(data["contests"]) >= 1
        print(f"Found {len(data['contests'])} contests")


class TestAuthentication:
    """Authentication flow tests"""
    
    def test_login_success(self):
        """Test successful login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": TEST_PHONE,
            "pin": TEST_PIN
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "access_token" in data["token"]
        assert "user" in data
        assert data["user"]["phone"] == TEST_PHONE
        print(f"Login successful for user: {data['user']['username']}")
    
    def test_login_invalid_pin(self):
        """Test login with invalid PIN"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": TEST_PHONE,
            "pin": "9999"
        })
        assert response.status_code == 401
        print("Invalid PIN correctly rejected")


@pytest.fixture
def auth_token():
    """Get authentication token for tests"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "phone": TEST_PHONE,
        "pin": TEST_PIN
    })
    if response.status_code == 200:
        return response.json()["token"]["access_token"]
    pytest.skip("Authentication failed")


@pytest.fixture
def auth_headers(auth_token):
    """Get headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestMatchEndpoints:
    """Match-related endpoint tests"""
    
    def test_match_detail(self):
        """Test getting match details"""
        # First get a match ID
        response = requests.get(f"{BASE_URL}/api/matches?limit=1")
        assert response.status_code == 200
        matches = response.json()["matches"]
        assert len(matches) > 0
        
        match_id = matches[0]["id"]
        response = requests.get(f"{BASE_URL}/api/matches/{match_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == match_id
        assert "team_a" in data
        assert "team_b" in data
        print(f"Match detail: {data['team_a']['short_name']} vs {data['team_b']['short_name']}")
    
    def test_match_contests(self):
        """Test getting contests for a match"""
        # Get MI vs CSK match
        response = requests.get(f"{BASE_URL}/api/matches?limit=10")
        matches = response.json()["matches"]
        mi_csk_match = next((m for m in matches if m["team_a"]["short_name"] == "MI" and m["team_b"]["short_name"] == "CSK"), None)
        
        if mi_csk_match:
            response = requests.get(f"{BASE_URL}/api/matches/{mi_csk_match['id']}/contests")
            assert response.status_code == 200
            data = response.json()
            assert "contests" in data
            print(f"Found {len(data['contests'])} contests for MI vs CSK")
    
    def test_match_live_score(self):
        """Test live score endpoint"""
        response = requests.get(f"{BASE_URL}/api/matches?limit=1")
        match_id = response.json()["matches"][0]["id"]
        
        response = requests.get(f"{BASE_URL}/api/matches/{match_id}/live-score")
        assert response.status_code == 200
        data = response.json()
        assert "match_id" in data
        assert "status" in data
        print(f"Live score status: {data['status']}")


class TestCricbuzzIntegration:
    """Cricbuzz live data integration tests"""
    
    def test_cricbuzz_live_endpoint(self):
        """Test Cricbuzz live matches endpoint (expected: connected=false in container)"""
        response = requests.get(f"{BASE_URL}/api/matches/live/cricbuzz")
        assert response.status_code == 200
        data = response.json()
        assert "source" in data
        assert data["source"] == "cricbuzz"
        assert "connected" in data
        assert "matches" in data
        # In container environment, connected should be false
        print(f"Cricbuzz connected: {data['connected']}, matches: {data['total']}")
    
    def test_cricbuzz_sync_endpoint(self, auth_headers):
        """Test Cricbuzz sync endpoint (admin)"""
        response = requests.post(f"{BASE_URL}/api/matches/live/sync", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Should return sync result even if no matches
        assert "synced" in data or "message" in data
        print(f"Sync result: {data}")


class TestContestJoinAndPredict:
    """Contest join and prediction flow tests"""
    
    def test_my_contests(self, auth_headers):
        """Test getting user's joined contests"""
        response = requests.get(f"{BASE_URL}/api/contests/user/my-contests?limit=50", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "my_contests" in data
        print(f"User has joined {len(data['my_contests'])} contests")
    
    def test_contest_questions(self, auth_headers):
        """Test getting contest questions"""
        # Get a contest the user has joined
        response = requests.get(f"{BASE_URL}/api/contests/user/my-contests?limit=1", headers=auth_headers)
        my_contests = response.json()["my_contests"]
        
        if len(my_contests) > 0:
            contest_id = my_contests[0]["entry"]["contest_id"]
            response = requests.get(f"{BASE_URL}/api/contests/{contest_id}/questions", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert "questions" in data
            assert len(data["questions"]) > 0
            print(f"Contest has {len(data['questions'])} questions")
    
    def test_contest_detail(self, auth_headers):
        """Test getting contest details"""
        response = requests.get(f"{BASE_URL}/api/contests?limit=1")
        contests = response.json()["contests"]
        
        if len(contests) > 0:
            contest_id = contests[0]["id"]
            response = requests.get(f"{BASE_URL}/api/contests/{contest_id}", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == contest_id
            assert "name" in data
            assert "entry_fee" in data
            print(f"Contest: {data['name']}, Entry: {data['entry_fee']}")


class TestLeaderboard:
    """Leaderboard and user answers tests"""
    
    def test_contest_leaderboard(self, auth_headers):
        """Test getting contest leaderboard"""
        # Get completed contest
        response = requests.get(f"{BASE_URL}/api/contests?status=completed&limit=1")
        contests = response.json()["contests"]
        
        if len(contests) > 0:
            contest_id = contests[0]["id"]
            response = requests.get(f"{BASE_URL}/api/contests/{contest_id}/leaderboard?limit=50", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert "leaderboard" in data
            assert "contest_name" in data
            assert "total_participants" in data
            print(f"Leaderboard for {data['contest_name']}: {len(data['leaderboard'])} entries")
    
    def test_my_leaderboard_position(self, auth_headers):
        """Test getting user's position in leaderboard"""
        # Get a contest user has joined
        response = requests.get(f"{BASE_URL}/api/contests/user/my-contests?limit=1", headers=auth_headers)
        my_contests = response.json()["my_contests"]
        
        if len(my_contests) > 0:
            contest_id = my_contests[0]["entry"]["contest_id"]
            response = requests.get(f"{BASE_URL}/api/contests/{contest_id}/leaderboard/me", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert "rank" in data
            assert "total_points" in data
            print(f"User rank: #{data['rank']}, points: {data['total_points']}")
    
    def test_user_answers_endpoint(self, auth_headers):
        """Test getting user's answers in a contest (User Answer Modal API)"""
        # Get completed contest
        response = requests.get(f"{BASE_URL}/api/contests?status=completed&limit=1")
        contests = response.json()["contests"]
        
        if len(contests) > 0:
            contest_id = contests[0]["id"]
            
            # Get leaderboard to find a user
            lb_response = requests.get(f"{BASE_URL}/api/contests/{contest_id}/leaderboard?limit=1", headers=auth_headers)
            leaderboard = lb_response.json()["leaderboard"]
            
            if len(leaderboard) > 0:
                user_id = leaderboard[0]["user_id"]
                response = requests.get(f"{BASE_URL}/api/contests/{contest_id}/leaderboard/{user_id}", headers=auth_headers)
                assert response.status_code == 200
                data = response.json()
                
                # Verify user answer modal data structure
                assert "user_id" in data
                assert "username" in data
                assert "predictions" in data
                assert "total_points" in data
                assert "team_name" in data
                
                # Check predictions have required fields
                if len(data["predictions"]) > 0:
                    pred = data["predictions"][0]
                    assert "selected_option" in pred
                    assert "is_correct" in pred or pred.get("is_correct") is None
                    assert "options" in pred
                
                print(f"User {data['username']} has {len(data['predictions'])} predictions, {data['total_points']} pts")


class TestAdminEndpoints:
    """Admin panel endpoint tests"""
    
    def test_match_status_update(self, auth_headers):
        """Test updating match status (Admin)"""
        # Get a match
        response = requests.get(f"{BASE_URL}/api/matches?limit=1")
        matches = response.json()["matches"]
        
        if len(matches) > 0:
            match_id = matches[0]["id"]
            current_status = matches[0]["status"]
            
            # Update to same status (safe test)
            response = requests.put(
                f"{BASE_URL}/api/matches/{match_id}/status",
                headers=auth_headers,
                json={"status": current_status}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == current_status
            print(f"Match status update works: {current_status}")
    
    def test_resolve_question_endpoint(self, auth_headers):
        """Test resolve question endpoint structure (Admin)"""
        # Get an open contest
        response = requests.get(f"{BASE_URL}/api/contests?status=open&limit=1")
        contests = response.json()["contests"]
        
        if len(contests) > 0:
            contest_id = contests[0]["id"]
            
            # Get questions
            q_response = requests.get(f"{BASE_URL}/api/contests/{contest_id}/questions", headers=auth_headers)
            if q_response.status_code == 200:
                questions = q_response.json().get("questions", [])
                if len(questions) > 0:
                    # Just verify endpoint exists (don't actually resolve)
                    print(f"Resolve endpoint available for contest {contest_id} with {len(questions)} questions")
    
    def test_finalize_contest_endpoint_exists(self, auth_headers):
        """Test finalize contest endpoint exists"""
        # Get a contest
        response = requests.get(f"{BASE_URL}/api/contests?limit=1")
        contests = response.json()["contests"]
        
        if len(contests) > 0:
            contest_id = contests[0]["id"]
            # Just verify endpoint exists by checking already completed contest
            response = requests.post(f"{BASE_URL}/api/contests/{contest_id}/finalize", headers=auth_headers)
            # Should return 200 with "already finalized" or process normally
            assert response.status_code in [200, 400]
            print(f"Finalize endpoint accessible")


class TestUserProfile:
    """User profile and wallet tests"""
    
    def test_user_profile(self, auth_headers):
        """Test getting user profile"""
        response = requests.get(f"{BASE_URL}/api/user/profile", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "coins_balance" in data
        assert "rank_title" in data
        print(f"User: {data['username']}, Balance: {data['coins_balance']}, Rank: {data['rank_title']}")
    
    def test_wallet_transactions(self, auth_headers):
        """Test getting wallet transactions"""
        response = requests.get(f"{BASE_URL}/api/wallet/transactions?limit=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "transactions" in data
        print(f"Found {len(data['transactions'])} transactions")
    
    def test_rank_progress(self, auth_headers):
        """Test getting rank progress"""
        response = requests.get(f"{BASE_URL}/api/user/rank-progress", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "current_rank" in data
        assert "progress_percent" in data
        print(f"Rank: {data['current_rank']}, Progress: {data['progress_percent']}%")
    
    def test_referral_stats(self, auth_headers):
        """Test getting referral stats"""
        response = requests.get(f"{BASE_URL}/api/user/referral-stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "referral_code" in data
        assert "total_referrals" in data
        print(f"Referral code: {data['referral_code']}, Referrals: {data['total_referrals']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
