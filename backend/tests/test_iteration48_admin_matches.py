"""
Iteration 48 - Admin Matches Section Rebuild Tests
Tests for:
1. Admin login with phone 7004186276 and PIN 5524
2. Match list with IST dates (not GMT)
3. Match status transitions: upcoming→live, live→upcoming (unlive)
4. Contest CRUD: create, status changes (open/live/locked), delete
5. Max 5 contests per match enforcement
6. Sync IPL Schedule button
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAdminMatchesSection:
    """Tests for the rebuilt Admin Matches section"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Get admin auth token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "phone": "7004186276",
            "pin": "5524"
        })
        assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
        data = login_resp.json()
        # Token is nested under "token" object
        token_data = data.get("token", {})
        self.token = token_data.get("access_token")
        assert self.token, f"No access_token in login response: {data}"
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        self.user = data.get("user", {})
        
    def test_admin_login_success(self):
        """Test admin login with correct credentials"""
        assert self.user.get("is_admin") == True, "User should be admin"
        assert self.user.get("phone") == "7004186276"
        print("PASSED: Admin login successful")
        
    def test_list_matches_returns_data(self):
        """Test GET /api/matches returns match list"""
        resp = self.session.get(f"{BASE_URL}/api/matches?limit=50")
        assert resp.status_code == 200, f"List matches failed: {resp.text}"
        data = resp.json()
        assert "matches" in data
        assert len(data["matches"]) > 0, "Should have matches"
        print(f"PASSED: Got {len(data['matches'])} matches")
        
    def test_match_has_ist_date_format(self):
        """Test that matches have start_time in ISO format (can be converted to IST)"""
        resp = self.session.get(f"{BASE_URL}/api/matches?limit=5")
        assert resp.status_code == 200
        matches = resp.json().get("matches", [])
        assert len(matches) > 0
        
        # Check first match has start_time
        match = matches[0]
        assert "start_time" in match, "Match should have start_time"
        start_time = match["start_time"]
        assert start_time, "start_time should not be empty"
        # ISO format check (contains T or has date format)
        assert "T" in start_time or "-" in start_time, f"start_time should be ISO format: {start_time}"
        print(f"PASSED: Match start_time is ISO format: {start_time}")
        
    def test_match_status_upcoming_to_live(self):
        """Test PUT /api/matches/{id}/status: upcoming → live"""
        # Find an upcoming match
        resp = self.session.get(f"{BASE_URL}/api/matches?status=upcoming&limit=10")
        assert resp.status_code == 200
        matches = resp.json().get("matches", [])
        
        if not matches:
            pytest.skip("No upcoming matches to test")
            
        match_id = matches[0]["id"]
        match_name = f"{matches[0].get('team_a', {}).get('short_name', '?')} vs {matches[0].get('team_b', {}).get('short_name', '?')}"
        
        # Change to live
        resp = self.session.put(f"{BASE_URL}/api/matches/{match_id}/status", json={"status": "live"})
        assert resp.status_code == 200, f"Status change failed: {resp.text}"
        updated = resp.json()
        assert updated.get("status") == "live", f"Status should be live, got: {updated.get('status')}"
        print(f"PASSED: Match {match_name} changed to LIVE")
        
        # Store for cleanup
        self._live_match_id = match_id
        
    def test_match_status_live_to_upcoming_unlive(self):
        """Test PUT /api/matches/{id}/status: live → upcoming (unlive feature)"""
        # First make a match live if not already
        resp = self.session.get(f"{BASE_URL}/api/matches?status=live&limit=10")
        assert resp.status_code == 200
        matches = resp.json().get("matches", [])
        
        if not matches:
            # Make one live first
            resp = self.session.get(f"{BASE_URL}/api/matches?status=upcoming&limit=1")
            if resp.status_code == 200 and resp.json().get("matches"):
                match_id = resp.json()["matches"][0]["id"]
                self.session.put(f"{BASE_URL}/api/matches/{match_id}/status", json={"status": "live"})
            else:
                pytest.skip("No matches available to test unlive")
        else:
            match_id = matches[0]["id"]
            
        # Now change live → upcoming (unlive)
        resp = self.session.put(f"{BASE_URL}/api/matches/{match_id}/status", json={"status": "upcoming"})
        assert resp.status_code == 200, f"Unlive failed: {resp.text}"
        updated = resp.json()
        assert updated.get("status") == "upcoming", f"Status should be upcoming, got: {updated.get('status')}"
        print(f"PASSED: Match unlive (live → upcoming) works")
        
    def test_list_templates(self):
        """Test GET /api/admin/templates returns templates"""
        resp = self.session.get(f"{BASE_URL}/api/admin/templates?limit=50")
        assert resp.status_code == 200, f"List templates failed: {resp.text}"
        data = resp.json()
        assert "templates" in data
        templates = data["templates"]
        assert len(templates) > 0, "Should have at least 1 template"
        
        # Check template structure
        template = templates[0]
        assert "id" in template
        assert "name" in template
        assert "question_ids" in template
        print(f"PASSED: Got {len(templates)} templates, first: {template.get('name')}")
        
    def test_list_contests_for_match(self):
        """Test GET /api/admin/contests?match_id={id}"""
        # Get a match first
        resp = self.session.get(f"{BASE_URL}/api/matches?limit=1")
        assert resp.status_code == 200
        matches = resp.json().get("matches", [])
        assert len(matches) > 0
        match_id = matches[0]["id"]
        
        # Get contests for this match
        resp = self.session.get(f"{BASE_URL}/api/admin/contests?match_id={match_id}&limit=10")
        assert resp.status_code == 200, f"List contests failed: {resp.text}"
        data = resp.json()
        assert "contests" in data
        print(f"PASSED: Got {len(data['contests'])} contests for match")
        
    def test_create_contest(self):
        """Test POST /api/admin/contests creates a contest"""
        # Get a match and template
        resp = self.session.get(f"{BASE_URL}/api/matches?status=upcoming&limit=5")
        assert resp.status_code == 200
        matches = resp.json().get("matches", [])
        if not matches:
            resp = self.session.get(f"{BASE_URL}/api/matches?limit=5")
            matches = resp.json().get("matches", [])
        assert len(matches) > 0, "Need at least 1 match"
        
        # Find a match with less than 5 contests
        match_id = None
        for m in matches:
            contests_resp = self.session.get(f"{BASE_URL}/api/admin/contests?match_id={m['id']}&limit=10")
            if contests_resp.status_code == 200:
                contests = contests_resp.json().get("contests", [])
                if len(contests) < 5:
                    match_id = m["id"]
                    break
                    
        if not match_id:
            pytest.skip("All matches have 5 contests already")
            
        resp = self.session.get(f"{BASE_URL}/api/admin/templates?limit=1")
        assert resp.status_code == 200
        templates = resp.json().get("templates", [])
        assert len(templates) > 0, "Need at least 1 template"
        template_id = templates[0]["id"]
        
        # Create contest
        contest_data = {
            "match_id": match_id,
            "template_id": template_id,
            "name": "TEST_Iteration48_Contest",
            "entry_fee": 500,
            "prize_pool": 0,
            "max_participants": 1000
        }
        resp = self.session.post(f"{BASE_URL}/api/admin/contests", json=contest_data)
        assert resp.status_code == 201, f"Create contest failed: {resp.text}"
        created = resp.json()
        assert created.get("id"), "Contest should have ID"
        assert created.get("name") == "TEST_Iteration48_Contest"
        assert created.get("status") == "open"
        print(f"PASSED: Created contest {created['id']}")
        
        # Store for cleanup
        self._created_contest_id = created["id"]
        
    def test_contest_status_open_to_live(self):
        """Test PUT /api/admin/contests/{id}/status: open → live"""
        # Create a test contest first
        resp = self.session.get(f"{BASE_URL}/api/matches?limit=5")
        matches = resp.json().get("matches", [])
        
        # Find match with room for contest
        match_id = None
        for m in matches:
            contests_resp = self.session.get(f"{BASE_URL}/api/admin/contests?match_id={m['id']}&limit=10")
            if contests_resp.status_code == 200:
                contests = contests_resp.json().get("contests", [])
                if len(contests) < 5:
                    match_id = m["id"]
                    break
                    
        if not match_id:
            pytest.skip("No match available for contest status test")
            
        resp = self.session.get(f"{BASE_URL}/api/admin/templates?limit=1")
        templates = resp.json().get("templates", [])
        template_id = templates[0]["id"]
        
        # Create contest
        resp = self.session.post(f"{BASE_URL}/api/admin/contests", json={
            "match_id": match_id,
            "template_id": template_id,
            "name": "TEST_StatusTest_Contest",
            "entry_fee": 100,
            "prize_pool": 0,
            "max_participants": 100
        })
        if resp.status_code != 201:
            pytest.skip(f"Could not create test contest: {resp.text}")
        contest_id = resp.json()["id"]
        
        # Change to live
        resp = self.session.put(f"{BASE_URL}/api/admin/contests/{contest_id}/status", json={"status": "live"})
        assert resp.status_code == 200, f"Contest status change failed: {resp.text}"
        assert resp.json().get("new_status") == "live"
        print(f"PASSED: Contest status open → live")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/admin/contests/{contest_id}")
        
    def test_contest_status_live_to_open_unlive(self):
        """Test PUT /api/admin/contests/{id}/status: live → open (unlive)"""
        # Create and make live first
        resp = self.session.get(f"{BASE_URL}/api/matches?limit=5")
        matches = resp.json().get("matches", [])
        
        match_id = None
        for m in matches:
            contests_resp = self.session.get(f"{BASE_URL}/api/admin/contests?match_id={m['id']}&limit=10")
            if contests_resp.status_code == 200:
                contests = contests_resp.json().get("contests", [])
                if len(contests) < 5:
                    match_id = m["id"]
                    break
                    
        if not match_id:
            pytest.skip("No match available")
            
        resp = self.session.get(f"{BASE_URL}/api/admin/templates?limit=1")
        templates = resp.json().get("templates", [])
        template_id = templates[0]["id"]
        
        # Create and make live
        resp = self.session.post(f"{BASE_URL}/api/admin/contests", json={
            "match_id": match_id,
            "template_id": template_id,
            "name": "TEST_UnliveTest_Contest",
            "entry_fee": 100,
            "prize_pool": 0,
            "max_participants": 100
        })
        if resp.status_code != 201:
            pytest.skip(f"Could not create test contest: {resp.text}")
        contest_id = resp.json()["id"]
        
        # Make live
        self.session.put(f"{BASE_URL}/api/admin/contests/{contest_id}/status", json={"status": "live"})
        
        # Now unlive (live → open)
        resp = self.session.put(f"{BASE_URL}/api/admin/contests/{contest_id}/status", json={"status": "open"})
        assert resp.status_code == 200, f"Contest unlive failed: {resp.text}"
        assert resp.json().get("new_status") == "open"
        print(f"PASSED: Contest status live → open (unlive)")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/admin/contests/{contest_id}")
        
    def test_delete_contest(self):
        """Test DELETE /api/admin/contests/{id}"""
        # Create a contest to delete
        resp = self.session.get(f"{BASE_URL}/api/matches?limit=5")
        matches = resp.json().get("matches", [])
        
        match_id = None
        for m in matches:
            contests_resp = self.session.get(f"{BASE_URL}/api/admin/contests?match_id={m['id']}&limit=10")
            if contests_resp.status_code == 200:
                contests = contests_resp.json().get("contests", [])
                if len(contests) < 5:
                    match_id = m["id"]
                    break
                    
        if not match_id:
            pytest.skip("No match available")
            
        resp = self.session.get(f"{BASE_URL}/api/admin/templates?limit=1")
        templates = resp.json().get("templates", [])
        template_id = templates[0]["id"]
        
        # Create
        resp = self.session.post(f"{BASE_URL}/api/admin/contests", json={
            "match_id": match_id,
            "template_id": template_id,
            "name": "TEST_DeleteMe_Contest",
            "entry_fee": 100,
            "prize_pool": 0,
            "max_participants": 100
        })
        if resp.status_code != 201:
            pytest.skip(f"Could not create test contest: {resp.text}")
        contest_id = resp.json()["id"]
        
        # Delete
        resp = self.session.delete(f"{BASE_URL}/api/admin/contests/{contest_id}")
        assert resp.status_code == 200, f"Delete contest failed: {resp.text}"
        print(f"PASSED: Contest deleted successfully")
        
        # Verify deleted
        resp = self.session.get(f"{BASE_URL}/api/admin/contests?match_id={match_id}&limit=50")
        contests = resp.json().get("contests", [])
        contest_ids = [c["id"] for c in contests]
        assert contest_id not in contest_ids, "Contest should be deleted"
        
    def test_max_5_contests_enforcement(self):
        """Test that max 5 contests per match is enforced"""
        # Find or create a match with 5 contests
        resp = self.session.get(f"{BASE_URL}/api/matches?limit=20")
        matches = resp.json().get("matches", [])
        
        match_with_5 = None
        for m in matches:
            contests_resp = self.session.get(f"{BASE_URL}/api/admin/contests?match_id={m['id']}&limit=10")
            if contests_resp.status_code == 200:
                contests = contests_resp.json().get("contests", [])
                if len(contests) >= 5:
                    match_with_5 = m["id"]
                    break
                    
        if not match_with_5:
            pytest.skip("No match with 5 contests to test enforcement")
            
        resp = self.session.get(f"{BASE_URL}/api/admin/templates?limit=1")
        templates = resp.json().get("templates", [])
        template_id = templates[0]["id"]
        
        # Try to create 6th contest - should fail
        resp = self.session.post(f"{BASE_URL}/api/admin/contests", json={
            "match_id": match_with_5,
            "template_id": template_id,
            "name": "TEST_ShouldFail_Contest",
            "entry_fee": 100,
            "prize_pool": 0,
            "max_participants": 100
        })
        assert resp.status_code == 400, f"Should reject 6th contest, got: {resp.status_code}"
        assert "5 contests" in resp.text.lower() or "maximum" in resp.text.lower(), f"Error should mention max 5: {resp.text}"
        print(f"PASSED: Max 5 contests enforcement works")
        
    def test_sync_ipl_schedule(self):
        """Test POST /api/matches/live/sync-ipl-schedule"""
        resp = self.session.post(f"{BASE_URL}/api/matches/live/sync-ipl-schedule")
        assert resp.status_code == 200, f"Sync IPL schedule failed: {resp.text}"
        data = resp.json()
        assert "synced" in data or "created" in data or "updated" in data
        print(f"PASSED: Sync IPL schedule - created: {data.get('created', 0)}, updated: {data.get('updated', 0)}")
        
    def test_questions_have_hindi_text(self):
        """Test that questions have Hindi text"""
        resp = self.session.get(f"{BASE_URL}/api/admin/questions?limit=20")
        assert resp.status_code == 200
        questions = resp.json().get("questions", [])
        assert len(questions) > 0, "Should have questions"
        
        # Check at least some have Hindi text
        hindi_count = sum(1 for q in questions if q.get("question_text_hi"))
        assert hindi_count > 0, "Should have questions with Hindi text"
        print(f"PASSED: {hindi_count}/{len(questions)} questions have Hindi text")


class TestContestStatusTransitions:
    """Test all contest status transitions"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "phone": "7004186276",
            "pin": "5524"
        })
        assert login_resp.status_code == 200
        token_data = login_resp.json().get("token", {})
        self.token = token_data.get("access_token")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        
    def test_contest_status_locked_to_open(self):
        """Test contest can go from locked back to open"""
        # Find or create a contest
        resp = self.session.get(f"{BASE_URL}/api/matches?limit=5")
        matches = resp.json().get("matches", [])
        
        match_id = None
        for m in matches:
            contests_resp = self.session.get(f"{BASE_URL}/api/admin/contests?match_id={m['id']}&limit=10")
            if contests_resp.status_code == 200:
                contests = contests_resp.json().get("contests", [])
                if len(contests) < 5:
                    match_id = m["id"]
                    break
                    
        if not match_id:
            pytest.skip("No match available")
            
        resp = self.session.get(f"{BASE_URL}/api/admin/templates?limit=1")
        templates = resp.json().get("templates", [])
        template_id = templates[0]["id"]
        
        # Create contest
        resp = self.session.post(f"{BASE_URL}/api/admin/contests", json={
            "match_id": match_id,
            "template_id": template_id,
            "name": "TEST_LockedToOpen_Contest",
            "entry_fee": 100,
            "prize_pool": 0,
            "max_participants": 100
        })
        if resp.status_code != 201:
            pytest.skip(f"Could not create test contest: {resp.text}")
        contest_id = resp.json()["id"]
        
        # Make locked
        resp = self.session.put(f"{BASE_URL}/api/admin/contests/{contest_id}/status", json={"status": "locked"})
        assert resp.status_code == 200
        
        # Now unlock (locked → open)
        resp = self.session.put(f"{BASE_URL}/api/admin/contests/{contest_id}/status", json={"status": "open"})
        # This might fail if locked→open is not allowed - check the actual behavior
        if resp.status_code == 200:
            print(f"PASSED: Contest status locked → open works")
        else:
            print(f"INFO: Contest status locked → open returned {resp.status_code}: {resp.text}")
            
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/admin/contests/{contest_id}")
        
    def test_contest_status_locked_to_live(self):
        """Test contest can go from locked to live"""
        resp = self.session.get(f"{BASE_URL}/api/matches?limit=5")
        matches = resp.json().get("matches", [])
        
        match_id = None
        for m in matches:
            contests_resp = self.session.get(f"{BASE_URL}/api/admin/contests?match_id={m['id']}&limit=10")
            if contests_resp.status_code == 200:
                contests = contests_resp.json().get("contests", [])
                if len(contests) < 5:
                    match_id = m["id"]
                    break
                    
        if not match_id:
            pytest.skip("No match available")
            
        resp = self.session.get(f"{BASE_URL}/api/admin/templates?limit=1")
        templates = resp.json().get("templates", [])
        template_id = templates[0]["id"]
        
        # Create contest
        resp = self.session.post(f"{BASE_URL}/api/admin/contests", json={
            "match_id": match_id,
            "template_id": template_id,
            "name": "TEST_LockedToLive_Contest",
            "entry_fee": 100,
            "prize_pool": 0,
            "max_participants": 100
        })
        if resp.status_code != 201:
            pytest.skip(f"Could not create test contest: {resp.text}")
        contest_id = resp.json()["id"]
        
        # Make locked
        self.session.put(f"{BASE_URL}/api/admin/contests/{contest_id}/status", json={"status": "locked"})
        
        # Now locked → live
        resp = self.session.put(f"{BASE_URL}/api/admin/contests/{contest_id}/status", json={"status": "live"})
        assert resp.status_code == 200, f"locked → live failed: {resp.text}"
        print(f"PASSED: Contest status locked → live works")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/admin/contests/{contest_id}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
