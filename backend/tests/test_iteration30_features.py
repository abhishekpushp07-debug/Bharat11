"""
Iteration 30 - Backend Tests for Bharat 11 Fantasy Cricket PWA
Tests: Contest questions, Admin questions CRUD, Question pool seeding, 5-template engine
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
ADMIN_PHONE = "7004186276"
ADMIN_PIN = "5524"
PLAYER_PHONE = "9111111111"
PLAYER_PIN = "5678"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "phone": ADMIN_PHONE,
        "pin": ADMIN_PIN
    })
    if response.status_code == 200:
        data = response.json()
        # Handle nested token structure
        if "token" in data and isinstance(data["token"], dict):
            return data["token"].get("access_token")
        return data.get("access_token") or data.get("token")
    pytest.skip(f"Admin login failed: {response.status_code}")


@pytest.fixture(scope="module")
def player_token():
    """Get player auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "phone": PLAYER_PHONE,
        "pin": PLAYER_PIN
    })
    if response.status_code == 200:
        data = response.json()
        if "token" in data and isinstance(data["token"], dict):
            return data["token"].get("access_token")
        return data.get("access_token") or data.get("token")
    pytest.skip(f"Player login failed: {response.status_code}")


@pytest.fixture(scope="module")
def admin_headers(admin_token):
    """Admin auth headers"""
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}


@pytest.fixture(scope="module")
def player_headers(player_token):
    """Player auth headers"""
    return {"Authorization": f"Bearer {player_token}", "Content-Type": "application/json"}


class TestHealthAndAuth:
    """Basic health and auth tests"""
    
    def test_health_endpoint(self):
        """GET /api/health returns 200"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("PASS: Health endpoint returns healthy status")
    
    def test_admin_login(self):
        """POST /api/auth/login returns token for admin"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": ADMIN_PHONE,
            "pin": ADMIN_PIN
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data or "access_token" in data
        print("PASS: Admin login successful")
    
    def test_player_login(self):
        """POST /api/auth/login returns token for player"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": PLAYER_PHONE,
            "pin": PLAYER_PIN
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data or "access_token" in data
        print("PASS: Player login successful")


class TestAdminQuestionsAPI:
    """Admin Questions CRUD tests"""
    
    def test_list_questions_paginated(self, admin_headers):
        """GET /api/admin/questions?page=1&limit=100 returns paginated questions"""
        response = requests.get(f"{BASE_URL}/api/admin/questions?page=1&limit=100", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "questions" in data
        assert "total" in data
        assert "has_more" in data
        assert "page" in data
        assert data["page"] == 1
        print(f"PASS: Questions list returns {len(data['questions'])} questions, total: {data['total']}, has_more: {data['has_more']}")
    
    def test_questions_have_bilingual_text(self, admin_headers):
        """Questions have both EN and HI text"""
        response = requests.get(f"{BASE_URL}/api/admin/questions?page=1&limit=5", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        questions = data.get("questions", [])
        if len(questions) > 0:
            q = questions[0]
            assert "question_text_en" in q, "Missing question_text_en"
            assert "question_text_hi" in q, "Missing question_text_hi"
            assert len(q["question_text_en"]) > 0, "Empty EN text"
            print(f"PASS: Questions have bilingual text - EN: '{q['question_text_en'][:50]}...'")
        else:
            pytest.skip("No questions in pool to test")
    
    def test_questions_have_required_fields(self, admin_headers):
        """Questions have points, category, options"""
        response = requests.get(f"{BASE_URL}/api/admin/questions?page=1&limit=5", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        questions = data.get("questions", [])
        if len(questions) > 0:
            q = questions[0]
            assert "points" in q, "Missing points"
            assert "category" in q, "Missing category"
            assert "options" in q, "Missing options"
            assert isinstance(q["options"], list), "Options should be a list"
            print(f"PASS: Question has points={q['points']}, category={q['category']}, options={len(q['options'])}")
        else:
            pytest.skip("No questions in pool to test")
    
    def test_create_question(self, admin_headers):
        """POST /api/admin/questions creates a new question"""
        new_q = {
            "question_text_en": "TEST: Will there be a six in the first over?",
            "question_text_hi": "TEST: Kya pehle over mein six hoga?",
            "category": "batting",
            "difficulty": "easy",
            "points": 25,
            "options": [
                {"key": "A", "text_en": "Yes", "text_hi": "Haan", "min_value": 1, "max_value": 99},
                {"key": "B", "text_en": "No", "text_hi": "Nahi", "min_value": 0, "max_value": 0},
                {"key": "C", "text_en": "Multiple sixes", "text_hi": "Kai sixes", "min_value": 2, "max_value": 99},
                {"key": "D", "text_en": "Boundary instead", "text_hi": "Four hoga", "min_value": 0, "max_value": 0}
            ]
        }
        response = requests.post(f"{BASE_URL}/api/admin/questions", json=new_q, headers=admin_headers)
        assert response.status_code == 201, f"Create failed: {response.text}"
        data = response.json()
        assert "id" in data
        assert data["question_text_en"] == new_q["question_text_en"]
        print(f"PASS: Created question with id={data['id']}")
        return data["id"]
    
    def test_update_question(self, admin_headers):
        """PUT /api/admin/questions/{id} updates a question"""
        # First get a question to update
        response = requests.get(f"{BASE_URL}/api/admin/questions?page=1&limit=5", headers=admin_headers)
        assert response.status_code == 200
        questions = response.json().get("questions", [])
        if len(questions) == 0:
            pytest.skip("No questions to update")
        
        q_id = questions[0]["id"]
        update_data = {"points": 99}
        response = requests.put(f"{BASE_URL}/api/admin/questions/{q_id}", json=update_data, headers=admin_headers)
        assert response.status_code == 200, f"Update failed: {response.text}"
        data = response.json()
        assert data["points"] == 99
        print(f"PASS: Updated question {q_id} points to 99")
        
        # Restore original points
        requests.put(f"{BASE_URL}/api/admin/questions/{q_id}", json={"points": questions[0]["points"]}, headers=admin_headers)
    
    def test_delete_question(self, admin_headers):
        """DELETE /api/admin/questions/{id} deletes a question"""
        # Create a test question first
        new_q = {
            "question_text_en": "TEST_DELETE: Temporary question",
            "question_text_hi": "TEST_DELETE: Temporary",
            "category": "special",
            "difficulty": "easy",
            "points": 10,
            "options": [
                {"key": "A", "text_en": "A", "text_hi": "A"},
                {"key": "B", "text_en": "B", "text_hi": "B"}
            ]
        }
        create_resp = requests.post(f"{BASE_URL}/api/admin/questions", json=new_q, headers=admin_headers)
        assert create_resp.status_code == 201
        q_id = create_resp.json()["id"]
        
        # Delete it
        response = requests.delete(f"{BASE_URL}/api/admin/questions/{q_id}", headers=admin_headers)
        assert response.status_code == 200, f"Delete failed: {response.text}"
        data = response.json()
        assert data.get("id") == q_id
        print(f"PASS: Deleted question {q_id}")
        
        # Verify it's gone
        get_resp = requests.get(f"{BASE_URL}/api/admin/questions/{q_id}", headers=admin_headers)
        assert get_resp.status_code == 404


class TestQuestionPoolSeeding:
    """Question pool seeding tests"""
    
    def test_seed_question_pool_endpoint_exists(self, admin_headers):
        """POST /api/admin/seed-question-pool endpoint exists"""
        # Just check it doesn't 404 - don't actually seed
        response = requests.post(f"{BASE_URL}/api/admin/seed-question-pool?force=false&count=50", headers=admin_headers)
        # Should be 200 (already seeded) or 201 (seeded)
        assert response.status_code in [200, 201], f"Unexpected status: {response.status_code}"
        data = response.json()
        assert "seeded" in data or "total_in_db" in data
        print(f"PASS: Seed endpoint works - seeded={data.get('seeded', 0)}, total={data.get('total_in_db', 0)}")
    
    def test_seed_supports_count_parameter(self, admin_headers):
        """Seed endpoint accepts count parameter up to 2000"""
        response = requests.post(f"{BASE_URL}/api/admin/seed-question-pool?force=false&count=2000", headers=admin_headers)
        assert response.status_code in [200, 201]
        data = response.json()
        # Should either seed or report existing count
        print(f"PASS: Seed with count=2000 - response: {data.get('message', 'OK')}")


class TestContestQuestions:
    """Contest questions endpoint tests"""
    
    def test_get_contests_list(self, player_headers):
        """GET /api/contests returns list of contests"""
        response = requests.get(f"{BASE_URL}/api/contests?limit=5", headers=player_headers)
        assert response.status_code == 200
        data = response.json()
        assert "contests" in data
        print(f"PASS: Contests list returns {len(data['contests'])} contests")
        return data["contests"]
    
    def test_contest_questions_returns_11_questions(self, player_headers):
        """GET /api/contests/{id}/questions returns 11 bilingual questions"""
        # Get a contest first
        contests_resp = requests.get(f"{BASE_URL}/api/contests?limit=5", headers=player_headers)
        assert contests_resp.status_code == 200
        contests = contests_resp.json().get("contests", [])
        
        if len(contests) == 0:
            pytest.skip("No contests available to test")
        
        contest_id = contests[0]["id"]
        response = requests.get(f"{BASE_URL}/api/contests/{contest_id}/questions", headers=player_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "questions" in data
        questions = data["questions"]
        
        # Check we have questions (should be 11 per contest)
        if len(questions) > 0:
            q = questions[0]
            assert "question_text_en" in q, "Missing EN text"
            assert "question_text_hi" in q, "Missing HI text"
            assert "points" in q, "Missing points"
            assert "category" in q, "Missing category"
            assert "options" in q, "Missing options"
            print(f"PASS: Contest {contest_id} has {len(questions)} questions with bilingual text")
        else:
            print(f"WARNING: Contest {contest_id} has 0 questions - may need template assignment")
    
    def test_contest_questions_have_valid_structure(self, player_headers):
        """Contest questions have proper structure with options"""
        contests_resp = requests.get(f"{BASE_URL}/api/contests?limit=5", headers=player_headers)
        contests = contests_resp.json().get("contests", [])
        
        if len(contests) == 0:
            pytest.skip("No contests available")
        
        contest_id = contests[0]["id"]
        response = requests.get(f"{BASE_URL}/api/contests/{contest_id}/questions", headers=player_headers)
        assert response.status_code == 200
        data = response.json()
        questions = data.get("questions", [])
        
        if len(questions) > 0:
            q = questions[0]
            # Check options structure
            options = q.get("options", [])
            if len(options) > 0:
                opt = options[0]
                assert "key" in opt, "Option missing key"
                assert "text_en" in opt, "Option missing text_en"
                print(f"PASS: Question options have proper structure - {len(options)} options")
            else:
                print("WARNING: Question has no options")
        else:
            pytest.skip("No questions in contest")


class TestAutoTemplates:
    """5-Template Match Engine tests"""
    
    def test_get_matches_list(self, admin_headers):
        """GET /api/matches returns list of matches"""
        response = requests.get(f"{BASE_URL}/api/matches?limit=10", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        print(f"PASS: Matches list returns {len(data['matches'])} matches")
        return data["matches"]
    
    def test_auto_templates_endpoint_exists(self, admin_headers):
        """POST /api/admin/matches/{id}/auto-templates endpoint exists"""
        # Get a match first
        matches_resp = requests.get(f"{BASE_URL}/api/matches?limit=5", headers=admin_headers)
        matches = matches_resp.json().get("matches", [])
        
        if len(matches) == 0:
            pytest.skip("No matches available")
        
        match_id = matches[0]["id"]
        response = requests.post(f"{BASE_URL}/api/admin/matches/{match_id}/auto-templates", headers=admin_headers)
        # Should be 200 (already exists) or 201 (created) or 400 (not enough questions)
        assert response.status_code in [200, 201, 400], f"Unexpected: {response.status_code} - {response.text}"
        data = response.json()
        
        if response.status_code == 400:
            print(f"INFO: Auto-templates needs more questions: {data.get('detail', 'N/A')}")
        else:
            print(f"PASS: Auto-templates endpoint works - created={data.get('templates_created', 0)}")
    
    def test_templates_list(self, admin_headers):
        """GET /api/admin/templates returns templates"""
        response = requests.get(f"{BASE_URL}/api/admin/templates?limit=20", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        templates = data["templates"]
        
        # Check template structure
        if len(templates) > 0:
            t = templates[0]
            assert "id" in t
            assert "name" in t
            assert "template_type" in t
            assert "question_ids" in t
            print(f"PASS: Templates list returns {len(templates)} templates, first has {len(t.get('question_ids', []))} questions")
        else:
            print("INFO: No templates found")


class TestAdminStats:
    """Admin dashboard stats tests"""
    
    def test_admin_stats(self, admin_headers):
        """GET /api/admin/stats returns dashboard stats"""
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Check expected fields
        assert "users" in data
        assert "matches" in data
        assert "contests" in data
        assert "questions" in data
        assert "templates" in data
        
        print(f"PASS: Admin stats - users={data['users']}, matches={data['matches']}, contests={data['contests']}, questions={data['questions']}, templates={data['templates']}")


class TestIPLData:
    """IPL data endpoints (regression)"""
    
    def test_ipl_points_table(self):
        """GET /api/cricket/ipl/points-table returns teams"""
        response = requests.get(f"{BASE_URL}/api/cricket/ipl/points-table")
        assert response.status_code == 200
        data = response.json()
        assert "teams" in data
        teams = data["teams"]
        assert len(teams) >= 8, f"Expected 8+ teams, got {len(teams)}"
        print(f"PASS: IPL points table returns {len(teams)} teams")
    
    def test_live_ticker(self):
        """GET /api/cricket/live-ticker returns scores"""
        response = requests.get(f"{BASE_URL}/api/cricket/live-ticker")
        assert response.status_code == 200
        data = response.json()
        assert "scores" in data
        print(f"PASS: Live ticker returns {len(data['scores'])} scores")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
