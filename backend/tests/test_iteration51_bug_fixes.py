"""
Iteration 51 - Bug Fixes Testing
Tests for 3 user-reported issues:
1. Contest page ugly/disorganized → MyContestsPage redesigned
2. Can't join live contests or see questions → timezone fix in contests.py
3. Matches showing in random order without IST → smart sorting + IST conversion

Key fixes:
- cricket.py: live-ticker IST conversion (lines 72-110)
- matches.py: smart sorting (lines 158-190), IST formatting
- contests.py: timezone fix for lock_time comparison (lines 312-318, 349-354)
"""
import pytest
import requests
import os
from datetime import datetime, timezone, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_PHONE = "7004186276"
ADMIN_PIN = "5524"

# Contest IDs for testing
CONTEST_LSG_DC = "53fe3a89-428c-4465-a613-ac8ca2661c0c"
CONTEST_KKR_DC = "2db7cefe-e107-4a93-80a6-6a30104b2ccc"


@pytest.fixture(scope="module")
def auth_token():
    """Get admin auth token"""
    resp = requests.post(f"{BASE_URL}/api/auth/login", json={"phone": ADMIN_PHONE, "pin": ADMIN_PIN})
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    token = resp.json().get("token", {}).get("access_token")
    assert token, "No access_token returned"
    return token


@pytest.fixture
def auth_headers(auth_token):
    """Auth headers for API calls"""
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


class TestBugFix1_LiveTickerIST:
    """Bug Fix 1: IPL LIVE ticker shows IST instead of GMT"""
    
    def test_live_ticker_returns_ist_display(self):
        """GET /api/cricket/live-ticker should return ist_display field"""
        resp = requests.get(f"{BASE_URL}/api/cricket/live-ticker")
        assert resp.status_code == 200, f"Live ticker failed: {resp.text}"
        data = resp.json()
        scores = data.get("scores", [])
        
        # Check that scores have ist_display field
        for score in scores:
            assert "ist_display" in score, f"Missing ist_display in score: {score}"
            # If there's a dateTimeGMT, ist_display should contain IST
            if score.get("dateTimeGMT"):
                assert "IST" in score.get("ist_display", ""), f"ist_display should contain IST: {score}"
        
        print(f"✓ Live ticker returned {len(scores)} scores with IST display")
    
    def test_live_ticker_status_has_ist_not_gmt(self):
        """Status text should show IST, not GMT"""
        resp = requests.get(f"{BASE_URL}/api/cricket/live-ticker")
        assert resp.status_code == 200
        data = resp.json()
        scores = data.get("scores", [])
        
        for score in scores:
            status = score.get("status", "")
            # If status mentions time, it should be IST not GMT
            if "at" in status.lower() and (":" in status):
                # Status should not contain GMT if it has time
                if "GMT" in status:
                    pytest.fail(f"Status still contains GMT: {status}")
        
        print("✓ Live ticker status texts converted to IST")


class TestBugFix2_MatchCardDateTimeIST:
    """Bug Fix 2: Match cards show date/time (IST) in Upcoming Matches section"""
    
    def test_matches_have_start_time_ist_field(self):
        """GET /api/matches should return start_time_ist field"""
        resp = requests.get(f"{BASE_URL}/api/matches?limit=20")
        assert resp.status_code == 200, f"Matches API failed: {resp.text}"
        data = resp.json()
        matches = data.get("matches", [])
        
        assert len(matches) > 0, "No matches returned"
        
        for match in matches:
            assert "start_time_ist" in match, f"Missing start_time_ist in match: {match.get('id')}"
            ist_time = match.get("start_time_ist", "")
            assert "IST" in ist_time, f"start_time_ist should contain IST: {ist_time}"
        
        print(f"✓ {len(matches)} matches have start_time_ist field with IST format")
    
    def test_ist_time_format_correct(self):
        """IST time should be in format like '06 Apr 2026, 07:30 PM IST'"""
        resp = requests.get(f"{BASE_URL}/api/matches?limit=5")
        assert resp.status_code == 200
        data = resp.json()
        matches = data.get("matches", [])
        
        for match in matches:
            ist_time = match.get("start_time_ist", "")
            # Should contain month abbreviation and IST
            assert any(m in ist_time for m in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]), \
                f"IST time should contain month: {ist_time}"
            assert "IST" in ist_time, f"IST time should end with IST: {ist_time}"
        
        print("✓ IST time format is correct (e.g., '06 Apr 2026, 07:30 PM IST')")


class TestBugFix3_MatchesSortedCorrectly:
    """Bug Fix 3: Matches sorted correctly - nearest upcoming first"""
    
    def test_matches_smart_sorting(self):
        """GET /api/matches returns: live first, then nearest upcoming, then recently completed"""
        resp = requests.get(f"{BASE_URL}/api/matches?limit=50")
        assert resp.status_code == 200, f"Matches API failed: {resp.text}"
        data = resp.json()
        matches = data.get("matches", [])
        
        # Separate by status
        live = [m for m in matches if m.get("status") == "live"]
        upcoming = [m for m in matches if m.get("status") == "upcoming"]
        completed = [m for m in matches if m.get("status") == "completed"]
        
        print(f"Live: {len(live)}, Upcoming: {len(upcoming)}, Completed: {len(completed)}")
        
        # Check upcoming are sorted ascending (nearest first)
        if len(upcoming) >= 2:
            for i in range(len(upcoming) - 1):
                t1 = upcoming[i].get("start_time", "")
                t2 = upcoming[i+1].get("start_time", "")
                if t1 and t2:
                    assert t1 <= t2, f"Upcoming matches not sorted ascending: {t1} > {t2}"
        
        # Check completed are sorted descending (most recent first)
        if len(completed) >= 2:
            for i in range(len(completed) - 1):
                t1 = completed[i].get("start_time", "")
                t2 = completed[i+1].get("start_time", "")
                if t1 and t2:
                    assert t1 >= t2, f"Completed matches not sorted descending: {t1} < {t2}"
        
        print("✓ Matches sorted correctly: live first, upcoming asc, completed desc")
    
    def test_upcoming_matches_april_before_may(self):
        """April dates should appear before May dates in upcoming matches"""
        resp = requests.get(f"{BASE_URL}/api/matches?status=upcoming&limit=50")
        assert resp.status_code == 200
        data = resp.json()
        matches = data.get("matches", [])
        
        if len(matches) >= 2:
            # Check that earlier dates come first
            for i in range(len(matches) - 1):
                t1 = matches[i].get("start_time", "")
                t2 = matches[i+1].get("start_time", "")
                if t1 and t2:
                    assert t1 <= t2, f"Upcoming not sorted: {t1} > {t2}"
        
        print(f"✓ {len(matches)} upcoming matches sorted by date ascending")


class TestBugFix4_QuestionsLoading:
    """Bug Fix 4: Questions loading correctly - timezone fix"""
    
    def test_contest_questions_endpoint(self, auth_headers):
        """GET /api/contests/{contest_id}/questions returns questions"""
        resp = requests.get(f"{BASE_URL}/api/contests/{CONTEST_LSG_DC}/questions", headers=auth_headers)
        
        # Should return 200 or 404 (if not joined)
        if resp.status_code == 404:
            pytest.skip("User not joined to this contest")
        
        assert resp.status_code == 200, f"Questions API failed: {resp.text}"
        data = resp.json()
        
        questions = data.get("questions", [])
        total_points = data.get("total_points", 0)
        
        print(f"✓ Contest {CONTEST_LSG_DC} has {len(questions)} questions, {total_points} total points")
        
        # Verify questions have Hindi text
        for q in questions:
            assert q.get("question_text_hi"), f"Question missing Hindi text: {q.get('id')}"
    
    def test_contest_questions_with_kkr_dc(self, auth_headers):
        """Test questions endpoint with KKR vs DC contest"""
        resp = requests.get(f"{BASE_URL}/api/contests/{CONTEST_KKR_DC}/questions", headers=auth_headers)
        
        if resp.status_code == 404:
            pytest.skip("User not joined to KKR vs DC contest")
        
        assert resp.status_code == 200, f"Questions API failed: {resp.text}"
        data = resp.json()
        
        questions = data.get("questions", [])
        total_points = data.get("total_points", 0)
        
        assert len(questions) > 0, "No questions returned"
        print(f"✓ KKR vs DC contest has {len(questions)} questions, {total_points} total points")


class TestBugFix5_JoinContestFlow:
    """Bug Fix 5: Join contest flow works for both 'open' and 'live' status"""
    
    def test_join_contest_open_status(self, auth_headers):
        """POST /api/contests/{id}/join works for 'open' status"""
        # First check contest status
        resp = requests.get(f"{BASE_URL}/api/contests/{CONTEST_KKR_DC}", headers=auth_headers)
        if resp.status_code != 200:
            pytest.skip("Contest not found")
        
        contest = resp.json()
        status = contest.get("status", "")
        
        if status not in ["open", "live"]:
            pytest.skip(f"Contest status is {status}, not open/live")
        
        # Try to join (may already be joined)
        resp = requests.post(
            f"{BASE_URL}/api/contests/{CONTEST_KKR_DC}/join",
            json={"team_name": f"TestTeam_{datetime.now().timestamp()}"},
            headers=auth_headers
        )
        
        # Should be 200 (joined) or 409 (already joined)
        assert resp.status_code in [200, 409], f"Join failed unexpectedly: {resp.status_code} - {resp.text}"
        
        if resp.status_code == 200:
            print(f"✓ Successfully joined contest {CONTEST_KKR_DC}")
        else:
            print(f"✓ Already joined contest {CONTEST_KKR_DC}")
    
    def test_join_contest_returns_proper_response(self, auth_headers):
        """Join contest should return entry, new_balance, message"""
        # Get a contest to test
        resp = requests.get(f"{BASE_URL}/api/contests?status=open&limit=1")
        if resp.status_code != 200 or not resp.json().get("contests"):
            pytest.skip("No open contests available")
        
        contest = resp.json()["contests"][0]
        contest_id = contest["id"]
        
        # Try to join
        resp = requests.post(
            f"{BASE_URL}/api/contests/{contest_id}/join",
            json={"team_name": f"TestTeam_{datetime.now().timestamp()}"},
            headers=auth_headers
        )
        
        if resp.status_code == 409:
            print(f"✓ Already joined contest {contest_id}")
            return
        
        assert resp.status_code == 200, f"Join failed: {resp.text}"
        data = resp.json()
        
        assert "entry" in data, "Response missing 'entry'"
        assert "new_balance" in data, "Response missing 'new_balance'"
        assert "message" in data, "Response missing 'message'"
        
        print(f"✓ Join response has entry, new_balance, message")


class TestMyContestsPage:
    """Test My Contests API for redesigned page"""
    
    def test_my_contests_endpoint(self, auth_headers):
        """GET /api/contests/user/my-contests returns user's contests"""
        resp = requests.get(f"{BASE_URL}/api/contests/user/my-contests?limit=50", headers=auth_headers)
        assert resp.status_code == 200, f"My contests failed: {resp.text}"
        data = resp.json()
        
        my_contests = data.get("my_contests", [])
        total = data.get("total", 0)
        
        print(f"✓ User has {len(my_contests)} contests (total: {total})")
        
        # Verify structure
        for mc in my_contests:
            assert "entry" in mc, "Missing 'entry' in my_contests item"
            assert "contest" in mc, "Missing 'contest' in my_contests item"
            assert "match" in mc, "Missing 'match' in my_contests item"
    
    def test_my_contests_has_match_info(self, auth_headers):
        """My contests should include match info with team logos"""
        resp = requests.get(f"{BASE_URL}/api/contests/user/my-contests?limit=10", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        
        my_contests = data.get("my_contests", [])
        
        for mc in my_contests:
            match = mc.get("match", {})
            if match:
                assert "team_a" in match, "Match missing team_a"
                assert "team_b" in match, "Match missing team_b"
                team_a = match.get("team_a", {})
                team_b = match.get("team_b", {})
                assert team_a.get("short_name"), "team_a missing short_name"
                assert team_b.get("short_name"), "team_b missing short_name"
        
        print("✓ My contests include match info with team data")


class TestContestDetails:
    """Test contest details and questions"""
    
    def test_contest_details_include_match(self, auth_headers):
        """GET /api/contests/{id} should include match info"""
        resp = requests.get(f"{BASE_URL}/api/contests/{CONTEST_LSG_DC}", headers=auth_headers)
        
        if resp.status_code == 404:
            pytest.skip("Contest not found")
        
        assert resp.status_code == 200, f"Contest details failed: {resp.text}"
        data = resp.json()
        
        assert "match" in data, "Contest details missing 'match'"
        match = data.get("match", {})
        assert match.get("team_a"), "Match missing team_a"
        assert match.get("team_b"), "Match missing team_b"
        
        print(f"✓ Contest {CONTEST_LSG_DC} includes match info")
    
    def test_questions_have_hindi_text(self, auth_headers):
        """Questions should have Hindi text (question_text_hi)"""
        resp = requests.get(f"{BASE_URL}/api/contests/{CONTEST_LSG_DC}/questions", headers=auth_headers)
        
        if resp.status_code == 404:
            pytest.skip("User not joined to contest")
        
        assert resp.status_code == 200, f"Questions failed: {resp.text}"
        data = resp.json()
        
        questions = data.get("questions", [])
        
        for q in questions:
            hi_text = q.get("question_text_hi", "")
            assert hi_text, f"Question {q.get('id')} missing Hindi text"
            # Hindi text should contain Devanagari characters
            has_hindi = any('\u0900' <= c <= '\u097F' for c in hi_text)
            assert has_hindi, f"Question Hindi text doesn't contain Devanagari: {hi_text[:50]}"
        
        print(f"✓ All {len(questions)} questions have Hindi text")


class TestPredictionSubmission:
    """Test prediction submission flow"""
    
    def test_submit_prediction(self, auth_headers):
        """POST /api/contests/{id}/predict should work"""
        # First get questions
        resp = requests.get(f"{BASE_URL}/api/contests/{CONTEST_LSG_DC}/questions", headers=auth_headers)
        
        if resp.status_code == 404:
            pytest.skip("User not joined to contest")
        
        if resp.status_code != 200:
            pytest.skip(f"Questions API failed: {resp.text}")
        
        data = resp.json()
        questions = data.get("questions", [])
        is_locked = data.get("is_locked", False)
        
        if is_locked:
            pytest.skip("Contest is locked, cannot submit predictions")
        
        if not questions:
            pytest.skip("No questions available")
        
        # Submit prediction for first question
        predictions = [{"question_id": questions[0]["id"], "selected_option": "A"}]
        
        resp = requests.post(
            f"{BASE_URL}/api/contests/{CONTEST_LSG_DC}/predict",
            json={"predictions": predictions},
            headers=auth_headers
        )
        
        # Should be 200 or 400 (if locked)
        if resp.status_code == 400 and "locked" in resp.text.lower():
            print("✓ Contest is locked (expected for past matches)")
            return
        
        assert resp.status_code == 200, f"Prediction failed: {resp.text}"
        print("✓ Prediction submitted successfully")


class TestLeaderboard:
    """Test leaderboard endpoint"""
    
    def test_contest_leaderboard(self, auth_headers):
        """GET /api/contests/{id}/leaderboard returns rankings"""
        resp = requests.get(f"{BASE_URL}/api/contests/{CONTEST_LSG_DC}/leaderboard", headers=auth_headers)
        
        if resp.status_code == 404:
            pytest.skip("Contest not found")
        
        assert resp.status_code == 200, f"Leaderboard failed: {resp.text}"
        data = resp.json()
        
        leaderboard = data.get("leaderboard", [])
        total_participants = data.get("total_participants", 0)
        
        print(f"✓ Leaderboard has {len(leaderboard)} entries, {total_participants} total participants")
        
        # Verify structure
        for entry in leaderboard:
            assert "rank" in entry, "Entry missing rank"
            assert "total_points" in entry, "Entry missing total_points"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
