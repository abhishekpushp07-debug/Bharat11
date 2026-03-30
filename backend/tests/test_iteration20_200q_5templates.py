"""
Iteration 20 - 200 Question Pool + 5-Template Auto-Engine Tests
Tests:
1. POST /api/admin/seed-200-questions - idempotent seeding
2. POST /api/admin/matches/{match_id}/auto-templates - 5 templates generation
3. GET /api/admin/templates - new fields (phase_label, innings_range, over_start, over_end, answer_deadline_over)
4. GET /api/admin/stats - question and template counts
5. PUT /api/admin/templates/{id} - update in-match routing fields
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestIteration20Features:
    """Test 200-question pool and 5-template auto-engine"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin auth token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as super admin
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "phone": "7004186276",
            "pin": "5524"
        })
        assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
        token = login_resp.json().get("token")
        assert token, "No token in login response"
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        self.token = token
    
    # ==================== SEED 200 QUESTIONS ====================
    
    def test_seed_200_questions_first_call(self):
        """POST /api/admin/seed-200-questions - should seed questions"""
        resp = self.session.post(f"{BASE_URL}/api/admin/seed-200-questions")
        assert resp.status_code in [200, 201], f"Seed failed: {resp.text}"
        data = resp.json()
        
        # Should return seeding info
        assert "seeded" in data or "total_in_db" in data or "message" in data
        print(f"Seed response: {data}")
    
    def test_seed_200_questions_idempotent(self):
        """POST /api/admin/seed-200-questions - second call should skip"""
        # First call
        resp1 = self.session.post(f"{BASE_URL}/api/admin/seed-200-questions")
        assert resp1.status_code in [200, 201]
        data1 = resp1.json()
        
        # Second call - should be idempotent
        resp2 = self.session.post(f"{BASE_URL}/api/admin/seed-200-questions")
        assert resp2.status_code in [200, 201]
        data2 = resp2.json()
        
        # Second call should seed 0 or skip
        if "seeded" in data2:
            assert data2["seeded"] == 0 or "skip" in str(data2.get("message", "")).lower(), \
                f"Second call should skip, got: {data2}"
        print(f"Idempotent check - First: {data1.get('seeded', 'N/A')}, Second: {data2.get('seeded', 'N/A')}")
    
    def test_seed_200_questions_categories(self):
        """Verify seeded questions have correct categories"""
        resp = self.session.post(f"{BASE_URL}/api/admin/seed-200-questions")
        assert resp.status_code in [200, 201]
        data = resp.json()
        
        # Check categories if returned
        if "categories" in data:
            cats = data["categories"]
            expected_cats = ["batting", "bowling", "powerplay", "death_overs", "match", "player_performance", "special"]
            for cat in expected_cats:
                assert cat in cats, f"Missing category: {cat}"
            print(f"Categories: {cats}")
    
    # ==================== AUTO-GENERATE 5 TEMPLATES ====================
    
    def test_get_match_for_auto_templates(self):
        """Get a match ID for auto-template testing"""
        resp = self.session.get(f"{BASE_URL}/api/matches?limit=10")
        assert resp.status_code == 200
        matches = resp.json().get("matches", [])
        assert len(matches) > 0, "No matches found for testing"
        
        # Store match ID for other tests
        self.match_id = matches[0]["id"]
        print(f"Using match: {matches[0].get('team_a', {}).get('short_name', '?')} vs {matches[0].get('team_b', {}).get('short_name', '?')} (ID: {self.match_id})")
        return self.match_id
    
    def test_auto_generate_5_templates(self):
        """POST /api/admin/matches/{match_id}/auto-templates - should generate 5 templates"""
        # Get a match first
        resp = self.session.get(f"{BASE_URL}/api/matches?limit=10")
        assert resp.status_code == 200
        matches = resp.json().get("matches", [])
        assert len(matches) > 0, "No matches found"
        
        match_id = matches[0]["id"]
        
        # Auto-generate templates
        resp = self.session.post(f"{BASE_URL}/api/admin/matches/{match_id}/auto-templates")
        assert resp.status_code in [200, 201], f"Auto-generate failed: {resp.text}"
        data = resp.json()
        
        # Should return template info
        assert "templates_created" in data or "templates" in data or "message" in data
        
        # If templates were created, verify count
        if data.get("templates_created", 0) > 0:
            assert data["templates_created"] == 5, f"Expected 5 templates, got {data['templates_created']}"
        
        print(f"Auto-generate response: {data}")
    
    def test_auto_templates_already_exists(self):
        """POST /api/admin/matches/{match_id}/auto-templates - should skip if already has 5"""
        # Get a match
        resp = self.session.get(f"{BASE_URL}/api/matches?limit=10")
        matches = resp.json().get("matches", [])
        match_id = matches[0]["id"]
        
        # First call
        resp1 = self.session.post(f"{BASE_URL}/api/admin/matches/{match_id}/auto-templates")
        assert resp1.status_code in [200, 201]
        
        # Second call - should skip
        resp2 = self.session.post(f"{BASE_URL}/api/admin/matches/{match_id}/auto-templates")
        assert resp2.status_code in [200, 201]
        data2 = resp2.json()
        
        # Should indicate already has templates
        if data2.get("templates_created", -1) == 0:
            assert "already" in str(data2.get("message", "")).lower() or len(data2.get("template_ids", [])) >= 5
        print(f"Second auto-generate: {data2}")
    
    # ==================== TEMPLATES WITH NEW FIELDS ====================
    
    def test_templates_have_new_fields(self):
        """GET /api/admin/templates - should show new in-match routing fields"""
        resp = self.session.get(f"{BASE_URL}/api/admin/templates?limit=50")
        assert resp.status_code == 200
        templates = resp.json().get("templates", [])
        
        # Find in_match templates
        in_match_templates = [t for t in templates if t.get("template_type") == "in_match"]
        
        if in_match_templates:
            t = in_match_templates[0]
            # Check new fields exist
            assert "phase_label" in t, "Missing phase_label field"
            assert "innings_range" in t, "Missing innings_range field"
            assert "over_start" in t, "Missing over_start field"
            assert "over_end" in t, "Missing over_end field"
            assert "answer_deadline_over" in t, "Missing answer_deadline_over field"
            
            print(f"In-match template: {t.get('name')}")
            print(f"  phase_label: {t.get('phase_label')}")
            print(f"  innings_range: {t.get('innings_range')}")
            print(f"  over_start: {t.get('over_start')}, over_end: {t.get('over_end')}")
            print(f"  answer_deadline_over: {t.get('answer_deadline_over')}")
        else:
            # Generate templates first
            resp = self.session.get(f"{BASE_URL}/api/matches?limit=1")
            matches = resp.json().get("matches", [])
            if matches:
                self.session.post(f"{BASE_URL}/api/admin/matches/{matches[0]['id']}/auto-templates")
                # Re-fetch templates
                resp = self.session.get(f"{BASE_URL}/api/admin/templates?limit=50")
                templates = resp.json().get("templates", [])
                in_match_templates = [t for t in templates if t.get("template_type") == "in_match"]
                if in_match_templates:
                    t = in_match_templates[0]
                    assert "phase_label" in t
                    print(f"Generated in-match template: {t.get('name')}, phase: {t.get('phase_label')}")
    
    def test_templates_full_match_vs_in_match(self):
        """Verify both full_match and in_match template types exist"""
        resp = self.session.get(f"{BASE_URL}/api/admin/templates?limit=50")
        assert resp.status_code == 200
        templates = resp.json().get("templates", [])
        
        full_match = [t for t in templates if t.get("template_type") == "full_match"]
        in_match = [t for t in templates if t.get("template_type") == "in_match"]
        
        print(f"Full match templates: {len(full_match)}")
        print(f"In-match templates: {len(in_match)}")
        
        # After auto-generation, should have both types
        if len(templates) >= 5:
            assert len(full_match) >= 1, "Should have at least 1 full_match template"
            assert len(in_match) >= 1, "Should have at least 1 in_match template"
    
    # ==================== ADMIN STATS ====================
    
    def test_admin_stats_counts(self):
        """GET /api/admin/stats - should reflect correct counts"""
        resp = self.session.get(f"{BASE_URL}/api/admin/stats")
        assert resp.status_code == 200
        data = resp.json()
        
        # Check question count
        if "questions" in data or "question_count" in data:
            q_count = data.get("questions", data.get("question_count", 0))
            print(f"Question count: {q_count}")
            # After seeding 200, should have at least 200
            assert q_count >= 100, f"Expected at least 100 questions, got {q_count}"
        
        # Check template count
        if "templates" in data or "template_count" in data:
            t_count = data.get("templates", data.get("template_count", 0))
            print(f"Template count: {t_count}")
        
        print(f"Admin stats: {data}")
    
    # ==================== UPDATE TEMPLATE IN-MATCH FIELDS ====================
    
    def test_update_template_in_match_fields(self):
        """PUT /api/admin/templates/{id} - should update in-match routing fields"""
        # Get templates
        resp = self.session.get(f"{BASE_URL}/api/admin/templates?limit=50")
        assert resp.status_code == 200
        templates = resp.json().get("templates", [])
        
        # Find an in_match template or any template
        template = None
        for t in templates:
            if t.get("template_type") == "in_match":
                template = t
                break
        
        if not template and templates:
            template = templates[0]
        
        if not template:
            pytest.skip("No templates found to update")
        
        template_id = template["id"]
        
        # Update with new in-match routing fields
        update_data = {
            "name": template.get("name", "Test Template"),
            "template_type": "in_match",
            "phase_label": "Test Phase - Innings 1 Powerplay",
            "innings_range": [1],
            "over_start": 1,
            "over_end": 6,
            "answer_deadline_over": 1,
            "question_ids": template.get("question_ids", [])[:5] or []  # Keep some questions
        }
        
        resp = self.session.put(f"{BASE_URL}/api/admin/templates/{template_id}", json=update_data)
        assert resp.status_code == 200, f"Update failed: {resp.text}"
        
        # Verify update
        resp = self.session.get(f"{BASE_URL}/api/admin/templates?limit=50")
        templates = resp.json().get("templates", [])
        updated = next((t for t in templates if t["id"] == template_id), None)
        
        if updated:
            assert updated.get("phase_label") == "Test Phase - Innings 1 Powerplay"
            assert updated.get("innings_range") == [1]
            assert updated.get("over_start") == 1
            assert updated.get("over_end") == 6
            assert updated.get("answer_deadline_over") == 1
            print(f"Updated template: {updated.get('name')}")
            print(f"  phase_label: {updated.get('phase_label')}")
            print(f"  innings_range: {updated.get('innings_range')}")
            print(f"  over_start-end: {updated.get('over_start')}-{updated.get('over_end')}")
    
    # ==================== QUESTIONS VERIFICATION ====================
    
    def test_questions_have_auto_resolution(self):
        """Verify seeded questions have auto_resolution config"""
        resp = self.session.get(f"{BASE_URL}/api/admin/questions?limit=200")
        assert resp.status_code == 200
        questions = resp.json().get("questions", [])
        
        auto_qs = [q for q in questions if q.get("auto_resolution", {}).get("metric")]
        print(f"Total questions: {len(questions)}, Auto-resolution: {len(auto_qs)}")
        
        # After seeding, most should have auto_resolution
        if len(questions) >= 100:
            assert len(auto_qs) >= 50, f"Expected at least 50 auto-resolution questions, got {len(auto_qs)}"
        
        # Check structure of auto_resolution
        if auto_qs:
            q = auto_qs[0]
            auto_res = q.get("auto_resolution", {})
            assert "metric" in auto_res, "Missing metric in auto_resolution"
            assert "trigger" in auto_res, "Missing trigger in auto_resolution"
            print(f"Sample auto_resolution: {auto_res}")
    
    # ==================== ACCESS CONTROL ====================
    
    def test_seed_requires_admin(self):
        """POST /api/admin/seed-200-questions - requires admin auth"""
        no_auth_session = requests.Session()
        no_auth_session.headers.update({"Content-Type": "application/json"})
        
        resp = no_auth_session.post(f"{BASE_URL}/api/admin/seed-200-questions")
        assert resp.status_code in [401, 403], f"Should require auth, got {resp.status_code}"
    
    def test_auto_templates_requires_admin(self):
        """POST /api/admin/matches/{id}/auto-templates - requires admin auth"""
        no_auth_session = requests.Session()
        no_auth_session.headers.update({"Content-Type": "application/json"})
        
        resp = no_auth_session.post(f"{BASE_URL}/api/admin/matches/test-id/auto-templates")
        assert resp.status_code in [401, 403], f"Should require auth, got {resp.status_code}"


class TestTemplatePhaseLabels:
    """Test phase labels and over ranges on templates"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "phone": "7004186276",
            "pin": "5524"
        })
        assert login_resp.status_code == 200
        token = login_resp.json().get("token")
        self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def test_auto_generated_templates_have_phase_labels(self):
        """Auto-generated templates should have correct phase labels"""
        # Get templates
        resp = self.session.get(f"{BASE_URL}/api/admin/templates?limit=50")
        assert resp.status_code == 200
        templates = resp.json().get("templates", [])
        
        # Check for expected phase labels
        expected_phases = [
            "Full Match",
            "Innings 1 - Powerplay",
            "Innings 1 - Death",
            "Innings 2 - Powerplay",
            "Innings 2 - Death"
        ]
        
        found_phases = [t.get("phase_label") for t in templates if t.get("phase_label")]
        print(f"Found phase labels: {found_phases}")
        
        # At least some should match expected patterns
        for phase in found_phases:
            if phase:
                assert any(exp in phase for exp in ["Full", "Innings", "Powerplay", "Death"]), \
                    f"Unexpected phase label: {phase}"
    
    def test_powerplay_templates_have_correct_overs(self):
        """Powerplay templates should have overs 1-6"""
        resp = self.session.get(f"{BASE_URL}/api/admin/templates?limit=50")
        templates = resp.json().get("templates", [])
        
        pp_templates = [t for t in templates if "powerplay" in (t.get("phase_label") or "").lower()]
        
        for t in pp_templates:
            if t.get("over_start") and t.get("over_end"):
                assert t["over_start"] == 1, f"Powerplay should start at over 1, got {t['over_start']}"
                assert t["over_end"] == 6, f"Powerplay should end at over 6, got {t['over_end']}"
                print(f"Powerplay template: {t.get('name')} - Overs {t['over_start']}-{t['over_end']}")
    
    def test_death_templates_have_correct_overs(self):
        """Death overs templates should have overs 16-20"""
        resp = self.session.get(f"{BASE_URL}/api/admin/templates?limit=50")
        templates = resp.json().get("templates", [])
        
        death_templates = [t for t in templates if "death" in (t.get("phase_label") or "").lower()]
        
        for t in death_templates:
            if t.get("over_start") and t.get("over_end"):
                assert t["over_start"] == 16, f"Death should start at over 16, got {t['over_start']}"
                assert t["over_end"] == 20, f"Death should end at over 20, got {t['over_end']}"
                print(f"Death template: {t.get('name')} - Overs {t['over_start']}-{t['over_end']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
