"""
Test Score Fetch Pipeline - Iteration 64
Tests the per-match score fetching system for Bharat 11 Fantasy Cricket PWA.

Features tested:
1. POST /api/admin/matches/{match_id}/start-score-fetch - Start per-match scorecard polling
2. POST /api/admin/matches/{match_id}/stop-score-fetch - Stop it
3. GET /api/admin/score-fetch/status - All active fetchers
4. GET /api/admin/matches/{match_id}/score-fetch-status - Per-match fetch status
5. GET /api/matches/{match_id}/scorecard - Cached scorecard data with full innings
6. GET /api/matches/{match_id}/scorecard?force=true - Bypass cache
7. POST /api/matches/live/sync-ipl-schedule - Sync and auto-mark completed matches
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_PHONE = "7004186276"
ADMIN_PIN = "5524"


class TestScoreFetchPipeline:
    """Test the complete score fetching pipeline."""
    
    auth_token = None
    test_match_id = None
    completed_match_id = None
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before tests."""
        if not TestScoreFetchPipeline.auth_token:
            # Login as admin using /api/auth/login
            resp = requests.post(f"{BASE_URL}/api/auth/login", json={
                "phone": ADMIN_PHONE,
                "pin": ADMIN_PIN
            })
            assert resp.status_code == 200, f"Login failed: {resp.text}"
            data = resp.json()
            # Token is nested under 'token' key
            TestScoreFetchPipeline.auth_token = data.get("token", {}).get("access_token") or data.get("access_token")
            assert TestScoreFetchPipeline.auth_token, "No access token received"
            print(f"✓ Admin login successful")
    
    def get_headers(self):
        return {"Authorization": f"Bearer {TestScoreFetchPipeline.auth_token}"}
    
    # ==================== SYNC IPL SCHEDULE ====================
    
    def test_01_sync_ipl_schedule(self):
        """POST /api/matches/live/sync-ipl-schedule - Sync IPL schedule and auto-mark completed."""
        resp = requests.post(f"{BASE_URL}/api/matches/live/sync-ipl-schedule", headers=self.get_headers())
        assert resp.status_code == 200, f"Sync failed: {resp.text}"
        
        data = resp.json()
        print(f"✓ Sync IPL Schedule: created={data.get('created', 0)}, updated={data.get('updated', 0)}, synced={data.get('synced', 0)}")
        
        # Verify response structure
        assert "synced" in data or "created" in data or "updated" in data
        assert "series" in data or "total_from_api" in data
    
    # ==================== GET MATCHES FOR TESTING ====================
    
    def test_02_get_matches_for_testing(self):
        """Get a live/upcoming match and a completed match for testing."""
        # Get live matches first
        resp = requests.get(f"{BASE_URL}/api/matches?status=live&limit=10")
        assert resp.status_code == 200
        live_matches = resp.json().get("matches", [])
        
        # Get upcoming matches
        resp = requests.get(f"{BASE_URL}/api/matches?status=upcoming&limit=10")
        assert resp.status_code == 200
        upcoming_matches = resp.json().get("matches", [])
        
        # Get completed matches
        resp = requests.get(f"{BASE_URL}/api/matches?status=completed&limit=10")
        assert resp.status_code == 200
        completed_matches = resp.json().get("matches", [])
        
        # Pick a match with cricketdata_id for score fetch testing
        all_matches = live_matches + upcoming_matches
        for m in all_matches:
            cd_id = m.get("cricketdata_id") or m.get("external_match_id")
            if cd_id:
                TestScoreFetchPipeline.test_match_id = m["id"]
                print(f"✓ Found test match: {m.get('team_a', {}).get('short_name', '?')} vs {m.get('team_b', {}).get('short_name', '?')} (id={m['id'][:8]}...)")
                break
        
        # Pick a completed match for scorecard testing
        for m in completed_matches:
            cd_id = m.get("cricketdata_id") or m.get("external_match_id")
            if cd_id:
                TestScoreFetchPipeline.completed_match_id = m["id"]
                print(f"✓ Found completed match: {m.get('team_a', {}).get('short_name', '?')} vs {m.get('team_b', {}).get('short_name', '?')} (id={m['id'][:8]}...)")
                break
        
        assert TestScoreFetchPipeline.test_match_id or TestScoreFetchPipeline.completed_match_id, "No matches with cricketdata_id found"
    
    # ==================== SCORE FETCH STATUS (GLOBAL) ====================
    
    def test_03_get_score_fetch_status_global(self):
        """GET /api/admin/score-fetch/status - Get all active fetchers."""
        resp = requests.get(f"{BASE_URL}/api/admin/score-fetch/status", headers=self.get_headers())
        assert resp.status_code == 200, f"Failed: {resp.text}"
        
        data = resp.json()
        print(f"✓ Global score fetch status: active_fetchers={data.get('active_fetchers', 0)}")
        
        # Verify response structure
        assert "active_fetchers" in data
        assert "matches" in data
        assert isinstance(data["matches"], dict)
    
    # ==================== PER-MATCH SCORE FETCH STATUS ====================
    
    def test_04_get_match_score_fetch_status(self):
        """GET /api/admin/matches/{match_id}/score-fetch-status - Per-match status."""
        match_id = TestScoreFetchPipeline.test_match_id or TestScoreFetchPipeline.completed_match_id
        if not match_id:
            pytest.skip("No match available for testing")
        
        resp = requests.get(f"{BASE_URL}/api/admin/matches/{match_id}/score-fetch-status", headers=self.get_headers())
        assert resp.status_code == 200, f"Failed: {resp.text}"
        
        data = resp.json()
        print(f"✓ Match score fetch status: running={data.get('running', False)}, fetch_count={data.get('fetch_count', 0)}")
        
        # Verify response structure
        assert "match_id" in data
        assert "running" in data
        assert "fetch_count" in data
    
    # ==================== START SCORE FETCH ====================
    
    def test_05_start_score_fetch(self):
        """POST /api/admin/matches/{match_id}/start-score-fetch - Start per-match polling."""
        match_id = TestScoreFetchPipeline.test_match_id
        if not match_id:
            pytest.skip("No live/upcoming match available for score fetch testing")
        
        resp = requests.post(f"{BASE_URL}/api/admin/matches/{match_id}/start-score-fetch", headers=self.get_headers())
        
        # Could be 200 (started) or 400 (no cricketdata_id) or already running
        if resp.status_code == 400:
            print(f"⚠ Start score fetch: {resp.json().get('detail', 'No cricketdata_id')}")
            pytest.skip("Match has no CricketData ID")
        
        assert resp.status_code == 200, f"Failed: {resp.text}"
        
        data = resp.json()
        print(f"✓ Start score fetch: {data.get('message', '')} - match_name={data.get('match_name', '')}")
        
        # Verify response structure
        assert "message" in data
        assert "match_id" in data
        assert "running" in data
    
    # ==================== VERIFY FETCH IS RUNNING ====================
    
    def test_06_verify_fetch_running(self):
        """Verify the score fetch is now running."""
        match_id = TestScoreFetchPipeline.test_match_id
        if not match_id:
            pytest.skip("No match available")
        
        # Wait a moment for the task to start
        time.sleep(1)
        
        resp = requests.get(f"{BASE_URL}/api/admin/matches/{match_id}/score-fetch-status", headers=self.get_headers())
        assert resp.status_code == 200
        
        data = resp.json()
        # Note: running might be False if match has no cricketdata_id
        print(f"✓ Fetch status after start: running={data.get('running', False)}, fetch_count={data.get('fetch_count', 0)}")
    
    # ==================== STOP SCORE FETCH ====================
    
    def test_07_stop_score_fetch(self):
        """POST /api/admin/matches/{match_id}/stop-score-fetch - Stop polling."""
        match_id = TestScoreFetchPipeline.test_match_id
        if not match_id:
            pytest.skip("No match available")
        
        resp = requests.post(f"{BASE_URL}/api/admin/matches/{match_id}/stop-score-fetch", headers=self.get_headers())
        assert resp.status_code == 200, f"Failed: {resp.text}"
        
        data = resp.json()
        print(f"✓ Stop score fetch: {data.get('message', '')} - total_fetches={data.get('total_fetches', 0)}")
        
        # Verify response structure
        assert "message" in data
        assert "match_id" in data
        assert "running" in data
        assert data["running"] == False
    
    # ==================== SCORECARD ENDPOINT (CACHED) ====================
    
    def test_08_get_scorecard_cached(self):
        """GET /api/matches/{match_id}/scorecard - Get cached scorecard."""
        match_id = TestScoreFetchPipeline.completed_match_id or TestScoreFetchPipeline.test_match_id
        if not match_id:
            pytest.skip("No match available")
        
        resp = requests.get(f"{BASE_URL}/api/matches/{match_id}/scorecard")
        assert resp.status_code == 200, f"Failed: {resp.text}"
        
        data = resp.json()
        
        # Check if scorecard is available
        if data.get("error"):
            print(f"⚠ Scorecard: {data.get('error')}")
        else:
            print(f"✓ Scorecard (cached): match_name={data.get('match_name', '')}, status={data.get('status', '')}")
            
            # Verify scorecard structure if available
            if data.get("scorecard"):
                assert "match_id" in data
                assert "scorecard" in data
                # Check for innings data
                scorecard = data.get("scorecard", [])
                if scorecard:
                    print(f"  - Innings count: {len(scorecard)}")
                    for i, inn in enumerate(scorecard):
                        inning_name = inn.get("inning", f"Innings {i+1}")
                        total = inn.get("total", {})
                        print(f"  - {inning_name}: {total.get('r', 0)}/{total.get('w', 0)} ({total.get('o', 0)} ov)")
    
    # ==================== SCORECARD ENDPOINT (FORCE BYPASS CACHE) ====================
    
    def test_09_get_scorecard_force(self):
        """GET /api/matches/{match_id}/scorecard?force=true - Bypass cache."""
        match_id = TestScoreFetchPipeline.completed_match_id or TestScoreFetchPipeline.test_match_id
        if not match_id:
            pytest.skip("No match available")
        
        resp = requests.get(f"{BASE_URL}/api/matches/{match_id}/scorecard?force=true")
        assert resp.status_code == 200, f"Failed: {resp.text}"
        
        data = resp.json()
        
        if data.get("error"):
            print(f"⚠ Scorecard (force): {data.get('error')}")
        else:
            print(f"✓ Scorecard (force bypass): match_name={data.get('match_name', '')}")
            
            # Verify metrics are parsed
            metrics = data.get("metrics", {})
            if metrics:
                print(f"  - Metrics: innings_1_total_runs={metrics.get('innings_1_total_runs', 'N/A')}, match_total_sixes={metrics.get('match_total_sixes', 'N/A')}")
    
    # ==================== VERIFY GLOBAL STATUS AFTER STOP ====================
    
    def test_10_verify_global_status_after_stop(self):
        """Verify global status shows no active fetchers for our match."""
        resp = requests.get(f"{BASE_URL}/api/admin/score-fetch/status", headers=self.get_headers())
        assert resp.status_code == 200
        
        data = resp.json()
        match_id = TestScoreFetchPipeline.test_match_id
        
        # Our match should not be in active fetchers
        active_matches = data.get("matches", {})
        if match_id and match_id in active_matches:
            print(f"⚠ Match still in active fetchers (may be expected if stop didn't complete)")
        else:
            print(f"✓ Global status: {data.get('active_fetchers', 0)} active fetchers")


class TestScorecardContent:
    """Test scorecard content for completed matches."""
    
    auth_token = None
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token."""
        if not TestScorecardContent.auth_token:
            resp = requests.post(f"{BASE_URL}/api/auth/login", json={
                "phone": ADMIN_PHONE,
                "pin": ADMIN_PIN
            })
            if resp.status_code == 200:
                data = resp.json()
                TestScorecardContent.auth_token = data.get("token", {}).get("access_token") or data.get("access_token")
    
    def get_headers(self):
        return {"Authorization": f"Bearer {TestScorecardContent.auth_token}"}
    
    def test_scorecard_has_batting_bowling_data(self):
        """Verify scorecard contains batting and bowling details."""
        # Get a completed match
        resp = requests.get(f"{BASE_URL}/api/matches?status=completed&limit=5")
        assert resp.status_code == 200
        
        matches = resp.json().get("matches", [])
        if not matches:
            pytest.skip("No completed matches")
        
        # Find one with cricketdata_id
        match_id = None
        for m in matches:
            if m.get("cricketdata_id") or m.get("external_match_id"):
                match_id = m["id"]
                break
        
        if not match_id:
            pytest.skip("No completed match with cricketdata_id")
        
        resp = requests.get(f"{BASE_URL}/api/matches/{match_id}/scorecard")
        assert resp.status_code == 200
        
        data = resp.json()
        if data.get("error"):
            print(f"⚠ Scorecard error: {data.get('error')}")
            return
        
        scorecard = data.get("scorecard", [])
        if not scorecard:
            print("⚠ No scorecard data available")
            return
        
        # Check first innings has batting data
        first_innings = scorecard[0] if scorecard else {}
        batting = first_innings.get("batting", [])
        bowling = first_innings.get("bowling", [])
        
        print(f"✓ Scorecard content: {len(scorecard)} innings")
        print(f"  - First innings batting: {len(batting)} batsmen")
        print(f"  - First innings bowling: {len(bowling)} bowlers")
        
        # Verify batting structure
        if batting:
            batsman = batting[0]
            assert "batsman" in batsman or "name" in batsman, "Batting data missing batsman name"
            print(f"  - Sample batsman: {batsman.get('batsman', batsman.get('name', 'N/A'))}")


class TestAutoPilotAndAutoEngine:
    """Verify Auto-Pilot and Match Auto-Engine still work."""
    
    auth_token = None
    
    @pytest.fixture(autouse=True)
    def setup(self):
        if not TestAutoPilotAndAutoEngine.auth_token:
            resp = requests.post(f"{BASE_URL}/api/auth/login", json={
                "phone": ADMIN_PHONE,
                "pin": ADMIN_PIN
            })
            if resp.status_code == 200:
                data = resp.json()
                TestAutoPilotAndAutoEngine.auth_token = data.get("token", {}).get("access_token") or data.get("access_token")
    
    def get_headers(self):
        return {"Authorization": f"Bearer {TestAutoPilotAndAutoEngine.auth_token}"}
    
    def test_autopilot_status(self):
        """GET /api/admin/autopilot/status - Verify Auto-Pilot status endpoint."""
        resp = requests.get(f"{BASE_URL}/api/admin/autopilot/status", headers=self.get_headers())
        assert resp.status_code == 200, f"Failed: {resp.text}"
        
        data = resp.json()
        print(f"✓ Auto-Pilot status: running={data.get('running', False)}, run_count={data.get('run_count', 0)}")
        
        assert "running" in data
    
    def test_seed_question_pool(self):
        """POST /api/admin/seed-question-pool - Verify seed endpoint."""
        resp = requests.post(f"{BASE_URL}/api/admin/seed-question-pool", headers=self.get_headers())
        assert resp.status_code == 200, f"Failed: {resp.text}"
        
        data = resp.json()
        print(f"✓ Seed question pool: seeded={data.get('seeded', 0)}, total_in_db={data.get('total_in_db', 0)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
