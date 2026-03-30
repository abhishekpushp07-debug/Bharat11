"""
Test Suite for Bharat 11 Admin Panel - Iteration 14
Tests: Super Admin login, Admin CRUD (Questions, Templates, Matches, Contests), 
       Template types, Default templates, Non-admin access restrictions
"""
import pytest
import requests
import os
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from requirements
SUPER_ADMIN = {"phone": "7004186276", "pin": "5524"}
OLD_ADMIN = {"phone": "9876543210", "pin": "1234"}
NON_ADMIN = {"phone": "9111111111", "pin": "5678"}


@pytest.fixture(scope="module")
def super_admin_token():
    """Get super admin auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json=SUPER_ADMIN)
    if response.status_code != 200:
        pytest.skip(f"Super admin login failed: {response.status_code} - {response.text}")
    data = response.json()
    return data.get("token", {}).get("access_token")


@pytest.fixture(scope="module")
def old_admin_token():
    """Get old admin auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json=OLD_ADMIN)
    if response.status_code != 200:
        pytest.skip(f"Old admin login failed: {response.status_code} - {response.text}")
    data = response.json()
    return data.get("token", {}).get("access_token")


@pytest.fixture(scope="module")
def non_admin_token():
    """Get non-admin user token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json=NON_ADMIN)
    if response.status_code != 200:
        pytest.skip(f"Non-admin login failed: {response.status_code} - {response.text}")
    data = response.json()
    return data.get("token", {}).get("access_token")


class TestSuperAdminLogin:
    """Test super admin authentication"""
    
    def test_super_admin_login_success(self):
        """Super admin 7004186276/5524 should login successfully"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=SUPER_ADMIN)
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["is_admin"] == True, "Super admin should have is_admin=true"
        assert data["user"]["phone"] == SUPER_ADMIN["phone"]
        print(f"PASS: Super admin login - is_admin={data['user']['is_admin']}")
    
    def test_super_admin_has_admin_flag(self, super_admin_token):
        """Verify super admin user has is_admin=true in profile"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        response = requests.get(f"{BASE_URL}/api/user/profile", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data.get("is_admin") == True
        print(f"PASS: Super admin profile has is_admin=true")


class TestAdminStats:
    """Test admin dashboard stats endpoint"""
    
    def test_admin_stats_returns_counts(self, super_admin_token):
        """GET /api/admin/stats should return all counts"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
        assert response.status_code == 200, f"Stats failed: {response.text}"
        data = response.json()
        
        # Verify all expected fields
        expected_fields = ["users", "matches", "contests", "questions", "templates", 
                          "live_matches", "upcoming_matches", "open_contests", "active_entries"]
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"
            assert isinstance(data[field], int), f"{field} should be int"
        
        print(f"PASS: Admin stats - users={data['users']}, questions={data['questions']}, templates={data['templates']}, matches={data['matches']}, contests={data['contests']}")
    
    def test_non_admin_cannot_access_stats(self, non_admin_token):
        """Non-admin should get 403 on /api/admin/stats"""
        headers = {"Authorization": f"Bearer {non_admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("PASS: Non-admin gets 403 on admin stats")


class TestAdminQuestionsCRUD:
    """Test admin questions CRUD operations"""
    
    def test_create_question(self, super_admin_token):
        """POST /api/admin/questions should create a question"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        payload = {
            "question_text_en": "TEST_How many runs in first innings?",
            "question_text_hi": "TEST_पहली पारी में कितने रन?",
            "category": "batting",
            "difficulty": "easy",
            "points": 20,
            "options": [
                {"key": "A", "text_en": "Less than 150", "text_hi": "150 से कम"},
                {"key": "B", "text_en": "150-180", "text_hi": "150-180"},
                {"key": "C", "text_en": "180-200", "text_hi": "180-200"},
                {"key": "D", "text_en": "More than 200", "text_hi": "200 से ज्यादा"}
            ],
            "is_active": True
        }
        response = requests.post(f"{BASE_URL}/api/admin/questions", json=payload, headers=headers)
        assert response.status_code == 201, f"Create failed: {response.text}"
        data = response.json()
        assert "id" in data
        assert data["question_text_en"] == payload["question_text_en"]
        assert data["category"] == "batting"
        assert data["points"] == 20
        assert len(data["options"]) == 4
        print(f"PASS: Question created with id={data['id']}")
        return data["id"]
    
    def test_list_questions(self, super_admin_token):
        """GET /api/admin/questions should list questions"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/questions?limit=10", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "questions" in data
        assert "total" in data
        print(f"PASS: Listed {len(data['questions'])} questions, total={data['total']}")
    
    def test_filter_questions_by_category(self, super_admin_token):
        """GET /api/admin/questions?category=batting should filter"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/questions?category=batting&limit=50", headers=headers)
        assert response.status_code == 200
        data = response.json()
        for q in data["questions"]:
            assert q["category"] == "batting"
        print(f"PASS: Filtered {len(data['questions'])} batting questions")
    
    def test_update_question(self, super_admin_token):
        """PUT /api/admin/questions/{id} should update"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        # First create a question
        create_payload = {
            "question_text_en": "TEST_Update question",
            "category": "match",
            "difficulty": "medium",
            "points": 15,
            "options": [
                {"key": "A", "text_en": "Yes", "text_hi": "हाँ"},
                {"key": "B", "text_en": "No", "text_hi": "नहीं"}
            ]
        }
        create_res = requests.post(f"{BASE_URL}/api/admin/questions", json=create_payload, headers=headers)
        assert create_res.status_code == 201
        q_id = create_res.json()["id"]
        
        # Update it
        update_payload = {"points": 25, "difficulty": "hard"}
        update_res = requests.put(f"{BASE_URL}/api/admin/questions/{q_id}", json=update_payload, headers=headers)
        assert update_res.status_code == 200
        updated = update_res.json()
        assert updated["points"] == 25
        assert updated["difficulty"] == "hard"
        print(f"PASS: Question {q_id} updated - points=25, difficulty=hard")
    
    def test_delete_question(self, super_admin_token):
        """DELETE /api/admin/questions/{id} should delete"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        # Create a question to delete
        create_payload = {
            "question_text_en": "TEST_Delete me",
            "category": "special",
            "difficulty": "easy",
            "points": 10,
            "options": [
                {"key": "A", "text_en": "A", "text_hi": "A"},
                {"key": "B", "text_en": "B", "text_hi": "B"}
            ]
        }
        create_res = requests.post(f"{BASE_URL}/api/admin/questions", json=create_payload, headers=headers)
        q_id = create_res.json()["id"]
        
        # Delete it
        delete_res = requests.delete(f"{BASE_URL}/api/admin/questions/{q_id}", headers=headers)
        assert delete_res.status_code == 200
        
        # Verify deleted
        get_res = requests.get(f"{BASE_URL}/api/admin/questions/{q_id}", headers=headers)
        assert get_res.status_code == 404
        print(f"PASS: Question {q_id} deleted and verified 404")


class TestAdminTemplatesCRUD:
    """Test admin templates CRUD with template_type"""
    
    @pytest.fixture(scope="class")
    def test_question_ids(self, super_admin_token):
        """Create test questions for template"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        ids = []
        for i in range(3):
            payload = {
                "question_text_en": f"TEST_Template Q{i+1}",
                "category": "match",
                "difficulty": "easy",
                "points": 10,
                "options": [
                    {"key": "A", "text_en": "A", "text_hi": "A"},
                    {"key": "B", "text_en": "B", "text_hi": "B"}
                ]
            }
            res = requests.post(f"{BASE_URL}/api/admin/questions", json=payload, headers=headers)
            if res.status_code == 201:
                ids.append(res.json()["id"])
        return ids
    
    def test_create_full_match_template(self, super_admin_token, test_question_ids):
        """POST /api/admin/templates with template_type=full_match"""
        if len(test_question_ids) < 2:
            pytest.skip("Need at least 2 questions")
        
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        payload = {
            "name": "TEST_Full Match Template",
            "description": "Test full match template",
            "match_type": "T20",
            "template_type": "full_match",
            "question_ids": test_question_ids[:2],
            "is_default": False
        }
        response = requests.post(f"{BASE_URL}/api/admin/templates", json=payload, headers=headers)
        assert response.status_code == 201, f"Create failed: {response.text}"
        data = response.json()
        assert data["template_type"] == "full_match"
        assert data["question_count"] == 2
        print(f"PASS: Full match template created - id={data['id']}, type={data['template_type']}")
        return data["id"]
    
    def test_create_in_match_template(self, super_admin_token, test_question_ids):
        """POST /api/admin/templates with template_type=in_match"""
        if len(test_question_ids) < 1:
            pytest.skip("Need at least 1 question")
        
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        payload = {
            "name": "TEST_In-Match Template",
            "description": "Test in-match phase template",
            "match_type": "T20",
            "template_type": "in_match",
            "question_ids": test_question_ids[:1],
            "is_default": False
        }
        response = requests.post(f"{BASE_URL}/api/admin/templates", json=payload, headers=headers)
        assert response.status_code == 201, f"Create failed: {response.text}"
        data = response.json()
        assert data["template_type"] == "in_match"
        print(f"PASS: In-match template created - id={data['id']}, type={data['template_type']}")
    
    def test_list_templates_shows_type(self, super_admin_token):
        """GET /api/admin/templates should show template_type"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/templates?limit=20", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        for t in data["templates"]:
            assert "template_type" in t
            assert t["template_type"] in ["full_match", "in_match"]
        print(f"PASS: Listed {len(data['templates'])} templates with template_type")
    
    def test_set_template_as_default(self, super_admin_token, test_question_ids):
        """POST /api/admin/templates/{id}/set-default should work"""
        if len(test_question_ids) < 1:
            pytest.skip("Need questions")
        
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        # Create a template
        payload = {
            "name": "TEST_Default Template",
            "template_type": "full_match",
            "question_ids": test_question_ids[:1],
            "is_default": False
        }
        create_res = requests.post(f"{BASE_URL}/api/admin/templates", json=payload, headers=headers)
        t_id = create_res.json()["id"]
        
        # Set as default
        default_res = requests.post(f"{BASE_URL}/api/admin/templates/{t_id}/set-default", headers=headers)
        assert default_res.status_code == 200, f"Set default failed: {default_res.text}"
        
        # Verify it's default
        get_res = requests.get(f"{BASE_URL}/api/admin/templates/{t_id}", headers=headers)
        assert get_res.json()["is_default"] == True
        print(f"PASS: Template {t_id} set as default")
    
    def test_delete_template(self, super_admin_token, test_question_ids):
        """DELETE /api/admin/templates/{id} should delete"""
        if len(test_question_ids) < 1:
            pytest.skip("Need questions")
        
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        # Create a template
        payload = {
            "name": "TEST_Delete Template",
            "template_type": "in_match",
            "question_ids": test_question_ids[:1]
        }
        create_res = requests.post(f"{BASE_URL}/api/admin/templates", json=payload, headers=headers)
        t_id = create_res.json()["id"]
        
        # Delete it
        delete_res = requests.delete(f"{BASE_URL}/api/admin/templates/{t_id}", headers=headers)
        assert delete_res.status_code == 200
        print(f"PASS: Template {t_id} deleted")


class TestAdminMatchManagement:
    """Test admin match creation and status management"""
    
    def test_admin_create_match(self, super_admin_token):
        """POST /api/matches should create match (admin only)"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        start_time = (datetime.utcnow() + timedelta(hours=2)).isoformat() + "Z"
        payload = {
            "team_a": {"name": "Mumbai Indians", "short_name": "MI"},
            "team_b": {"name": "Chennai Super Kings", "short_name": "CSK"},
            "venue": "Wankhede Stadium, Mumbai",
            "match_type": "T20",
            "start_time": start_time
        }
        response = requests.post(f"{BASE_URL}/api/matches", json=payload, headers=headers)
        assert response.status_code == 201, f"Create match failed: {response.text}"
        data = response.json()
        assert data["team_a"]["short_name"] == "MI"
        assert data["team_b"]["short_name"] == "CSK"
        assert data["status"] == "upcoming"
        print(f"PASS: Match created - {data['team_a']['short_name']} vs {data['team_b']['short_name']}, id={data['id']}")
        return data["id"]
    
    def test_non_admin_cannot_create_match(self, non_admin_token):
        """Non-admin should get 403 on POST /api/matches"""
        headers = {"Authorization": f"Bearer {non_admin_token}"}
        start_time = (datetime.utcnow() + timedelta(hours=2)).isoformat() + "Z"
        payload = {
            "team_a": {"name": "Test A", "short_name": "TA"},
            "team_b": {"name": "Test B", "short_name": "TB"},
            "venue": "Test Venue",
            "match_type": "T20",
            "start_time": start_time
        }
        response = requests.post(f"{BASE_URL}/api/matches", json=payload, headers=headers)
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("PASS: Non-admin gets 403 on create match")
    
    def test_admin_update_match_status(self, super_admin_token):
        """PUT /api/matches/{id}/status should update status"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        # Get an existing match
        matches_res = requests.get(f"{BASE_URL}/api/matches?limit=5", headers=headers)
        matches = matches_res.json().get("matches", [])
        if not matches:
            pytest.skip("No matches to test")
        
        match_id = matches[0]["id"]
        original_status = matches[0]["status"]
        
        # Update to live
        new_status = "live" if original_status != "live" else "upcoming"
        update_res = requests.put(f"{BASE_URL}/api/matches/{match_id}/status", 
                                  json={"status": new_status}, headers=headers)
        assert update_res.status_code == 200, f"Status update failed: {update_res.text}"
        
        # Revert
        requests.put(f"{BASE_URL}/api/matches/{match_id}/status", 
                    json={"status": original_status}, headers=headers)
        print(f"PASS: Match status updated to {new_status} and reverted")
    
    def test_non_admin_cannot_update_status(self, non_admin_token):
        """Non-admin should get 403 on PUT /api/matches/{id}/status"""
        headers = {"Authorization": f"Bearer {non_admin_token}"}
        # Get a match
        matches_res = requests.get(f"{BASE_URL}/api/matches?limit=1")
        matches = matches_res.json().get("matches", [])
        if not matches:
            pytest.skip("No matches")
        
        match_id = matches[0]["id"]
        response = requests.put(f"{BASE_URL}/api/matches/{match_id}/status", 
                               json={"status": "live"}, headers=headers)
        assert response.status_code == 403
        print("PASS: Non-admin gets 403 on update match status")


class TestAdminAssignTemplates:
    """Test template assignment to matches"""
    
    def test_assign_templates_requires_full_match(self, super_admin_token):
        """POST /api/admin/matches/{id}/assign-templates validates min 1 full_match"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        
        # Get a match
        matches_res = requests.get(f"{BASE_URL}/api/matches?limit=1", headers=headers)
        matches = matches_res.json().get("matches", [])
        if not matches:
            pytest.skip("No matches")
        match_id = matches[0]["id"]
        
        # Get templates
        templates_res = requests.get(f"{BASE_URL}/api/admin/templates?limit=20", headers=headers)
        templates = templates_res.json().get("templates", [])
        
        # Find in_match only templates
        in_match_only = [t["id"] for t in templates if t.get("template_type") == "in_match"]
        
        if in_match_only:
            # Try to assign only in_match templates (should fail)
            response = requests.post(f"{BASE_URL}/api/admin/matches/{match_id}/assign-templates",
                                    json=in_match_only[:1], headers=headers)
            assert response.status_code == 400, f"Expected 400, got {response.status_code}"
            assert "full_match" in response.text.lower()
            print("PASS: Assign templates requires at least 1 full_match")
        else:
            # If no in_match templates, test with valid full_match
            full_match = [t["id"] for t in templates if t.get("template_type") == "full_match"]
            if full_match:
                response = requests.post(f"{BASE_URL}/api/admin/matches/{match_id}/assign-templates",
                                        json=full_match[:1], headers=headers)
                assert response.status_code == 200
                print("PASS: Assign templates with full_match works")
    
    def test_assign_templates_max_4_in_match(self, super_admin_token):
        """POST /api/admin/matches/{id}/assign-templates validates max 4 in_match"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        
        # Get templates
        templates_res = requests.get(f"{BASE_URL}/api/admin/templates?limit=50", headers=headers)
        templates = templates_res.json().get("templates", [])
        
        in_match = [t["id"] for t in templates if t.get("template_type") == "in_match"]
        full_match = [t["id"] for t in templates if t.get("template_type") == "full_match"]
        
        if len(in_match) >= 5 and len(full_match) >= 1:
            # Get a match
            matches_res = requests.get(f"{BASE_URL}/api/matches?limit=1", headers=headers)
            match_id = matches_res.json()["matches"][0]["id"]
            
            # Try to assign 5 in_match + 1 full_match (should fail)
            template_ids = full_match[:1] + in_match[:5]
            response = requests.post(f"{BASE_URL}/api/admin/matches/{match_id}/assign-templates",
                                    json=template_ids, headers=headers)
            assert response.status_code == 400
            print("PASS: Max 4 in_match templates enforced")
        else:
            print("SKIP: Not enough templates to test max 4 in_match")


class TestAdminContestCreation:
    """Test admin contest creation"""
    
    def test_create_contest(self, super_admin_token):
        """POST /api/admin/contests should create contest"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        
        # Get a match
        matches_res = requests.get(f"{BASE_URL}/api/matches?limit=5", headers=headers)
        matches = [m for m in matches_res.json().get("matches", []) if m["status"] in ["upcoming", "live"]]
        if not matches:
            pytest.skip("No upcoming/live matches")
        match_id = matches[0]["id"]
        
        # Get a template
        templates_res = requests.get(f"{BASE_URL}/api/admin/templates?limit=5", headers=headers)
        templates = templates_res.json().get("templates", [])
        if not templates:
            pytest.skip("No templates")
        template_id = templates[0]["id"]
        
        payload = {
            "match_id": match_id,
            "template_id": template_id,
            "name": "TEST_Admin Contest",
            "entry_fee": 50,
            "prize_pool": 500,
            "max_participants": 50
        }
        response = requests.post(f"{BASE_URL}/api/admin/contests", json=payload, headers=headers)
        assert response.status_code == 201, f"Create contest failed: {response.text}"
        data = response.json()
        assert data["name"] == "TEST_Admin Contest"
        assert data["entry_fee"] == 50
        assert data["prize_pool"] == 500
        assert data["status"] == "open"
        print(f"PASS: Contest created - id={data['id']}, name={data['name']}")
    
    def test_non_admin_cannot_create_contest(self, non_admin_token):
        """Non-admin should get 403 on POST /api/admin/contests"""
        headers = {"Authorization": f"Bearer {non_admin_token}"}
        payload = {
            "match_id": "fake",
            "template_id": "fake",
            "name": "Fake Contest",
            "entry_fee": 0,
            "prize_pool": 100,
            "max_participants": 10
        }
        response = requests.post(f"{BASE_URL}/api/admin/contests", json=payload, headers=headers)
        assert response.status_code == 403
        print("PASS: Non-admin gets 403 on create contest")


class TestRegressionBasics:
    """Regression tests for basic functionality"""
    
    def test_health_check(self):
        """GET /api/health should work"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("PASS: Health check")
    
    def test_matches_list_public(self):
        """GET /api/matches should work without auth"""
        response = requests.get(f"{BASE_URL}/api/matches?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        print(f"PASS: Public matches list - {len(data['matches'])} matches")
    
    def test_old_admin_still_works(self, old_admin_token):
        """Old admin 9876543210/1234 should still have admin access"""
        headers = {"Authorization": f"Bearer {old_admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
        assert response.status_code == 200
        print("PASS: Old admin still has admin access")
    
    def test_non_admin_wallet_works(self, non_admin_token):
        """Non-admin user wallet should work"""
        headers = {"Authorization": f"Bearer {non_admin_token}"}
        response = requests.get(f"{BASE_URL}/api/wallet/balance", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "balance" in data
        print(f"PASS: Non-admin wallet balance = {data['balance']}")


# Cleanup fixture
@pytest.fixture(scope="module", autouse=True)
def cleanup_test_data(super_admin_token):
    """Cleanup TEST_ prefixed data after tests"""
    yield
    if not super_admin_token:
        return
    
    headers = {"Authorization": f"Bearer {super_admin_token}"}
    
    # Cleanup questions
    try:
        res = requests.get(f"{BASE_URL}/api/admin/questions?limit=200", headers=headers)
        for q in res.json().get("questions", []):
            if q.get("question_text_en", "").startswith("TEST_"):
                requests.delete(f"{BASE_URL}/api/admin/questions/{q['id']}", headers=headers)
    except:
        pass
    
    # Cleanup templates
    try:
        res = requests.get(f"{BASE_URL}/api/admin/templates?limit=100", headers=headers)
        for t in res.json().get("templates", []):
            if t.get("name", "").startswith("TEST_"):
                requests.delete(f"{BASE_URL}/api/admin/templates/{t['id']}", headers=headers)
    except:
        pass
    
    print("Cleanup: TEST_ prefixed data removed")
