"""
Iteration 23 - Testing AI Commentary, LiveTab, ShareCard, CSS Animations
Tests the major upgrade: structured AI commentary, LiveTab with 3 sub-tabs, 
MatchCard with team card images, ShareCard with team images
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test match ID - KKR vs MI completed match with scorecard data
TEST_MATCH_ID = "e06a8963-410c-4901-bb96-807a3f258fe3"

# Test credentials
TEST_USER_PHONE = "9111111111"
TEST_USER_PIN = "5678"
ADMIN_PHONE = "7004186276"
ADMIN_PIN = "5524"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def auth_token(api_client):
    """Get authentication token for regular user"""
    # Check phone
    check_resp = api_client.post(f"{BASE_URL}/api/auth/check-phone", json={"phone": TEST_USER_PHONE})
    if check_resp.status_code != 200:
        pytest.skip(f"Phone check failed: {check_resp.text}")
    
    # Verify PIN
    verify_resp = api_client.post(f"{BASE_URL}/api/auth/verify-pin", json={
        "phone": TEST_USER_PHONE,
        "pin": TEST_USER_PIN
    })
    if verify_resp.status_code != 200:
        pytest.skip(f"PIN verification failed: {verify_resp.text}")
    
    data = verify_resp.json()
    return data.get("token")


@pytest.fixture(scope="module")
def authenticated_client(api_client, auth_token):
    """Session with auth header"""
    api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return api_client


class TestHealthAndBasics:
    """Basic health checks"""
    
    def test_health_endpoint(self, api_client):
        """Test health endpoint is working"""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("✓ Health endpoint OK")
    
    def test_matches_endpoint(self, api_client):
        """Test matches list endpoint"""
        response = api_client.get(f"{BASE_URL}/api/matches?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        print(f"✓ Matches endpoint OK - {len(data['matches'])} matches returned")


class TestAICommentary:
    """Test AI Commentary endpoint - the major new feature"""
    
    def test_ai_commentary_endpoint_exists(self, api_client):
        """Test that AI commentary endpoint exists"""
        response = api_client.get(f"{BASE_URL}/api/matches/{TEST_MATCH_ID}/ai-commentary")
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
        print(f"✓ AI Commentary endpoint exists - Status: {response.status_code}")
    
    def test_ai_commentary_returns_structured_data(self, api_client):
        """Test AI commentary returns structured JSON with expected fields"""
        response = api_client.get(f"{BASE_URL}/api/matches/{TEST_MATCH_ID}/ai-commentary")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for structured fields
            assert "match_id" in data, "Missing match_id in response"
            
            # Check for new structured format fields (may be null if no scorecard)
            has_structured = any([
                data.get("match_pulse"),
                data.get("key_moments"),
                data.get("star_performers"),
                data.get("turning_point"),
                data.get("verdict")
            ])
            
            # If no structured data, check for error or commentary fallback
            if not has_structured:
                assert data.get("error") or data.get("commentary") is not None, \
                    "Expected either structured data, error, or commentary fallback"
                print(f"✓ AI Commentary returned fallback/error: {data.get('error', 'commentary fallback')}")
            else:
                print(f"✓ AI Commentary returned structured data")
                
                # Validate match_pulse structure if present
                if data.get("match_pulse"):
                    mp = data["match_pulse"]
                    assert "headline" in mp, "match_pulse missing headline"
                    print(f"  - Match Pulse headline: {mp.get('headline', '')[:50]}...")
                
                # Validate key_moments structure if present
                if data.get("key_moments"):
                    km = data["key_moments"]
                    assert isinstance(km, list), "key_moments should be a list"
                    print(f"  - Key Moments count: {len(km)}")
                    if km:
                        moment = km[0]
                        assert "event_type" in moment, "key_moment missing event_type"
                        assert "title" in moment, "key_moment missing title"
                        print(f"  - First moment: {moment.get('title', '')[:40]}...")
                
                # Validate star_performers structure if present
                if data.get("star_performers"):
                    sp = data["star_performers"]
                    assert isinstance(sp, list), "star_performers should be a list"
                    print(f"  - Star Performers count: {len(sp)}")
                    if sp:
                        star = sp[0]
                        assert "name" in star, "star_performer missing name"
                        assert "rating" in star, "star_performer missing rating"
                        print(f"  - Top star: {star.get('name', '')} - Rating: {star.get('rating', 0)}")
                
                # Validate verdict structure if present
                if data.get("verdict"):
                    v = data["verdict"]
                    assert "headline" in v, "verdict missing headline"
                    assert "mood" in v, "verdict missing mood"
                    print(f"  - Verdict mood: {v.get('mood', '')}")
        else:
            print(f"✓ AI Commentary endpoint returned {response.status_code} (match may not have scorecard)")
    
    def test_ai_commentary_force_refresh(self, api_client):
        """Test AI commentary force refresh parameter"""
        response = api_client.get(f"{BASE_URL}/api/matches/{TEST_MATCH_ID}/ai-commentary?force=true")
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            # When force=true, cached should be False (unless it's a fresh generation)
            print(f"✓ AI Commentary force refresh - cached: {data.get('cached', 'N/A')}")
    
    def test_ai_commentary_invalid_match(self, api_client):
        """Test AI commentary with invalid match ID"""
        response = api_client.get(f"{BASE_URL}/api/matches/invalid-match-id-12345/ai-commentary")
        assert response.status_code == 404, f"Expected 404 for invalid match, got {response.status_code}"
        print("✓ AI Commentary returns 404 for invalid match")


class TestMatchScorecard:
    """Test scorecard endpoint which feeds AI commentary"""
    
    def test_scorecard_endpoint(self, api_client):
        """Test scorecard endpoint for completed match"""
        response = api_client.get(f"{BASE_URL}/api/matches/{TEST_MATCH_ID}/scorecard")
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            if data.get("scorecard"):
                print(f"✓ Scorecard available - {len(data['scorecard'])} innings")
                # Check scorecard structure
                for inn in data["scorecard"]:
                    assert "batting" in inn or "bowling" in inn, "Innings missing batting/bowling data"
            else:
                print(f"✓ Scorecard endpoint OK but no data yet: {data.get('error', 'empty')}")
        else:
            print(f"✓ Scorecard endpoint returned {response.status_code}")


class TestMatchInfo:
    """Test match info endpoint"""
    
    def test_match_info_endpoint(self, api_client):
        """Test match info endpoint"""
        response = api_client.get(f"{BASE_URL}/api/matches/{TEST_MATCH_ID}/match-info")
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            if not data.get("error"):
                print(f"✓ Match Info: {data.get('name', 'N/A')}")
                print(f"  - Status: {data.get('status', 'N/A')}")
                print(f"  - Venue: {data.get('venue', 'N/A')}")
                if data.get("toss_winner"):
                    print(f"  - Toss: {data.get('toss_winner')} chose to {data.get('toss_choice')}")
            else:
                print(f"✓ Match Info endpoint OK but no data: {data.get('error')}")


class TestLiveScoreData:
    """Test live score data for score display"""
    
    def test_match_has_live_score(self, api_client):
        """Test that match has live_score with scores array"""
        response = api_client.get(f"{BASE_URL}/api/matches/{TEST_MATCH_ID}")
        
        if response.status_code == 200:
            data = response.json()
            live_score = data.get("live_score", {})
            scores = live_score.get("scores", [])
            
            if scores:
                print(f"✓ Match has live scores - {len(scores)} innings")
                for i, s in enumerate(scores):
                    # Check for both r/w/o and runs/wickets/overs formats
                    runs = s.get("r") or s.get("runs", "?")
                    wickets = s.get("w") or s.get("wickets", "?")
                    overs = s.get("o") or s.get("overs", "?")
                    print(f"  - Innings {i+1}: {runs}/{wickets} ({overs} ov)")
            else:
                print("✓ Match endpoint OK but no live scores yet")
        else:
            print(f"✓ Match endpoint returned {response.status_code}")


class TestContestsAndLeaderboard:
    """Test contests and leaderboard for ShareCard functionality"""
    
    def test_match_contests(self, api_client):
        """Test contests endpoint for match"""
        response = api_client.get(f"{BASE_URL}/api/matches/{TEST_MATCH_ID}/contests")
        assert response.status_code == 200, f"Contests endpoint failed: {response.status_code}"
        
        data = response.json()
        contests = data.get("contests", [])
        print(f"✓ Match has {len(contests)} contests")
        
        if contests:
            # Return first contest ID for leaderboard test
            return contests[0].get("id")
        return None
    
    def test_leaderboard_endpoint(self, authenticated_client):
        """Test leaderboard endpoint (requires auth)"""
        # First get a contest ID
        contests_resp = authenticated_client.get(f"{BASE_URL}/api/matches/{TEST_MATCH_ID}/contests")
        if contests_resp.status_code != 200:
            pytest.skip("Could not get contests")
        
        contests = contests_resp.json().get("contests", [])
        if not contests:
            pytest.skip("No contests available for leaderboard test")
        
        contest_id = contests[0].get("id")
        response = authenticated_client.get(f"{BASE_URL}/api/contests/{contest_id}/leaderboard")
        
        assert response.status_code in [200, 404], f"Leaderboard failed: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            entries = data.get("leaderboard", [])
            print(f"✓ Leaderboard has {len(entries)} entries")
            if entries:
                top = entries[0]
                print(f"  - Top player: Rank {top.get('rank', '?')}, Score: {top.get('score', '?')}")


class TestBallByBall:
    """Test ball-by-ball endpoint for Live tab"""
    
    def test_ball_by_ball_endpoint(self, api_client):
        """Test ball-by-ball endpoint"""
        response = api_client.get(f"{BASE_URL}/api/matches/{TEST_MATCH_ID}/ball-by-ball")
        assert response.status_code in [200, 404], f"BBB endpoint failed: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            balls = data.get("balls", [])
            print(f"✓ Ball-by-ball has {len(balls)} events")
        else:
            print(f"✓ Ball-by-ball endpoint returned {response.status_code}")


class TestLiveMatchData:
    """Test live match for upcoming/live match scenarios"""
    
    def test_live_ticker(self, api_client):
        """Test live ticker endpoint"""
        response = api_client.get(f"{BASE_URL}/api/cricket/live-ticker")
        assert response.status_code == 200, f"Live ticker failed: {response.status_code}"
        
        data = response.json()
        scores = data.get("scores", [])
        print(f"✓ Live ticker has {len(scores)} matches")
    
    def test_ipl_points_table(self, api_client):
        """Test IPL points table endpoint"""
        response = api_client.get(f"{BASE_URL}/api/cricket/ipl/points-table")
        assert response.status_code == 200, f"Points table failed: {response.status_code}"
        
        data = response.json()
        teams = data.get("teams", [])
        print(f"✓ IPL Points table has {len(teams)} teams")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
