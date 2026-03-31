"""
Iteration 57 - Contest Status Access Control Tests
Tests the bug fix: When admin unlives a contest (status→open), users should NOT be able to edit answers.
Only 'live' contests allow join/submit/edit. Open contests show leaderboard + user answers.

Status terminology:
- LIVE = open for participation/prediction editing
- OPEN = participation closed but match ongoing (NO editing allowed, shows leaderboard)
- DONE/COMPLETED = completed with results
"""
import pytest
import requests
import os
from pymongo import MongoClient

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://fantasy-points.preview.emergentagent.com')
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'crickpredict')

# Test credentials
ADMIN_PHONE = "7004186276"
ADMIN_PIN = "5524"
TEST_CONTEST_ID = "c5e299a7-d5c8-4ecc-9010-81964a60d0d4"


@pytest.fixture(scope="module")
def mongo_client():
    """MongoDB client for direct status manipulation"""
    client = MongoClient(MONGO_URL)
    yield client[DB_NAME]
    client.close()


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for admin user"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "phone": ADMIN_PHONE,
        "pin": ADMIN_PIN
    })
    if response.status_code == 200:
        data = response.json()
        # Token structure: {"token": {"access_token": "...", "refresh_token": "..."}, "user": {...}}
        token_data = data.get("token", {})
        if isinstance(token_data, dict):
            token = token_data.get("access_token")
        else:
            token = token_data or data.get("access_token")
        if token:
            return token
    pytest.skip(f"Authentication failed: {response.text}")


@pytest.fixture(scope="module")
def api_client(auth_token):
    """Authenticated requests session"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    })
    return session


def set_contest_status(mongo_db, contest_id, status):
    """Helper to set contest status directly in MongoDB"""
    result = mongo_db.contests.update_one(
        {"id": contest_id},
        {"$set": {"status": status}}
    )
    return result.modified_count > 0 or result.matched_count > 0


class TestContestStatusAccessControl:
    """
    CRITICAL BUG FIX: Test that only 'live' contests allow joining and submitting predictions.
    Status 'open' means participation is closed (match ongoing) - NO editing allowed.
    """

    # ==================== JOIN CONTEST TESTS ====================

    def test_join_contest_rejects_when_status_open(self, api_client, mongo_client):
        """POST /api/contests/{id}/join should REJECT when contest status is 'open'"""
        # Set contest to 'open' status
        set_contest_status(mongo_client, TEST_CONTEST_ID, "open")
        
        response = api_client.post(f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/join", json={
            "team_name": "TEST_Team_Open"
        })
        
        # Should be rejected with 400
        assert response.status_code == 400, f"Expected 400 for open contest, got {response.status_code}: {response.text}"
        data = response.json()
        assert "detail" in data
        # Hindi message: "Sirf live contests mein join kar sakte ho"
        print(f"✓ JOIN rejected for 'open' status: {data.get('detail')}")

    def test_join_contest_allows_when_status_live(self, api_client, mongo_client):
        """POST /api/contests/{id}/join should ALLOW when contest status is 'live'"""
        # Set contest to 'live' status
        set_contest_status(mongo_client, TEST_CONTEST_ID, "live")
        
        response = api_client.post(f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/join", json={
            "team_name": f"TEST_Team_Live_{os.urandom(4).hex()}"
        })
        
        # Should be allowed (200) or already joined (409)
        assert response.status_code in [200, 409], f"Expected 200/409 for live contest, got {response.status_code}: {response.text}"
        
        if response.status_code == 200:
            print(f"✓ JOIN allowed for 'live' status: {response.json().get('message')}")
        else:
            print(f"✓ Already joined (409) - JOIN would be allowed for 'live' status")

    def test_join_contest_rejects_when_status_completed(self, api_client, mongo_client):
        """POST /api/contests/{id}/join should REJECT when contest status is 'completed'"""
        # Set contest to 'completed' status
        set_contest_status(mongo_client, TEST_CONTEST_ID, "completed")
        
        response = api_client.post(f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/join", json={
            "team_name": "TEST_Team_Completed"
        })
        
        # Should be rejected with 400
        assert response.status_code == 400, f"Expected 400 for completed contest, got {response.status_code}: {response.text}"
        print(f"✓ JOIN rejected for 'completed' status: {response.json().get('detail')}")

    # ==================== PREDICT/SUBMIT TESTS ====================

    def test_predict_rejects_when_status_open(self, api_client, mongo_client):
        """POST /api/contests/{id}/predict should REJECT when contest status is 'open'"""
        # First ensure user has joined (set to live, join, then set to open)
        set_contest_status(mongo_client, TEST_CONTEST_ID, "live")
        api_client.post(f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/join", json={
            "team_name": f"TEST_Predict_{os.urandom(4).hex()}"
        })
        
        # Now set to 'open' and try to predict
        set_contest_status(mongo_client, TEST_CONTEST_ID, "open")
        
        # Get questions to get valid question IDs
        q_response = api_client.get(f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/questions")
        if q_response.status_code != 200:
            pytest.skip("Could not get questions")
        
        questions = q_response.json().get("questions", [])
        if not questions:
            pytest.skip("No questions in contest")
        
        predictions = [{"question_id": q["id"], "selected_option": "A"} for q in questions[:3]]
        
        response = api_client.post(f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/predict", json={
            "predictions": predictions
        })
        
        # Should be rejected with 400
        assert response.status_code == 400, f"Expected 400 for open contest, got {response.status_code}: {response.text}"
        data = response.json()
        # Hindi message: "Contest participation band ho chuki hai..."
        print(f"✓ PREDICT rejected for 'open' status: {data.get('detail')}")

    def test_predict_allows_when_status_live(self, api_client, mongo_client):
        """POST /api/contests/{id}/predict should ALLOW when contest status is 'live'"""
        # Set contest to 'live' status
        set_contest_status(mongo_client, TEST_CONTEST_ID, "live")
        
        # Ensure user has joined
        api_client.post(f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/join", json={
            "team_name": f"TEST_Predict_Live_{os.urandom(4).hex()}"
        })
        
        # Get questions
        q_response = api_client.get(f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/questions")
        if q_response.status_code != 200:
            pytest.skip("Could not get questions")
        
        questions = q_response.json().get("questions", [])
        if not questions:
            pytest.skip("No questions in contest")
        
        predictions = [{"question_id": q["id"], "selected_option": "B"} for q in questions[:3]]
        
        response = api_client.post(f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/predict", json={
            "predictions": predictions
        })
        
        # Should be allowed (200) or forbidden if not joined (403)
        assert response.status_code in [200, 403], f"Expected 200/403 for live contest, got {response.status_code}: {response.text}"
        
        if response.status_code == 200:
            print(f"✓ PREDICT allowed for 'live' status: {response.json().get('message')}")
        else:
            print(f"✓ PREDICT would be allowed for 'live' status (403 = not joined)")

    def test_predict_rejects_when_status_completed(self, api_client, mongo_client):
        """POST /api/contests/{id}/predict should REJECT when contest status is 'completed'"""
        # Set contest to 'completed' status
        set_contest_status(mongo_client, TEST_CONTEST_ID, "completed")
        
        # Get questions
        q_response = api_client.get(f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/questions")
        if q_response.status_code != 200:
            pytest.skip("Could not get questions")
        
        questions = q_response.json().get("questions", [])
        if not questions:
            pytest.skip("No questions in contest")
        
        predictions = [{"question_id": q["id"], "selected_option": "C"} for q in questions[:3]]
        
        response = api_client.post(f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/predict", json={
            "predictions": predictions
        })
        
        # Should be rejected with 400
        assert response.status_code == 400, f"Expected 400 for completed contest, got {response.status_code}: {response.text}"
        print(f"✓ PREDICT rejected for 'completed' status: {response.json().get('detail')}")

    # ==================== GET QUESTIONS TESTS ====================

    def test_get_questions_returns_is_locked_true_when_open(self, api_client, mongo_client):
        """GET /api/contests/{id}/questions should return is_locked:true when status is 'open'"""
        set_contest_status(mongo_client, TEST_CONTEST_ID, "open")
        
        response = api_client.get(f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/questions")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "is_locked" in data, "Response should contain 'is_locked' field"
        assert "contest_status" in data, "Response should contain 'contest_status' field"
        
        assert data["is_locked"] == True, f"Expected is_locked=True for 'open' status, got {data['is_locked']}"
        assert data["contest_status"] == "open", f"Expected contest_status='open', got {data['contest_status']}"
        
        print(f"✓ GET questions returns is_locked=True, contest_status='open' for 'open' status")

    def test_get_questions_returns_is_locked_false_when_live(self, api_client, mongo_client):
        """GET /api/contests/{id}/questions should return is_locked:false when status is 'live'"""
        set_contest_status(mongo_client, TEST_CONTEST_ID, "live")
        
        response = api_client.get(f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/questions")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "is_locked" in data, "Response should contain 'is_locked' field"
        assert "contest_status" in data, "Response should contain 'contest_status' field"
        
        assert data["is_locked"] == False, f"Expected is_locked=False for 'live' status, got {data['is_locked']}"
        assert data["contest_status"] == "live", f"Expected contest_status='live', got {data['contest_status']}"
        
        print(f"✓ GET questions returns is_locked=False, contest_status='live' for 'live' status")

    def test_get_questions_returns_is_locked_true_when_completed(self, api_client, mongo_client):
        """GET /api/contests/{id}/questions should return is_locked:true when status is 'completed'"""
        set_contest_status(mongo_client, TEST_CONTEST_ID, "completed")
        
        response = api_client.get(f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/questions")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["is_locked"] == True, f"Expected is_locked=True for 'completed' status, got {data['is_locked']}"
        assert data["contest_status"] == "completed", f"Expected contest_status='completed', got {data['contest_status']}"
        
        print(f"✓ GET questions returns is_locked=True, contest_status='completed' for 'completed' status")

    # ==================== LEADERBOARD TESTS ====================

    def test_leaderboard_accessible_when_open(self, api_client, mongo_client):
        """GET /api/contests/{id}/leaderboard should be accessible when status is 'open'"""
        set_contest_status(mongo_client, TEST_CONTEST_ID, "open")
        
        response = api_client.get(f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/leaderboard")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "leaderboard" in data, "Response should contain 'leaderboard' field"
        print(f"✓ Leaderboard accessible for 'open' status with {len(data.get('leaderboard', []))} entries")

    def test_user_answers_accessible_when_open(self, api_client, mongo_client):
        """GET /api/contests/{id}/leaderboard/{user_id} should be accessible when status is 'open'"""
        set_contest_status(mongo_client, TEST_CONTEST_ID, "open")
        
        # First get leaderboard to find a user_id
        lb_response = api_client.get(f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/leaderboard")
        if lb_response.status_code != 200:
            pytest.skip("Could not get leaderboard")
        
        leaderboard = lb_response.json().get("leaderboard", [])
        if not leaderboard:
            pytest.skip("No entries in leaderboard")
        
        user_id = leaderboard[0]["user_id"]
        
        response = api_client.get(f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/leaderboard/{user_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "predictions" in data, "Response should contain 'predictions' field"
        assert "username" in data, "Response should contain 'username' field"
        print(f"✓ User answers accessible for 'open' status: {data.get('username')} with {len(data.get('predictions', []))} predictions")


class TestContestStatusCleanup:
    """Cleanup: Restore contest to 'open' status after tests"""

    def test_restore_contest_status(self, mongo_client):
        """Restore contest to 'open' status after all tests"""
        result = set_contest_status(mongo_client, TEST_CONTEST_ID, "open")
        assert result, "Failed to restore contest status"
        
        # Verify
        contest = mongo_client.contests.find_one({"id": TEST_CONTEST_ID})
        assert contest["status"] == "open", f"Contest status not restored, got {contest['status']}"
        print(f"✓ Contest status restored to 'open'")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
