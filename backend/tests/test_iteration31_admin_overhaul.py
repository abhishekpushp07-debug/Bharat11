"""
Iteration 31 - Super Admin Overhaul Tests
Tests for:
1. POST /api/admin/questions/bulk-delete - bulk delete questions
2. POST /api/admin/templates/bulk-delete - bulk delete templates
3. POST /api/admin/contests/bulk-delete - bulk delete contests
4. GET /api/admin/default-templates - list default templates (max 5)
5. POST /api/admin/templates/{id}/toggle-default - toggle template default status
6. GET /api/admin/contests - enriched contest list with template_type, match_label, question_count
7. GET /api/admin/contests/{id}/ai-preview - AI predicted answers for contest questions
8. POST /api/admin/contests/{id}/resolve-override - resolve with admin overrides
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
    # Token is nested under token.access_token
    token = data.get("token", {}).get("access_token")
    assert token, f"No token in response: {data}"
    return token


# Module-level fixture for admin auth
@pytest.fixture(scope="module")
def admin_headers():
    """Get admin headers with auth token - shared across all tests"""
    token = get_admin_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


class TestAdminAuth:
    """Admin authentication tests"""
    
    def test_admin_login(self, admin_headers):
        """Test admin can login successfully"""
        assert admin_headers is not None
        assert "Authorization" in admin_headers
        print(f"Admin login successful")


class TestBulkDeleteQuestions:
    """Tests for POST /api/admin/questions/bulk-delete"""
    
    def test_bulk_delete_questions_endpoint_exists(self, admin_headers):
        """Test bulk delete questions endpoint exists"""
        # Create test questions first
        test_questions = []
        for i in range(3):
            q_data = {
                "question_text_en": f"TEST_BULK_DELETE_Q{i} - What is the score?",
                "question_text_hi": f"TEST_BULK_DELETE_Q{i} - Score kya hai?",
                "category": "match",
                "difficulty": "easy",
                "points": 10,
                "options": [
                    {"key": "A", "text_en": "0-100", "text_hi": "0-100"},
                    {"key": "B", "text_en": "101-200", "text_hi": "101-200"}
                ]
            }
            resp = requests.post(f"{BASE_URL}/api/admin/questions", json=q_data, headers=admin_headers)
            if resp.status_code == 201:
                test_questions.append(resp.json().get("id"))
        
        if len(test_questions) > 0:
            # Now bulk delete
            response = requests.post(f"{BASE_URL}/api/admin/questions/bulk-delete", 
                json={"ids": test_questions}, headers=admin_headers)
            assert response.status_code == 200, f"Bulk delete failed: {response.text}"
            data = response.json()
            assert "deleted" in data
            print(f"Bulk deleted {data.get('deleted')} questions")
        else:
            pytest.skip("Could not create test questions")
    
    def test_bulk_delete_empty_ids(self, admin_headers):
        """Test bulk delete with empty ids returns error"""
        response = requests.post(f"{BASE_URL}/api/admin/questions/bulk-delete", 
            json={"ids": []}, headers=admin_headers)
        # Should return 422 for validation error (min_length=1)
        assert response.status_code == 422


class TestBulkDeleteTemplates:
    """Tests for POST /api/admin/templates/bulk-delete"""
    
    def test_bulk_delete_templates_endpoint_exists(self, admin_headers):
        """Test bulk delete templates endpoint exists"""
        # Get existing questions first
        q_resp = requests.get(f"{BASE_URL}/api/admin/questions?limit=5", headers=admin_headers)
        questions = q_resp.json().get("questions", [])
        if len(questions) < 2:
            pytest.skip("Not enough questions to create template")
        
        q_ids = [q["id"] for q in questions[:2]]
        
        # Create test template
        t_data = {
            "name": "TEST_BULK_DELETE_TEMPLATE",
            "description": "Test template for bulk delete",
            "match_type": "T20",
            "template_type": "full_match",
            "question_ids": q_ids,
            "is_default": False
        }
        t_resp = requests.post(f"{BASE_URL}/api/admin/templates", json=t_data, headers=admin_headers)
        if t_resp.status_code != 201:
            pytest.skip(f"Could not create test template: {t_resp.text}")
        
        template_id = t_resp.json().get("id")
        
        # Bulk delete
        response = requests.post(f"{BASE_URL}/api/admin/templates/bulk-delete", 
            json={"ids": [template_id]}, headers=admin_headers)
        assert response.status_code == 200, f"Bulk delete templates failed: {response.text}"
        data = response.json()
        assert "deleted" in data
        print(f"Bulk deleted {data.get('deleted')} templates")


class TestBulkDeleteContests:
    """Tests for POST /api/admin/contests/bulk-delete"""
    
    def test_bulk_delete_contests_endpoint_exists(self, admin_headers):
        """Test bulk delete contests endpoint exists"""
        # Get existing contests
        c_resp = requests.get(f"{BASE_URL}/api/admin/contests?limit=5", headers=admin_headers)
        assert c_resp.status_code == 200, f"Get contests failed: {c_resp.text}"
        
        # Just verify endpoint works with empty/non-existent IDs
        response = requests.post(f"{BASE_URL}/api/admin/contests/bulk-delete", 
            json={"ids": ["non_existent_id_12345"]}, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "deleted" in data
        assert data["deleted"] == 0  # Should delete 0 since ID doesn't exist
        print(f"Bulk delete contests endpoint working, deleted: {data.get('deleted')}")


class TestDefaultTemplates:
    """Tests for GET /api/admin/default-templates and POST /api/admin/templates/{id}/toggle-default"""
    
    def test_get_default_templates(self, admin_headers):
        """Test GET /api/admin/default-templates returns list with max 5"""
        response = requests.get(f"{BASE_URL}/api/admin/default-templates", headers=admin_headers)
        assert response.status_code == 200, f"Get default templates failed: {response.text}"
        data = response.json()
        
        assert "default_templates" in data
        assert "count" in data
        assert "max_allowed" in data
        assert data["max_allowed"] == 5
        assert "slots_remaining" in data
        
        print(f"Default templates: {data['count']}/5, slots remaining: {data['slots_remaining']}")
        
        # Verify each template has questions enriched
        for t in data["default_templates"]:
            assert "id" in t
            assert "name" in t
            assert "questions" in t  # Should be enriched with question details
    
    def test_toggle_default_template(self, admin_headers):
        """Test POST /api/admin/templates/{id}/toggle-default"""
        # Get a non-default template
        t_resp = requests.get(f"{BASE_URL}/api/admin/templates?limit=20", headers=admin_headers)
        templates = t_resp.json().get("templates", [])
        
        # Find a non-default template
        non_default = next((t for t in templates if not t.get("is_default")), None)
        if not non_default:
            pytest.skip("No non-default templates to test toggle")
        
        template_id = non_default["id"]
        
        # Toggle to default
        response = requests.post(f"{BASE_URL}/api/admin/templates/{template_id}/toggle-default", 
            headers=admin_headers)
        assert response.status_code in [200, 400], f"Toggle default failed: {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            assert "is_default" in data
            assert "message" in data
            print(f"Toggle default: {data['message']}")
            
            # Toggle back
            requests.post(f"{BASE_URL}/api/admin/templates/{template_id}/toggle-default", 
                headers=admin_headers)
        else:
            # 400 means max 5 defaults reached
            print(f"Max defaults reached: {response.json()}")


class TestAdminContestsList:
    """Tests for GET /api/admin/contests with enriched data"""
    
    def test_admin_contests_list_enriched(self, admin_headers):
        """Test GET /api/admin/contests returns enriched data"""
        response = requests.get(f"{BASE_URL}/api/admin/contests?limit=10", headers=admin_headers)
        assert response.status_code == 200, f"Get admin contests failed: {response.text}"
        data = response.json()
        
        assert "contests" in data
        assert "total" in data
        assert "page" in data
        
        if len(data["contests"]) > 0:
            contest = data["contests"][0]
            # Check enriched fields
            assert "template_type" in contest, "Missing template_type"
            assert "match_label" in contest, "Missing match_label"
            assert "question_count" in contest, "Missing question_count"
            assert "template_name" in contest, "Missing template_name"
            
            print(f"Contest enriched: template_type={contest['template_type']}, match_label={contest['match_label']}, question_count={contest['question_count']}")
        else:
            print("No contests found to verify enrichment")


class TestAIPreview:
    """Tests for GET /api/admin/contests/{id}/ai-preview"""
    
    def test_ai_preview_endpoint(self, admin_headers):
        """Test GET /api/admin/contests/{id}/ai-preview returns AI predictions"""
        # Get a contest
        c_resp = requests.get(f"{BASE_URL}/api/admin/contests?limit=5", headers=admin_headers)
        contests = c_resp.json().get("contests", [])
        
        if len(contests) == 0:
            pytest.skip("No contests to test AI preview")
        
        contest_id = contests[0]["id"]
        
        response = requests.get(f"{BASE_URL}/api/admin/contests/{contest_id}/ai-preview", 
            headers=admin_headers)
        assert response.status_code == 200, f"AI preview failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "contest_id" in data
        assert "contest_name" in data
        assert "match_label" in data
        assert "match_status" in data
        assert "template_type" in data
        assert "scorecard_available" in data
        assert "questions" in data
        assert "total_questions" in data
        assert "resolved_count" in data
        assert "ai_answered_count" in data
        
        print(f"AI Preview: {data['contest_name']}, scorecard_available={data['scorecard_available']}, questions={data['total_questions']}, ai_answered={data['ai_answered_count']}")
        
        # Check question structure
        if len(data["questions"]) > 0:
            q = data["questions"][0]
            assert "question_id" in q
            assert "question_text_en" in q
            assert "options" in q
            assert "ai_predicted_answer" in q  # Can be null
            assert "ai_confidence" in q
            assert "ai_reason" in q
            assert "already_resolved" in q
    
    def test_ai_preview_not_found(self, admin_headers):
        """Test AI preview with non-existent contest returns 404"""
        response = requests.get(f"{BASE_URL}/api/admin/contests/non_existent_id/ai-preview", 
            headers=admin_headers)
        assert response.status_code == 404


class TestResolveOverride:
    """Tests for POST /api/admin/contests/{id}/resolve-override"""
    
    def test_resolve_override_endpoint_exists(self, admin_headers):
        """Test POST /api/admin/contests/{id}/resolve-override endpoint exists"""
        # Get a contest
        c_resp = requests.get(f"{BASE_URL}/api/admin/contests?limit=5", headers=admin_headers)
        contests = c_resp.json().get("contests", [])
        
        if len(contests) == 0:
            pytest.skip("No contests to test resolve override")
        
        contest_id = contests[0]["id"]
        
        # Get AI preview to find unresolved questions
        preview_resp = requests.get(f"{BASE_URL}/api/admin/contests/{contest_id}/ai-preview", 
            headers=admin_headers)
        if preview_resp.status_code != 200:
            pytest.skip("Could not get AI preview")
        
        preview = preview_resp.json()
        unresolved = [q for q in preview.get("questions", []) if not q.get("already_resolved")]
        
        if len(unresolved) == 0:
            # Test with empty answers - should work but resolve 0
            response = requests.post(f"{BASE_URL}/api/admin/contests/{contest_id}/resolve-override",
                json={"answers": [{"question_id": "fake_id", "correct_option": "A"}], "auto_finalize": False},
                headers=admin_headers)
            # Should return 200 even if question not found
            assert response.status_code == 200
            print("Resolve override endpoint working (no unresolved questions)")
        else:
            # Test with a real unresolved question
            q = unresolved[0]
            response = requests.post(f"{BASE_URL}/api/admin/contests/{contest_id}/resolve-override",
                json={
                    "answers": [{"question_id": q["question_id"], "correct_option": "A"}],
                    "auto_finalize": False
                },
                headers=admin_headers)
            assert response.status_code == 200, f"Resolve override failed: {response.text}"
            data = response.json()
            assert "resolved" in data
            assert "skipped" in data
            assert "finalized" in data
            assert "details" in data
            print(f"Resolve override: resolved={data['resolved']}, skipped={data['skipped']}")
    
    def test_resolve_override_validation(self, admin_headers):
        """Test resolve override validates correct_option pattern"""
        c_resp = requests.get(f"{BASE_URL}/api/admin/contests?limit=1", headers=admin_headers)
        contests = c_resp.json().get("contests", [])
        
        if len(contests) == 0:
            pytest.skip("No contests")
        
        contest_id = contests[0]["id"]
        
        # Invalid option (not A-D)
        response = requests.post(f"{BASE_URL}/api/admin/contests/{contest_id}/resolve-override",
            json={"answers": [{"question_id": "test", "correct_option": "E"}], "auto_finalize": False},
            headers=admin_headers)
        assert response.status_code == 422  # Validation error


class TestEndpointSecurity:
    """Test that admin endpoints require authentication"""
    
    def test_bulk_delete_questions_requires_auth(self):
        """Test bulk delete questions requires auth"""
        response = requests.post(f"{BASE_URL}/api/admin/questions/bulk-delete", 
            json={"ids": ["test"]})
        assert response.status_code == 401
    
    def test_bulk_delete_templates_requires_auth(self):
        """Test bulk delete templates requires auth"""
        response = requests.post(f"{BASE_URL}/api/admin/templates/bulk-delete", 
            json={"ids": ["test"]})
        assert response.status_code == 401
    
    def test_bulk_delete_contests_requires_auth(self):
        """Test bulk delete contests requires auth"""
        response = requests.post(f"{BASE_URL}/api/admin/contests/bulk-delete", 
            json={"ids": ["test"]})
        assert response.status_code == 401
    
    def test_default_templates_requires_auth(self):
        """Test default templates requires auth"""
        response = requests.get(f"{BASE_URL}/api/admin/default-templates")
        assert response.status_code == 401
    
    def test_toggle_default_requires_auth(self):
        """Test toggle default requires auth"""
        response = requests.post(f"{BASE_URL}/api/admin/templates/test/toggle-default")
        assert response.status_code == 401
    
    def test_ai_preview_requires_auth(self):
        """Test AI preview requires auth"""
        response = requests.get(f"{BASE_URL}/api/admin/contests/test/ai-preview")
        assert response.status_code == 401
    
    def test_resolve_override_requires_auth(self):
        """Test resolve override requires auth"""
        response = requests.post(f"{BASE_URL}/api/admin/contests/test/resolve-override",
            json={"answers": []})
        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
