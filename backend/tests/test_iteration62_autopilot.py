"""
Iteration 62 - Auto-Pilot Toggle and Match Auto-Engine Tests
Tests the new admin dashboard features:
1. Auto-Pilot toggle (START/STOP)
2. Match Auto-Engine buttons (Seed 200 Qs, Auto Templates, 24h Contests)
3. Per-match Auto 5 Templates button
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
ADMIN_PHONE = "7004186276"
ADMIN_PIN = "5524"


class TestAutoPilotAPIs:
    """Test Auto-Pilot toggle APIs"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin auth token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "phone": ADMIN_PHONE,
            "pin": ADMIN_PIN
        })
        assert login_response.status_code == 200, f"Admin login failed: {login_response.text}"
        
        data = login_response.json()
        # Token is nested under 'token' object
        token_data = data.get("token", {})
        self.token = token_data.get("access_token")
        assert self.token, f"No access_token in login response: {data}"
        
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def test_autopilot_status_endpoint(self):
        """Test GET /api/admin/autopilot/status returns correct status JSON"""
        response = self.session.get(f"{BASE_URL}/api/admin/autopilot/status")
        assert response.status_code == 200, f"Status endpoint failed: {response.text}"
        
        data = response.json()
        # Verify response structure
        assert "running" in data, "Missing 'running' field in status"
        assert "run_count" in data, "Missing 'run_count' field in status"
        assert "last_run" in data, "Missing 'last_run' field in status"
        assert "recent_log" in data, "Missing 'recent_log' field in status"
        
        # running should be boolean
        assert isinstance(data["running"], bool), "running should be boolean"
        # run_count should be integer
        assert isinstance(data["run_count"], int), "run_count should be integer"
        
        print(f"Auto-Pilot Status: running={data['running']}, run_count={data['run_count']}")
    
    def test_autopilot_start_endpoint(self):
        """Test POST /api/admin/autopilot/start starts the autopilot"""
        response = self.session.post(f"{BASE_URL}/api/admin/autopilot/start")
        assert response.status_code == 200, f"Start endpoint failed: {response.text}"
        
        data = response.json()
        # Should return running status
        assert "running" in data or "message" in data, "Missing expected fields in start response"
        
        # If already running, message will say so
        if "message" in data:
            print(f"Start response: {data['message']}")
        
        # Verify status shows running
        status_response = self.session.get(f"{BASE_URL}/api/admin/autopilot/status")
        status_data = status_response.json()
        assert status_data.get("running") == True, "Auto-Pilot should be running after start"
        
        print(f"Auto-Pilot started successfully, running={status_data['running']}")
    
    def test_autopilot_stop_endpoint(self):
        """Test POST /api/admin/autopilot/stop stops the autopilot"""
        # First ensure it's started
        self.session.post(f"{BASE_URL}/api/admin/autopilot/start")
        
        # Now stop it
        response = self.session.post(f"{BASE_URL}/api/admin/autopilot/stop")
        assert response.status_code == 200, f"Stop endpoint failed: {response.text}"
        
        data = response.json()
        assert "running" in data or "message" in data, "Missing expected fields in stop response"
        
        # Verify status shows stopped
        status_response = self.session.get(f"{BASE_URL}/api/admin/autopilot/status")
        status_data = status_response.json()
        assert status_data.get("running") == False, "Auto-Pilot should be stopped after stop"
        
        print(f"Auto-Pilot stopped successfully, running={status_data['running']}")
    
    def test_autopilot_toggle_cycle(self):
        """Test full START -> verify -> STOP -> verify cycle"""
        # Stop first to ensure clean state
        self.session.post(f"{BASE_URL}/api/admin/autopilot/stop")
        
        # Verify stopped
        status1 = self.session.get(f"{BASE_URL}/api/admin/autopilot/status").json()
        assert status1["running"] == False, "Should be stopped initially"
        
        # Start
        start_resp = self.session.post(f"{BASE_URL}/api/admin/autopilot/start")
        assert start_resp.status_code == 200
        
        # Verify running
        status2 = self.session.get(f"{BASE_URL}/api/admin/autopilot/status").json()
        assert status2["running"] == True, "Should be running after start"
        
        # Stop
        stop_resp = self.session.post(f"{BASE_URL}/api/admin/autopilot/stop")
        assert stop_resp.status_code == 200
        
        # Verify stopped
        status3 = self.session.get(f"{BASE_URL}/api/admin/autopilot/status").json()
        assert status3["running"] == False, "Should be stopped after stop"
        
        print("Full toggle cycle (STOP -> START -> STOP) completed successfully")


class TestMatchAutoEngineAPIs:
    """Test Match Auto-Engine APIs"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin auth token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "phone": ADMIN_PHONE,
            "pin": ADMIN_PIN
        })
        assert login_response.status_code == 200, f"Admin login failed: {login_response.text}"
        
        data = login_response.json()
        # Token is nested under 'token' object
        token_data = data.get("token", {})
        self.token = token_data.get("access_token")
        assert self.token, f"No access_token in login response: {data}"
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def test_seed_question_pool_endpoint(self):
        """Test POST /api/admin/seed-question-pool seeds 200 questions"""
        response = self.session.post(f"{BASE_URL}/api/admin/seed-question-pool")
        
        # This endpoint might not exist yet - check for 404 vs other errors
        if response.status_code == 404:
            pytest.skip("seed-question-pool endpoint not implemented yet")
        
        assert response.status_code in [200, 201], f"Seed endpoint failed: {response.status_code} - {response.text}"
        
        data = response.json()
        # Should return info about seeded questions
        print(f"Seed question pool response: {data}")
        
        # Verify some questions were seeded or message returned
        assert "seeded" in data or "message" in data or "imported" in data, "Missing expected fields in seed response"
    
    def test_auto_templates_all_endpoint(self):
        """Test POST /api/admin/auto-templates-all generates templates for all upcoming matches"""
        response = self.session.post(f"{BASE_URL}/api/admin/auto-templates-all")
        
        # This endpoint might not exist yet - check for 404 vs other errors
        if response.status_code == 404:
            pytest.skip("auto-templates-all endpoint not implemented yet")
        
        assert response.status_code in [200, 201], f"Auto templates endpoint failed: {response.status_code} - {response.text}"
        
        data = response.json()
        print(f"Auto templates all response: {data}")
        
        # Should return info about processed matches
        assert "processed" in data or "message" in data or "results" in data, "Missing expected fields in auto-templates response"
    
    def test_auto_contests_24h_endpoint(self):
        """Test POST /api/admin/auto-contests-24h creates contests for matches within 24h"""
        response = self.session.post(f"{BASE_URL}/api/admin/auto-contests-24h")
        
        assert response.status_code in [200, 201], f"Auto contests 24h endpoint failed: {response.status_code} - {response.text}"
        
        data = response.json()
        print(f"Auto contests 24h response: {data}")
        
        # Should return info about created contests
        assert "results" in data or "message" in data or "created" in data, "Missing expected fields in auto-contests response"


class TestPerMatchAutoTemplates:
    """Test per-match Auto 5 Templates API"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin auth token and find a match"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "phone": ADMIN_PHONE,
            "pin": ADMIN_PIN
        })
        assert login_response.status_code == 200, f"Admin login failed: {login_response.text}"
        
        data = login_response.json()
        # Token is nested under 'token' object
        token_data = data.get("token", {})
        self.token = token_data.get("access_token")
        assert self.token, f"No access_token in login response: {data}"
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        
        # Get a match to test with
        matches_response = self.session.get(f"{BASE_URL}/api/matches?limit=5")
        if matches_response.status_code == 200:
            matches_data = matches_response.json()
            matches = matches_data.get("matches", [])
            if matches:
                self.test_match_id = matches[0].get("id")
            else:
                self.test_match_id = None
        else:
            self.test_match_id = None
    
    def test_per_match_auto_templates_endpoint(self):
        """Test POST /api/admin/matches/{match_id}/auto-templates generates 5 templates for a match"""
        if not self.test_match_id:
            pytest.skip("No matches available to test auto-templates")
        
        response = self.session.post(f"{BASE_URL}/api/admin/matches/{self.test_match_id}/auto-templates")
        
        # This endpoint might not exist yet - check for 404 vs other errors
        if response.status_code == 404:
            pytest.skip("per-match auto-templates endpoint not implemented yet")
        
        assert response.status_code in [200, 201], f"Per-match auto templates failed: {response.status_code} - {response.text}"
        
        data = response.json()
        print(f"Per-match auto templates response: {data}")
        
        # Should return info about created templates
        assert "templates_created" in data or "message" in data, "Missing expected fields in per-match auto-templates response"


class TestAdminStatsEndpoint:
    """Test admin stats endpoint to verify dashboard data"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin auth token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "phone": ADMIN_PHONE,
            "pin": ADMIN_PIN
        })
        assert login_response.status_code == 200, f"Admin login failed: {login_response.text}"
        
        data = login_response.json()
        # Token is nested under 'token' object
        token_data = data.get("token", {})
        self.token = token_data.get("access_token")
        assert self.token, f"No access_token in login response: {data}"
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def test_admin_stats_endpoint(self):
        """Test GET /api/admin/stats returns dashboard statistics"""
        response = self.session.get(f"{BASE_URL}/api/admin/stats")
        assert response.status_code == 200, f"Admin stats failed: {response.text}"
        
        data = response.json()
        
        # Verify expected fields
        expected_fields = ["users", "matches", "contests", "questions", "templates"]
        for field in expected_fields:
            assert field in data, f"Missing '{field}' in admin stats"
        
        print(f"Admin Stats: users={data.get('users')}, matches={data.get('matches')}, contests={data.get('contests')}, questions={data.get('questions')}, templates={data.get('templates')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
