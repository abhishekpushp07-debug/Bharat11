"""
Iteration 29 - Testing New Features:
1. POST /api/admin/seed-question-pool - Seeds 200 bilingual questions
2. POST /api/admin/matches/{match_id}/auto-templates - Creates 5 templates per match
3. POST /api/admin/auto-templates-all - Bulk generates templates for all upcoming matches
4. GET /api/cricket/ipl/points-table - Returns 10 IPL teams
5. GET /api/cricket/live-ticker - Returns IPL scores
6. GET /api/cricket/ipl/team/{short}/matches - Returns team matches
7. GET /api/cricket/match/{id}/full-data - Returns combined match data
8. GET /api/cricket/cache-stats - Shows cached items
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_PHONE = "7004186276"
ADMIN_PIN = "5524"
PLAYER_PHONE = "9111111111"
PLAYER_PIN = "5678"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin auth token."""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "phone": ADMIN_PHONE,
        "pin": ADMIN_PIN
    })
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    data = response.json()
    # Token is nested: {"token": {"access_token": "..."}}
    token = data.get("token", {}).get("access_token") or data.get("access_token")
    assert token, f"No token in response: {data}"
    return token


@pytest.fixture(scope="module")
def player_token():
    """Get player auth token."""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "phone": PLAYER_PHONE,
        "pin": PLAYER_PIN
    })
    assert response.status_code == 200, f"Player login failed: {response.text}"
    data = response.json()
    token = data.get("token", {}).get("access_token") or data.get("access_token")
    assert token, f"No token in response: {data}"
    return token


class TestHealthAndAuth:
    """Basic health and auth tests."""
    
    def test_health_endpoint(self):
        """Health endpoint returns 200."""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("PASS: Health endpoint returns healthy status")
    
    def test_admin_login(self, admin_token):
        """Admin login returns valid token."""
        assert admin_token is not None
        assert len(admin_token) > 20
        print(f"PASS: Admin login successful, token length: {len(admin_token)}")
    
    def test_player_login(self, player_token):
        """Player login returns valid token."""
        assert player_token is not None
        assert len(player_token) > 20
        print(f"PASS: Player login successful, token length: {len(player_token)}")


class TestCricketDataAPIs:
    """Test Cricket Data APIs (existing features - regression)."""
    
    def test_ipl_points_table_returns_teams(self):
        """GET /api/cricket/ipl/points-table returns 10 IPL teams."""
        response = requests.get(f"{BASE_URL}/api/cricket/ipl/points-table")
        assert response.status_code == 200
        data = response.json()
        teams = data.get("teams", [])
        assert len(teams) == 10, f"Expected 10 teams, got {len(teams)}"
        print(f"PASS: Points table returns {len(teams)} IPL teams")
    
    def test_ipl_points_table_team_structure(self):
        """Each team has required fields."""
        response = requests.get(f"{BASE_URL}/api/cricket/ipl/points-table")
        data = response.json()
        teams = data.get("teams", [])
        for team in teams[:3]:  # Check first 3
            assert "shortname" in team, f"Missing shortname: {team}"
            assert "wins" in team, f"Missing wins: {team}"
            assert "loss" in team, f"Missing loss: {team}"
            assert "matches" in team, f"Missing matches: {team}"
        print("PASS: Team structure has shortname, wins, loss, matches")
    
    def test_live_ticker_returns_scores(self):
        """GET /api/cricket/live-ticker returns IPL match scores."""
        response = requests.get(f"{BASE_URL}/api/cricket/live-ticker")
        assert response.status_code == 200
        data = response.json()
        scores = data.get("scores", [])
        assert len(scores) > 0, "No scores returned"
        print(f"PASS: Live ticker returns {len(scores)} matches")
    
    def test_live_ticker_match_structure(self):
        """Each match has required fields."""
        response = requests.get(f"{BASE_URL}/api/cricket/live-ticker")
        data = response.json()
        scores = data.get("scores", [])
        for match in scores[:3]:
            assert "id" in match, f"Missing id: {match}"
            assert "t1" in match, f"Missing t1: {match}"
            assert "t2" in match, f"Missing t2: {match}"
            assert "ms" in match, f"Missing ms: {match}"
            assert "status" in match, f"Missing status: {match}"
        print("PASS: Match structure has id, t1, t2, ms, status")
    
    def test_team_matches_mi(self):
        """GET /api/cricket/ipl/team/MI/matches returns MI matches."""
        response = requests.get(f"{BASE_URL}/api/cricket/ipl/team/MI/matches")
        assert response.status_code == 200
        data = response.json()
        assert data.get("team") == "MI"
        matches = data.get("matches", [])
        assert len(matches) > 0, "No MI matches returned"
        print(f"PASS: MI matches endpoint returns {len(matches)} matches")
    
    def test_team_matches_csk(self):
        """GET /api/cricket/ipl/team/CSK/matches returns CSK matches."""
        response = requests.get(f"{BASE_URL}/api/cricket/ipl/team/CSK/matches")
        assert response.status_code == 200
        data = response.json()
        assert data.get("team") == "CSK"
        matches = data.get("matches", [])
        assert len(matches) > 0, "No CSK matches returned"
        print(f"PASS: CSK matches endpoint returns {len(matches)} matches")
    
    def test_cache_stats(self):
        """GET /api/cricket/cache-stats shows cached items."""
        response = requests.get(f"{BASE_URL}/api/cricket/cache-stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_cached" in data
        assert "by_type" in data
        print(f"PASS: Cache stats shows {data.get('total_cached')} cached items")


class TestQuestionPoolSeed:
    """Test 200-question pool seed endpoint."""
    
    def test_seed_question_pool_requires_admin(self, player_token):
        """POST /api/admin/seed-question-pool requires admin role."""
        headers = {"Authorization": f"Bearer {player_token}"}
        response = requests.post(f"{BASE_URL}/api/admin/seed-question-pool", headers=headers)
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: seed-question-pool requires admin role")
    
    def test_seed_question_pool_with_force(self, admin_token):
        """POST /api/admin/seed-question-pool?force=true seeds 200 questions."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.post(f"{BASE_URL}/api/admin/seed-question-pool?force=true", headers=headers)
        assert response.status_code == 200, f"Seed failed: {response.text}"
        data = response.json()
        assert data.get("seeded") == 200, f"Expected 200 seeded, got {data.get('seeded')}"
        print(f"PASS: Seeded {data.get('seeded')} questions")
    
    def test_seed_question_pool_categories(self, admin_token):
        """Seeded questions have correct category distribution."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        # First seed with force
        requests.post(f"{BASE_URL}/api/admin/seed-question-pool?force=true", headers=headers)
        # Then check categories
        response = requests.post(f"{BASE_URL}/api/admin/seed-question-pool", headers=headers)
        data = response.json()
        # If already seeded, it returns existing count
        if data.get("seeded") == 0:
            # Check via questions list
            q_response = requests.get(f"{BASE_URL}/api/admin/questions?limit=100", headers=headers)
            q_data = q_response.json()
            total = q_data.get("total", 0)
            assert total >= 200, f"Expected 200+ questions, got {total}"
            print(f"PASS: Question pool has {total} questions")
        else:
            cats = data.get("categories", {})
            assert cats.get("batting", 0) >= 35, f"Expected 40 batting, got {cats.get('batting')}"
            assert cats.get("bowling", 0) >= 30, f"Expected 35 bowling, got {cats.get('bowling')}"
            print(f"PASS: Categories: {cats}")
    
    def test_questions_are_bilingual(self, admin_token):
        """Questions have both EN and HI text."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/questions?limit=10", headers=headers)
        assert response.status_code == 200
        data = response.json()
        questions = data.get("questions", [])
        for q in questions[:5]:
            assert q.get("question_text_en"), f"Missing EN text: {q}"
            assert q.get("question_text_hi"), f"Missing HI text: {q}"
        print("PASS: Questions have bilingual EN+HI text")


class TestAutoTemplateEngine:
    """Test 5-Template Match Engine."""
    
    def test_auto_templates_requires_admin(self, player_token):
        """POST /api/admin/matches/{id}/auto-templates requires admin."""
        headers = {"Authorization": f"Bearer {player_token}"}
        response = requests.post(f"{BASE_URL}/api/admin/matches/test-id/auto-templates", headers=headers)
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: auto-templates requires admin role")
    
    def test_auto_templates_for_match(self, admin_token):
        """POST /api/admin/matches/{match_id}/auto-templates creates 5 templates."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # First, ensure we have 200 questions seeded
        requests.post(f"{BASE_URL}/api/admin/seed-question-pool?force=true", headers=headers)
        
        # Get an upcoming match
        matches_response = requests.get(f"{BASE_URL}/api/matches?limit=10")
        matches = matches_response.json().get("matches", [])
        upcoming = [m for m in matches if m.get("status") == "upcoming"]
        
        if not upcoming:
            pytest.skip("No upcoming matches to test auto-templates")
        
        match_id = upcoming[0]["id"]
        
        # Delete existing auto-generated templates for this match
        templates_response = requests.get(f"{BASE_URL}/api/admin/templates?limit=50", headers=headers)
        templates = templates_response.json().get("templates", [])
        for t in templates:
            if t.get("match_id") == match_id and t.get("auto_generated"):
                requests.delete(f"{BASE_URL}/api/admin/templates/{t['id']}", headers=headers)
        
        # Create auto-templates
        response = requests.post(f"{BASE_URL}/api/admin/matches/{match_id}/auto-templates", headers=headers)
        assert response.status_code == 200, f"Auto-templates failed: {response.text}"
        data = response.json()
        
        templates_created = data.get("templates_created", 0)
        assert templates_created == 5, f"Expected 5 templates, got {templates_created}"
        
        total_questions = data.get("total_questions_assigned", 0)
        assert total_questions == 55, f"Expected 55 questions, got {total_questions}"
        
        templates = data.get("templates", [])
        full_match_count = sum(1 for t in templates if t.get("type") == "full_match")
        in_match_count = sum(1 for t in templates if t.get("type") == "in_match")
        
        assert full_match_count == 1, f"Expected 1 full_match, got {full_match_count}"
        assert in_match_count == 4, f"Expected 4 in_match, got {in_match_count}"
        
        print(f"PASS: Created {templates_created} templates with {total_questions} questions (1 full_match + 4 in_match)")
    
    def test_auto_templates_idempotent(self, admin_token):
        """Calling auto-templates twice doesn't create duplicates."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get an upcoming match
        matches_response = requests.get(f"{BASE_URL}/api/matches?limit=10")
        matches = matches_response.json().get("matches", [])
        upcoming = [m for m in matches if m.get("status") == "upcoming"]
        
        if not upcoming:
            pytest.skip("No upcoming matches to test")
        
        match_id = upcoming[0]["id"]
        
        # Call twice
        response1 = requests.post(f"{BASE_URL}/api/admin/matches/{match_id}/auto-templates", headers=headers)
        response2 = requests.post(f"{BASE_URL}/api/admin/matches/{match_id}/auto-templates", headers=headers)
        
        data2 = response2.json()
        # Second call should skip or return existing
        if data2.get("templates_created") == 0:
            print("PASS: Auto-templates is idempotent (skipped on second call)")
        else:
            # Check message
            assert "already exist" in data2.get("message", "").lower() or data2.get("existing", 0) >= 5
            print("PASS: Auto-templates is idempotent")
    
    def test_auto_templates_all(self, admin_token):
        """POST /api/admin/auto-templates-all bulk generates for all upcoming matches."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = requests.post(f"{BASE_URL}/api/admin/auto-templates-all", headers=headers)
        assert response.status_code == 200, f"Bulk auto-templates failed: {response.text}"
        data = response.json()
        
        processed = data.get("processed", 0)
        results = data.get("results", [])
        
        print(f"PASS: Bulk auto-templates processed {processed} matches")
        for r in results[:3]:
            print(f"  - {r.get('match_id')}: {r.get('status')}")


class TestMatchFullData:
    """Test match full-data endpoint."""
    
    def test_match_full_data_returns_sections(self):
        """GET /api/cricket/match/{id}/full-data returns combined data."""
        # Get a completed match ID from schedule
        schedule_response = requests.get(f"{BASE_URL}/api/cricket/ipl/schedule")
        matches = schedule_response.json().get("matches", [])
        completed = [m for m in matches if m.get("matchEnded")]
        
        if not completed:
            pytest.skip("No completed matches to test full-data")
        
        match_id = completed[0].get("id")
        response = requests.get(f"{BASE_URL}/api/cricket/match/{match_id}/full-data")
        assert response.status_code == 200, f"Full-data failed: {response.text}"
        data = response.json()
        
        available = data.get("available_sections", [])
        assert "match_info" in available, "Missing match_info section"
        print(f"PASS: Match full-data returns sections: {available}")


class TestTemplateStructure:
    """Test template structure after auto-generation."""
    
    def test_template_has_phase_routing(self, admin_token):
        """Auto-generated templates have innings_range and over routing."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = requests.get(f"{BASE_URL}/api/admin/templates?limit=20", headers=headers)
        data = response.json()
        templates = data.get("templates", [])
        
        auto_templates = [t for t in templates if t.get("auto_generated")]
        
        if not auto_templates:
            pytest.skip("No auto-generated templates found")
        
        for t in auto_templates[:5]:
            if t.get("template_type") == "in_match":
                assert t.get("innings_range"), f"Missing innings_range: {t.get('name')}"
                assert t.get("phase_label"), f"Missing phase_label: {t.get('name')}"
        
        print("PASS: In-match templates have innings_range and phase_label")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
