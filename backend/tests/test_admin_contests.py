"""
Admin Contests API Tests - Iteration 46
Tests for contest management within matches:
- Admin login
- List matches with status
- List contests for a match
- Create contest (with template selection)
- Delete contest
- Max 5 contests per match enforcement
- 16 questions seeded verification
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
ADMIN_PHONE = "7004186276"
ADMIN_PIN = "5524"


class TestAdminContests:
    """Admin Contest Management Tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": ADMIN_PHONE,
            "pin": ADMIN_PIN
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        # Token path: response.token.access_token
        token = data.get("token", {}).get("access_token")
        assert token, f"No access_token in response: {data}"
        return token
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Auth headers for admin requests"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    # ==================== ADMIN LOGIN ====================
    
    def test_admin_login_success(self):
        """Test admin login with correct credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": ADMIN_PHONE,
            "pin": ADMIN_PIN
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["is_admin"] == True
        print(f"✓ Admin login successful: {data['user'].get('username', 'admin')}")
    
    def test_admin_login_wrong_pin(self):
        """Test admin login with wrong PIN"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": ADMIN_PHONE,
            "pin": "0000"
        })
        assert response.status_code == 401
        print("✓ Wrong PIN correctly rejected")
    
    # ==================== MATCHES LIST ====================
    
    def test_list_matches(self, auth_headers):
        """Test listing matches with status (COMPLETED/UPCOMING)"""
        response = requests.get(f"{BASE_URL}/api/matches?limit=50", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        matches = data["matches"]
        assert len(matches) > 0, "No matches found"
        
        # Check match structure
        first_match = matches[0]
        assert "id" in first_match
        assert "status" in first_match
        assert "team_a" in first_match
        assert "team_b" in first_match
        
        # Count by status
        statuses = {}
        for m in matches:
            s = m.get("status", "unknown")
            statuses[s] = statuses.get(s, 0) + 1
        
        print(f"✓ Found {len(matches)} matches. Status breakdown: {statuses}")
        return matches
    
    # ==================== TEMPLATES ====================
    
    def test_list_templates(self, auth_headers):
        """Test listing templates (should have 2: First Innings + Full Match)"""
        response = requests.get(f"{BASE_URL}/api/admin/templates?limit=50", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        templates = data["templates"]
        
        # Should have at least 2 templates
        assert len(templates) >= 2, f"Expected at least 2 templates, got {len(templates)}"
        
        # Check for default templates
        default_templates = [t for t in templates if t.get("is_default")]
        print(f"✓ Found {len(templates)} templates, {len(default_templates)} are default")
        
        for t in templates:
            print(f"  - {t.get('name')}: {t.get('template_type')}, {len(t.get('question_ids', []))} questions, default={t.get('is_default')}")
        
        return templates
    
    # ==================== QUESTIONS SEEDED ====================
    
    def test_questions_seeded(self, auth_headers):
        """Test that 16 questions are seeded with correct Hindi text"""
        response = requests.get(f"{BASE_URL}/api/admin/questions?limit=50", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "questions" in data
        questions = data["questions"]
        
        # Should have 16 questions
        assert len(questions) >= 16, f"Expected 16 questions, got {len(questions)}"
        
        # Check Hindi text exists
        hindi_count = 0
        for q in questions:
            if q.get("question_text_hi"):
                hindi_count += 1
        
        assert hindi_count >= 16, f"Expected 16 questions with Hindi text, got {hindi_count}"
        print(f"✓ Found {len(questions)} questions, {hindi_count} have Hindi text")
        
        # Sample check
        sample = questions[0]
        print(f"  Sample: {sample.get('question_text_hi', '')[:50]}...")
        
        return questions
    
    # ==================== CONTESTS FOR MATCH ====================
    
    def test_list_contests_for_match(self, auth_headers):
        """Test listing contests for a specific match"""
        # First get a match
        matches_resp = requests.get(f"{BASE_URL}/api/matches?limit=10", headers=auth_headers)
        assert matches_resp.status_code == 200
        matches = matches_resp.json().get("matches", [])
        assert len(matches) > 0
        
        match_id = matches[0]["id"]
        
        # Get contests for this match
        response = requests.get(f"{BASE_URL}/api/admin/contests?match_id={match_id}&limit=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "contests" in data
        
        contests = data["contests"]
        print(f"✓ Match {match_id[:8]}... has {len(contests)} contests")
        
        for c in contests:
            print(f"  - {c.get('name')}: status={c.get('status')}, template_type={c.get('template_type')}")
        
        return {"match_id": match_id, "contests": contests}
    
    # ==================== CREATE CONTEST ====================
    
    def test_create_contest(self, auth_headers):
        """Test creating a new contest for a match"""
        # Get a match
        matches_resp = requests.get(f"{BASE_URL}/api/matches?limit=50", headers=auth_headers)
        matches = matches_resp.json().get("matches", [])
        
        # Find a match with less than 5 contests
        target_match = None
        for m in matches:
            contests_resp = requests.get(f"{BASE_URL}/api/admin/contests?match_id={m['id']}&limit=10", headers=auth_headers)
            contests = contests_resp.json().get("contests", [])
            if len(contests) < 5:
                target_match = m
                existing_count = len(contests)
                break
        
        if not target_match:
            pytest.skip("All matches have 5 contests already")
        
        # Get a template
        templates_resp = requests.get(f"{BASE_URL}/api/admin/templates?limit=10", headers=auth_headers)
        templates = templates_resp.json().get("templates", [])
        assert len(templates) > 0, "No templates available"
        
        template = templates[0]
        
        # Create contest
        team_a = target_match.get("team_a", {}).get("short_name", "A")
        team_b = target_match.get("team_b", {}).get("short_name", "B")
        contest_name = f"TEST_{team_a} vs {team_b} Contest"
        
        response = requests.post(f"{BASE_URL}/api/admin/contests", headers=auth_headers, json={
            "match_id": target_match["id"],
            "template_id": template["id"],
            "name": contest_name,
            "entry_fee": 500,
            "prize_pool": 0,
            "max_participants": 100
        })
        
        assert response.status_code == 201, f"Create contest failed: {response.text}"
        data = response.json()
        assert "id" in data
        assert data["name"] == contest_name
        assert data["match_id"] == target_match["id"]
        assert data["template_id"] == template["id"]
        
        print(f"✓ Created contest: {contest_name} (id: {data['id'][:8]}...)")
        
        # Verify it appears in list
        verify_resp = requests.get(f"{BASE_URL}/api/admin/contests?match_id={target_match['id']}&limit=10", headers=auth_headers)
        verify_contests = verify_resp.json().get("contests", [])
        assert len(verify_contests) == existing_count + 1, "Contest count didn't increase"
        
        return {"contest_id": data["id"], "match_id": target_match["id"]}
    
    # ==================== DELETE CONTEST ====================
    
    def test_delete_contest(self, auth_headers):
        """Test deleting a contest"""
        # First create a contest to delete
        matches_resp = requests.get(f"{BASE_URL}/api/matches?limit=50", headers=auth_headers)
        matches = matches_resp.json().get("matches", [])
        
        # Find a match with less than 5 contests
        target_match = None
        for m in matches:
            contests_resp = requests.get(f"{BASE_URL}/api/admin/contests?match_id={m['id']}&limit=10", headers=auth_headers)
            contests = contests_resp.json().get("contests", [])
            if len(contests) < 5:
                target_match = m
                break
        
        if not target_match:
            pytest.skip("All matches have 5 contests")
        
        # Get template
        templates_resp = requests.get(f"{BASE_URL}/api/admin/templates?limit=10", headers=auth_headers)
        templates = templates_resp.json().get("templates", [])
        template = templates[0]
        
        # Create a test contest
        create_resp = requests.post(f"{BASE_URL}/api/admin/contests", headers=auth_headers, json={
            "match_id": target_match["id"],
            "template_id": template["id"],
            "name": "TEST_DELETE_ME_Contest",
            "entry_fee": 100,
            "prize_pool": 0,
            "max_participants": 50
        })
        
        if create_resp.status_code != 201:
            pytest.skip(f"Could not create test contest: {create_resp.text}")
        
        contest_id = create_resp.json()["id"]
        
        # Get count before delete
        before_resp = requests.get(f"{BASE_URL}/api/admin/contests?match_id={target_match['id']}&limit=10", headers=auth_headers)
        before_count = len(before_resp.json().get("contests", []))
        
        # Delete the contest
        delete_resp = requests.delete(f"{BASE_URL}/api/admin/contests/{contest_id}", headers=auth_headers)
        assert delete_resp.status_code == 200, f"Delete failed: {delete_resp.text}"
        
        # Verify deletion
        after_resp = requests.get(f"{BASE_URL}/api/admin/contests?match_id={target_match['id']}&limit=10", headers=auth_headers)
        after_count = len(after_resp.json().get("contests", []))
        
        assert after_count == before_count - 1, f"Contest count didn't decrease: {before_count} -> {after_count}"
        print(f"✓ Deleted contest {contest_id[:8]}... Count: {before_count} -> {after_count}")
    
    # ==================== MAX 5 CONTESTS ENFORCEMENT ====================
    
    def test_max_5_contests_enforcement(self, auth_headers):
        """Test that max 5 contests per match is enforced"""
        # Find a match with 5 contests (RCB vs SRH should have 4 test contests)
        matches_resp = requests.get(f"{BASE_URL}/api/matches?limit=50", headers=auth_headers)
        matches = matches_resp.json().get("matches", [])
        
        # Find match with most contests
        max_contests_match = None
        max_count = 0
        
        for m in matches:
            contests_resp = requests.get(f"{BASE_URL}/api/admin/contests?match_id={m['id']}&limit=10", headers=auth_headers)
            contests = contests_resp.json().get("contests", [])
            if len(contests) > max_count:
                max_count = len(contests)
                max_contests_match = m
        
        if max_count < 5:
            # Need to create contests to reach 5
            templates_resp = requests.get(f"{BASE_URL}/api/admin/templates?limit=10", headers=auth_headers)
            templates = templates_resp.json().get("templates", [])
            template = templates[0]
            
            for i in range(5 - max_count):
                requests.post(f"{BASE_URL}/api/admin/contests", headers=auth_headers, json={
                    "match_id": max_contests_match["id"],
                    "template_id": template["id"],
                    "name": f"TEST_MAX5_Contest_{i}",
                    "entry_fee": 100,
                    "prize_pool": 0,
                    "max_participants": 50
                })
            max_count = 5
        
        # Now try to create a 6th contest
        templates_resp = requests.get(f"{BASE_URL}/api/admin/templates?limit=10", headers=auth_headers)
        templates = templates_resp.json().get("templates", [])
        template = templates[0]
        
        response = requests.post(f"{BASE_URL}/api/admin/contests", headers=auth_headers, json={
            "match_id": max_contests_match["id"],
            "template_id": template["id"],
            "name": "TEST_6TH_CONTEST_SHOULD_FAIL",
            "entry_fee": 100,
            "prize_pool": 0,
            "max_participants": 50
        })
        
        assert response.status_code == 400, f"Expected 400 for 6th contest, got {response.status_code}"
        assert "Maximum 5 contests" in response.json().get("detail", "")
        print(f"✓ Max 5 contests enforced. Match {max_contests_match['id'][:8]}... has {max_count} contests")
    
    # ==================== ADMIN STATS ====================
    
    def test_admin_stats(self, auth_headers):
        """Test admin dashboard stats endpoint"""
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "users" in data
        assert "matches" in data
        assert "contests" in data
        assert "questions" in data
        assert "templates" in data
        
        print(f"✓ Admin stats: {data['users']} users, {data['matches']} matches, {data['contests']} contests, {data['questions']} questions, {data['templates']} templates")


# Cleanup fixture
@pytest.fixture(scope="module", autouse=True)
def cleanup_test_contests():
    """Cleanup TEST_ prefixed contests after all tests"""
    yield
    
    # Login and cleanup
    try:
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": ADMIN_PHONE,
            "pin": ADMIN_PIN
        })
        if login_resp.status_code == 200:
            token = login_resp.json().get("token", {}).get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Get all contests
            contests_resp = requests.get(f"{BASE_URL}/api/admin/contests?limit=100", headers=headers)
            if contests_resp.status_code == 200:
                contests = contests_resp.json().get("contests", [])
                test_contests = [c for c in contests if c.get("name", "").startswith("TEST_")]
                
                for c in test_contests:
                    requests.delete(f"{BASE_URL}/api/admin/contests/{c['id']}", headers=headers)
                
                if test_contests:
                    print(f"\n✓ Cleaned up {len(test_contests)} test contests")
    except Exception as e:
        print(f"Cleanup error: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
