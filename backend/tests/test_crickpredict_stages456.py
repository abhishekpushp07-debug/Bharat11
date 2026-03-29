"""
CrickPredict Stages 4-6 - Backend API Tests
Tests: User Profile, Wallet, Admin Questions/Templates, Match Management
"""
import pytest
import requests
import os
import random
import string

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://plan-then-build-1.preview.emergentagent.com')

# Test credentials from test_credentials.md
TEST_PHONE = "9876543210"
TEST_PIN = "1234"


def generate_phone():
    """Generate random 10-digit phone number."""
    return "9" + ''.join(random.choices(string.digits, k=9))


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def auth_token(api_client):
    """Get authentication token for test user."""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "phone": TEST_PHONE,
        "pin": TEST_PIN
    })
    if response.status_code == 200:
        data = response.json()
        return data.get("token", {}).get("access_token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture(scope="module")
def authenticated_client(api_client, auth_token):
    """Session with auth header."""
    api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return api_client


# ==================== USER PROFILE TESTS (Stage 4) ====================

class TestUserProfile:
    """User profile endpoint tests."""
    
    def test_get_profile(self, authenticated_client):
        """GET /api/user/profile returns user data."""
        response = authenticated_client.get(f"{BASE_URL}/api/user/profile")
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert "phone" in data
        assert "username" in data
        assert "coins_balance" in data
        assert "rank_title" in data
        assert "total_points" in data
        assert "matches_played" in data
        assert "contests_won" in data
        assert "referral_code" in data
        print(f"✓ Profile: username={data['username']}, rank={data['rank_title']}, balance={data['coins_balance']}")
    
    def test_update_profile_username(self, authenticated_client):
        """PUT /api/user/profile updates username."""
        new_username = f"TestPlayer_{random.randint(1000, 9999)}"
        response = authenticated_client.put(f"{BASE_URL}/api/user/profile", json={
            "username": new_username
        })
        assert response.status_code == 200
        data = response.json()
        
        assert data["username"] == new_username
        print(f"✓ Profile updated: username={new_username}")
    
    def test_get_rank_progress(self, authenticated_client):
        """GET /api/user/rank-progress returns rank and progress."""
        response = authenticated_client.get(f"{BASE_URL}/api/user/rank-progress")
        assert response.status_code == 200
        data = response.json()
        
        assert "current_rank" in data
        assert "total_points" in data
        assert "progress_percent" in data
        assert "rank_min" in data
        assert "rank_max" in data
        print(f"✓ Rank progress: rank={data['current_rank']}, points={data['total_points']}, progress={data['progress_percent']}%")
    
    def test_get_referral_stats(self, authenticated_client):
        """GET /api/user/referral-stats returns referral code and count."""
        response = authenticated_client.get(f"{BASE_URL}/api/user/referral-stats")
        assert response.status_code == 200
        data = response.json()
        
        assert "referral_code" in data
        assert "total_referrals" in data
        assert "bonus_per_referral" in data
        assert data["bonus_per_referral"] == 1000
        print(f"✓ Referral stats: code={data['referral_code']}, referrals={data['total_referrals']}")
    
    def test_get_leaderboard(self, api_client):
        """GET /api/user/leaderboard returns ranked users."""
        response = api_client.get(f"{BASE_URL}/api/user/leaderboard?limit=10")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        if len(data) > 0:
            user = data[0]
            assert "rank" in user
            assert "user_id" in user
            assert "username" in user
            assert "total_points" in user
            assert "rank_title" in user
            assert user["rank"] == 1  # First user should have rank 1
        print(f"✓ Leaderboard: {len(data)} users")


# ==================== WALLET TESTS (Stage 4) ====================

class TestWallet:
    """Wallet endpoint tests."""
    
    def test_get_balance(self, authenticated_client):
        """GET /api/wallet/balance returns balance and daily reward status."""
        response = authenticated_client.get(f"{BASE_URL}/api/wallet/balance")
        assert response.status_code == 200
        data = response.json()
        
        assert "user_id" in data
        assert "balance" in data
        assert "daily_streak" in data
        assert "can_claim_daily" in data
        assert isinstance(data["balance"], int)
        assert isinstance(data["daily_streak"], int)
        assert isinstance(data["can_claim_daily"], bool)
        print(f"✓ Balance: {data['balance']} coins, streak={data['daily_streak']}, can_claim={data['can_claim_daily']}")
    
    def test_get_transactions(self, authenticated_client):
        """GET /api/wallet/transactions returns paginated transaction history."""
        response = authenticated_client.get(f"{BASE_URL}/api/wallet/transactions?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        
        assert "transactions" in data
        assert "page" in data
        assert "limit" in data
        assert "total" in data
        assert "has_more" in data
        
        if len(data["transactions"]) > 0:
            tx = data["transactions"][0]
            assert "id" in tx
            assert "type" in tx
            assert "amount" in tx
            assert "reason" in tx
            assert "balance_after" in tx
            assert "created_at" in tx
            assert tx["type"] in ["credit", "debit"]
        print(f"✓ Transactions: {len(data['transactions'])} items, total={data['total']}")
    
    def test_claim_daily_reward_or_already_claimed(self, authenticated_client):
        """POST /api/wallet/claim-daily claims daily reward or returns already claimed."""
        response = authenticated_client.post(f"{BASE_URL}/api/wallet/claim-daily")
        
        # Either success (200) or already claimed (400)
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            data = response.json()
            assert "reward_amount" in data
            assert "new_balance" in data
            assert "streak" in data
            assert "is_streak_bonus" in data
            assert "next_reward" in data
            print(f"✓ Daily reward claimed: +{data['reward_amount']} coins, streak={data['streak']}")
        else:
            # Already claimed today
            print(f"✓ Daily reward already claimed today (expected)")


# ==================== ADMIN QUESTIONS TESTS (Stage 5) ====================

class TestAdminQuestions:
    """Admin questions CRUD tests."""
    
    def test_list_questions(self, authenticated_client):
        """GET /api/admin/questions returns paginated questions."""
        response = authenticated_client.get(f"{BASE_URL}/api/admin/questions?limit=10")
        assert response.status_code == 200
        data = response.json()
        
        assert "questions" in data
        assert "page" in data
        assert "limit" in data
        assert "total" in data
        assert "has_more" in data
        assert data["total"] >= 72  # 72 seeded questions
        
        if len(data["questions"]) > 0:
            q = data["questions"][0]
            assert "id" in q
            assert "question_text_en" in q
            assert "category" in q
            assert "difficulty" in q
            assert "options" in q
            assert "points" in q
        print(f"✓ Questions: {len(data['questions'])} items, total={data['total']}")
    
    def test_list_questions_by_category(self, authenticated_client):
        """GET /api/admin/questions with category filter."""
        response = authenticated_client.get(f"{BASE_URL}/api/admin/questions?category=match_outcome")
        assert response.status_code == 200
        data = response.json()
        
        assert "questions" in data
        for q in data["questions"]:
            assert q["category"] == "match_outcome"
        print(f"✓ Questions filtered by category: {len(data['questions'])} match_outcome questions")
    
    def test_create_question(self, authenticated_client):
        """POST /api/admin/questions creates a new question."""
        response = authenticated_client.post(f"{BASE_URL}/api/admin/questions", json={
            "question_text_en": "TEST: Who will score the most runs?",
            "question_text_hi": "टेस्ट: सबसे ज्यादा रन कौन बनाएगा?",
            "category": "player_performance",
            "difficulty": "medium",
            "options": [
                {"key": "A", "text_en": "Player A", "text_hi": "खिलाड़ी A"},
                {"key": "B", "text_en": "Player B", "text_hi": "खिलाड़ी B"},
                {"key": "C", "text_en": "Player C", "text_hi": "खिलाड़ी C"},
                {"key": "D", "text_en": "Player D", "text_hi": "खिलाड़ी D"}
            ],
            "points": 15,
            "is_active": True
        })
        assert response.status_code == 201
        data = response.json()
        
        assert "id" in data
        assert data["question_text_en"] == "TEST: Who will score the most runs?"
        assert data["category"] == "player_performance"
        assert data["difficulty"] == "medium"
        assert data["points"] == 15
        assert len(data["options"]) == 4
        print(f"✓ Question created: id={data['id']}")
        
        # Store for cleanup
        TestAdminQuestions.created_question_id = data["id"]
    
    def test_update_question(self, authenticated_client):
        """PUT /api/admin/questions/{id} updates a question."""
        question_id = getattr(TestAdminQuestions, 'created_question_id', None)
        if not question_id:
            pytest.skip("No question created to update")
        
        response = authenticated_client.put(f"{BASE_URL}/api/admin/questions/{question_id}", json={
            "points": 20,
            "difficulty": "hard"
        })
        assert response.status_code == 200
        data = response.json()
        
        assert data["points"] == 20
        assert data["difficulty"] == "hard"
        print(f"✓ Question updated: points=20, difficulty=hard")
    
    def test_delete_question(self, authenticated_client):
        """DELETE /api/admin/questions/{id} deletes a question."""
        question_id = getattr(TestAdminQuestions, 'created_question_id', None)
        if not question_id:
            pytest.skip("No question created to delete")
        
        response = authenticated_client.delete(f"{BASE_URL}/api/admin/questions/{question_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["message"] == "Question deleted"
        assert data["id"] == question_id
        print(f"✓ Question deleted: id={question_id}")
    
    def test_bulk_import_questions(self, authenticated_client):
        """POST /api/admin/questions/bulk-import imports multiple questions."""
        response = authenticated_client.post(f"{BASE_URL}/api/admin/questions/bulk-import", json={
            "questions": [
                {
                    "question_text_en": "TEST_BULK: Question 1",
                    "category": "match_outcome",
                    "difficulty": "easy",
                    "options": [
                        {"key": "A", "text_en": "Option A", "text_hi": ""},
                        {"key": "B", "text_en": "Option B", "text_hi": ""}
                    ],
                    "points": 10
                },
                {
                    "question_text_en": "TEST_BULK: Question 2",
                    "category": "match_outcome",
                    "difficulty": "easy",
                    "options": [
                        {"key": "A", "text_en": "Option A", "text_hi": ""},
                        {"key": "B", "text_en": "Option B", "text_hi": ""}
                    ],
                    "points": 10
                }
            ]
        })
        assert response.status_code == 201
        data = response.json()
        
        assert data["imported"] == 2
        assert "successfully" in data["message"]
        print(f"✓ Bulk import: {data['imported']} questions imported")


# ==================== ADMIN TEMPLATES TESTS (Stage 5) ====================

class TestAdminTemplates:
    """Admin templates CRUD tests."""
    
    def test_list_templates(self, authenticated_client):
        """GET /api/admin/templates returns paginated templates."""
        response = authenticated_client.get(f"{BASE_URL}/api/admin/templates")
        assert response.status_code == 200
        data = response.json()
        
        assert "templates" in data
        assert "page" in data
        assert "limit" in data
        assert "total" in data
        assert data["total"] >= 5  # At least 5 templates
        
        if len(data["templates"]) > 0:
            t = data["templates"][0]
            assert "id" in t
            assert "name" in t
            assert "match_type" in t
            assert "question_ids" in t
            assert "total_points" in t
            assert "question_count" in t
        print(f"✓ Templates: {len(data['templates'])} items, total={data['total']}")
        
        # Store template ID for later tests
        if len(data["templates"]) > 0:
            TestAdminTemplates.existing_template_id = data["templates"][0]["id"]
    
    def test_get_template_with_resolved_questions(self, authenticated_client):
        """GET /api/admin/templates/{id} returns template with resolved questions."""
        template_id = getattr(TestAdminTemplates, 'existing_template_id', None)
        if not template_id:
            pytest.skip("No template available")
        
        response = authenticated_client.get(f"{BASE_URL}/api/admin/templates/{template_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert "name" in data
        assert "questions" in data  # Resolved questions
        assert isinstance(data["questions"], list)
        
        if len(data["questions"]) > 0:
            q = data["questions"][0]
            assert "id" in q
            assert "question_text_en" in q
            assert "options" in q
        print(f"✓ Template resolved: name={data['name']}, questions={len(data['questions'])}")
    
    def test_create_template(self, authenticated_client):
        """POST /api/admin/templates creates a new template."""
        # First get some question IDs
        q_response = authenticated_client.get(f"{BASE_URL}/api/admin/questions?limit=3")
        questions = q_response.json()["questions"]
        question_ids = [q["id"] for q in questions[:3]]
        
        response = authenticated_client.post(f"{BASE_URL}/api/admin/templates", json={
            "name": "TEST Template",
            "description": "Test template for automated testing",
            "match_type": "T20",
            "question_ids": question_ids,
            "is_active": True
        })
        assert response.status_code == 201
        data = response.json()
        
        assert "id" in data
        assert data["name"] == "TEST Template"
        assert data["match_type"] == "T20"
        assert data["question_count"] == len(question_ids)
        assert "total_points" in data
        print(f"✓ Template created: id={data['id']}, questions={data['question_count']}")
        
        TestAdminTemplates.created_template_id = data["id"]
    
    def test_clone_template(self, authenticated_client):
        """POST /api/admin/templates/{id}/clone clones a template."""
        template_id = getattr(TestAdminTemplates, 'created_template_id', None)
        if not template_id:
            pytest.skip("No template created to clone")
        
        response = authenticated_client.post(f"{BASE_URL}/api/admin/templates/{template_id}/clone")
        assert response.status_code == 201
        data = response.json()
        
        assert "id" in data
        assert data["id"] != template_id  # New ID
        assert "(Copy)" in data["name"]
        print(f"✓ Template cloned: id={data['id']}, name={data['name']}")
        
        TestAdminTemplates.cloned_template_id = data["id"]
    
    def test_delete_template(self, authenticated_client):
        """DELETE /api/admin/templates/{id} deletes a template."""
        # Delete the cloned template
        template_id = getattr(TestAdminTemplates, 'cloned_template_id', None)
        if not template_id:
            pytest.skip("No template to delete")
        
        response = authenticated_client.delete(f"{BASE_URL}/api/admin/templates/{template_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["message"] == "Template deleted"
        print(f"✓ Template deleted: id={template_id}")


# ==================== MATCH MANAGEMENT TESTS (Stage 6) ====================

class TestMatches:
    """Match management endpoint tests."""
    
    def test_list_matches(self, api_client):
        """GET /api/matches returns paginated matches (no auth required)."""
        response = api_client.get(f"{BASE_URL}/api/matches?limit=10")
        assert response.status_code == 200
        data = response.json()
        
        assert "matches" in data
        assert "page" in data
        assert "limit" in data
        assert "total" in data
        assert data["total"] >= 6  # 6 seeded matches
        
        if len(data["matches"]) > 0:
            m = data["matches"][0]
            assert "id" in m
            assert "team_a" in m
            assert "team_b" in m
            assert "venue" in m
            assert "status" in m
            assert "start_time" in m
            assert m["team_a"]["short_name"] is not None
            assert m["team_b"]["short_name"] is not None
        print(f"✓ Matches: {len(data['matches'])} items, total={data['total']}")
        
        if len(data["matches"]) > 0:
            TestMatches.existing_match_id = data["matches"][0]["id"]
    
    def test_get_match_detail(self, api_client):
        """GET /api/matches/{id} returns match details with contests count."""
        match_id = getattr(TestMatches, 'existing_match_id', None)
        if not match_id:
            pytest.skip("No match available")
        
        response = api_client.get(f"{BASE_URL}/api/matches/{match_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == match_id
        assert "team_a" in data
        assert "team_b" in data
        assert "venue" in data
        assert "status" in data
        assert "contests_count" in data
        print(f"✓ Match detail: {data['team_a']['short_name']} vs {data['team_b']['short_name']}, contests={data['contests_count']}")
    
    def test_get_match_contests(self, api_client):
        """GET /api/matches/{id}/contests returns match contests."""
        match_id = getattr(TestMatches, 'existing_match_id', None)
        if not match_id:
            pytest.skip("No match available")
        
        response = api_client.get(f"{BASE_URL}/api/matches/{match_id}/contests")
        assert response.status_code == 200
        data = response.json()
        
        assert "match_id" in data
        assert "contests" in data
        assert "total" in data
        assert data["match_id"] == match_id
        print(f"✓ Match contests: {data['total']} contests")
    
    def test_create_match(self, authenticated_client):
        """POST /api/matches creates a new match (admin)."""
        response = authenticated_client.post(f"{BASE_URL}/api/matches", json={
            "team_a": {
                "name": "Test Team A",
                "short_name": "TTA",
                "logo_url": ""
            },
            "team_b": {
                "name": "Test Team B",
                "short_name": "TTB",
                "logo_url": ""
            },
            "match_type": "T20",
            "venue": "Test Stadium",
            "start_time": "2026-04-15T19:30:00Z",
            "tournament": "Test Tournament"
        })
        assert response.status_code == 201
        data = response.json()
        
        assert "id" in data
        assert data["team_a"]["short_name"] == "TTA"
        assert data["team_b"]["short_name"] == "TTB"
        assert data["status"] == "upcoming"
        print(f"✓ Match created: id={data['id']}")
        
        TestMatches.created_match_id = data["id"]
    
    def test_update_match_status(self, authenticated_client):
        """PUT /api/matches/{id}/status updates match status."""
        match_id = getattr(TestMatches, 'created_match_id', None)
        if not match_id:
            pytest.skip("No match created")
        
        response = authenticated_client.put(f"{BASE_URL}/api/matches/{match_id}/status", json={
            "status": "live"
        })
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "live"
        print(f"✓ Match status updated: status=live")
    
    def test_assign_template_to_match(self, authenticated_client):
        """POST /api/matches/{id}/assign-template assigns template to match."""
        match_id = getattr(TestMatches, 'created_match_id', None)
        template_id = getattr(TestAdminTemplates, 'created_template_id', None)
        
        if not match_id or not template_id:
            pytest.skip("No match or template available")
        
        response = authenticated_client.post(
            f"{BASE_URL}/api/matches/{match_id}/assign-template?template_id={template_id}"
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["assigned"] == True
        assert data["match_id"] == match_id
        assert data["template_id"] == template_id
        print(f"✓ Template assigned to match")


# ==================== SECURITY HEADERS TESTS ====================

class TestSecurityHeaders:
    """Security header tests."""
    
    def test_security_headers_present(self, api_client):
        """All responses have security headers."""
        response = api_client.get(f"{BASE_URL}/api/health")
        
        assert response.headers.get("X-Request-ID") is not None
        assert response.headers.get("X-Response-Time") is not None
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        print(f"✓ Security headers: X-Request-ID, X-Response-Time, X-Content-Type-Options, X-Frame-Options")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
