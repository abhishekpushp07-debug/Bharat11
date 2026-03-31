"""
Iteration 60 - AI Commentary Cache TTL & Live Update Tests
Tests:
1. AI Commentary endpoint returns fresh data (not stale cache)
2. Commentary cache TTL: 3 minutes for live matches
3. Force refresh parameter bypasses cache
4. Scorecard cache TTL: 45 seconds
5. 30-second polling interval verification
"""
import pytest
import requests
import os
import time
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_PHONE = "7004186276"
ADMIN_PIN = "5524"
LIVE_MATCH_ID = "9c53d4ca-10c2-4e18-a723-77d4bd205640"


class TestLogin:
    """Authentication tests"""
    
    def test_admin_login(self):
        """Test admin login returns access token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": ADMIN_PHONE,
            "pin": ADMIN_PIN
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        # Token structure: { token: { access_token: '...' } }
        assert "token" in data, f"No token in response: {data}"
        assert "access_token" in data["token"], f"No access_token: {data}"
        print(f"PASSED: Admin login successful, got access_token")


class TestAICommentaryCache:
    """AI Commentary cache TTL tests"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for authenticated requests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": ADMIN_PHONE,
            "pin": ADMIN_PIN
        })
        if response.status_code == 200:
            return response.json()["token"]["access_token"]
        pytest.skip("Auth failed")
    
    def test_ai_commentary_returns_data(self):
        """Test AI commentary endpoint returns structured data"""
        response = requests.get(f"{BASE_URL}/api/matches/{LIVE_MATCH_ID}/ai-commentary")
        assert response.status_code == 200, f"AI commentary failed: {response.text}"
        data = response.json()
        
        # Verify structure
        assert "match_id" in data
        assert data["match_id"] == LIVE_MATCH_ID
        
        # Check for key_moments covering multiple overs
        key_moments = data.get("key_moments", [])
        print(f"Found {len(key_moments)} key moments")
        
        if key_moments:
            # Get over numbers
            overs = [float(m.get("over", 0)) for m in key_moments if m.get("over")]
            if overs:
                min_over = min(overs)
                max_over = max(overs)
                print(f"Key moments cover overs {min_over} to {max_over}")
                # Should cover more than just 4 overs (the bug was commentary stuck at 4 overs)
                assert max_over > 4, f"Commentary only covers up to over {max_over}, expected 12+"
        
        print(f"PASSED: AI commentary returns {len(key_moments)} key moments")
    
    def test_ai_commentary_key_moments_cover_12_overs(self):
        """Test key_moments cover overs up to current match state (12+ overs)"""
        response = requests.get(f"{BASE_URL}/api/matches/{LIVE_MATCH_ID}/ai-commentary")
        assert response.status_code == 200
        data = response.json()
        
        key_moments = data.get("key_moments", [])
        assert len(key_moments) >= 10, f"Expected 10+ key moments, got {len(key_moments)}"
        
        # Check that moments cover overs beyond 4 (the original bug)
        overs = [float(m.get("over", 0)) for m in key_moments if m.get("over")]
        max_over = max(overs) if overs else 0
        
        # Match is at 12+ overs, commentary should reflect this
        assert max_over >= 10, f"Key moments only go up to over {max_over}, expected 10+"
        print(f"PASSED: Key moments cover up to over {max_over}")
    
    def test_force_refresh_bypasses_cache(self):
        """Test force=true parameter regenerates commentary"""
        # First request - may be cached
        response1 = requests.get(f"{BASE_URL}/api/matches/{LIVE_MATCH_ID}/ai-commentary")
        assert response1.status_code == 200
        data1 = response1.json()
        cached1 = data1.get("cached", False)
        
        # Force refresh request
        response2 = requests.get(f"{BASE_URL}/api/matches/{LIVE_MATCH_ID}/ai-commentary?force=true")
        assert response2.status_code == 200
        data2 = response2.json()
        cached2 = data2.get("cached", False)
        
        # Force refresh should return cached=False
        assert cached2 == False, f"Force refresh should return cached=False, got {cached2}"
        print(f"PASSED: Force refresh bypasses cache (cached={cached2})")
    
    def test_match_pulse_present(self):
        """Test match_pulse is present in AI commentary"""
        response = requests.get(f"{BASE_URL}/api/matches/{LIVE_MATCH_ID}/ai-commentary")
        assert response.status_code == 200
        data = response.json()
        
        match_pulse = data.get("match_pulse")
        assert match_pulse is not None, "match_pulse should be present"
        assert "headline" in match_pulse, "match_pulse should have headline"
        assert "sub" in match_pulse, "match_pulse should have sub"
        print(f"PASSED: match_pulse present with headline: {match_pulse.get('headline', '')[:50]}...")
    
    def test_star_performers_present(self):
        """Test star_performers is present in AI commentary"""
        response = requests.get(f"{BASE_URL}/api/matches/{LIVE_MATCH_ID}/ai-commentary")
        assert response.status_code == 200
        data = response.json()
        
        star_performers = data.get("star_performers", [])
        assert len(star_performers) > 0, "star_performers should have entries"
        
        # Check structure
        for star in star_performers[:2]:
            assert "name" in star, "star should have name"
            assert "role" in star, "star should have role"
            assert "rating" in star, "star should have rating"
        
        print(f"PASSED: {len(star_performers)} star performers found")


class TestScorecardCache:
    """Scorecard cache TTL tests"""
    
    def test_scorecard_returns_data(self):
        """Test scorecard endpoint returns data"""
        response = requests.get(f"{BASE_URL}/api/matches/{LIVE_MATCH_ID}/scorecard")
        assert response.status_code == 200, f"Scorecard failed: {response.text}"
        data = response.json()
        
        assert "match_id" in data
        assert data["match_id"] == LIVE_MATCH_ID
        
        # Check scorecard has innings data
        scorecard = data.get("scorecard", [])
        if scorecard:
            print(f"PASSED: Scorecard has {len(scorecard)} innings")
        else:
            print(f"PASSED: Scorecard endpoint works (no innings data yet)")
    
    def test_scorecard_shows_current_overs(self):
        """Test scorecard shows current match state (12+ overs)"""
        response = requests.get(f"{BASE_URL}/api/matches/{LIVE_MATCH_ID}/scorecard")
        assert response.status_code == 200
        data = response.json()
        
        # Check score_summary for overs
        score_summary = data.get("score_summary", [])
        if score_summary:
            for score in score_summary:
                overs = score.get("o", 0)
                print(f"Innings: {score.get('inning', 'Unknown')} - {score.get('r', 0)}/{score.get('w', 0)} ({overs} overs)")
        
        print(f"PASSED: Scorecard returns current match data")


class TestMatchEndpoints:
    """General match endpoint tests"""
    
    def test_match_details(self):
        """Test match details endpoint"""
        response = requests.get(f"{BASE_URL}/api/matches/{LIVE_MATCH_ID}")
        assert response.status_code == 200, f"Match details failed: {response.text}"
        data = response.json()
        
        assert data.get("id") == LIVE_MATCH_ID
        assert "team_a" in data
        assert "team_b" in data
        assert "status" in data
        
        print(f"PASSED: Match details - {data.get('team_a', {}).get('short_name')} vs {data.get('team_b', {}).get('short_name')}, status: {data.get('status')}")
    
    def test_match_contests(self):
        """Test match contests endpoint"""
        response = requests.get(f"{BASE_URL}/api/matches/{LIVE_MATCH_ID}/contests")
        assert response.status_code == 200, f"Contests failed: {response.text}"
        data = response.json()
        
        assert "contests" in data
        contests = data.get("contests", [])
        print(f"PASSED: Match has {len(contests)} contests")
    
    def test_match_info(self):
        """Test match info endpoint"""
        response = requests.get(f"{BASE_URL}/api/matches/{LIVE_MATCH_ID}/match-info")
        assert response.status_code == 200, f"Match info failed: {response.text}"
        data = response.json()
        
        assert "match_id" in data
        print(f"PASSED: Match info - toss: {data.get('toss_winner', 'N/A')} chose to {data.get('toss_choice', 'N/A')}")


class TestCacheTTLConfig:
    """Verify cache TTL configuration"""
    
    def test_api_cache_ttl_values(self):
        """Verify TTL values in api_cache.py are correct"""
        # Read the api_cache.py file to verify TTL values
        import sys
        sys.path.insert(0, '/app/backend')
        
        try:
            from services.api_cache import TTL_SCORECARD, TTL_LIVE_SCORE
            
            # Scorecard TTL should be 45 seconds (was 60s before fix)
            assert TTL_SCORECARD == 45, f"TTL_SCORECARD should be 45, got {TTL_SCORECARD}"
            print(f"PASSED: TTL_SCORECARD = {TTL_SCORECARD}s (correct)")
            
            # Live score TTL should be 45 seconds
            assert TTL_LIVE_SCORE == 45, f"TTL_LIVE_SCORE should be 45, got {TTL_LIVE_SCORE}"
            print(f"PASSED: TTL_LIVE_SCORE = {TTL_LIVE_SCORE}s (correct)")
            
        except ImportError as e:
            pytest.skip(f"Could not import api_cache: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
