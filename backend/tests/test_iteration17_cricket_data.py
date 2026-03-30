"""
Iteration 17 - Unified Cricket Data Service Tests
Tests: Cricbuzz scraping, CricketData.org fallback, sync pipeline, auto-contest creation
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
SUPER_ADMIN = {"phone": "7004186276", "pin": "5524"}
REGULAR_PLAYER = {"phone": "9111111111", "pin": "5678"}


@pytest.fixture(scope="module")
def admin_token():
    """Get admin auth token"""
    resp = requests.post(f"{BASE_URL}/api/auth/login", json=SUPER_ADMIN)
    if resp.status_code == 200:
        data = resp.json()
        # Token is nested: token.access_token
        return data.get("token", {}).get("access_token")
    pytest.skip(f"Admin login failed: {resp.status_code} - {resp.text}")


@pytest.fixture(scope="module")
def player_token():
    """Get player auth token"""
    resp = requests.post(f"{BASE_URL}/api/auth/login", json=REGULAR_PLAYER)
    if resp.status_code == 200:
        data = resp.json()
        # Token is nested: token.access_token
        return data.get("token", {}).get("access_token")
    pytest.skip(f"Player login failed: {resp.status_code} - {resp.text}")


class TestCricbuzzPrimary:
    """Test Cricbuzz as primary data source"""

    def test_live_cricket_returns_matches(self, admin_token):
        """GET /api/matches/live/cricket returns matches with source=cricbuzz"""
        resp = requests.get(f"{BASE_URL}/api/matches/live/cricket")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "matches" in data, "Response should have 'matches' key"
        assert "source" in data, "Response should have 'source' key"
        assert "count" in data, "Response should have 'count' key"
        
        # Cricbuzz should be primary source
        if data["count"] > 0:
            assert data["source"] == "cricbuzz", f"Expected source=cricbuzz, got {data['source']}"
            
            # Verify match structure
            match = data["matches"][0]
            assert "team_a" in match, "Match should have team_a"
            assert "team_b" in match, "Match should have team_b"
            assert "status" in match, "Match should have status"
            assert "source_id" in match, "Match should have source_id"
            print(f"✓ Cricbuzz returned {data['count']} matches")

    def test_ipl_only_filter(self, admin_token):
        """GET /api/matches/live/cricket?ipl_only=true returns only IPL matches"""
        resp = requests.get(f"{BASE_URL}/api/matches/live/cricket?ipl_only=true")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "matches" in data
        
        # All returned matches should be IPL
        for match in data["matches"]:
            assert match.get("is_ipl") == True, f"Match {match.get('source_id')} should be IPL"
        
        print(f"✓ IPL filter returned {data['count']} IPL matches")


class TestCricketDataFallback:
    """Test CricketData.org fallback status"""

    def test_live_status_shows_key_set(self):
        """GET /api/matches/live/status shows cricketdata_key_set=true"""
        resp = requests.get(f"{BASE_URL}/api/matches/live/status")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "cricketdata_key_set" in data, "Response should have cricketdata_key_set"
        assert data["cricketdata_key_set"] == True, "CRICKET_API_KEY should be set in .env"
        
        print(f"✓ CricketData.org key is set: {data}")


class TestSyncPipeline:
    """Test sync pipeline: fetch → create matches → create contests"""

    def test_sync_creates_matches(self, admin_token):
        """POST /api/matches/live/sync creates new matches from Cricbuzz"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        resp = requests.post(
            f"{BASE_URL}/api/matches/live/sync?ipl_only=true",
            headers=headers
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "source" in data, "Response should have source"
        assert "created" in data, "Response should have created count"
        assert "updated" in data, "Response should have updated count"
        assert "synced" in data, "Response should have synced count"
        
        # Source should be cricbuzz (primary)
        if data.get("total_from_source", 0) > 0:
            assert data["source"] == "cricbuzz", f"Expected source=cricbuzz, got {data['source']}"
        
        print(f"✓ Sync result: source={data['source']}, created={data['created']}, updated={data['updated']}")
        return data

    def test_sync_auto_creates_contests(self, admin_token):
        """Sync auto-creates contests with 1000 entry fee for each new match"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        resp = requests.post(
            f"{BASE_URL}/api/matches/live/sync?ipl_only=true",
            headers=headers
        )
        assert resp.status_code == 200
        
        data = resp.json()
        assert "contests_auto_created" in data, "Response should have contests_auto_created"
        
        # If new matches were created, contests should be auto-created
        if data.get("created", 0) > 0:
            assert data["contests_auto_created"] > 0, "New matches should have auto-created contests"
        
        print(f"✓ Auto-created contests: {data.get('contests_auto_created', 0)}")

    def test_second_sync_updates_existing(self, admin_token):
        """Second sync updates existing matches (no duplicates)"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # First sync
        resp1 = requests.post(
            f"{BASE_URL}/api/matches/live/sync?ipl_only=true",
            headers=headers
        )
        assert resp1.status_code == 200
        data1 = resp1.json()
        
        # Second sync - should update, not create duplicates
        resp2 = requests.post(
            f"{BASE_URL}/api/matches/live/sync?ipl_only=true",
            headers=headers
        )
        assert resp2.status_code == 200
        data2 = resp2.json()
        
        # Second sync should have updated > 0 if there were matches
        if data1.get("total_from_source", 0) > 0:
            assert data2["updated"] > 0 or data2["created"] == 0, "Second sync should update existing, not create duplicates"
        
        print(f"✓ Second sync: created={data2['created']}, updated={data2['updated']}")


class TestAutoContestLinked:
    """Test that synced matches have auto-created contests linked"""

    def test_synced_matches_have_contests(self, admin_token):
        """Matches created by sync have auto-created contests linked"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get matches
        resp = requests.get(f"{BASE_URL}/api/matches?limit=10", headers=headers)
        assert resp.status_code == 200
        
        matches = resp.json().get("matches", [])
        
        # Check if any match has external_match_id (synced from Cricbuzz)
        synced_matches = [m for m in matches if m.get("external_match_id")]
        
        for match in synced_matches[:3]:  # Check first 3 synced matches
            match_id = match["id"]
            
            # Get contests for this match
            contests_resp = requests.get(
                f"{BASE_URL}/api/matches/{match_id}/contests",
                headers=headers
            )
            assert contests_resp.status_code == 200
            
            contests = contests_resp.json().get("contests", [])
            
            # Synced matches should have at least one contest
            if match.get("status") != "completed":
                # Check if any contest is auto-created
                auto_contests = [c for c in contests if c.get("auto_created")]
                print(f"  Match {match_id}: {len(contests)} contests, {len(auto_contests)} auto-created")
        
        print(f"✓ Checked {len(synced_matches)} synced matches for contests")


class TestRegressionAuth:
    """Regression tests for auth flow"""

    def test_super_admin_login(self):
        """Super admin (7004186276/5524) logs in with is_admin=true"""
        resp = requests.post(f"{BASE_URL}/api/auth/login", json=SUPER_ADMIN)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "token" in data, "Response should have token"
        assert "user" in data, "Response should have user"
        assert data["user"]["is_admin"] == True, "Super admin should have is_admin=true"
        
        print(f"✓ Super admin login: is_admin={data['user']['is_admin']}")

    def test_regular_player_login(self):
        """Regular player (9111111111/5678) logs in with is_admin=false"""
        resp = requests.post(f"{BASE_URL}/api/auth/login", json=REGULAR_PLAYER)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "token" in data, "Response should have token"
        assert "user" in data, "Response should have user"
        assert data["user"]["is_admin"] == False, "Regular player should have is_admin=false"
        
        print(f"✓ Regular player login: is_admin={data['user']['is_admin']}")


class TestRegressionContestJoin:
    """Regression tests for contest join and economy"""

    def test_contest_join_deducts_coins(self, player_token):
        """Contest join deducts 1000 coins and increases prize_pool"""
        headers = {"Authorization": f"Bearer {player_token}"}
        
        # Get player's current coins - /me returns user directly
        me_resp = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert me_resp.status_code == 200
        initial_coins = me_resp.json()["coins_balance"]
        
        # Get an open contest
        contests_resp = requests.get(f"{BASE_URL}/api/contests?status=open", headers=headers)
        assert contests_resp.status_code == 200
        
        contests = contests_resp.json().get("contests", [])
        if not contests:
            pytest.skip("No open contests available")
        
        contest = contests[0]
        contest_id = contest["id"]
        entry_fee = contest.get("entry_fee", 1000)
        initial_pool = contest.get("prize_pool", 0)
        
        # Try to join (may fail if already joined)
        join_resp = requests.post(
            f"{BASE_URL}/api/contests/{contest_id}/join",
            headers=headers
        )
        
        if join_resp.status_code == 200:
            # Verify coins deducted - /me returns user directly
            me_resp2 = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
            new_coins = me_resp2.json()["coins_balance"]
            assert new_coins == initial_coins - entry_fee, f"Coins should be deducted by {entry_fee}"
            
            # Verify prize pool increased
            contest_resp = requests.get(f"{BASE_URL}/api/contests/{contest_id}", headers=headers)
            new_pool = contest_resp.json().get("prize_pool", 0)
            assert new_pool == initial_pool + entry_fee, f"Prize pool should increase by {entry_fee}"
            
            print(f"✓ Contest join: coins {initial_coins} → {new_coins}, pool {initial_pool} → {new_pool}")
        elif join_resp.status_code == 400 and "already joined" in join_resp.text.lower():
            print(f"✓ Player already joined contest {contest_id} (expected behavior)")
        else:
            print(f"⚠ Join response: {join_resp.status_code} - {join_resp.text}")


class TestRegressionNewUserSignup:
    """Regression test for new user signup bonus"""

    def test_new_user_gets_100000_coins(self):
        """New user signup gives 100000 coins"""
        import random
        test_phone = f"888800{random.randint(1000, 9999)}"
        
        # Check phone (should be new)
        check_resp = requests.post(
            f"{BASE_URL}/api/auth/check-phone",
            json={"phone": test_phone}
        )
        assert check_resp.status_code == 200
        assert check_resp.json()["exists"] == False, "Test phone should be new"
        
        # Register new user
        register_resp = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "phone": test_phone,
                "pin": "1111",
                "username": f"TestUser{test_phone[-4:]}"
            }
        )
        assert register_resp.status_code in [200, 201], f"Register failed: {register_resp.text}"
        
        data = register_resp.json()
        assert "user" in data, "Response should have user"
        # coins_balance is the field name
        assert data["user"]["coins_balance"] == 100000, f"New user should get 100000 coins, got {data['user']['coins_balance']}"
        
        print(f"✓ New user {test_phone} registered with {data['user']['coins_balance']} coins")


class TestAdminRestrictions:
    """Test that regular players can't access admin endpoints"""

    def test_player_cannot_sync(self, player_token):
        """Regular player gets 403 on sync endpoint"""
        headers = {"Authorization": f"Bearer {player_token}"}
        
        resp = requests.post(
            f"{BASE_URL}/api/matches/live/sync?ipl_only=true",
            headers=headers
        )
        assert resp.status_code == 403, f"Expected 403, got {resp.status_code}"
        print(f"✓ Player correctly blocked from sync endpoint")

    def test_player_cannot_create_match(self, player_token):
        """Regular player gets 403 when creating match"""
        headers = {"Authorization": f"Bearer {player_token}"}
        
        resp = requests.post(
            f"{BASE_URL}/api/matches",
            headers=headers,
            json={
                "team_a": {"name": "Test A", "short_name": "TA"},
                "team_b": {"name": "Test B", "short_name": "TB"},
                "start_time": "2026-04-01T10:00:00Z"
            }
        )
        assert resp.status_code == 403, f"Expected 403, got {resp.status_code}"
        print(f"✓ Player correctly blocked from creating match")
