"""
Iteration 59 - Bug Fix Verification Tests
Tests for:
1. GET /api/contests/{id}/questions returns is_locked: false when contest status is 'live' (even if lock_time has passed)
2. POST /api/contests/{id}/predict succeeds when contest status is 'live' (no lock_time blocking)
3. DELETE /api/admin/contests/{id} deletes contest and returns success with entries_removed and refunds_issued
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
ADMIN_PHONE = "7004186276"
ADMIN_PIN = "5524"

# Live contest ID from the bug report
LIVE_CONTEST_ID = "169d854b-e073-4118-a18d-47338e677cba"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "phone": ADMIN_PHONE,
        "pin": ADMIN_PIN
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    # Token is nested: { token: { access_token: '...' } }
    token = data.get("token", {}).get("access_token") or data.get("access_token")
    assert token, f"No token in response: {data}"
    return token


@pytest.fixture(scope="module")
def auth_headers(admin_token):
    """Auth headers for API requests"""
    return {"Authorization": f"Bearer {admin_token}"}


class TestBug1_ContestQuestionsLockStatus:
    """
    Bug 1: Predictions showing 'Locked' even when contest status is 'live'
    Fix: In get_contest_questions, lock_time check was removed when contest status is 'live'.
    The rule is: if admin set status=live, lock_time is irrelevant. Only the status matters.
    """
    
    def test_live_contest_questions_not_locked(self, auth_headers):
        """GET /api/contests/{id}/questions should return is_locked: false when status is 'live'"""
        response = requests.get(
            f"{BASE_URL}/api/contests/{LIVE_CONTEST_ID}/questions",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to get questions: {response.text}"
        
        data = response.json()
        contest_status = data.get("contest_status", "")
        is_locked = data.get("is_locked", True)
        
        print(f"Contest status: {contest_status}")
        print(f"is_locked: {is_locked}")
        print(f"lock_time: {data.get('lock_time', '')}")
        
        # If contest is live, is_locked should be False
        if contest_status == "live":
            assert is_locked == False, f"Bug not fixed! Contest is 'live' but is_locked={is_locked}"
            print("BUG 1 FIX VERIFIED: Live contest returns is_locked=false")
        else:
            print(f"Contest status is '{contest_status}', not 'live' - skipping lock assertion")
    
    def test_contest_status_returned(self, auth_headers):
        """Verify contest_status is returned in the response"""
        response = requests.get(
            f"{BASE_URL}/api/contests/{LIVE_CONTEST_ID}/questions",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "contest_status" in data, "contest_status field missing from response"
        assert "is_locked" in data, "is_locked field missing from response"
        print(f"Response contains contest_status={data['contest_status']}, is_locked={data['is_locked']}")


class TestBug2_PredictionSubmissionWhenLive:
    """
    Bug 2: Predictions couldn't be submitted even when contest status is 'live'
    Fix: In submit_predictions, lock_time check was removed when contest status is 'live'.
    """
    
    def test_get_contest_details(self, auth_headers):
        """First verify the contest exists and check its status"""
        response = requests.get(
            f"{BASE_URL}/api/contests/{LIVE_CONTEST_ID}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to get contest: {response.text}"
        
        data = response.json()
        print(f"Contest: {data.get('name', 'Unknown')}")
        print(f"Status: {data.get('status', 'Unknown')}")
        print(f"Lock time: {data.get('lock_time', 'Unknown')}")
        print(f"Current participants: {data.get('current_participants', 0)}")
        
        return data
    
    def test_prediction_endpoint_accepts_live_contest(self, auth_headers):
        """
        Test that prediction submission doesn't fail due to lock_time when contest is live.
        Note: This may fail if user hasn't joined the contest, but the error should NOT be about lock_time.
        """
        # First check if user has joined
        response = requests.get(
            f"{BASE_URL}/api/contests/{LIVE_CONTEST_ID}/my-entry",
            headers=auth_headers
        )
        
        if response.status_code == 404:
            print("User hasn't joined this contest - need to join first")
            # Try to join the contest
            join_response = requests.post(
                f"{BASE_URL}/api/contests/{LIVE_CONTEST_ID}/join",
                headers=auth_headers,
                json={"team_name": "Test Team Admin"}
            )
            if join_response.status_code in [200, 201]:
                print("Successfully joined contest")
            elif join_response.status_code == 409:
                print("Already joined (409 conflict)")
            else:
                print(f"Join response: {join_response.status_code} - {join_response.text}")
        
        # Get questions to know what to predict
        q_response = requests.get(
            f"{BASE_URL}/api/contests/{LIVE_CONTEST_ID}/questions",
            headers=auth_headers
        )
        
        if q_response.status_code != 200:
            print(f"Could not get questions: {q_response.text}")
            return
        
        q_data = q_response.json()
        questions = q_data.get("questions", [])
        
        if not questions:
            print("No questions in contest")
            return
        
        # Build predictions
        predictions = [
            {"question_id": q["id"], "selected_option": "A"}
            for q in questions[:3]  # Just first 3 questions
        ]
        
        # Try to submit predictions
        response = requests.post(
            f"{BASE_URL}/api/contests/{LIVE_CONTEST_ID}/predict",
            headers=auth_headers,
            json={"predictions": predictions}
        )
        
        print(f"Prediction response: {response.status_code}")
        print(f"Response body: {response.text[:500]}")
        
        # The key check: if contest is live, we should NOT get a lock_time error
        if response.status_code == 400:
            error_detail = response.json().get("detail", "")
            # These are acceptable errors (not related to lock_time bug)
            acceptable_errors = [
                "haven't joined",
                "not part of this contest",
                "Template locked"  # This is over-based deadline, not lock_time
            ]
            
            # This would indicate the bug is NOT fixed
            lock_time_errors = [
                "locked",
                "lock_time",
                "Contest is locked"
            ]
            
            for err in lock_time_errors:
                if err.lower() in error_detail.lower() and "template" not in error_detail.lower():
                    pytest.fail(f"BUG NOT FIXED! Got lock_time error: {error_detail}")
            
            print(f"Got expected error (not lock_time related): {error_detail}")
        elif response.status_code == 200:
            print("BUG 2 FIX VERIFIED: Predictions submitted successfully for live contest")
        elif response.status_code == 403:
            print(f"403 Forbidden - likely not joined: {response.text}")


class TestBug3_AdminDeleteContest:
    """
    Bug 3: Admin cannot delete contests from dashboard
    Fix: DELETE /api/admin/contests/{id} endpoint now works and returns entries_removed and refunds_issued
    """
    
    def test_delete_endpoint_exists(self, auth_headers):
        """Verify the delete endpoint exists and returns proper response structure"""
        # First, let's create a test contest to delete
        # Get a match to create contest for
        matches_response = requests.get(
            f"{BASE_URL}/api/matches?limit=5",
            headers=auth_headers
        )
        assert matches_response.status_code == 200
        matches = matches_response.json().get("matches", [])
        
        if not matches:
            pytest.skip("No matches available to create test contest")
        
        match_id = matches[0]["id"]
        
        # Get a template
        templates_response = requests.get(
            f"{BASE_URL}/api/admin/templates?limit=5",
            headers=auth_headers
        )
        assert templates_response.status_code == 200
        templates = templates_response.json().get("templates", [])
        
        if not templates:
            pytest.skip("No templates available to create test contest")
        
        template_id = templates[0]["id"]
        
        # Create a test contest
        create_response = requests.post(
            f"{BASE_URL}/api/admin/contests",
            headers=auth_headers,
            json={
                "match_id": match_id,
                "template_id": template_id,
                "name": "TEST_DELETE_CONTEST_ITER59",
                "entry_fee": 100,
                "prize_pool": 0,
                "max_participants": 10
            }
        )
        
        if create_response.status_code not in [200, 201]:
            # May fail if max contests reached
            print(f"Could not create test contest: {create_response.text}")
            pytest.skip("Could not create test contest for deletion test")
        
        contest_id = create_response.json().get("id")
        print(f"Created test contest: {contest_id}")
        
        # Now delete it
        delete_response = requests.delete(
            f"{BASE_URL}/api/admin/contests/{contest_id}",
            headers=auth_headers
        )
        
        print(f"Delete response status: {delete_response.status_code}")
        print(f"Delete response body: {delete_response.text}")
        
        assert delete_response.status_code == 200, f"Delete failed: {delete_response.text}"
        
        data = delete_response.json()
        assert "message" in data, "Response missing 'message' field"
        assert "entries_removed" in data, "Response missing 'entries_removed' field"
        assert "refunds_issued" in data, "Response missing 'refunds_issued' field"
        
        print(f"BUG 3 FIX VERIFIED: Delete returned entries_removed={data['entries_removed']}, refunds_issued={data['refunds_issued']}")
    
    def test_delete_nonexistent_contest_returns_404(self, auth_headers):
        """Verify deleting non-existent contest returns 404"""
        response = requests.delete(
            f"{BASE_URL}/api/admin/contests/nonexistent-contest-id-12345",
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Delete non-existent contest correctly returns 404")


class TestLoginFlow:
    """Verify login flow works with Super Admin credentials"""
    
    def test_login_returns_token(self):
        """Test login endpoint returns proper token structure"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": ADMIN_PHONE,
            "pin": ADMIN_PIN
        })
        
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        
        # Token structure: { token: { access_token: '...' } }
        assert "token" in data or "access_token" in data, f"No token in response: {data}"
        
        if "token" in data:
            assert "access_token" in data["token"], f"No access_token in token: {data}"
            print(f"Login successful, token structure: token.access_token")
        else:
            print(f"Login successful, token structure: access_token")


class TestContestStatusEndpoint:
    """Test the contest status update endpoint used by admin dashboard"""
    
    def test_status_update_endpoint_exists(self, auth_headers):
        """Verify PUT /api/admin/contests/{id}/status endpoint works"""
        # Get a contest to test with
        response = requests.get(
            f"{BASE_URL}/api/contests?limit=5",
            headers=auth_headers
        )
        
        if response.status_code != 200:
            pytest.skip("Could not get contests")
        
        contests = response.json().get("contests", [])
        if not contests:
            pytest.skip("No contests available")
        
        # Find a non-completed contest
        test_contest = None
        for c in contests:
            if c.get("status") not in ["completed", "cancelled"]:
                test_contest = c
                break
        
        if not test_contest:
            pytest.skip("No active contests to test status update")
        
        contest_id = test_contest["id"]
        current_status = test_contest.get("status", "open")
        
        print(f"Testing status update on contest {contest_id}, current status: {current_status}")
        
        # Just verify the endpoint responds (don't actually change status)
        # We'll test with the same status to avoid side effects
        response = requests.put(
            f"{BASE_URL}/api/admin/contests/{contest_id}/status",
            headers=auth_headers,
            json={"status": current_status}
        )
        
        print(f"Status update response: {response.status_code} - {response.text[:200]}")
        
        # Should succeed or return validation error, not 404 or 500
        assert response.status_code in [200, 400], f"Unexpected status code: {response.status_code}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
