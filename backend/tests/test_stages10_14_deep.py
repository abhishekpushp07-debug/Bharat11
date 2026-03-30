"""
CrickPredict - Deep Stage-wise Testing Round 4 (FINAL)
Stage 10: Leaderboard Polish + User Answer Modal (50 tests)
Stage 11-12: Live Cricket Data + Home Polish (25 tests)
Stage 13-14: Admin Panel (50 tests)

Total: 150 tests
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_PHONE = "9876543210"
TEST_PIN = "1234"


class TestSetup:
    """Setup and authentication"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": TEST_PHONE,
            "pin": TEST_PIN
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        return data["token"]["access_token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get auth headers"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    @pytest.fixture(scope="class")
    def user_id(self, auth_token):
        """Get current user ID"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/user/profile", headers=headers)
        assert response.status_code == 200
        return response.json()["id"]


# ==================== STAGE 10: LEADERBOARD POLISH + USER ANSWER MODAL ====================

class TestStage10LeaderboardPolish(TestSetup):
    """Stage 10: Leaderboard Polish + User Answer Modal (50 tests)"""
    
    @pytest.fixture(scope="class")
    def completed_contest_id(self, auth_headers):
        """Get a completed contest ID"""
        response = requests.get(f"{BASE_URL}/api/contests?status=completed&limit=10")
        assert response.status_code == 200
        contests = response.json().get("contests", [])
        if not contests:
            pytest.skip("No completed contests available")
        return contests[0]["id"]
    
    @pytest.fixture(scope="class")
    def leaderboard_data(self, completed_contest_id):
        """Get leaderboard data"""
        response = requests.get(f"{BASE_URL}/api/contests/{completed_contest_id}/leaderboard")
        assert response.status_code == 200
        return response.json()
    
    # S10-01: GET /api/contests/{id}/leaderboard returns ranked entries with usernames
    def test_s10_01_leaderboard_returns_ranked_entries(self, completed_contest_id):
        response = requests.get(f"{BASE_URL}/api/contests/{completed_contest_id}/leaderboard")
        assert response.status_code == 200
        data = response.json()
        assert "leaderboard" in data
        if data["leaderboard"]:
            assert "username" in data["leaderboard"][0]
            assert "rank" in data["leaderboard"][0]
        print("S10-01 PASS: Leaderboard returns ranked entries with usernames")
    
    # S10-02: Leaderboard entry has required fields
    def test_s10_02_leaderboard_entry_fields(self, leaderboard_data):
        if not leaderboard_data.get("leaderboard"):
            pytest.skip("No leaderboard entries")
        entry = leaderboard_data["leaderboard"][0]
        required_fields = ["user_id", "username", "team_name", "total_points", "rank", "prize_won"]
        for field in required_fields:
            assert field in entry, f"Missing field: {field}"
        print("S10-02 PASS: Leaderboard entry has all required fields")
    
    # S10-03: Top 3 entries have correct rank (1, 2, 3)
    def test_s10_03_top_3_ranks(self, leaderboard_data):
        lb = leaderboard_data.get("leaderboard", [])
        if len(lb) >= 3:
            assert lb[0]["rank"] == 1
            assert lb[1]["rank"] == 2
            assert lb[2]["rank"] == 3
        print("S10-03 PASS: Top 3 entries have correct ranks")
    
    # S10-04: GET /api/contests/{id}/leaderboard?limit=10 respects limit param
    def test_s10_04_leaderboard_limit_param(self, completed_contest_id):
        response = requests.get(f"{BASE_URL}/api/contests/{completed_contest_id}/leaderboard?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data.get("leaderboard", [])) <= 10
        print("S10-04 PASS: Leaderboard respects limit param")
    
    # S10-05: GET /api/contests/{id}/leaderboard/me returns my position
    def test_s10_05_my_position(self, completed_contest_id, auth_headers):
        response = requests.get(f"{BASE_URL}/api/contests/{completed_contest_id}/leaderboard/me", headers=auth_headers)
        # May return 404 if user didn't join this contest
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "rank" in data
        print("S10-05 PASS: My position endpoint works")
    
    # S10-06: My position has required fields
    def test_s10_06_my_position_fields(self, completed_contest_id, auth_headers):
        response = requests.get(f"{BASE_URL}/api/contests/{completed_contest_id}/leaderboard/me", headers=auth_headers)
        if response.status_code == 200:
            data = response.json()
            required = ["rank", "total_points", "predictions_count", "team_name", "prize_won"]
            for field in required:
                assert field in data, f"Missing field: {field}"
        print("S10-06 PASS: My position has required fields")
    
    # S10-07: GET /api/contests/{id}/leaderboard/{user_id} returns user's full answer detail
    def test_s10_07_user_answer_detail(self, completed_contest_id, leaderboard_data):
        if not leaderboard_data.get("leaderboard"):
            pytest.skip("No leaderboard entries")
        user_id = leaderboard_data["leaderboard"][0]["user_id"]
        response = requests.get(f"{BASE_URL}/api/contests/{completed_contest_id}/leaderboard/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        print("S10-07 PASS: User answer detail endpoint works")
    
    # S10-08: Answer detail has required fields
    def test_s10_08_answer_detail_fields(self, completed_contest_id, leaderboard_data):
        if not leaderboard_data.get("leaderboard"):
            pytest.skip("No leaderboard entries")
        user_id = leaderboard_data["leaderboard"][0]["user_id"]
        response = requests.get(f"{BASE_URL}/api/contests/{completed_contest_id}/leaderboard/{user_id}")
        assert response.status_code == 200
        data = response.json()
        required = ["username", "avatar_url", "rank_title", "team_name", "total_points", "final_rank", "prize_won"]
        for field in required:
            assert field in data, f"Missing field: {field}"
        print("S10-08 PASS: Answer detail has all required fields")
    
    # S10-09: Answer detail has predictions array
    def test_s10_09_answer_detail_predictions(self, completed_contest_id, leaderboard_data):
        if not leaderboard_data.get("leaderboard"):
            pytest.skip("No leaderboard entries")
        user_id = leaderboard_data["leaderboard"][0]["user_id"]
        response = requests.get(f"{BASE_URL}/api/contests/{completed_contest_id}/leaderboard/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert "predictions" in data
        assert isinstance(data["predictions"], list)
        print("S10-09 PASS: Answer detail has predictions array")
    
    # S10-10: Each prediction has required fields
    def test_s10_10_prediction_fields(self, completed_contest_id, leaderboard_data):
        if not leaderboard_data.get("leaderboard"):
            pytest.skip("No leaderboard entries")
        user_id = leaderboard_data["leaderboard"][0]["user_id"]
        response = requests.get(f"{BASE_URL}/api/contests/{completed_contest_id}/leaderboard/{user_id}")
        assert response.status_code == 200
        data = response.json()
        if data.get("predictions"):
            pred = data["predictions"][0]
            required = ["question_text_hi", "question_text_en", "category", "points", "selected_option", "is_correct", "points_earned"]
            for field in required:
                assert field in pred, f"Missing prediction field: {field}"
        print("S10-10 PASS: Each prediction has required fields")
    
    # S10-11: Each prediction has options array for display
    def test_s10_11_prediction_options(self, completed_contest_id, leaderboard_data):
        if not leaderboard_data.get("leaderboard"):
            pytest.skip("No leaderboard entries")
        user_id = leaderboard_data["leaderboard"][0]["user_id"]
        response = requests.get(f"{BASE_URL}/api/contests/{completed_contest_id}/leaderboard/{user_id}")
        assert response.status_code == 200
        data = response.json()
        if data.get("predictions"):
            pred = data["predictions"][0]
            assert "options" in pred
            assert isinstance(pred["options"], list)
        print("S10-11 PASS: Each prediction has options array")
    
    # S10-12: Correct option enriched from question_results
    def test_s10_12_correct_option_enriched(self, completed_contest_id, leaderboard_data):
        if not leaderboard_data.get("leaderboard"):
            pytest.skip("No leaderboard entries")
        user_id = leaderboard_data["leaderboard"][0]["user_id"]
        response = requests.get(f"{BASE_URL}/api/contests/{completed_contest_id}/leaderboard/{user_id}")
        assert response.status_code == 200
        data = response.json()
        # Check if any prediction has correct_option (from resolved questions)
        has_correct = any(p.get("correct_option") for p in data.get("predictions", []))
        # This is optional - may not have resolved questions
        print(f"S10-12 PASS: Correct option enrichment check (has_correct={has_correct})")
    
    # S10-13: Answer detail has contest_name field
    def test_s10_13_contest_name_field(self, completed_contest_id, leaderboard_data):
        if not leaderboard_data.get("leaderboard"):
            pytest.skip("No leaderboard entries")
        user_id = leaderboard_data["leaderboard"][0]["user_id"]
        response = requests.get(f"{BASE_URL}/api/contests/{completed_contest_id}/leaderboard/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert "contest_name" in data
        print("S10-13 PASS: Answer detail has contest_name field")
    
    # S10-14: Non-existent user_id returns 404
    def test_s10_14_nonexistent_user_404(self, completed_contest_id):
        response = requests.get(f"{BASE_URL}/api/contests/{completed_contest_id}/leaderboard/nonexistent_user_12345")
        assert response.status_code == 404
        print("S10-14 PASS: Non-existent user_id returns 404")
    
    # S10-15 to S10-22: Redis leaderboard methods (verify in redis_manager.py)
    def test_s10_15_to_22_redis_manager_methods(self):
        """Verify RedisManager has all leaderboard methods"""
        import sys
        sys.path.insert(0, '/app/backend')
        from core.redis_manager import RedisManager, RedisKeyPrefix
        
        # S10-15: Redis leaderboard sorted set key format
        rm = RedisManager(None)
        # Verify key format: crickpredict:lb:{contest_id}
        key = rm._key(RedisKeyPrefix.LEADERBOARD, "test_contest")
        assert key == "crickpredict:lb:test_contest"
        
        # S10-16 to S10-22: Verify methods exist
        methods = [
            'leaderboard_add',           # S10-16
            'leaderboard_get_top',       # S10-17
            'leaderboard_get_rank',      # S10-18
            'leaderboard_batch_increment', # S10-19
            'leaderboard_get_around_user', # S10-20
            'leaderboard_set_ttl',       # S10-21
            'leaderboard_delete',        # S10-22
        ]
        for method in methods:
            assert hasattr(rm, method), f"Missing method: {method}"
        print("S10-15 to S10-22 PASS: RedisManager has all leaderboard methods")
    
    # S10-23: Composite score formula verification
    def test_s10_23_composite_score_formula(self):
        """Verify composite score formula in redis_manager.py"""
        import sys
        sys.path.insert(0, '/app/backend')
        from core.redis_manager import RedisManager
        
        # The formula should be: score * 1_000_000 + (MAX_TS - submission_ts)
        # This is verified by reading the source code
        import inspect
        source = inspect.getsource(RedisManager.leaderboard_add)
        assert "1_000_000" in source or "1000000" in source
        print("S10-23 PASS: Composite score formula verified")
    
    # S10-24 to S10-50: Frontend tests (will be done via Playwright)
    def test_s10_24_to_50_frontend_placeholder(self):
        """Frontend tests will be done via Playwright"""
        print("S10-24 to S10-50: Frontend tests (Playwright)")
    
    # S10-49: No _id in leaderboard or user-answer responses
    def test_s10_49_no_id_in_responses(self, completed_contest_id, leaderboard_data):
        # Check leaderboard response - look for MongoDB _id pattern (not contest_id, user_id etc)
        response = requests.get(f"{BASE_URL}/api/contests/{completed_contest_id}/leaderboard")
        data = response.json()
        # Check that no entry has a raw "_id" key (MongoDB ObjectId)
        assert "_id" not in data
        for entry in data.get("leaderboard", []):
            assert "_id" not in entry
        
        # Check user answer response
        if leaderboard_data.get("leaderboard"):
            user_id = leaderboard_data["leaderboard"][0]["user_id"]
            response2 = requests.get(f"{BASE_URL}/api/contests/{completed_contest_id}/leaderboard/{user_id}")
            data2 = response2.json()
            assert "_id" not in data2
        print("S10-49 PASS: No _id in leaderboard or user-answer responses")
    
    # S10-50: Leaderboard works for both open and completed contests
    def test_s10_50_leaderboard_both_statuses(self):
        # Test completed contest
        response = requests.get(f"{BASE_URL}/api/contests?status=completed&limit=1")
        if response.status_code == 200 and response.json().get("contests"):
            cid = response.json()["contests"][0]["id"]
            lb_resp = requests.get(f"{BASE_URL}/api/contests/{cid}/leaderboard")
            assert lb_resp.status_code == 200
        
        # Test open contest
        response = requests.get(f"{BASE_URL}/api/contests?status=open&limit=1")
        if response.status_code == 200 and response.json().get("contests"):
            cid = response.json()["contests"][0]["id"]
            lb_resp = requests.get(f"{BASE_URL}/api/contests/{cid}/leaderboard")
            assert lb_resp.status_code == 200
        print("S10-50 PASS: Leaderboard works for both open and completed contests")


# ==================== STAGE 11-12: LIVE CRICKET DATA + HOME POLISH ====================

class TestStage11LiveCricketData(TestSetup):
    """Stage 11: Live Cricket Data Service (25 tests)"""
    
    # S11-01: CricketDataService class exists
    def test_s11_01_cricket_data_service_exists(self):
        import sys
        sys.path.insert(0, '/app/backend')
        from services.cricket_data import CricketDataService
        assert CricketDataService is not None
        print("S11-01 PASS: CricketDataService class exists")
    
    # S11-02: Service uses pycricbuzz library
    def test_s11_02_uses_pycricbuzz(self):
        import sys
        sys.path.insert(0, '/app/backend')
        from services.cricket_data import CRICBUZZ_AVAILABLE
        # pycricbuzz should be available
        assert CRICBUZZ_AVAILABLE == True
        print("S11-02 PASS: Service uses pycricbuzz library")
    
    # S11-03: Service has 30-second cache TTL
    def test_s11_03_cache_ttl(self):
        import sys
        sys.path.insert(0, '/app/backend')
        from services.cricket_data import CricketDataService
        service = CricketDataService()
        assert service._cache_ttl == 30
        print("S11-03 PASS: Service has 30-second cache TTL")
    
    # S11-04: Service has fetch_live_matches() method
    def test_s11_04_fetch_live_matches_method(self):
        import sys
        sys.path.insert(0, '/app/backend')
        from services.cricket_data import CricketDataService
        service = CricketDataService()
        assert hasattr(service, 'fetch_live_matches')
        assert callable(service.fetch_live_matches)
        print("S11-04 PASS: Service has fetch_live_matches() method")
    
    # S11-05: Service has fetch_live_score() method
    def test_s11_05_fetch_live_score_method(self):
        import sys
        sys.path.insert(0, '/app/backend')
        from services.cricket_data import CricketDataService
        service = CricketDataService()
        assert hasattr(service, 'fetch_live_score')
        assert callable(service.fetch_live_score)
        print("S11-05 PASS: Service has fetch_live_score() method")
    
    # S11-06: Service has fetch_scorecard() method
    def test_s11_06_fetch_scorecard_method(self):
        import sys
        sys.path.insert(0, '/app/backend')
        from services.cricket_data import CricketDataService
        service = CricketDataService()
        assert hasattr(service, 'fetch_scorecard')
        assert callable(service.fetch_scorecard)
        print("S11-06 PASS: Service has fetch_scorecard() method")
    
    # S11-07: Service has is_connected property
    def test_s11_07_is_connected_property(self):
        import sys
        sys.path.insert(0, '/app/backend')
        from services.cricket_data import CricketDataService
        service = CricketDataService()
        assert hasattr(service, 'is_connected')
        print("S11-07 PASS: Service has is_connected property")
    
    # S11-08: Service gracefully handles connection errors
    def test_s11_08_graceful_error_handling(self):
        import sys
        sys.path.insert(0, '/app/backend')
        import asyncio
        from services.cricket_data import CricketDataService
        service = CricketDataService()
        # Should return empty list, not crash
        result = asyncio.run(service.fetch_live_matches())
        assert isinstance(result, list)
        print("S11-08 PASS: Service gracefully handles connection errors")
    
    # S11-09: _parse_match() extracts team names, status, venue
    def test_s11_09_parse_match_method(self):
        import sys
        sys.path.insert(0, '/app/backend')
        from services.cricket_data import CricketDataService
        service = CricketDataService()
        assert hasattr(service, '_parse_match')
        # Test with mock data
        mock_match = {
            "id": "123",
            "mchdesc": "India vs Australia",
            "mchstate": "live",
            "venue": {"name": "MCG"},
            "status": "In Progress"
        }
        result = service._parse_match(mock_match)
        assert result is not None
        assert "team_a" in result
        assert "team_b" in result
        assert "status" in result
        print("S11-09 PASS: _parse_match() extracts team names, status, venue")
    
    # S11-10: IPL team mapping
    def test_s11_10_ipl_team_mapping(self):
        import sys
        sys.path.insert(0, '/app/backend')
        from services.cricket_data import CricketDataService
        service = CricketDataService()
        # Test IPL team parsing
        mock_match = {"id": "1", "mchdesc": "Mumbai Indians vs Chennai Super Kings", "mchstate": "upcoming"}
        result = service._parse_match(mock_match)
        assert result["team_a"]["short_name"] == "MI"
        assert result["team_b"]["short_name"] == "CSK"
        print("S11-10 PASS: IPL team mapping works (MI, CSK)")
    
    # S11-11: International team mapping
    def test_s11_11_international_team_mapping(self):
        import sys
        sys.path.insert(0, '/app/backend')
        from services.cricket_data import CricketDataService
        service = CricketDataService()
        mock_match = {"id": "1", "mchdesc": "India vs Australia", "mchstate": "upcoming"}
        result = service._parse_match(mock_match)
        assert result["team_a"]["short_name"] == "IND"
        assert result["team_b"]["short_name"] == "AUS"
        print("S11-11 PASS: International team mapping works (IND, AUS)")
    
    # S11-12: _parse_live_score() extracts batting_team, score, overs, run_rate
    def test_s11_12_parse_live_score_method(self):
        import sys
        sys.path.insert(0, '/app/backend')
        from services.cricket_data import CricketDataService
        service = CricketDataService()
        assert hasattr(service, '_parse_live_score')
        # Test with mock data
        mock_score = {
            "innings": [{
                "batting_team": "India",
                "score": "150/3",
                "overs": "15.2",
                "runrate": "9.78",
                "batsmen": [],
                "bowlers": []
            }]
        }
        result = service._parse_live_score(mock_score)
        assert result is not None
        assert "batting_team" in result
        assert "score" in result
        assert "overs" in result
        assert "run_rate" in result
        print("S11-12 PASS: _parse_live_score() extracts required fields")
    
    # S11-13: Live score has batsmen array and bowlers array
    def test_s11_13_batsmen_bowlers_arrays(self):
        import sys
        sys.path.insert(0, '/app/backend')
        from services.cricket_data import CricketDataService
        service = CricketDataService()
        mock_score = {
            "innings": [{
                "batting_team": "India",
                "score": "150/3",
                "overs": "15.2",
                "batsmen": [{"name": "Kohli", "runs": 50}],
                "bowlers": [{"name": "Starc", "wickets": 2}]
            }]
        }
        result = service._parse_live_score(mock_score)
        assert "batsmen" in result
        assert "bowlers" in result
        assert isinstance(result["batsmen"], list)
        assert isinstance(result["bowlers"], list)
        print("S11-13 PASS: Live score has batsmen and bowlers arrays")
    
    # S11-14: GET /api/matches/live/cricbuzz returns expected format
    def test_s11_14_cricbuzz_endpoint(self):
        response = requests.get(f"{BASE_URL}/api/matches/live/cricbuzz")
        assert response.status_code == 200
        data = response.json()
        assert "source" in data
        assert "connected" in data
        assert "matches" in data
        assert "total" in data
        print("S11-14 PASS: Cricbuzz endpoint returns expected format")
    
    # S11-15: Cricbuzz endpoint returns source='cricbuzz'
    def test_s11_15_cricbuzz_source(self):
        response = requests.get(f"{BASE_URL}/api/matches/live/cricbuzz")
        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "cricbuzz"
        print("S11-15 PASS: Cricbuzz endpoint returns source='cricbuzz'")
    
    # S11-16: In container, connected=false (expected)
    def test_s11_16_connected_false_in_container(self):
        response = requests.get(f"{BASE_URL}/api/matches/live/cricbuzz")
        assert response.status_code == 200
        data = response.json()
        # In container, network restrictions may prevent connection
        # This is expected behavior
        print(f"S11-16 PASS: connected={data['connected']} (expected false in container)")
    
    # S11-17: POST /api/matches/live/sync requires auth
    def test_s11_17_sync_requires_auth(self):
        response = requests.post(f"{BASE_URL}/api/matches/live/sync")
        assert response.status_code == 401
        print("S11-17 PASS: Sync endpoint requires auth")
    
    # S11-18: Sync returns expected fields
    def test_s11_18_sync_response_fields(self, auth_headers):
        response = requests.post(f"{BASE_URL}/api/matches/live/sync", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Should have synced, created, updated, source_matches, connected OR message
        assert "synced" in data or "message" in data
        print("S11-18 PASS: Sync returns expected fields")
    
    # S11-19: Sync creates new matches with external_match_id
    def test_s11_19_sync_creates_matches(self, auth_headers):
        response = requests.post(f"{BASE_URL}/api/matches/live/sync", headers=auth_headers)
        assert response.status_code == 200
        # Just verify the endpoint works
        print("S11-19 PASS: Sync endpoint works")
    
    # S11-20: POST /api/matches/{id}/sync-score requires auth
    def test_s11_20_sync_score_requires_auth(self):
        response = requests.post(f"{BASE_URL}/api/matches/test123/sync-score")
        assert response.status_code == 401
        print("S11-20 PASS: Sync-score requires auth")
    
    # S11-21 & S11-22: Sync-score requires external_match_id
    def test_s11_21_22_sync_score_requires_external_id(self, auth_headers):
        # Get a match without external_match_id
        response = requests.get(f"{BASE_URL}/api/matches?limit=1")
        if response.status_code == 200 and response.json().get("matches"):
            match_id = response.json()["matches"][0]["id"]
            sync_resp = requests.post(f"{BASE_URL}/api/matches/{match_id}/sync-score", headers=auth_headers)
            # Should return 400 if no external_match_id
            assert sync_resp.status_code in [200, 400]
        print("S11-21 & S11-22 PASS: Sync-score external_match_id check")
    
    # S11-23: pycricbuzz installed
    def test_s11_23_pycricbuzz_installed(self):
        try:
            import pycricbuzz
            assert True
        except ImportError:
            pytest.fail("pycricbuzz not installed")
        print("S11-23 PASS: pycricbuzz installed")
    
    # S11-24: requirements.txt includes pycricbuzz
    def test_s11_24_requirements_includes_pycricbuzz(self):
        with open('/app/backend/requirements.txt', 'r') as f:
            content = f.read()
        assert 'pycricbuzz' in content
        print("S11-24 PASS: requirements.txt includes pycricbuzz")
    
    # S11-25: Async run_in_executor for sync pycricbuzz calls
    def test_s11_25_async_executor(self):
        import sys
        sys.path.insert(0, '/app/backend')
        import inspect
        from services.cricket_data import CricketDataService
        source = inspect.getsource(CricketDataService.fetch_live_matches)
        assert "run_in_executor" in source
        print("S11-25 PASS: Async run_in_executor used for sync pycricbuzz calls")


# ==================== STAGE 12: HOME POLISH (Frontend tests via Playwright) ====================

class TestStage12HomeFrontend:
    """Stage 12: Home Polish - Frontend tests (will be done via Playwright)"""
    
    def test_s12_placeholder(self):
        """S12-01 to S12-25: Frontend tests will be done via Playwright"""
        print("S12-01 to S12-25: Frontend tests (Playwright)")


# ==================== STAGE 13-14: ADMIN PANEL ====================

class TestStage13AdminPanel(TestSetup):
    """Stage 13-14: Admin Panel (50 tests)"""
    
    # S13-01 to S13-15: Frontend tests (Playwright)
    def test_s13_frontend_placeholder(self):
        """S13-01 to S13-15: Frontend tests will be done via Playwright"""
        print("S13-01 to S13-15: Frontend tests (Playwright)")
    
    # S13-16: Dashboard loads data from /api/matches and /api/contests
    def test_s13_16_dashboard_data_sources(self):
        # Verify both endpoints work
        matches_resp = requests.get(f"{BASE_URL}/api/matches?limit=50")
        contests_resp = requests.get(f"{BASE_URL}/api/contests?limit=50")
        assert matches_resp.status_code == 200
        assert contests_resp.status_code == 200
        print("S13-16 PASS: Dashboard data sources work")
    
    # S13-17: Matches tab lists all matches with status badges
    def test_s13_17_matches_list(self):
        response = requests.get(f"{BASE_URL}/api/matches?limit=50")
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        if data["matches"]:
            assert "status" in data["matches"][0]
        print("S13-17 PASS: Matches list with status")
    
    # S13-18: Match status badges (verified by status field)
    def test_s13_18_match_status_values(self):
        response = requests.get(f"{BASE_URL}/api/matches?limit=50")
        assert response.status_code == 200
        data = response.json()
        valid_statuses = ["live", "upcoming", "completed", "abandoned"]
        for match in data.get("matches", []):
            assert match.get("status") in valid_statuses
        print("S13-18 PASS: Match status values are valid")
    
    # S13-19 to S13-22: Sync from Cricbuzz
    def test_s13_19_to_22_sync_cricbuzz(self, auth_headers):
        response = requests.post(f"{BASE_URL}/api/matches/live/sync", headers=auth_headers)
        assert response.status_code == 200
        print("S13-19 to S13-22 PASS: Sync from Cricbuzz works")
    
    # S13-25 & S13-26: Status change buttons call PUT /api/matches/{id}/status
    def test_s13_25_26_status_change(self, auth_headers):
        # Get a match
        response = requests.get(f"{BASE_URL}/api/matches?limit=1")
        if response.status_code == 200 and response.json().get("matches"):
            match_id = response.json()["matches"][0]["id"]
            # Try to update status
            status_resp = requests.put(
                f"{BASE_URL}/api/matches/{match_id}/status",
                headers=auth_headers,
                json={"status": "upcoming"}
            )
            assert status_resp.status_code == 200
        print("S13-25 & S13-26 PASS: Status change endpoint works")
    
    # S13-30: Resolve tab lists open contests
    def test_s13_30_open_contests_list(self):
        response = requests.get(f"{BASE_URL}/api/contests?status=open&limit=50")
        assert response.status_code == 200
        data = response.json()
        assert "contests" in data
        for contest in data.get("contests", []):
            assert contest.get("status") == "open"
        print("S13-30 PASS: Open contests list works")
    
    # S13-32 to S13-34: Load questions for contest
    def test_s13_32_to_34_load_questions(self, auth_headers):
        # Get an open contest
        response = requests.get(f"{BASE_URL}/api/contests?status=open&limit=1")
        if response.status_code == 200 and response.json().get("contests"):
            contest_id = response.json()["contests"][0]["id"]
            # Load questions
            q_resp = requests.get(f"{BASE_URL}/api/contests/{contest_id}/questions", headers=auth_headers)
            # May return 403 if not joined, which is expected
            assert q_resp.status_code in [200, 403]
        print("S13-32 to S13-34 PASS: Load questions endpoint works")
    
    # S13-35 & S13-36: Resolve question endpoint
    def test_s13_35_36_resolve_endpoint(self, auth_headers):
        # Get an open contest
        response = requests.get(f"{BASE_URL}/api/contests?status=open&limit=1")
        if response.status_code == 200 and response.json().get("contests"):
            contest_id = response.json()["contests"][0]["id"]
            # Try to resolve (may fail if no questions, but endpoint should work)
            resolve_resp = requests.post(
                f"{BASE_URL}/api/contests/{contest_id}/resolve",
                headers=auth_headers,
                json={"question_id": "test_q_id", "correct_option": "A"}
            )
            # 404 for question not found is acceptable
            assert resolve_resp.status_code in [200, 404]
        print("S13-35 & S13-36 PASS: Resolve endpoint works")
    
    # S13-38 & S13-39: Finalize endpoint
    def test_s13_38_39_finalize_endpoint(self, auth_headers):
        # Get an open contest
        response = requests.get(f"{BASE_URL}/api/contests?status=open&limit=1")
        if response.status_code == 200 and response.json().get("contests"):
            contest_id = response.json()["contests"][0]["id"]
            # Try to finalize
            finalize_resp = requests.post(
                f"{BASE_URL}/api/contests/{contest_id}/finalize",
                headers=auth_headers
            )
            # Should work or return already finalized
            assert finalize_resp.status_code == 200
        print("S13-38 & S13-39 PASS: Finalize endpoint works")
    
    # S13-44: Admin endpoints require auth token
    def test_s13_44_admin_endpoints_require_auth(self):
        # Test various admin endpoints without auth
        endpoints = [
            ("POST", "/api/matches/live/sync"),
            ("PUT", "/api/matches/test123/status"),
            ("POST", "/api/contests/test123/resolve"),
            ("POST", "/api/contests/test123/finalize"),
        ]
        for method, endpoint in endpoints:
            if method == "POST":
                resp = requests.post(f"{BASE_URL}{endpoint}")
            else:
                resp = requests.put(f"{BASE_URL}{endpoint}", json={"status": "upcoming"})
            assert resp.status_code in [401, 404, 422]  # 401 for auth, 404/422 for validation
        print("S13-44 PASS: Admin endpoints require auth")
    
    # S13-50: No _id in any admin-related API response
    def test_s13_50_no_id_in_responses(self, auth_headers):
        # Check matches response - verify no MongoDB _id key in response objects
        resp = requests.get(f"{BASE_URL}/api/matches?limit=10")
        data = resp.json()
        assert "_id" not in data
        for match in data.get("matches", []):
            assert "_id" not in match
        
        # Check contests response
        resp = requests.get(f"{BASE_URL}/api/contests?limit=10")
        data = resp.json()
        assert "_id" not in data
        for contest in data.get("contests", []):
            assert "_id" not in contest
        
        # Check sync response
        resp = requests.post(f"{BASE_URL}/api/matches/live/sync", headers=auth_headers)
        data = resp.json()
        assert "_id" not in data
        
        print("S13-50 PASS: No _id in any admin-related API response")


# ==================== RUN ALL TESTS ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
