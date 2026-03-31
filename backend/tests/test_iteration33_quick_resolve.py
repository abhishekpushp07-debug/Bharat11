"""
Iteration 33 - Quick Resolve All Endpoint Tests
Tests the new POST /api/admin/quick-resolve-all endpoint
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://fantasy-points.preview.emergentagent.com')

# Test credentials
ADMIN_PHONE = "7004186276"
ADMIN_PIN = "5524"


class TestQuickResolveEndpoint:
    """Tests for the Quick Resolve All feature"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        # Login with phone and PIN
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": ADMIN_PHONE,
            "pin": ADMIN_PIN
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        # Token is nested under data["token"]["access_token"]
        assert "token" in data, "No token in response"
        return data["token"]["access_token"]
    
    def test_quick_resolve_endpoint_exists(self, admin_token):
        """Test that the quick-resolve-all endpoint exists and is accessible"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.post(f"{BASE_URL}/api/admin/quick-resolve-all", headers=headers)
        
        # Should return 200 (success) or 403 (forbidden if not admin) - not 404
        assert response.status_code != 404, "Quick resolve endpoint not found (404)"
        print(f"Quick resolve endpoint status: {response.status_code}")
        print(f"Response: {response.json()}")
    
    def test_quick_resolve_returns_expected_structure(self, admin_token):
        """Test that quick-resolve-all returns the expected response structure"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.post(f"{BASE_URL}/api/admin/quick-resolve-all", headers=headers)
        
        assert response.status_code == 200, f"Quick resolve failed: {response.text}"
        data = response.json()
        
        # Check expected fields in response
        assert "message" in data, "Response missing 'message' field"
        assert "total_resolved" in data, "Response missing 'total_resolved' field"
        assert "total_skipped" in data, "Response missing 'total_skipped' field"
        assert "total_errors" in data, "Response missing 'total_errors' field"
        assert "results" in data, "Response missing 'results' field"
        
        print(f"Quick Resolve Response:")
        print(f"  Message: {data['message']}")
        print(f"  Total Resolved: {data['total_resolved']}")
        print(f"  Total Skipped: {data['total_skipped']}")
        print(f"  Total Errors: {data['total_errors']}")
        print(f"  Contests Processed: {data.get('contests_processed', 'N/A')}")
    
    def test_quick_resolve_without_auth_fails(self):
        """Test that quick-resolve-all requires authentication"""
        response = requests.post(f"{BASE_URL}/api/admin/quick-resolve-all")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print(f"Unauthenticated request correctly rejected with status {response.status_code}")


class TestAdminStatsEndpoint:
    """Tests for admin stats endpoint (used by dashboard)"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": ADMIN_PHONE,
            "pin": ADMIN_PIN
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json()["token"]["access_token"]
    
    def test_admin_stats_endpoint(self, admin_token):
        """Test admin stats endpoint returns expected data"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
        
        assert response.status_code == 200, f"Admin stats failed: {response.text}"
        data = response.json()
        
        # Check expected fields
        expected_fields = ["users", "matches", "contests", "questions", "templates", 
                          "live_matches", "upcoming_matches", "open_contests", "active_entries"]
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"
        
        print(f"Admin Stats: {data}")


class TestMatchesEndpoint:
    """Tests for matches endpoint (used by SearchPage)"""
    
    def test_matches_list_public(self):
        """Test that matches list is accessible"""
        response = requests.get(f"{BASE_URL}/api/matches?limit=50")
        assert response.status_code == 200, f"Matches list failed: {response.text}"
        data = response.json()
        
        assert "matches" in data, "Response missing 'matches' field"
        print(f"Found {len(data['matches'])} matches")
        
        # Check match structure if any exist
        if data["matches"]:
            match = data["matches"][0]
            print(f"Sample match: {match.get('team_a', {}).get('short_name', '?')} vs {match.get('team_b', {}).get('short_name', '?')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
