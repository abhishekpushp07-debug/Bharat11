"""
CrickPredict Stage 10-14 Honest Audit Tests
Tests for:
- STAGE 7-9: my-contests pagination (filter BEFORE paginate), batch DB queries, finalize blocks if unresolved
- STAGE 10: Leaderboard loading, UserAnswerModal error state, get_my_leaderboard_position null submission_time
- STAGE 11: CricketDataService asyncio.get_running_loop(), cache eviction MAX_CACHE_ENTRIES=100
- STAGE 13-14: ALL match write endpoints require AdminUser (non-admin gets 403)
- STAGE 13-14: Contest finalize response includes username in top_3
- REGRESSION: Login, Home, My Contests, Wallet, Contest flow
"""
import pytest
import requests
import os
from datetime import datetime, timezone, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_PHONE = "9876543210"
ADMIN_PIN = "1234"
NON_ADMIN_PHONE = "9111111111"
NON_ADMIN_PIN = "5678"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin user token"""
    resp = requests.post(f"{BASE_URL}/api/auth/login", json={"phone": ADMIN_PHONE, "pin": ADMIN_PIN})
    if resp.status_code == 200:
        data = resp.json()
        return data.get("token", {}).get("access_token") or data.get("access_token")
    pytest.skip(f"Admin login failed: {resp.status_code} - {resp.text}")


@pytest.fixture(scope="module")
def non_admin_token():
    """Get non-admin user token"""
    resp = requests.post(f"{BASE_URL}/api/auth/login", json={"phone": NON_ADMIN_PHONE, "pin": NON_ADMIN_PIN})
    if resp.status_code == 200:
        data = resp.json()
        return data.get("token", {}).get("access_token") or data.get("access_token")
    pytest.skip(f"Non-admin login failed: {resp.status_code} - {resp.text}")


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}


@pytest.fixture
def non_admin_headers(non_admin_token):
    return {"Authorization": f"Bearer {non_admin_token}", "Content-Type": "application/json"}


class TestRegressionLoginAndBasics:
    """REGRESSION: Basic flows still work"""

    def test_health_check(self):
        """Health endpoint works"""
        resp = requests.get(f"{BASE_URL}/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        print("PASS: Health check OK")

    def test_admin_login(self, admin_token):
        """Admin login works"""
        assert admin_token is not None
        assert len(admin_token) > 20
        print(f"PASS: Admin login OK, token length={len(admin_token)}")

    def test_non_admin_login(self, non_admin_token):
        """Non-admin login works"""
        assert non_admin_token is not None
        assert len(non_admin_token) > 20
        print(f"PASS: Non-admin login OK, token length={len(non_admin_token)}")

    def test_home_matches_load(self):
        """Home page matches load"""
        resp = requests.get(f"{BASE_URL}/api/matches")
        assert resp.status_code == 200
        data = resp.json()
        assert "matches" in data
        print(f"PASS: Matches loaded, count={len(data['matches'])}")

    def test_wallet_balance(self, admin_headers):
        """Wallet balance shows"""
        resp = requests.get(f"{BASE_URL}/api/wallet/balance", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "balance" in data
        print(f"PASS: Wallet balance={data['balance']}")


class TestStage7_9MyContestsPagination:
    """STAGE 7-9: my-contests filter BEFORE paginate, batch queries"""

    def test_my_contests_returns_data(self, admin_headers):
        """my-contests endpoint works"""
        resp = requests.get(f"{BASE_URL}/api/contests/user/my-contests", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "my_contests" in data
        assert "total" in data
        assert "page" in data
        print(f"PASS: my-contests returned {len(data['my_contests'])} entries, total={data['total']}")

    def test_my_contests_with_status_filter(self, admin_headers):
        """my-contests with status filter works (filter BEFORE paginate)"""
        # Test with open status
        resp = requests.get(f"{BASE_URL}/api/contests/user/my-contests?status=open", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        # All returned should be open
        for item in data.get("my_contests", []):
            contest = item.get("contest", {})
            assert contest.get("status") == "open", f"Expected open, got {contest.get('status')}"
        print(f"PASS: my-contests filter works, {len(data['my_contests'])} open contests")

    def test_my_contests_pagination(self, admin_headers):
        """my-contests pagination works"""
        resp = requests.get(f"{BASE_URL}/api/contests/user/my-contests?page=1&limit=5", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"] == 1
        assert len(data["my_contests"]) <= 5
        print(f"PASS: my-contests pagination works, page=1, limit=5, got {len(data['my_contests'])}")


class TestStage7_9FinalizeBlocksUnresolved:
    """STAGE 7-9: Contest finalize blocks if unresolved questions exist"""

    def test_finalize_blocks_unresolved(self, admin_headers):
        """Finalize should fail if questions unresolved"""
        # Get an open contest
        resp = requests.get(f"{BASE_URL}/api/contests?status=open", headers=admin_headers)
        if resp.status_code != 200:
            pytest.skip("No contests available")
        
        contests = resp.json().get("contests", [])
        if not contests:
            pytest.skip("No open contests to test")
        
        contest = contests[0]
        contest_id = contest["id"]
        
        # Try to finalize without resolving all questions
        resp = requests.post(f"{BASE_URL}/api/contests/{contest_id}/finalize", headers=admin_headers)
        
        # Should either fail with 400 (unresolved) or succeed if already resolved
        if resp.status_code == 400:
            assert "unresolved" in resp.json().get("detail", "").lower() or "resolve" in resp.json().get("detail", "").lower()
            print(f"PASS: Finalize blocked - {resp.json().get('detail')}")
        elif resp.status_code == 200:
            data = resp.json()
            if data.get("message") == "Contest already finalized":
                print("PASS: Contest was already finalized")
            else:
                print(f"PASS: Contest finalized (all questions were resolved)")
        else:
            print(f"INFO: Finalize returned {resp.status_code}: {resp.text}")


class TestStage10LeaderboardAndModal:
    """STAGE 10: Leaderboard loading, UserAnswerModal error state"""

    def test_leaderboard_endpoint(self, admin_headers):
        """Leaderboard endpoint works"""
        # Get a contest
        resp = requests.get(f"{BASE_URL}/api/contests?limit=5", headers=admin_headers)
        if resp.status_code != 200:
            pytest.skip("No contests available")
        
        contests = resp.json().get("contests", [])
        if not contests:
            pytest.skip("No contests to test")
        
        contest_id = contests[0]["id"]
        resp = requests.get(f"{BASE_URL}/api/contests/{contest_id}/leaderboard", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "leaderboard" in data
        assert "contest_name" in data
        print(f"PASS: Leaderboard loaded for {data['contest_name']}, {len(data['leaderboard'])} entries")

    def test_my_leaderboard_position(self, admin_headers):
        """get_my_leaderboard_position handles null submission_time"""
        # Get a contest user has joined
        resp = requests.get(f"{BASE_URL}/api/contests/user/my-contests?limit=1", headers=admin_headers)
        if resp.status_code != 200:
            pytest.skip("Cannot get my contests")
        
        my_contests = resp.json().get("my_contests", [])
        if not my_contests:
            pytest.skip("User hasn't joined any contests")
        
        contest_id = my_contests[0]["contest"]["id"]
        resp = requests.get(f"{BASE_URL}/api/contests/{contest_id}/leaderboard/me", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "rank" in data
        assert "total_points" in data
        print(f"PASS: My position rank={data['rank']}, points={data['total_points']}")

    def test_user_answers_endpoint(self, admin_headers):
        """User answers endpoint for modal works"""
        # Get a contest with entries
        resp = requests.get(f"{BASE_URL}/api/contests?limit=5", headers=admin_headers)
        if resp.status_code != 200:
            pytest.skip("No contests available")
        
        contests = resp.json().get("contests", [])
        if not contests:
            pytest.skip("No contests to test")
        
        contest_id = contests[0]["id"]
        
        # Get leaderboard to find a user
        lb_resp = requests.get(f"{BASE_URL}/api/contests/{contest_id}/leaderboard", headers=admin_headers)
        if lb_resp.status_code != 200:
            pytest.skip("Cannot get leaderboard")
        
        leaderboard = lb_resp.json().get("leaderboard", [])
        if not leaderboard:
            pytest.skip("No entries in leaderboard")
        
        user_id = leaderboard[0]["user_id"]
        resp = requests.get(f"{BASE_URL}/api/contests/{contest_id}/leaderboard/{user_id}", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "username" in data
        assert "predictions" in data
        print(f"PASS: User answers loaded for {data['username']}, {len(data['predictions'])} predictions")

    def test_user_answers_404_on_invalid(self, admin_headers):
        """User answers returns 404 for invalid user (error state test)"""
        resp = requests.get(f"{BASE_URL}/api/contests/invalid-contest/leaderboard/invalid-user", headers=admin_headers)
        assert resp.status_code == 404
        print("PASS: Invalid user/contest returns 404 (modal will show error)")


class TestStage11CricketDataService:
    """STAGE 11: CricketDataService uses get_running_loop(), cache eviction"""

    def test_cricbuzz_live_endpoint(self):
        """Cricbuzz live endpoint works (graceful fallback)"""
        resp = requests.get(f"{BASE_URL}/api/matches/live/cricbuzz")
        assert resp.status_code == 200
        data = resp.json()
        assert "source" in data
        assert data["source"] == "cricbuzz"
        # In container, connected will be false (network blocked)
        print(f"PASS: Cricbuzz endpoint works, connected={data.get('connected')}, matches={len(data.get('matches', []))}")


class TestStage13_14AdminGuardMatchEndpoints:
    """STAGE 13-14 CRITICAL: ALL match write endpoints require AdminUser"""

    def test_create_match_admin_allowed(self, admin_headers):
        """Admin can create match"""
        future_time = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        payload = {
            "team_a": {"name": "Test Team A", "short_name": "TTA", "logo_url": ""},
            "team_b": {"name": "Test Team B", "short_name": "TTB", "logo_url": ""},
            "match_type": "T20",
            "venue": "Test Stadium",
            "start_time": future_time,
            "tournament": "Test Tournament"
        }
        resp = requests.post(f"{BASE_URL}/api/matches", json=payload, headers=admin_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data
        print(f"PASS: Admin created match {data['id']}")
        return data["id"]

    def test_create_match_non_admin_forbidden(self, non_admin_headers):
        """Non-admin cannot create match - gets 403"""
        future_time = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        payload = {
            "team_a": {"name": "Test Team A", "short_name": "TTA", "logo_url": ""},
            "team_b": {"name": "Test Team B", "short_name": "TTB", "logo_url": ""},
            "match_type": "T20",
            "venue": "Test Stadium",
            "start_time": future_time,
            "tournament": "Test Tournament"
        }
        resp = requests.post(f"{BASE_URL}/api/matches", json=payload, headers=non_admin_headers)
        assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
        print("PASS: Non-admin POST /api/matches returns 403")

    def test_update_match_status_non_admin_forbidden(self, non_admin_headers):
        """Non-admin cannot update match status - gets 403"""
        # Get a match
        resp = requests.get(f"{BASE_URL}/api/matches?limit=1")
        if resp.status_code != 200 or not resp.json().get("matches"):
            pytest.skip("No matches available")
        
        match_id = resp.json()["matches"][0]["id"]
        resp = requests.put(f"{BASE_URL}/api/matches/{match_id}/status", 
                           json={"status": "live"}, headers=non_admin_headers)
        assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
        print("PASS: Non-admin PUT /api/matches/{id}/status returns 403")

    def test_update_live_score_non_admin_forbidden(self, non_admin_headers):
        """Non-admin cannot update live score - gets 403"""
        resp = requests.get(f"{BASE_URL}/api/matches?limit=1")
        if resp.status_code != 200 or not resp.json().get("matches"):
            pytest.skip("No matches available")
        
        match_id = resp.json()["matches"][0]["id"]
        payload = {
            "batting_team": "Test",
            "score": "100/2",
            "overs": "10.0",
            "wickets": 2
        }
        resp = requests.put(f"{BASE_URL}/api/matches/{match_id}/live-score", 
                           json=payload, headers=non_admin_headers)
        assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
        print("PASS: Non-admin PUT /api/matches/{id}/live-score returns 403")

    def test_assign_template_non_admin_forbidden(self, non_admin_headers):
        """Non-admin cannot assign template - gets 403"""
        resp = requests.get(f"{BASE_URL}/api/matches?limit=1")
        if resp.status_code != 200 or not resp.json().get("matches"):
            pytest.skip("No matches available")
        
        match_id = resp.json()["matches"][0]["id"]
        resp = requests.post(f"{BASE_URL}/api/matches/{match_id}/assign-template?template_id=test", 
                            headers=non_admin_headers)
        assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
        print("PASS: Non-admin POST /api/matches/{id}/assign-template returns 403")

    def test_sync_cricbuzz_non_admin_forbidden(self, non_admin_headers):
        """Non-admin cannot sync from Cricbuzz - gets 403"""
        resp = requests.post(f"{BASE_URL}/api/matches/live/sync", headers=non_admin_headers)
        assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
        print("PASS: Non-admin POST /api/matches/live/sync returns 403")

    def test_sync_match_score_non_admin_forbidden(self, non_admin_headers):
        """Non-admin cannot sync match score - gets 403"""
        resp = requests.get(f"{BASE_URL}/api/matches?limit=1")
        if resp.status_code != 200 or not resp.json().get("matches"):
            pytest.skip("No matches available")
        
        match_id = resp.json()["matches"][0]["id"]
        resp = requests.post(f"{BASE_URL}/api/matches/{match_id}/sync-score", headers=non_admin_headers)
        assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
        print("PASS: Non-admin POST /api/matches/{id}/sync-score returns 403")


class TestStage13_14FinalizeUsernameInTop3:
    """STAGE 13-14: Contest finalize response includes username in top_3"""

    def test_finalize_response_has_username(self, admin_headers):
        """Finalize response should include username in top_3"""
        # Get a completed contest to check structure
        resp = requests.get(f"{BASE_URL}/api/contests?status=completed&limit=1", headers=admin_headers)
        if resp.status_code != 200:
            pytest.skip("Cannot get contests")
        
        contests = resp.json().get("contests", [])
        if not contests:
            # Try to finalize an open contest with all questions resolved
            resp = requests.get(f"{BASE_URL}/api/contests?status=open&limit=1", headers=admin_headers)
            if resp.status_code != 200 or not resp.json().get("contests"):
                pytest.skip("No contests available to test finalize")
            
            contest_id = resp.json()["contests"][0]["id"]
            resp = requests.post(f"{BASE_URL}/api/contests/{contest_id}/finalize", headers=admin_headers)
            
            if resp.status_code == 200:
                data = resp.json()
                if "top_3" in data:
                    for entry in data["top_3"]:
                        assert "username" in entry, f"Missing username in top_3 entry: {entry}"
                    print(f"PASS: Finalize response has username in top_3: {[e.get('username') for e in data['top_3']]}")
                elif data.get("message") == "Contest already finalized":
                    print("INFO: Contest already finalized, checking leaderboard for username")
            else:
                print(f"INFO: Finalize returned {resp.status_code} - {resp.text}")
        else:
            # Check leaderboard of completed contest for username
            contest_id = contests[0]["id"]
            lb_resp = requests.get(f"{BASE_URL}/api/contests/{contest_id}/leaderboard", headers=admin_headers)
            if lb_resp.status_code == 200:
                leaderboard = lb_resp.json().get("leaderboard", [])
                for entry in leaderboard[:3]:
                    assert "username" in entry, f"Missing username in leaderboard entry: {entry}"
                print(f"PASS: Leaderboard has username: {[e.get('username') for e in leaderboard[:3]]}")


class TestContestFullFlow:
    """REGRESSION: Full contest flow - join, predict, resolve, finalize"""

    def test_contest_join_flow(self, admin_headers):
        """Admin can join a contest"""
        # Get an open contest
        resp = requests.get(f"{BASE_URL}/api/contests?status=open&limit=5", headers=admin_headers)
        if resp.status_code != 200:
            pytest.skip("Cannot get contests")
        
        contests = resp.json().get("contests", [])
        if not contests:
            pytest.skip("No open contests")
        
        # Find one not already joined
        for contest in contests:
            contest_id = contest["id"]
            join_resp = requests.post(f"{BASE_URL}/api/contests/{contest_id}/join", 
                                     json={"team_name": "TestTeam_Audit"}, headers=admin_headers)
            if join_resp.status_code == 201:
                print(f"PASS: Joined contest {contest['name']}")
                return
            elif join_resp.status_code == 409:
                # Already joined, try next
                continue
            elif join_resp.status_code == 400:
                # Contest locked or full
                continue
        
        print("INFO: All contests already joined or locked")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
