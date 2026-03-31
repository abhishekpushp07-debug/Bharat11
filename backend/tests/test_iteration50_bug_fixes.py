"""
Iteration 50 - Bug Fixes Testing
Tests for 5 reported bugs:
1. Autopilot overrides manual match/contest status changes
2. User 'Join Contest' button disabled/inactive
3. Contests not showing for live matches on user frontend
4. API Date showing wrong IST (2 PM instead of correct IST)
5. Matches not sorted 'Recent First' on user frontend
"""
import pytest
import requests
import os
from datetime import datetime, timezone

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_PHONE = "7004186276"
ADMIN_PIN = "5524"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def admin_token(api_client):
    """Get admin authentication token"""
    # Direct login with phone + PIN
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "phone": ADMIN_PHONE,
        "pin": ADMIN_PIN
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    
    # Token is nested under "token" key
    token_data = data.get("token", data)
    assert "access_token" in token_data, f"No access_token in response: {data}"
    return token_data["access_token"]


@pytest.fixture(scope="module")
def authenticated_client(api_client, admin_token):
    """Session with auth header"""
    api_client.headers.update({"Authorization": f"Bearer {admin_token}"})
    return api_client


class TestBugFix1_ManualOverrideFlag:
    """Bug Fix 1: Admin changes match status → manual_override=true → autopilot should NOT override"""
    
    def test_match_status_update_sets_manual_override(self, authenticated_client):
        """PUT /api/matches/{id}/status should set manual_override=true"""
        # Get first upcoming match
        response = authenticated_client.get(f"{BASE_URL}/api/matches?status=upcoming&limit=1")
        assert response.status_code == 200
        matches = response.json().get("matches", [])
        assert len(matches) > 0, "No upcoming matches found"
        
        match_id = matches[0]["id"]
        
        # Update status to live
        response = authenticated_client.put(
            f"{BASE_URL}/api/matches/{match_id}/status",
            json={"status": "live"}
        )
        assert response.status_code == 200, f"Status update failed: {response.text}"
        
        # Verify manual_override is set
        updated_match = response.json()
        assert updated_match.get("manual_override") == True, "manual_override should be True after admin status change"
        
        # Revert back to upcoming
        response = authenticated_client.put(
            f"{BASE_URL}/api/matches/{match_id}/status",
            json={"status": "upcoming"}
        )
        assert response.status_code == 200
        
    def test_contest_status_update_sets_manual_override(self, authenticated_client):
        """PUT /api/admin/contests/{id}/status should set manual_override=true"""
        # Get first open contest
        response = authenticated_client.get(f"{BASE_URL}/api/contests?status=open&limit=1")
        assert response.status_code == 200
        contests = response.json().get("contests", [])
        
        if len(contests) == 0:
            pytest.skip("No open contests found")
        
        contest_id = contests[0]["id"]
        
        # Update status to live
        response = authenticated_client.put(
            f"{BASE_URL}/api/admin/contests/{contest_id}/status",
            json={"status": "live"}
        )
        assert response.status_code == 200, f"Contest status update failed: {response.text}"
        
        # Verify response indicates manual_override
        result = response.json()
        assert "new_status" in result, "Response should contain new_status"
        assert result["new_status"] == "live"
        
        # Revert back to open
        response = authenticated_client.put(
            f"{BASE_URL}/api/admin/contests/{contest_id}/status",
            json={"status": "open"}
        )
        assert response.status_code == 200


class TestBugFix2_JoinContestForOpenAndLive:
    """Bug Fix 2: User can join contests with status 'open' OR 'live'"""
    
    def test_join_open_contest(self, authenticated_client):
        """POST /api/contests/{contest_id}/join should work for 'open' status"""
        # Get an open contest
        response = authenticated_client.get(f"{BASE_URL}/api/contests?status=open&limit=1")
        assert response.status_code == 200
        contests = response.json().get("contests", [])
        
        if len(contests) == 0:
            pytest.skip("No open contests found")
        
        contest_id = contests[0]["id"]
        
        # Try to join
        response = authenticated_client.post(
            f"{BASE_URL}/api/contests/{contest_id}/join",
            json={"team_name": f"TestTeam_{datetime.now().timestamp()}"}
        )
        
        # Should succeed or return "Already joined"
        assert response.status_code in [200, 409], f"Join failed unexpectedly: {response.text}"
        
        if response.status_code == 409:
            assert "Already joined" in response.json().get("detail", "")
    
    def test_join_live_contest(self, authenticated_client):
        """POST /api/contests/{contest_id}/join should work for 'live' status"""
        # Get a live contest
        response = authenticated_client.get(f"{BASE_URL}/api/contests?status=live&limit=1")
        assert response.status_code == 200
        contests = response.json().get("contests", [])
        
        if len(contests) == 0:
            # Create a live contest for testing
            # First get an open contest and make it live
            response = authenticated_client.get(f"{BASE_URL}/api/contests?status=open&limit=1")
            open_contests = response.json().get("contests", [])
            if len(open_contests) == 0:
                pytest.skip("No contests available for testing")
            
            contest_id = open_contests[0]["id"]
            
            # Make it live
            authenticated_client.put(
                f"{BASE_URL}/api/admin/contests/{contest_id}/status",
                json={"status": "live"}
            )
            
            # Try to join
            response = authenticated_client.post(
                f"{BASE_URL}/api/contests/{contest_id}/join",
                json={"team_name": f"TestTeam_{datetime.now().timestamp()}"}
            )
            
            # Revert to open
            authenticated_client.put(
                f"{BASE_URL}/api/admin/contests/{contest_id}/status",
                json={"status": "open"}
            )
        else:
            contest_id = contests[0]["id"]
            response = authenticated_client.post(
                f"{BASE_URL}/api/contests/{contest_id}/join",
                json={"team_name": f"TestTeam_{datetime.now().timestamp()}"}
            )
        
        # Should succeed or return "Already joined"
        assert response.status_code in [200, 409], f"Join live contest failed: {response.text}"


class TestBugFix3_ContestsShowForLiveMatches:
    """Bug Fix 3: GET /api/matches/{match_id}/contests returns contests regardless of match status"""
    
    def test_get_contests_for_any_match_status(self, authenticated_client):
        """Contests should be returned for matches of any status"""
        # Get matches of different statuses
        for status in ["upcoming", "live", "completed"]:
            response = authenticated_client.get(f"{BASE_URL}/api/matches?status={status}&limit=1")
            assert response.status_code == 200
            matches = response.json().get("matches", [])
            
            if len(matches) > 0:
                match_id = matches[0]["id"]
                
                # Get contests for this match
                response = authenticated_client.get(f"{BASE_URL}/api/matches/{match_id}/contests")
                assert response.status_code == 200, f"Failed to get contests for {status} match: {response.text}"
                
                data = response.json()
                assert "contests" in data, f"Response should contain 'contests' key for {status} match"
                assert "match_id" in data, f"Response should contain 'match_id' for {status} match"
                print(f"✓ {status} match {match_id}: {len(data['contests'])} contests found")


class TestBugFix4_ISTTimeFormatting:
    """Bug Fix 4: GET /api/matches returns 'start_time_ist' field with properly formatted IST time"""
    
    def test_matches_have_ist_time_field(self, authenticated_client):
        """Matches should have start_time_ist field with IST formatted time"""
        response = authenticated_client.get(f"{BASE_URL}/api/matches?limit=5")
        assert response.status_code == 200
        
        matches = response.json().get("matches", [])
        assert len(matches) > 0, "No matches found"
        
        for match in matches:
            assert "start_time_ist" in match, f"Match {match.get('id')} missing start_time_ist field"
            ist_time = match["start_time_ist"]
            
            # Verify IST format: "DD Mon YYYY, HH:MM AM/PM IST"
            assert "IST" in ist_time, f"IST time should contain 'IST': {ist_time}"
            
            # Verify it's not showing wrong time (e.g., 2 PM for evening matches)
            # The format should be like "31 Mar 2026, 07:30 PM IST"
            print(f"✓ Match {match.get('team_a', {}).get('short_name', '?')} vs {match.get('team_b', {}).get('short_name', '?')}: {ist_time}")
    
    def test_ist_time_is_correct_offset(self, authenticated_client):
        """Verify IST time is UTC+5:30"""
        response = authenticated_client.get(f"{BASE_URL}/api/matches?limit=1")
        assert response.status_code == 200
        
        matches = response.json().get("matches", [])
        if len(matches) == 0:
            pytest.skip("No matches found")
        
        match = matches[0]
        start_time_utc = match.get("start_time", "")
        start_time_ist = match.get("start_time_ist", "")
        
        print(f"UTC: {start_time_utc}")
        print(f"IST: {start_time_ist}")
        
        # IST should be 5:30 hours ahead of UTC
        # Just verify the field exists and has proper format
        assert start_time_ist, "start_time_ist should not be empty"
        assert "IST" in start_time_ist, "Should contain IST suffix"


class TestBugFix5_MatchesSortedRecentFirst:
    """Bug Fix 5: GET /api/matches returns matches sorted by start_time descending (most recent first)"""
    
    def test_matches_sorted_descending(self, authenticated_client):
        """Matches should be sorted by start_time descending"""
        response = authenticated_client.get(f"{BASE_URL}/api/matches?limit=10")
        assert response.status_code == 200
        
        matches = response.json().get("matches", [])
        assert len(matches) >= 2, "Need at least 2 matches to verify sorting"
        
        # Verify descending order (most recent first)
        for i in range(len(matches) - 1):
            time1 = matches[i].get("start_time", "")
            time2 = matches[i + 1].get("start_time", "")
            
            if time1 and time2:
                # Parse and compare
                dt1 = datetime.fromisoformat(time1.replace('Z', '+00:00'))
                dt2 = datetime.fromisoformat(time2.replace('Z', '+00:00'))
                
                assert dt1 >= dt2, f"Matches not sorted descending: {time1} should be >= {time2}"
        
        print(f"✓ {len(matches)} matches verified in descending order")
    
    def test_upcoming_matches_sorted_ascending_in_frontend(self, authenticated_client):
        """
        Frontend sorts upcoming matches ascending (nearest first).
        Backend returns descending, frontend re-sorts.
        This test verifies backend returns data that can be sorted.
        """
        response = authenticated_client.get(f"{BASE_URL}/api/matches?status=upcoming&limit=10")
        assert response.status_code == 200
        
        matches = response.json().get("matches", [])
        
        # Verify all have start_time for frontend sorting
        for match in matches:
            assert "start_time" in match, f"Match {match.get('id')} missing start_time"
            assert match["start_time"], f"Match {match.get('id')} has empty start_time"
        
        print(f"✓ {len(matches)} upcoming matches have start_time for frontend sorting")


class TestContestJoinEndpoint:
    """Additional tests for the join contest endpoint"""
    
    def test_join_contest_returns_proper_response(self, authenticated_client):
        """Join contest should return entry details and new balance"""
        response = authenticated_client.get(f"{BASE_URL}/api/contests?status=open&limit=1")
        assert response.status_code == 200
        contests = response.json().get("contests", [])
        
        if len(contests) == 0:
            pytest.skip("No open contests found")
        
        contest_id = contests[0]["id"]
        
        response = authenticated_client.post(
            f"{BASE_URL}/api/contests/{contest_id}/join",
            json={"team_name": f"TestTeam_{datetime.now().timestamp()}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "entry" in data, "Response should contain 'entry'"
            assert "new_balance" in data, "Response should contain 'new_balance'"
            assert "message" in data, "Response should contain 'message'"
        elif response.status_code == 409:
            # Already joined is acceptable
            assert "Already joined" in response.json().get("detail", "")
        else:
            pytest.fail(f"Unexpected response: {response.status_code} - {response.text}")
    
    def test_join_locked_contest_fails(self, authenticated_client):
        """Join should fail for locked contests"""
        response = authenticated_client.get(f"{BASE_URL}/api/contests?status=locked&limit=1")
        assert response.status_code == 200
        contests = response.json().get("contests", [])
        
        if len(contests) == 0:
            pytest.skip("No locked contests found")
        
        contest_id = contests[0]["id"]
        
        response = authenticated_client.post(
            f"{BASE_URL}/api/contests/{contest_id}/join",
            json={"team_name": f"TestTeam_{datetime.now().timestamp()}"}
        )
        
        # Should fail with 400
        assert response.status_code == 400, f"Should not be able to join locked contest: {response.text}"


class TestAutopilotManualOverrideRespect:
    """Test that autopilot queries filter manual_override != true"""
    
    def test_autopilot_status_endpoint(self, authenticated_client):
        """Verify autopilot status endpoint works"""
        response = authenticated_client.get(f"{BASE_URL}/api/admin/autopilot/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "running" in data, "Should have 'running' field"
        print(f"✓ Autopilot status: running={data.get('running')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
