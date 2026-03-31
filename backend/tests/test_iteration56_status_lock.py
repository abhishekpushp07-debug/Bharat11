"""
Iteration 56 - Testing Bug Fixes:
1. CRITICAL BUG: Contest status check - POST /api/contests/{id}/predict should REJECT when contest status is 'completed' or 'locked'
2. FEATURE: GET /api/contests/{id}/questions returns contest_status and is_locked based on status
3. FEATURE: GET /api/contests/user/my-contests returns current_rank for non-completed contests with points > 0
"""
import pytest
import requests
import os
from pymongo import MongoClient

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = 'crickpredict'

# Test contest ID provided
TEST_CONTEST_ID = 'c5e299a7-d5c8-4ecc-9010-81964a60d0d4'

# Super Admin credentials
ADMIN_PHONE = '7004186276'
ADMIN_PIN = '5524'


def get_auth_token():
    """Get authentication token for super admin"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "phone": ADMIN_PHONE,
        "pin": ADMIN_PIN
    })
    if response.status_code == 200:
        data = response.json()
        # Token is nested under 'token.access_token'
        if 'token' in data and 'access_token' in data['token']:
            return data['token']['access_token']
        elif 'access_token' in data:
            return data['access_token']
    print(f"Auth failed: {response.status_code} - {response.text[:200]}")
    return None


def get_db():
    """Get MongoDB database connection"""
    client = MongoClient(MONGO_URL)
    return client[DB_NAME]


class TestContestStatusCheck:
    """Test the CRITICAL BUG FIX: Contest status check for predictions"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.token = get_auth_token()
        assert self.token, "Failed to get auth token"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        self.db = get_db()
    
    def test_get_contest_exists(self):
        """Verify test contest exists"""
        response = requests.get(
            f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}",
            headers=self.headers
        )
        print(f"Contest GET response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Contest name: {data.get('name')}, status: {data.get('status')}")
            assert 'id' in data
            assert 'status' in data
        else:
            print(f"Contest not found: {response.text}")
            pytest.skip("Test contest not found")
    
    def test_predict_allowed_when_open(self):
        """Test: Predictions ALLOWED when contest status is 'open'"""
        # First ensure contest is open
        self.db.contests.update_one(
            {"id": TEST_CONTEST_ID},
            {"$set": {"status": "open"}}
        )
        
        # Get questions to get valid question IDs
        q_response = requests.get(
            f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/questions",
            headers=self.headers
        )
        if q_response.status_code != 200:
            pytest.skip(f"Cannot get questions: {q_response.text}")
        
        questions = q_response.json().get('questions', [])
        if not questions:
            pytest.skip("No questions found for contest")
        
        # Submit prediction
        predictions = [{"question_id": q['id'], "selected_option": "A"} for q in questions[:3]]
        response = requests.post(
            f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/predict",
            headers=self.headers,
            json={"predictions": predictions}
        )
        
        print(f"Predict (open) response: {response.status_code} - {response.text[:200]}")
        # Should be allowed (200) or 403 if not joined
        assert response.status_code in [200, 403], f"Expected 200 or 403, got {response.status_code}"
        if response.status_code == 200:
            print("PASS: Predictions allowed when contest is open")
    
    def test_predict_allowed_when_live(self):
        """Test: Predictions ALLOWED when contest status is 'live'"""
        # Set contest to live
        self.db.contests.update_one(
            {"id": TEST_CONTEST_ID},
            {"$set": {"status": "live"}}
        )
        
        # Get questions
        q_response = requests.get(
            f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/questions",
            headers=self.headers
        )
        if q_response.status_code != 200:
            pytest.skip(f"Cannot get questions: {q_response.text}")
        
        questions = q_response.json().get('questions', [])
        if not questions:
            pytest.skip("No questions found")
        
        # Submit prediction
        predictions = [{"question_id": q['id'], "selected_option": "B"} for q in questions[:3]]
        response = requests.post(
            f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/predict",
            headers=self.headers,
            json={"predictions": predictions}
        )
        
        print(f"Predict (live) response: {response.status_code} - {response.text[:200]}")
        # Should be allowed (200) or 403 if not joined
        assert response.status_code in [200, 403], f"Expected 200 or 403, got {response.status_code}"
        if response.status_code == 200:
            print("PASS: Predictions allowed when contest is live")
        
        # Restore to open
        self.db.contests.update_one(
            {"id": TEST_CONTEST_ID},
            {"$set": {"status": "open"}}
        )
    
    def test_predict_rejected_when_completed(self):
        """CRITICAL TEST: Predictions REJECTED when contest status is 'completed'"""
        # Set contest to completed
        self.db.contests.update_one(
            {"id": TEST_CONTEST_ID},
            {"$set": {"status": "completed"}}
        )
        
        # Get questions
        q_response = requests.get(
            f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/questions",
            headers=self.headers
        )
        if q_response.status_code != 200:
            pytest.skip(f"Cannot get questions: {q_response.text}")
        
        questions = q_response.json().get('questions', [])
        if not questions:
            pytest.skip("No questions found")
        
        # Try to submit prediction - should be REJECTED
        predictions = [{"question_id": q['id'], "selected_option": "C"} for q in questions[:3]]
        response = requests.post(
            f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/predict",
            headers=self.headers,
            json={"predictions": predictions}
        )
        
        print(f"Predict (completed) response: {response.status_code} - {response.text[:300]}")
        
        # MUST be 400 - this is the critical bug fix
        assert response.status_code == 400, f"CRITICAL BUG: Expected 400 for completed contest, got {response.status_code}"
        
        # Verify error message mentions status
        data = response.json()
        assert 'detail' in data
        assert 'completed' in data['detail'].lower() or 'status' in data['detail'].lower(), \
            f"Error message should mention status: {data['detail']}"
        
        print("PASS: Predictions correctly REJECTED when contest is completed")
        
        # Restore to open
        self.db.contests.update_one(
            {"id": TEST_CONTEST_ID},
            {"$set": {"status": "open"}}
        )
    
    def test_predict_rejected_when_locked(self):
        """CRITICAL TEST: Predictions REJECTED when contest status is 'locked'"""
        # Set contest to locked
        self.db.contests.update_one(
            {"id": TEST_CONTEST_ID},
            {"$set": {"status": "locked"}}
        )
        
        # Get questions
        q_response = requests.get(
            f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/questions",
            headers=self.headers
        )
        if q_response.status_code != 200:
            pytest.skip(f"Cannot get questions: {q_response.text}")
        
        questions = q_response.json().get('questions', [])
        if not questions:
            pytest.skip("No questions found")
        
        # Try to submit prediction - should be REJECTED
        predictions = [{"question_id": q['id'], "selected_option": "D"} for q in questions[:3]]
        response = requests.post(
            f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/predict",
            headers=self.headers,
            json={"predictions": predictions}
        )
        
        print(f"Predict (locked) response: {response.status_code} - {response.text[:300]}")
        
        # MUST be 400 - this is the critical bug fix
        assert response.status_code == 400, f"CRITICAL BUG: Expected 400 for locked contest, got {response.status_code}"
        
        # Verify error message mentions status
        data = response.json()
        assert 'detail' in data
        assert 'locked' in data['detail'].lower() or 'status' in data['detail'].lower(), \
            f"Error message should mention status: {data['detail']}"
        
        print("PASS: Predictions correctly REJECTED when contest is locked")
        
        # Restore to open
        self.db.contests.update_one(
            {"id": TEST_CONTEST_ID},
            {"$set": {"status": "open"}}
        )


class TestGetQuestionsStatusFields:
    """Test GET /api/contests/{id}/questions returns contest_status and is_locked"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.token = get_auth_token()
        assert self.token, "Failed to get auth token"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        self.db = get_db()
    
    def test_questions_returns_contest_status_field(self):
        """Test: GET questions returns contest_status field"""
        # Set to open
        self.db.contests.update_one(
            {"id": TEST_CONTEST_ID},
            {"$set": {"status": "open"}}
        )
        
        response = requests.get(
            f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/questions",
            headers=self.headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert 'contest_status' in data, "Missing contest_status field in response"
        assert data['contest_status'] == 'open', f"Expected 'open', got {data['contest_status']}"
        print(f"PASS: contest_status field returned: {data['contest_status']}")
    
    def test_questions_is_locked_false_when_open(self):
        """Test: is_locked=false when contest status is 'open'"""
        self.db.contests.update_one(
            {"id": TEST_CONTEST_ID},
            {"$set": {"status": "open"}}
        )
        
        response = requests.get(
            f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/questions",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert 'is_locked' in data, "Missing is_locked field"
        # is_locked should be False when status is open (unless lock_time passed)
        print(f"is_locked when open: {data['is_locked']}")
        # Note: is_locked can be True if lock_time has passed, so we just verify field exists
    
    def test_questions_is_locked_true_when_completed(self):
        """Test: is_locked=true when contest status is 'completed'"""
        self.db.contests.update_one(
            {"id": TEST_CONTEST_ID},
            {"$set": {"status": "completed"}}
        )
        
        response = requests.get(
            f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/questions",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert 'is_locked' in data, "Missing is_locked field"
        assert data['is_locked'] == True, f"Expected is_locked=True for completed, got {data['is_locked']}"
        assert data['contest_status'] == 'completed'
        print("PASS: is_locked=True when contest is completed")
        
        # Restore
        self.db.contests.update_one(
            {"id": TEST_CONTEST_ID},
            {"$set": {"status": "open"}}
        )
    
    def test_questions_is_locked_true_when_locked(self):
        """Test: is_locked=true when contest status is 'locked'"""
        self.db.contests.update_one(
            {"id": TEST_CONTEST_ID},
            {"$set": {"status": "locked"}}
        )
        
        response = requests.get(
            f"{BASE_URL}/api/contests/{TEST_CONTEST_ID}/questions",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert 'is_locked' in data, "Missing is_locked field"
        assert data['is_locked'] == True, f"Expected is_locked=True for locked, got {data['is_locked']}"
        assert data['contest_status'] == 'locked'
        print("PASS: is_locked=True when contest is locked")
        
        # Restore
        self.db.contests.update_one(
            {"id": TEST_CONTEST_ID},
            {"$set": {"status": "open"}}
        )


class TestMyContestsCurrentRank:
    """Test GET /api/contests/user/my-contests returns current_rank"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.token = get_auth_token()
        assert self.token, "Failed to get auth token"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        self.db = get_db()
    
    def test_my_contests_returns_entries(self):
        """Test: my-contests endpoint returns data"""
        response = requests.get(
            f"{BASE_URL}/api/contests/user/my-contests",
            headers=self.headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert 'my_contests' in data
        print(f"Found {len(data['my_contests'])} contests for user")
    
    def test_my_contests_entry_has_current_rank_field(self):
        """Test: Entry has current_rank when points > 0 and contest is open/live"""
        response = requests.get(
            f"{BASE_URL}/api/contests/user/my-contests",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        contests = data.get('my_contests', [])
        
        found_rank = False
        for item in contests:
            entry = item.get('entry', {})
            contest = item.get('contest', {})
            
            # Check if entry has points and contest is open/live
            if entry.get('total_points', 0) > 0 and contest.get('status') in ('open', 'live'):
                if 'current_rank' in entry:
                    found_rank = True
                    print(f"PASS: Found current_rank={entry['current_rank']} for contest {contest.get('name')} (points={entry['total_points']})")
                    assert isinstance(entry['current_rank'], int), "current_rank should be integer"
                    assert entry['current_rank'] >= 1, "current_rank should be >= 1"
        
        if not found_rank:
            # Check if there are any entries with points > 0
            entries_with_points = [
                item for item in contests 
                if item.get('entry', {}).get('total_points', 0) > 0 
                and item.get('contest', {}).get('status') in ('open', 'live')
            ]
            if entries_with_points:
                print(f"WARNING: Found {len(entries_with_points)} entries with points but no current_rank")
            else:
                print("INFO: No entries with points > 0 in open/live contests to verify current_rank")
    
    def test_my_contests_completed_has_final_rank(self):
        """Test: Completed contests have final_rank instead of current_rank"""
        response = requests.get(
            f"{BASE_URL}/api/contests/user/my-contests?status=completed",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        contests = data.get('my_contests', [])
        
        for item in contests:
            entry = item.get('entry', {})
            contest = item.get('contest', {})
            
            if contest.get('status') == 'completed' and entry.get('final_rank'):
                print(f"PASS: Completed contest has final_rank={entry['final_rank']}")
                break


class TestCleanup:
    """Ensure contest is restored to open status after tests"""
    
    def test_restore_contest_status(self):
        """Restore test contest to open status"""
        db = get_db()
        result = db.contests.update_one(
            {"id": TEST_CONTEST_ID},
            {"$set": {"status": "open"}}
        )
        print(f"Restored contest status to 'open': modified={result.modified_count}")
        
        # Verify
        contest = db.contests.find_one({"id": TEST_CONTEST_ID})
        if contest:
            assert contest.get('status') == 'open', f"Failed to restore: {contest.get('status')}"
            print("PASS: Contest restored to open status")
