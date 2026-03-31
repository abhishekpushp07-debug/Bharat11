"""
Iteration 37 - Testing 6 New Features:
1. User Management Admin Tab (/api/admin/users endpoints)
2. Celebration Animations (CelebrationOverlay component)
3. Confetti on ShareCard (ConfettiEffect component)
4. React.lazy code splitting (App.js)
5. Service Worker offline page
6. Auto template generation (match_engine.py)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
ADMIN_PHONE = "7004186276"
ADMIN_PIN = "5524"


class TestAuth:
    """Authentication tests"""
    
    def test_admin_login(self):
        """Test admin login returns token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": ADMIN_PHONE,
            "pin": ADMIN_PIN
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in response"
        assert "access_token" in data["token"], "No access_token in token"
        return data["token"]["access_token"]


class TestAdminUsersEndpoints:
    """Test /api/admin/users endpoints - User Management Tab"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token for authenticated requests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": ADMIN_PHONE,
            "pin": ADMIN_PIN
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        self.token = response.json()["token"]["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_list_users_endpoint_exists(self):
        """Test GET /api/admin/users returns users list"""
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "users" in data, "No 'users' key in response"
        assert "total" in data, "No 'total' key in response"
        assert isinstance(data["users"], list), "users should be a list"
        print(f"✓ Found {data['total']} users")
    
    def test_list_users_with_search(self):
        """Test GET /api/admin/users?search=7004 searches by phone"""
        response = requests.get(f"{BASE_URL}/api/admin/users?search=7004", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "users" in data
        # Should find admin user with phone 7004186276
        if data["total"] > 0:
            phones = [u.get("phone", "") for u in data["users"]]
            assert any("7004" in p for p in phones), "Search should find users with 7004 in phone"
            print(f"✓ Search found {data['total']} users matching '7004'")
    
    def test_get_user_detail(self):
        """Test GET /api/admin/users/{user_id} returns detailed user info"""
        # First get a user ID
        list_response = requests.get(f"{BASE_URL}/api/admin/users?limit=1", headers=self.headers)
        assert list_response.status_code == 200
        users = list_response.json().get("users", [])
        if not users:
            pytest.skip("No users to test")
        
        user_id = users[0]["id"]
        response = requests.get(f"{BASE_URL}/api/admin/users/{user_id}", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Check response structure
        assert "user" in data, "No 'user' key in response"
        assert "stats" in data, "No 'stats' key in response"
        
        # Check stats structure
        stats = data["stats"]
        assert "total_contests" in stats or "total_entries" in stats, "Missing contest/entry stats"
        print(f"✓ User detail: {data['user'].get('name', 'N/A')} - {stats}")
    
    def test_user_detail_not_found(self):
        """Test GET /api/admin/users/{invalid_id} returns 404"""
        response = requests.get(f"{BASE_URL}/api/admin/users/invalid_user_id_12345", headers=self.headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    def test_users_pagination(self):
        """Test users list supports pagination"""
        response = requests.get(f"{BASE_URL}/api/admin/users?page=1&limit=5", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "page" in data or "pages" in data, "Missing pagination info"
        assert len(data.get("users", [])) <= 5, "Limit not respected"
        print(f"✓ Pagination working: page 1, {len(data.get('users', []))} users")


class TestAdminStats:
    """Test admin dashboard stats endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": ADMIN_PHONE,
            "pin": ADMIN_PIN
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        self.token = response.json()["token"]["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_admin_stats_endpoint(self):
        """Test GET /api/admin/stats returns dashboard stats"""
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Check expected stats fields
        expected_fields = ["users", "matches", "contests", "questions", "templates"]
        for field in expected_fields:
            assert field in data, f"Missing '{field}' in stats"
        
        print(f"✓ Admin stats: {data['users']} users, {data['matches']} matches, {data['contests']} contests")


class TestServiceWorkerAndOffline:
    """Test service worker and offline page exist"""
    
    def test_service_worker_exists(self):
        """Test /service-worker.js is accessible"""
        response = requests.get(f"{BASE_URL}/service-worker.js")
        assert response.status_code == 200, f"Service worker not found: {response.status_code}"
        content = response.text
        assert "bharat11" in content.lower() or "cache" in content.lower(), "Service worker content invalid"
        print("✓ Service worker exists and contains caching logic")
    
    def test_offline_page_exists(self):
        """Test /offline.html is accessible with Bharat 11 branding"""
        response = requests.get(f"{BASE_URL}/offline.html")
        assert response.status_code == 200, f"Offline page not found: {response.status_code}"
        content = response.text.lower()
        # Check for Bharat 11 branding
        assert "offline" in content, "Offline page missing 'offline' text"
        assert "bharat" in content or "retry" in content, "Offline page missing branding"
        print("✓ Offline page exists with proper branding")


class TestFontLoadingOptimization:
    """Test font loading uses media=print onload pattern"""
    
    def test_index_html_font_optimization(self):
        """Test index.html uses non-blocking font loading"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        content = response.text
        # Check for media="print" onload pattern
        assert 'media="print"' in content or "media='print'" in content, "Font loading not optimized with media=print"
        assert 'onload=' in content, "Font loading missing onload handler"
        print("✓ Font loading uses media=print onload pattern for non-blocking fetch")


class TestTemplatesAndContests:
    """Test template and contest endpoints for auto-generation"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": ADMIN_PHONE,
            "pin": ADMIN_PIN
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        self.token = response.json()["token"]["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_templates_list(self):
        """Test GET /api/admin/templates returns templates"""
        response = requests.get(f"{BASE_URL}/api/admin/templates", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "templates" in data, "No templates key"
        print(f"✓ Found {data.get('total', len(data.get('templates', [])))} templates")
    
    def test_auto_contests_24h_endpoint(self):
        """Test POST /api/admin/auto-contests-24h endpoint exists"""
        response = requests.post(f"{BASE_URL}/api/admin/auto-contests-24h", headers=self.headers)
        # Should return 200 even if no matches to process
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "processed" in data or "results" in data, "Missing expected response fields"
        print(f"✓ Auto-contests-24h endpoint working: {data}")


class TestMatchesAndContests:
    """Test matches and contests endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": ADMIN_PHONE,
            "pin": ADMIN_PIN
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        self.token = response.json()["token"]["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_matches_list(self):
        """Test GET /api/matches returns matches"""
        response = requests.get(f"{BASE_URL}/api/matches", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "matches" in data, "No matches key"
        print(f"✓ Found {len(data.get('matches', []))} matches")
    
    def test_contests_list(self):
        """Test GET /api/admin/contests returns contests"""
        response = requests.get(f"{BASE_URL}/api/admin/contests", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "contests" in data, "No contests key"
        print(f"✓ Found {len(data.get('contests', []))} contests")


class TestQuestionsBank:
    """Test questions bank for template generation"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": ADMIN_PHONE,
            "pin": ADMIN_PIN
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        self.token = response.json()["token"]["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_questions_list(self):
        """Test GET /api/admin/questions returns questions"""
        response = requests.get(f"{BASE_URL}/api/admin/questions", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "questions" in data, "No questions key"
        print(f"✓ Found {data.get('total', len(data.get('questions', [])))} questions in bank")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
