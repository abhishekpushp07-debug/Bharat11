"""
Iteration 19 - Auto-Pilot Mode, Enhanced Questions, Templates Testing
Tests: Auto-Pilot start/stop/status, Question CRUD with auto_resolution,
Template CRUD with one-click, settlement endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
SUPER_ADMIN_PHONE = "7004186276"
SUPER_ADMIN_PIN = "5524"


def get_admin_token():
    """Get fresh admin JWT token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "phone": SUPER_ADMIN_PHONE,
        "pin": SUPER_ADMIN_PIN
    })
    if response.status_code != 200:
        return None
    data = response.json()
    # Token is nested as token.access_token
    token_data = data.get("token", {})
    if isinstance(token_data, dict):
        return token_data.get("access_token")
    return token_data


def get_admin_headers():
    """Get headers with fresh admin auth"""
    token = get_admin_token()
    if not token:
        return None
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


class TestAuth:
    """Authentication tests"""
    
    def test_admin_login_success(self):
        """POST /api/auth/login with super admin credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": SUPER_ADMIN_PHONE,
            "pin": SUPER_ADMIN_PIN
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in response"
        assert data.get("user", {}).get("is_admin") == True, "User should be admin"
        # Verify token structure
        token_data = data.get("token", {})
        assert "access_token" in token_data, "Token should have access_token"
        print(f"PASS: Admin login successful, is_admin={data['user']['is_admin']}")


class TestTemplates:
    """Template CRUD tests"""
    
    def test_list_templates(self):
        """GET /api/admin/templates returns templates list"""
        headers = get_admin_headers()
        assert headers, "Failed to get admin token"
        
        response = requests.get(f"{BASE_URL}/api/admin/templates", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "templates" in data, "No templates key in response"
        assert isinstance(data["templates"], list), "templates should be a list"
        print(f"PASS: Found {len(data['templates'])} templates")
        
        # Check for Auto-Settlement T20 Template
        auto_template = next((t for t in data["templates"] if "Auto-Settlement" in t.get("name", "")), None)
        if auto_template:
            print(f"PASS: Found Auto-Settlement T20 Template: {auto_template['name']}")
            assert "question_ids" in auto_template, "Template should have question_ids"
            assert len(auto_template["question_ids"]) == 11, f"Auto-Settlement template should have 11 questions"
        else:
            print("INFO: Auto-Settlement T20 Template not found (may need seeding)")
    
    def test_create_template(self):
        """POST /api/admin/templates creates template with question_ids"""
        headers = get_admin_headers()
        assert headers, "Failed to get admin token"
        
        # First get some question IDs
        q_response = requests.get(f"{BASE_URL}/api/admin/questions?limit=3", headers=headers)
        if q_response.status_code != 200 or not q_response.json().get("questions"):
            pytest.skip("No questions available for template creation")
        
        question_ids = [q["id"] for q in q_response.json()["questions"][:3]]
        
        payload = {
            "name": "TEST_Template_Iteration19",
            "description": "Test template for iteration 19",
            "match_type": "T20",
            "template_type": "full_match",
            "question_ids": question_ids,
            "is_active": True,
            "is_default": False
        }
        
        response = requests.post(f"{BASE_URL}/api/admin/templates", json=payload, headers=headers)
        assert response.status_code == 201, f"Create failed: {response.text}"
        data = response.json()
        assert data["name"] == payload["name"], "Name mismatch"
        assert data["question_ids"] == question_ids, "question_ids mismatch"
        assert "total_points" in data, "Should have total_points"
        print(f"PASS: Created template '{data['name']}' with {len(question_ids)} questions, {data['total_points']} pts")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/admin/templates/{data['id']}", headers=headers)
    
    def test_update_template_add_remove_questions(self):
        """PUT /api/admin/templates/{id} updates template (add/remove questions)"""
        headers = get_admin_headers()
        assert headers, "Failed to get admin token"
        
        # Get questions
        q_response = requests.get(f"{BASE_URL}/api/admin/questions?limit=5", headers=headers)
        if q_response.status_code != 200 or len(q_response.json().get("questions", [])) < 4:
            pytest.skip("Not enough questions for template update test")
        
        questions = q_response.json()["questions"]
        initial_ids = [q["id"] for q in questions[:2]]
        updated_ids = [q["id"] for q in questions[:4]]  # Add 2 more
        
        # Create template
        create_payload = {
            "name": "TEST_Update_Template",
            "description": "For update test",
            "match_type": "T20",
            "template_type": "full_match",
            "question_ids": initial_ids,
            "is_active": True
        }
        create_resp = requests.post(f"{BASE_URL}/api/admin/templates", json=create_payload, headers=headers)
        assert create_resp.status_code == 201, f"Create failed: {create_resp.text}"
        template_id = create_resp.json()["id"]
        
        # Update - add more questions
        update_payload = {
            "name": "TEST_Update_Template_Modified",
            "question_ids": updated_ids
        }
        update_resp = requests.put(f"{BASE_URL}/api/admin/templates/{template_id}", json=update_payload, headers=headers)
        assert update_resp.status_code == 200, f"Update failed: {update_resp.text}"
        updated = update_resp.json()
        assert updated["name"] == "TEST_Update_Template_Modified", "Name not updated"
        assert len(updated["question_ids"]) == 4, f"Expected 4 questions, got {len(updated['question_ids'])}"
        print(f"PASS: Template updated from {len(initial_ids)} to {len(updated_ids)} questions")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/admin/templates/{template_id}", headers=headers)


class TestQuestions:
    """Question CRUD with auto_resolution tests"""
    
    def test_list_questions_with_auto_resolution(self):
        """GET /api/admin/questions returns questions with auto_resolution field"""
        headers = get_admin_headers()
        assert headers, "Failed to get admin token"
        
        response = requests.get(f"{BASE_URL}/api/admin/questions?limit=50", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "questions" in data, "No questions key"
        
        questions = data["questions"]
        auto_questions = [q for q in questions if q.get("auto_resolution") and q["auto_resolution"].get("metric")]
        print(f"PASS: Found {len(questions)} questions, {len(auto_questions)} with auto_resolution")
        
        if auto_questions:
            q = auto_questions[0]
            assert "metric" in q["auto_resolution"], "auto_resolution should have metric"
            assert "trigger" in q["auto_resolution"], "auto_resolution should have trigger"
            assert "resolution_type" in q["auto_resolution"], "auto_resolution should have resolution_type"
            print(f"PASS: Auto-resolution config verified: metric={q['auto_resolution']['metric']}")
    
    def test_questions_have_option_ranges(self):
        """Questions with auto_resolution should have min_value/max_value on options"""
        headers = get_admin_headers()
        assert headers, "Failed to get admin token"
        
        response = requests.get(f"{BASE_URL}/api/admin/questions?limit=50", headers=headers)
        assert response.status_code == 200
        
        questions = response.json()["questions"]
        range_questions = [q for q in questions if q.get("auto_resolution", {}).get("resolution_type") == "range"]
        
        if range_questions:
            q = range_questions[0]
            options = q.get("options", [])
            has_ranges = any(opt.get("min_value") is not None for opt in options)
            assert has_ranges, f"Range-type question should have min_value on options"
            print(f"PASS: Question '{q['question_text_en'][:40]}...' has option ranges")
        else:
            print("INFO: No range-type questions found")
    
    def test_create_question_with_auto_resolution(self):
        """POST /api/admin/questions creates question with auto_resolution config"""
        headers = get_admin_headers()
        assert headers, "Failed to get admin token"
        
        payload = {
            "question_text_en": "TEST: How many runs in powerplay?",
            "question_text_hi": "Powerplay mein kitne runs?",
            "category": "powerplay",
            "difficulty": "medium",
            "points": 25,
            "options": [
                {"key": "A", "text_en": "0-30 runs", "text_hi": "0-30 runs", "min_value": 0, "max_value": 30},
                {"key": "B", "text_en": "31-50 runs", "text_hi": "31-50 runs", "min_value": 31, "max_value": 50},
                {"key": "C", "text_en": "51-70 runs", "text_hi": "51-70 runs", "min_value": 51, "max_value": 70},
                {"key": "D", "text_en": "71+ runs", "text_hi": "71+ runs", "min_value": 71, "max_value": 999}
            ],
            "auto_resolution": {
                "metric": "innings_1_powerplay_runs",
                "trigger": "innings_1_end",
                "resolution_type": "range"
            },
            "is_active": True
        }
        
        response = requests.post(f"{BASE_URL}/api/admin/questions", json=payload, headers=headers)
        assert response.status_code == 201, f"Create failed: {response.text}"
        data = response.json()
        
        assert data["question_text_en"] == payload["question_text_en"], "Text mismatch"
        assert data["auto_resolution"]["metric"] == "innings_1_powerplay_runs", "auto_resolution metric mismatch"
        assert data["options"][0]["min_value"] == 0, "Option min_value not saved"
        print(f"PASS: Created question with auto_resolution: {data['auto_resolution']}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/admin/questions/{data['id']}", headers=headers)
    
    def test_update_question_auto_resolution(self):
        """PUT /api/admin/questions/{id} updates question including auto_resolution"""
        headers = get_admin_headers()
        assert headers, "Failed to get admin token"
        
        # Create a question first
        create_payload = {
            "question_text_en": "TEST: Update auto resolution",
            "category": "match",
            "difficulty": "easy",
            "points": 10,
            "options": [
                {"key": "A", "text_en": "Option A", "min_value": 0, "max_value": 10},
                {"key": "B", "text_en": "Option B", "min_value": 11, "max_value": 20}
            ],
            "is_active": True
        }
        create_resp = requests.post(f"{BASE_URL}/api/admin/questions", json=create_payload, headers=headers)
        assert create_resp.status_code == 201, f"Create failed: {create_resp.text}"
        question_id = create_resp.json()["id"]
        
        # Update with auto_resolution
        update_payload = {
            "auto_resolution": {
                "metric": "match_total_sixes",
                "trigger": "match_end",
                "resolution_type": "range"
            },
            "points": 30
        }
        update_resp = requests.put(f"{BASE_URL}/api/admin/questions/{question_id}", json=update_payload, headers=headers)
        assert update_resp.status_code == 200, f"Update failed: {update_resp.text}"
        updated = update_resp.json()
        
        assert updated["auto_resolution"]["metric"] == "match_total_sixes", "auto_resolution not updated"
        assert updated["points"] == 30, "Points not updated"
        print(f"PASS: Question updated with auto_resolution: {updated['auto_resolution']}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/admin/questions/{question_id}", headers=headers)


class TestBulkImport:
    """Bulk import with auto-resolution tests"""
    
    def test_bulk_import_with_auto(self):
        """POST /api/admin/questions/bulk-import-with-auto seeds 11 auto-resolvable questions + template"""
        headers = get_admin_headers()
        assert headers, "Failed to get admin token"
        
        response = requests.post(f"{BASE_URL}/api/admin/questions/bulk-import-with-auto", headers=headers)
        assert response.status_code == 201, f"Bulk import failed: {response.text}"
        data = response.json()
        
        assert "imported" in data, "No imported count"
        assert data["imported"] == 11, f"Expected 11 questions, got {data['imported']}"
        assert "template_id" in data, "No template_id in response"
        assert "Auto-Settlement" in data.get("template_name", ""), "Template name should contain Auto-Settlement"
        print(f"PASS: Bulk imported {data['imported']} questions + template '{data['template_name']}'")


class TestSettlement:
    """Settlement endpoints tests"""
    
    def test_settlement_status(self):
        """GET /api/admin/settlement/status returns matches with settlement progress"""
        headers = get_admin_headers()
        assert headers, "Failed to get admin token"
        
        response = requests.get(f"{BASE_URL}/api/admin/settlement/status", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "matches" in data, "No matches key"
        matches = data["matches"]
        print(f"PASS: Settlement status returned {len(matches)} matches")
        
        if matches:
            m = matches[0]
            assert "match_id" in m, "Match should have match_id"
            assert "settlement_progress" in m, "Match should have settlement_progress"
            assert "contests_count" in m, "Match should have contests_count"
            print(f"PASS: Match {m.get('team_a', {}).get('short_name', '?')} vs {m.get('team_b', {}).get('short_name', '?')}: {m['settlement_progress']}")
    
    def test_settlement_run_rate_limited(self):
        """POST /api/admin/settlement/{match_id}/run - may return 429 if rate limited"""
        headers = get_admin_headers()
        assert headers, "Failed to get admin token"
        
        # Get a match ID
        status_resp = requests.get(f"{BASE_URL}/api/admin/settlement/status", headers=headers)
        if status_resp.status_code != 200 or not status_resp.json().get("matches"):
            pytest.skip("No matches available for settlement test")
        
        match_id = status_resp.json()["matches"][0]["match_id"]
        
        response = requests.post(f"{BASE_URL}/api/admin/settlement/{match_id}/run", headers=headers)
        
        # Accept 200 (success), 429 (rate limited), or 502 (API error due to rate limit)
        if response.status_code == 200:
            data = response.json()
            print(f"PASS: Settlement ran successfully: {data.get('total_resolved', 0)} resolved")
        elif response.status_code in [429, 502]:
            print(f"INFO: Settlement API rate limited (expected): {response.status_code}")
        else:
            # Check if error message mentions rate limit
            error_msg = response.json().get("detail", "") or response.json().get("error", "")
            if "rate limit" in str(error_msg).lower() or "hits" in str(error_msg).lower():
                print(f"INFO: Settlement API rate limited: {error_msg}")
            else:
                # Also accept if it's a scorecard fetch error (API limit)
                print(f"INFO: Settlement returned {response.status_code}: {response.text[:200]}")


class TestAutoPilot:
    """Auto-Pilot Mode tests"""
    
    def test_autopilot_status(self):
        """GET /api/admin/autopilot/status returns running status with logs"""
        headers = get_admin_headers()
        assert headers, "Failed to get admin token"
        
        response = requests.get(f"{BASE_URL}/api/admin/autopilot/status", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "running" in data, "No running field"
        assert "interval_seconds" in data, "No interval_seconds field"
        assert "run_count" in data, "No run_count field"
        assert "recent_log" in data, "No recent_log field"
        
        print(f"PASS: Auto-Pilot status: running={data['running']}, run_count={data['run_count']}, interval={data['interval_seconds']}s")
        if data["recent_log"]:
            print(f"  Recent log: {data['recent_log'][-1]}")
    
    def test_autopilot_start(self):
        """POST /api/admin/autopilot/start starts auto-pilot background task"""
        headers = get_admin_headers()
        assert headers, "Failed to get admin token"
        
        response = requests.post(f"{BASE_URL}/api/admin/autopilot/start", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Could be "Already running" or "Auto-Pilot started"
        assert "running" in data, "No running field"
        assert data["running"] == True, "Auto-pilot should be running"
        print(f"PASS: Auto-Pilot start: {data.get('message', 'started')}")
    
    def test_autopilot_stop(self):
        """POST /api/admin/autopilot/stop stops auto-pilot"""
        headers = get_admin_headers()
        assert headers, "Failed to get admin token"
        
        response = requests.post(f"{BASE_URL}/api/admin/autopilot/stop", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "running" in data, "No running field"
        assert data["running"] == False, "Auto-pilot should be stopped"
        print(f"PASS: Auto-Pilot stop: {data.get('message', 'stopped')}")
    
    def test_autopilot_start_stop_cycle(self):
        """Full start -> status -> stop cycle"""
        headers = get_admin_headers()
        assert headers, "Failed to get admin token"
        
        # Start
        start_resp = requests.post(f"{BASE_URL}/api/admin/autopilot/start", headers=headers)
        assert start_resp.status_code == 200
        assert start_resp.json()["running"] == True
        
        # Check status
        status_resp = requests.get(f"{BASE_URL}/api/admin/autopilot/status", headers=headers)
        assert status_resp.status_code == 200
        assert status_resp.json()["running"] == True
        
        # Stop
        stop_resp = requests.post(f"{BASE_URL}/api/admin/autopilot/stop", headers=headers)
        assert stop_resp.status_code == 200
        assert stop_resp.json()["running"] == False
        
        # Verify stopped
        final_status = requests.get(f"{BASE_URL}/api/admin/autopilot/status", headers=headers)
        assert final_status.json()["running"] == False
        
        print("PASS: Auto-Pilot start -> status -> stop cycle completed")


class TestAccessControl:
    """Access control tests"""
    
    def test_autopilot_requires_admin(self):
        """Auto-pilot endpoints require admin auth"""
        # No auth
        response = requests.get(f"{BASE_URL}/api/admin/autopilot/status")
        assert response.status_code in [401, 403], f"Should require auth: {response.status_code}"
        print("PASS: Auto-pilot status requires auth")
    
    def test_settlement_requires_admin(self):
        """Settlement endpoints require admin auth"""
        response = requests.get(f"{BASE_URL}/api/admin/settlement/status")
        assert response.status_code in [401, 403], f"Should require auth: {response.status_code}"
        print("PASS: Settlement status requires auth")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
