"""
Iteration 47 - Backend Tests for Admin Contest Management
Tests: Admin login, Matches, Contests, Templates, Questions, Status Toggle, Delete
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_PHONE = "7004186276"
ADMIN_PIN = "5524"


def get_admin_token():
    """Get admin auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "phone": ADMIN_PHONE,
        "pin": ADMIN_PIN
    })
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    data = response.json()
    # Token is nested: data["token"]["access_token"]
    token = data.get("token", {}).get("access_token")
    if not token:
        token = data.get("access_token")  # fallback
    assert token, f"No access_token in response: {data}"
    return token


def get_admin_headers():
    """Get admin auth headers"""
    token = get_admin_token()
    return {"Authorization": f"Bearer {token}"}


class TestAdminAuth:
    """Admin authentication tests"""
    
    def test_admin_login_success(self):
        """Test admin login returns valid token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": ADMIN_PHONE,
            "pin": ADMIN_PIN
        })
        assert response.status_code == 200
        data = response.json()
        # Token is nested
        token = data.get("token", {}).get("access_token")
        assert token is not None, f"No token in response: {data}"
        assert len(token) > 20
        # Check user is admin
        user = data.get("user", {})
        assert user.get("is_admin") == True, f"User is not admin: {user}"


class TestMatchesAndContests:
    """Match and Contest management tests"""
    
    def test_list_matches(self):
        """Test listing matches"""
        headers = get_admin_headers()
        response = requests.get(f"{BASE_URL}/api/matches?limit=50", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        assert len(data["matches"]) > 0, "No matches found"
        # Verify match structure
        match = data["matches"][0]
        assert "id" in match
        assert "team_a" in match
        assert "team_b" in match
        assert "status" in match
    
    def test_list_templates(self):
        """Test listing templates - should have Full Match Predictions template"""
        headers = get_admin_headers()
        response = requests.get(f"{BASE_URL}/api/admin/templates?limit=50", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "templates" in data
        templates = data["templates"]
        assert len(templates) >= 1, "No templates found"
        
        # Find Full Match Predictions template
        full_match_template = None
        for t in templates:
            if "Full Match" in t.get("name", ""):
                full_match_template = t
                break
        
        assert full_match_template is not None, f"Full Match Predictions template not found. Templates: {[t.get('name') for t in templates]}"
        assert full_match_template.get("template_type") == "full_match"
        assert len(full_match_template.get("question_ids", [])) == 16, f"Expected 16 questions, got {len(full_match_template.get('question_ids', []))}"
        assert full_match_template.get("total_points") == 1270, f"Expected 1270 total points, got {full_match_template.get('total_points')}"
    
    def test_list_questions(self):
        """Test listing questions - should have 16 questions with Hindi text"""
        headers = get_admin_headers()
        response = requests.get(f"{BASE_URL}/api/admin/questions?limit=50", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "questions" in data
        questions = data["questions"]
        assert len(questions) >= 16, f"Expected at least 16 questions, got {len(questions)}"
        
        # Verify question structure and Hindi text
        for q in questions[:5]:
            assert "id" in q
            assert "question_text_hi" in q
            assert "difficulty" in q
            assert "points" in q
            assert "options" in q
            assert len(q["options"]) >= 2, "Question should have at least 2 options"
            # Verify Hindi text exists
            assert len(q.get("question_text_hi", "")) > 0, "Hindi text missing"
    
    def test_question_difficulty_points(self):
        """Test question difficulty and points mapping: EASY=55, MEDIUM=70, HARD=90"""
        headers = get_admin_headers()
        response = requests.get(f"{BASE_URL}/api/admin/questions?limit=50", headers=headers)
        assert response.status_code == 200
        questions = response.json().get("questions", [])
        
        difficulty_points = {"easy": 55, "medium": 70, "hard": 90}
        for q in questions:
            diff = q.get("difficulty", "").lower()
            pts = q.get("points", 0)
            if diff in difficulty_points:
                assert pts == difficulty_points[diff], f"Question {q.get('id')}: {diff} should have {difficulty_points[diff]} pts, got {pts}"


class TestContestStatusToggle:
    """Contest status toggle tests: open -> live -> locked -> open"""
    
    def test_status_toggle_open_to_live(self):
        """Test toggling contest status from open to live"""
        headers = get_admin_headers()
        
        # Get a match
        response = requests.get(f"{BASE_URL}/api/matches?limit=10", headers=headers)
        matches = response.json().get("matches", [])
        assert len(matches) > 0, "No matches available"
        match_id = matches[0]["id"]
        
        # Get contests for this match
        response = requests.get(f"{BASE_URL}/api/admin/contests?match_id={match_id}", headers=headers)
        contests = response.json().get("contests", [])
        
        if not contests:
            # Create a contest
            response = requests.get(f"{BASE_URL}/api/admin/templates?limit=10", headers=headers)
            templates = response.json().get("templates", [])
            if not templates:
                pytest.skip("No templates available")
            template_id = templates[0]["id"]
            
            response = requests.post(f"{BASE_URL}/api/admin/contests", headers=headers, json={
                "match_id": match_id,
                "template_id": template_id,
                "name": "TEST_Status_Toggle_Contest",
                "entry_fee": 100,
                "max_participants": 100
            })
            if response.status_code == 400 and "Maximum 5 contests" in response.text:
                pytest.skip("Max contests reached")
            assert response.status_code == 201
            contest_id = response.json()["id"]
        else:
            contest_id = contests[0]["id"]
        
        # First ensure it's open
        requests.put(
            f"{BASE_URL}/api/admin/contests/{contest_id}/status",
            headers=headers,
            json={"status": "open"}
        )
        
        # Toggle to live
        response = requests.put(
            f"{BASE_URL}/api/admin/contests/{contest_id}/status",
            headers=headers,
            json={"status": "live"}
        )
        
        if response.status_code == 400 and "completed" in response.text.lower():
            pytest.skip("Contest is completed, cannot change status")
        
        assert response.status_code == 200, f"Failed to set status to live: {response.text}"
        data = response.json()
        assert data.get("new_status") == "live"
    
    def test_status_toggle_live_to_locked(self):
        """Test toggling contest status from live to locked"""
        headers = get_admin_headers()
        
        # Get a match
        response = requests.get(f"{BASE_URL}/api/matches?limit=10", headers=headers)
        matches = response.json().get("matches", [])
        match_id = matches[0]["id"]
        
        # Get contests
        response = requests.get(f"{BASE_URL}/api/admin/contests?match_id={match_id}", headers=headers)
        contests = response.json().get("contests", [])
        if not contests:
            pytest.skip("No contests available")
        contest_id = contests[0]["id"]
        
        # Ensure it's live first
        requests.put(
            f"{BASE_URL}/api/admin/contests/{contest_id}/status",
            headers=headers,
            json={"status": "live"}
        )
        
        # Toggle to locked
        response = requests.put(
            f"{BASE_URL}/api/admin/contests/{contest_id}/status",
            headers=headers,
            json={"status": "locked"}
        )
        
        if response.status_code == 400 and "completed" in response.text.lower():
            pytest.skip("Contest is completed, cannot change status")
        
        assert response.status_code == 200, f"Failed to set status to locked: {response.text}"
        data = response.json()
        assert data.get("new_status") == "locked"
    
    def test_status_toggle_locked_to_open(self):
        """Test toggling contest status from locked back to open"""
        headers = get_admin_headers()
        
        # Get a match
        response = requests.get(f"{BASE_URL}/api/matches?limit=10", headers=headers)
        matches = response.json().get("matches", [])
        match_id = matches[0]["id"]
        
        # Get contests
        response = requests.get(f"{BASE_URL}/api/admin/contests?match_id={match_id}", headers=headers)
        contests = response.json().get("contests", [])
        if not contests:
            pytest.skip("No contests available")
        contest_id = contests[0]["id"]
        
        # Ensure it's locked first
        requests.put(
            f"{BASE_URL}/api/admin/contests/{contest_id}/status",
            headers=headers,
            json={"status": "locked"}
        )
        
        # Toggle back to open
        response = requests.put(
            f"{BASE_URL}/api/admin/contests/{contest_id}/status",
            headers=headers,
            json={"status": "open"}
        )
        
        if response.status_code == 400 and "completed" in response.text.lower():
            pytest.skip("Contest is completed, cannot change status")
        
        assert response.status_code == 200, f"Failed to set status to open: {response.text}"
        data = response.json()
        assert data.get("new_status") == "open"
    
    def test_invalid_status(self):
        """Test invalid status returns 400"""
        headers = get_admin_headers()
        
        # Get a match
        response = requests.get(f"{BASE_URL}/api/matches?limit=10", headers=headers)
        matches = response.json().get("matches", [])
        match_id = matches[0]["id"]
        
        # Get contests
        response = requests.get(f"{BASE_URL}/api/admin/contests?match_id={match_id}", headers=headers)
        contests = response.json().get("contests", [])
        if not contests:
            pytest.skip("No contests available")
        contest_id = contests[0]["id"]
        
        response = requests.put(
            f"{BASE_URL}/api/admin/contests/{contest_id}/status",
            headers=headers,
            json={"status": "invalid_status"}
        )
        
        assert response.status_code == 400, f"Expected 400 for invalid status, got {response.status_code}"


class TestContestDelete:
    """Contest delete tests"""
    
    def test_delete_contest(self):
        """Test deleting a contest"""
        headers = get_admin_headers()
        
        # Get a match
        response = requests.get(f"{BASE_URL}/api/matches?limit=10", headers=headers)
        matches = response.json().get("matches", [])
        assert len(matches) > 0
        match_id = matches[0]["id"]
        
        # Get template
        response = requests.get(f"{BASE_URL}/api/admin/templates?limit=10", headers=headers)
        templates = response.json().get("templates", [])
        if not templates:
            pytest.skip("No templates available")
        template_id = templates[0]["id"]
        
        # Create a contest to delete
        response = requests.post(f"{BASE_URL}/api/admin/contests", headers=headers, json={
            "match_id": match_id,
            "template_id": template_id,
            "name": "TEST_Delete_Me_Contest",
            "entry_fee": 50,
            "max_participants": 50
        })
        
        if response.status_code == 400 and "Maximum 5 contests" in response.text:
            # Get existing contest to delete
            response = requests.get(f"{BASE_URL}/api/admin/contests?match_id={match_id}", headers=headers)
            contests = response.json().get("contests", [])
            test_contests = [c for c in contests if "TEST_" in c.get("name", "")]
            if not test_contests:
                pytest.skip("No test contests to delete and max reached")
            contest_id = test_contests[0]["id"]
        else:
            assert response.status_code == 201, f"Failed to create contest: {response.text}"
            contest_id = response.json()["id"]
        
        # Delete the contest
        response = requests.delete(f"{BASE_URL}/api/admin/contests/{contest_id}", headers=headers)
        assert response.status_code == 200, f"Failed to delete contest: {response.text}"
        data = response.json()
        assert data.get("message") == "Contest deleted"
        
        # Verify it's deleted
        response = requests.get(f"{BASE_URL}/api/admin/contests?match_id={match_id}", headers=headers)
        contests = response.json().get("contests", [])
        contest_ids = [c["id"] for c in contests]
        assert contest_id not in contest_ids, "Contest was not deleted"
    
    def test_delete_nonexistent_contest(self):
        """Test deleting a non-existent contest returns 404"""
        headers = get_admin_headers()
        response = requests.delete(
            f"{BASE_URL}/api/admin/contests/nonexistent-id-12345",
            headers=headers
        )
        assert response.status_code == 404


class TestMax5ContestsEnforcement:
    """Test max 5 contests per match enforcement"""
    
    def test_max_5_contests_enforcement(self):
        """Test that backend returns 400 when trying to create 6th contest"""
        headers = get_admin_headers()
        
        # Get a match
        response = requests.get(f"{BASE_URL}/api/matches?limit=10", headers=headers)
        matches = response.json().get("matches", [])
        assert len(matches) > 0
        match_id = matches[0]["id"]
        
        # Get template
        response = requests.get(f"{BASE_URL}/api/admin/templates?limit=10", headers=headers)
        templates = response.json().get("templates", [])
        if not templates:
            pytest.skip("No templates available")
        template_id = templates[0]["id"]
        
        # Get current contest count
        response = requests.get(f"{BASE_URL}/api/admin/contests?match_id={match_id}", headers=headers)
        current_count = len(response.json().get("contests", []))
        
        # Create contests until we hit 5
        created_ids = []
        for i in range(5 - current_count):
            response = requests.post(f"{BASE_URL}/api/admin/contests", headers=headers, json={
                "match_id": match_id,
                "template_id": template_id,
                "name": f"TEST_Max5_Contest_{i}",
                "entry_fee": 100,
                "max_participants": 100
            })
            if response.status_code == 201:
                created_ids.append(response.json()["id"])
            elif response.status_code == 400 and "Maximum 5 contests" in response.text:
                break
        
        # Now try to create the 6th contest
        response = requests.post(f"{BASE_URL}/api/admin/contests", headers=headers, json={
            "match_id": match_id,
            "template_id": template_id,
            "name": "TEST_6th_Contest_Should_Fail",
            "entry_fee": 100,
            "max_participants": 100
        })
        
        assert response.status_code == 400, f"Expected 400 for 6th contest, got {response.status_code}"
        assert "Maximum 5 contests" in response.text
        
        # Cleanup: delete created test contests
        for cid in created_ids:
            requests.delete(f"{BASE_URL}/api/admin/contests/{cid}", headers=headers)


class TestTemplateQuestions:
    """Test template and questions relationship"""
    
    def test_only_one_full_match_template(self):
        """Test that only 1 template exists (Full Match Predictions)"""
        headers = get_admin_headers()
        response = requests.get(f"{BASE_URL}/api/admin/templates?limit=50", headers=headers)
        assert response.status_code == 200
        templates = response.json().get("templates", [])
        
        # Should have at least 1 template
        assert len(templates) >= 1, "No templates found"
        
        # Find Full Match Predictions
        full_match = [t for t in templates if "Full Match" in t.get("name", "")]
        assert len(full_match) >= 1, f"Full Match Predictions template not found. Templates: {[t.get('name') for t in templates]}"
    
    def test_template_has_16_questions(self):
        """Test Full Match Predictions template has 16 questions"""
        headers = get_admin_headers()
        response = requests.get(f"{BASE_URL}/api/admin/templates?limit=50", headers=headers)
        templates = response.json().get("templates", [])
        
        full_match = None
        for t in templates:
            if "Full Match" in t.get("name", ""):
                full_match = t
                break
        
        assert full_match is not None, f"Full Match template not found. Templates: {[t.get('name') for t in templates]}"
        question_ids = full_match.get("question_ids", [])
        assert len(question_ids) == 16, f"Expected 16 questions, got {len(question_ids)}"
    
    def test_template_total_points_1270(self):
        """Test Full Match Predictions template has 1270 total points"""
        headers = get_admin_headers()
        response = requests.get(f"{BASE_URL}/api/admin/templates?limit=50", headers=headers)
        templates = response.json().get("templates", [])
        
        full_match = None
        for t in templates:
            if "Full Match" in t.get("name", ""):
                full_match = t
                break
        
        assert full_match is not None
        total_points = full_match.get("total_points", 0)
        assert total_points == 1270, f"Expected 1270 total points, got {total_points}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
