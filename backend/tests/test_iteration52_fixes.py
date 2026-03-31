"""
Iteration 52 - Bug Fixes Test Suite
Tests for:
1. Prediction submit with 16 predictions (max_length 15→50)
2. HomePage Upcoming/Completed tabs
3. Match sorting (nearest first for upcoming, recent first for completed)
4. Match cards show IST date/time
5. Contest page redesign
6. Admin Matches page separate status fetches
7. Admin Contest cards show team names
8. GET /api/matches smart sorting
9. GET /api/cricket/live-ticker IST times
"""
import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://fantasy-points.preview.emergentagent.com')

# Test credentials
ADMIN_PHONE = "7004186276"
ADMIN_PIN = "5524"


@pytest.fixture(scope="module")
def auth_token():
    """Get admin auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "phone": ADMIN_PHONE,
        "pin": ADMIN_PIN
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    token = data.get("token", {}).get("access_token", "")
    assert token, "No access token returned"
    return token


@pytest.fixture(scope="module")
def api_client(auth_token):
    """Authenticated requests session"""
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    })
    return session


class TestPredictionSubmit:
    """Fix 1: Prediction submit works with 16 predictions (was limited to 15, now 50)"""
    
    def test_get_contest_with_16_questions(self, api_client):
        """Verify contest has 16 questions"""
        # Get first available contest
        response = api_client.get(f"{BASE_URL}/api/contests?limit=5")
        assert response.status_code == 200
        contests = response.json().get("contests", [])
        assert len(contests) > 0, "No contests found"
        
        contest_id = contests[0]["id"]
        
        # Get questions
        response = api_client.get(f"{BASE_URL}/api/contests/{contest_id}/questions")
        assert response.status_code == 200
        data = response.json()
        total_questions = data.get("total_questions", 0)
        print(f"Contest {contest_id} has {total_questions} questions")
        assert total_questions == 16, f"Expected 16 questions, got {total_questions}"
    
    def test_submit_16_predictions_no_422(self, api_client):
        """Verify 16 predictions can be submitted without 422 error"""
        # Get first available contest
        response = api_client.get(f"{BASE_URL}/api/contests?limit=5")
        contests = response.json().get("contests", [])
        contest_id = contests[0]["id"]
        
        # Get questions
        response = api_client.get(f"{BASE_URL}/api/contests/{contest_id}/questions")
        questions = response.json().get("questions", [])
        
        # Build 16 predictions
        predictions = [
            {"question_id": q["id"], "selected_option": "A"}
            for q in questions[:16]
        ]
        
        # Submit predictions
        response = api_client.post(
            f"{BASE_URL}/api/contests/{contest_id}/predict",
            json={"predictions": predictions}
        )
        
        # Should NOT return 422 (validation error)
        assert response.status_code != 422, f"Got 422 error: {response.text}"
        # Should return 200 or message about already predicted
        assert response.status_code in [200, 400], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert data.get("predictions_count") == 16, "Should have 16 predictions"
            print(f"Successfully submitted 16 predictions: {data.get('message')}")


class TestMatchSorting:
    """Fix 3 & 9: Matches sorted correctly - live first, upcoming nearest first, completed recent first"""
    
    def test_matches_smart_sorting(self, api_client):
        """GET /api/matches returns smart sorted results"""
        response = api_client.get(f"{BASE_URL}/api/matches?limit=50")
        assert response.status_code == 200
        matches = response.json().get("matches", [])
        assert len(matches) > 0, "No matches found"
        
        # Check live matches come first
        live_indices = [i for i, m in enumerate(matches) if m["status"] == "live"]
        upcoming_indices = [i for i, m in enumerate(matches) if m["status"] == "upcoming"]
        completed_indices = [i for i, m in enumerate(matches) if m["status"] == "completed"]
        
        if live_indices and upcoming_indices:
            assert max(live_indices) < min(upcoming_indices), "Live matches should come before upcoming"
        
        print(f"Live: {len(live_indices)}, Upcoming: {len(upcoming_indices)}, Completed: {len(completed_indices)}")
    
    def test_upcoming_matches_sorted_nearest_first(self, api_client):
        """Upcoming matches sorted by start_time ascending (nearest first)"""
        response = api_client.get(f"{BASE_URL}/api/matches?status=upcoming&limit=20")
        assert response.status_code == 200
        matches = response.json().get("matches", [])
        
        if len(matches) >= 2:
            dates = [m.get("start_time", "") for m in matches]
            # Check ascending order
            for i in range(len(dates) - 1):
                assert dates[i] <= dates[i+1], f"Upcoming not sorted ascending: {dates[i]} > {dates[i+1]}"
            print(f"Upcoming matches sorted correctly: {dates[:3]}")
    
    def test_completed_matches_sorted_recent_first(self, api_client):
        """Completed matches sorted by start_time descending (recent first)"""
        response = api_client.get(f"{BASE_URL}/api/matches?status=completed&limit=20")
        assert response.status_code == 200
        matches = response.json().get("matches", [])
        
        if len(matches) >= 2:
            dates = [m.get("start_time", "") for m in matches]
            # Check descending order
            for i in range(len(dates) - 1):
                assert dates[i] >= dates[i+1], f"Completed not sorted descending: {dates[i]} < {dates[i+1]}"
            print(f"Completed matches sorted correctly: {dates[:3]}")


class TestISTTimeDisplay:
    """Fix 4 & 10: Match cards and live ticker show IST date/time"""
    
    def test_matches_have_start_time_ist(self, api_client):
        """Each match has start_time_ist field with IST format"""
        response = api_client.get(f"{BASE_URL}/api/matches?limit=10")
        assert response.status_code == 200
        matches = response.json().get("matches", [])
        
        for match in matches[:5]:
            ist_time = match.get("start_time_ist", "")
            assert ist_time, f"Match {match['id']} missing start_time_ist"
            assert "IST" in ist_time, f"IST not in time string: {ist_time}"
            print(f"{match['team_a']['short_name']} vs {match['team_b']['short_name']}: {ist_time}")
    
    def test_ist_time_format_correct(self, api_client):
        """IST time format is like '31 Mar 2026, 07:30 PM IST'"""
        response = api_client.get(f"{BASE_URL}/api/matches?limit=5")
        matches = response.json().get("matches", [])
        
        for match in matches[:3]:
            ist_time = match.get("start_time_ist", "")
            # Should contain month abbreviation, year, time, and IST
            assert any(m in ist_time for m in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]), f"No month in: {ist_time}"
            assert "2026" in ist_time or "2025" in ist_time, f"No year in: {ist_time}"
            assert "IST" in ist_time, f"No IST in: {ist_time}"
    
    def test_live_ticker_returns_ist_display(self, api_client):
        """Live ticker has ist_display field"""
        response = api_client.get(f"{BASE_URL}/api/cricket/live-ticker")
        assert response.status_code == 200
        scores = response.json().get("scores", [])
        
        for score in scores[:3]:
            ist_display = score.get("ist_display", "")
            assert ist_display, f"Missing ist_display for {score.get('t1')} vs {score.get('t2')}"
            assert "IST" in ist_display, f"IST not in display: {ist_display}"
            print(f"{score.get('t1')} vs {score.get('t2')}: {ist_display}")
    
    def test_live_ticker_status_has_ist_not_gmt(self, api_client):
        """Live ticker status text shows IST instead of GMT"""
        response = api_client.get(f"{BASE_URL}/api/cricket/live-ticker")
        scores = response.json().get("scores", [])
        
        for score in scores[:5]:
            status = score.get("status", "")
            if "starts at" in status.lower():
                # Should have IST, not GMT
                assert "GMT" not in status, f"GMT found in status: {status}"
                print(f"Status: {status[:60]}...")


class TestMyContestsPage:
    """Fix 5: Contest page (My Contests) redesigned with stats, filters, team logos"""
    
    def test_my_contests_endpoint(self, api_client):
        """GET /api/contests/user/my-contests returns proper structure"""
        response = api_client.get(f"{BASE_URL}/api/contests/user/my-contests?limit=20")
        assert response.status_code == 200
        data = response.json()
        
        assert "my_contests" in data, "Missing my_contests key"
        assert "total" in data, "Missing total key"
        print(f"My contests: {data.get('total', 0)} total")
    
    def test_my_contests_has_match_info(self, api_client):
        """Each contest entry has match info with team data"""
        response = api_client.get(f"{BASE_URL}/api/contests/user/my-contests?limit=10")
        contests = response.json().get("my_contests", [])
        
        for item in contests[:3]:
            match = item.get("match", {})
            if match:
                assert "team_a" in match, "Missing team_a in match"
                assert "team_b" in match, "Missing team_b in match"
                print(f"Contest: {item.get('contest',{}).get('name','')} - {match.get('team_a',{}).get('short_name','')} vs {match.get('team_b',{}).get('short_name','')}")


class TestAdminMatchesPage:
    """Fix 6: Admin Matches page fetches each status separately"""
    
    def test_admin_matches_live_status(self, api_client):
        """GET /api/matches?status=live returns live matches"""
        response = api_client.get(f"{BASE_URL}/api/matches?status=live&limit=50")
        assert response.status_code == 200
        data = response.json()
        matches = data.get("matches", [])
        
        for m in matches:
            assert m["status"] == "live", f"Non-live match in live filter: {m['status']}"
        print(f"Live matches: {len(matches)}")
    
    def test_admin_matches_upcoming_status(self, api_client):
        """GET /api/matches?status=upcoming returns upcoming matches sorted nearest first"""
        response = api_client.get(f"{BASE_URL}/api/matches?status=upcoming&limit=50")
        assert response.status_code == 200
        matches = response.json().get("matches", [])
        
        for m in matches:
            assert m["status"] == "upcoming", f"Non-upcoming match in upcoming filter: {m['status']}"
        
        # Check sorted ascending
        if len(matches) >= 2:
            dates = [m.get("start_time", "") for m in matches]
            for i in range(len(dates) - 1):
                assert dates[i] <= dates[i+1], "Upcoming not sorted ascending"
        print(f"Upcoming matches: {len(matches)}")
    
    def test_admin_matches_completed_status(self, api_client):
        """GET /api/matches?status=completed returns completed matches sorted recent first"""
        response = api_client.get(f"{BASE_URL}/api/matches?status=completed&limit=50")
        assert response.status_code == 200
        matches = response.json().get("matches", [])
        
        for m in matches:
            assert m["status"] == "completed", f"Non-completed match in completed filter: {m['status']}"
        
        # Check sorted descending
        if len(matches) >= 2:
            dates = [m.get("start_time", "") for m in matches]
            for i in range(len(dates) - 1):
                assert dates[i] >= dates[i+1], "Completed not sorted descending"
        print(f"Completed matches: {len(matches)}")


class TestAdminContests:
    """Fix 7: Admin Contest cards show proper team names"""
    
    def test_admin_contests_endpoint(self, api_client):
        """GET /api/admin/contests returns contests with match info"""
        response = api_client.get(f"{BASE_URL}/api/admin/contests?limit=20")
        assert response.status_code == 200
        data = response.json()
        contests = data.get("contests", [])
        print(f"Admin contests: {len(contests)}")
    
    def test_contest_details_include_match(self, api_client):
        """GET /api/contests/{id} includes match with team names"""
        # Get first contest
        response = api_client.get(f"{BASE_URL}/api/contests?limit=5")
        contests = response.json().get("contests", [])
        if not contests:
            pytest.skip("No contests available")
        
        contest_id = contests[0]["id"]
        response = api_client.get(f"{BASE_URL}/api/contests/{contest_id}")
        assert response.status_code == 200
        data = response.json()
        
        match = data.get("match", {})
        if match:
            team_a = match.get("team_a", {}).get("short_name", "?")
            team_b = match.get("team_b", {}).get("short_name", "?")
            assert team_a != "?", "Team A should not be '?'"
            assert team_b != "?", "Team B should not be '?'"
            print(f"Contest {data.get('name')}: {team_a} vs {team_b}")


class TestHealthAndBasics:
    """Basic health checks"""
    
    def test_api_health(self):
        """API health endpoint works"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
    
    def test_login_works(self):
        """Login with admin credentials works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": ADMIN_PHONE,
            "pin": ADMIN_PIN
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data or "access_token" in data.get("token", {})
        print(f"Logged in as: {data.get('user', {}).get('username', 'Unknown')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
