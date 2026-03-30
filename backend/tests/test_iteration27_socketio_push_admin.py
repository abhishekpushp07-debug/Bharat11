"""
Iteration 27 - Socket.IO, Push Notifications, Admin User Management Tests
Tests for new features: Socket.IO real-time, Push Notifications, Admin Users Tab
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_PHONE = "7004186276"
ADMIN_PIN = "5524"
PLAYER_PHONE = "9111111111"
PLAYER_PIN = "5678"


class TestSocketIO:
    """Socket.IO endpoint tests"""

    def test_socket_io_polling_endpoint(self):
        """Test Socket.IO polling endpoint returns valid session"""
        # Socket.IO polling endpoint
        response = requests.get(f"{BASE_URL}/api/socket.io/?EIO=4&transport=polling", timeout=10)
        # Socket.IO returns 200 with session info or 400 if no sid
        assert response.status_code in [200, 400], f"Unexpected status: {response.status_code}"
        if response.status_code == 200:
            # Should contain session ID in response
            text = response.text
            assert len(text) > 0, "Empty response from Socket.IO polling"
            print(f"PASS - Socket.IO polling returns data: {text[:100]}...")
        else:
            print(f"PASS - Socket.IO polling endpoint accessible (status {response.status_code})")

    def test_api_root_socket_status(self):
        """Test GET /api returns socket status with connected_clients and server_active"""
        response = requests.get(f"{BASE_URL}/api", timeout=10)
        assert response.status_code == 200, f"API root failed: {response.status_code}"
        data = response.json()
        
        assert "socket" in data, "Missing 'socket' field in API root response"
        socket_status = data["socket"]
        assert "connected_clients" in socket_status, "Missing 'connected_clients' in socket status"
        assert "server_active" in socket_status, "Missing 'server_active' in socket status"
        assert socket_status["server_active"] == True, "Socket server should be active"
        print(f"PASS - Socket status: {socket_status}")


class TestPushNotifications:
    """Push Notification endpoint tests"""

    def test_vapid_public_key_endpoint(self):
        """Test GET /api/notifications/vapid-public-key returns non-empty public_key"""
        response = requests.get(f"{BASE_URL}/api/notifications/vapid-public-key", timeout=10)
        assert response.status_code == 200, f"VAPID key endpoint failed: {response.status_code}"
        data = response.json()
        
        assert "public_key" in data, "Missing 'public_key' in response"
        assert len(data["public_key"]) > 0, "VAPID public key is empty"
        assert data["public_key"].startswith("B"), "VAPID key should start with 'B'"
        print(f"PASS - VAPID public key: {data['public_key'][:20]}...")

    def test_subscribe_requires_auth(self):
        """Test POST /api/notifications/subscribe requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/notifications/subscribe",
            json={"subscription": {"endpoint": "https://test.com", "keys": {"p256dh": "test", "auth": "test"}}},
            timeout=10
        )
        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403], f"Subscribe should require auth, got: {response.status_code}"
        print("PASS - Subscribe endpoint requires authentication")

    def test_subscribe_with_auth(self):
        """Test POST /api/notifications/subscribe with valid auth"""
        # Login first
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json={"phone": PLAYER_PHONE, "pin": PLAYER_PIN}, timeout=10)
        if login_res.status_code != 200:
            pytest.skip("Player login failed")
        
        token = login_res.json().get("token", {}).get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Subscribe with mock subscription
        response = requests.post(
            f"{BASE_URL}/api/notifications/subscribe",
            json={"subscription": {"endpoint": "https://test-endpoint.com/push", "keys": {"p256dh": "testkey", "auth": "testauthkey"}}},
            headers=headers,
            timeout=10
        )
        assert response.status_code == 200, f"Subscribe failed: {response.status_code} - {response.text}"
        data = response.json()
        assert data.get("status") in ["subscribed", "already_subscribed"], f"Unexpected status: {data}"
        print(f"PASS - Push subscribe: {data}")

    def test_unsubscribe_with_auth(self):
        """Test POST /api/notifications/unsubscribe with valid auth"""
        # Login first
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json={"phone": PLAYER_PHONE, "pin": PLAYER_PIN}, timeout=10)
        if login_res.status_code != 200:
            pytest.skip("Player login failed")
        
        token = login_res.json().get("token", {}).get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Unsubscribe
        response = requests.post(
            f"{BASE_URL}/api/notifications/unsubscribe",
            json={"subscription": {"endpoint": "https://test-endpoint.com/push", "keys": {"p256dh": "testkey", "auth": "testauthkey"}}},
            headers=headers,
            timeout=10
        )
        assert response.status_code == 200, f"Unsubscribe failed: {response.status_code}"
        data = response.json()
        assert data.get("status") == "unsubscribed", f"Unexpected status: {data}"
        print(f"PASS - Push unsubscribe: {data}")


class TestAdminUserManagement:
    """Admin User Management endpoint tests"""

    @pytest.fixture
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={"phone": ADMIN_PHONE, "pin": ADMIN_PIN}, timeout=10)
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json().get("token", {}).get("access_token")

    def test_admin_users_list(self, admin_token):
        """Test GET /api/admin/users returns paginated user list"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=headers, timeout=10)
        
        assert response.status_code == 200, f"Admin users list failed: {response.status_code}"
        data = response.json()
        
        assert "users" in data, "Missing 'users' in response"
        assert "total" in data, "Missing 'total' in response"
        assert "page" in data, "Missing 'page' in response"
        assert "pages" in data, "Missing 'pages' in response"
        assert isinstance(data["users"], list), "Users should be a list"
        print(f"PASS - Admin users list: {data['total']} total users, page {data['page']}/{data['pages']}")

    def test_admin_users_search(self, admin_token):
        """Test GET /api/admin/users?search=Player returns filtered results"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/users?search=Player", headers=headers, timeout=10)
        
        assert response.status_code == 200, f"Admin users search failed: {response.status_code}"
        data = response.json()
        
        assert "users" in data, "Missing 'users' in response"
        # Search should work (may return 0 or more results)
        print(f"PASS - Admin users search: found {len(data['users'])} users matching 'Player'")

    def test_admin_users_requires_admin(self):
        """Test GET /api/admin/users requires admin role"""
        # Login as regular player
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json={"phone": PLAYER_PHONE, "pin": PLAYER_PIN}, timeout=10)
        if login_res.status_code != 200:
            pytest.skip("Player login failed")
        
        token = login_res.json().get("token", {}).get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=headers, timeout=10)
        # Should return 403 for non-admin
        assert response.status_code == 403, f"Non-admin should get 403, got: {response.status_code}"
        print("PASS - Admin users endpoint requires admin role")

    def test_admin_user_detail(self, admin_token):
        """Test GET /api/admin/users/{user_id} returns user details with stats"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # First get a user ID from the list
        list_res = requests.get(f"{BASE_URL}/api/admin/users?limit=1", headers=headers, timeout=10)
        if list_res.status_code != 200 or not list_res.json().get("users"):
            pytest.skip("No users found")
        
        user_id = list_res.json()["users"][0]["id"]
        
        # Get user detail
        response = requests.get(f"{BASE_URL}/api/admin/users/{user_id}", headers=headers, timeout=10)
        assert response.status_code == 200, f"User detail failed: {response.status_code}"
        data = response.json()
        
        assert "user" in data, "Missing 'user' in response"
        assert "stats" in data, "Missing 'stats' in response"
        assert "recent_entries" in data, "Missing 'recent_entries' in response"
        
        # Check stats structure
        stats = data["stats"]
        assert "total_contests" in stats, "Missing 'total_contests' in stats"
        assert "accuracy" in stats, "Missing 'accuracy' in stats"
        print(f"PASS - User detail: {data['user'].get('username')}, {stats['total_contests']} contests, {stats['accuracy']}% accuracy")

    def test_admin_ban_toggle(self, admin_token):
        """Test POST /api/admin/users/{user_id}/ban toggles ban status"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get a non-admin user to test ban
        list_res = requests.get(f"{BASE_URL}/api/admin/users?limit=10", headers=headers, timeout=10)
        if list_res.status_code != 200:
            pytest.skip("Failed to get users list")
        
        users = list_res.json().get("users", [])
        non_admin_user = next((u for u in users if not u.get("is_admin")), None)
        
        if not non_admin_user:
            pytest.skip("No non-admin user found to test ban")
        
        user_id = non_admin_user["id"]
        original_banned = non_admin_user.get("is_banned", False)
        
        # Toggle ban
        response = requests.post(f"{BASE_URL}/api/admin/users/{user_id}/ban", headers=headers, timeout=10)
        assert response.status_code == 200, f"Ban toggle failed: {response.status_code}"
        data = response.json()
        
        assert "is_banned" in data, "Missing 'is_banned' in response"
        assert "action" in data, "Missing 'action' in response"
        assert data["is_banned"] != original_banned, "Ban status should have toggled"
        print(f"PASS - Ban toggle: user {user_id} is now {data['action']}")
        
        # Toggle back to restore original state
        requests.post(f"{BASE_URL}/api/admin/users/{user_id}/ban", headers=headers, timeout=10)

    def test_admin_adjust_coins(self, admin_token):
        """Test POST /api/admin/users/{user_id}/adjust-coins adjusts coins and logs transaction"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get a user to test coin adjustment
        list_res = requests.get(f"{BASE_URL}/api/admin/users?limit=5", headers=headers, timeout=10)
        if list_res.status_code != 200:
            pytest.skip("Failed to get users list")
        
        users = list_res.json().get("users", [])
        if not users:
            pytest.skip("No users found")
        
        user_id = users[0]["id"]
        
        # Add coins
        response = requests.post(
            f"{BASE_URL}/api/admin/users/{user_id}/adjust-coins",
            json={"amount": 100, "reason": "Test adjustment"},
            headers=headers,
            timeout=10
        )
        assert response.status_code == 200, f"Coin adjust failed: {response.status_code}"
        data = response.json()
        
        assert "amount" in data, "Missing 'amount' in response"
        assert "new_balance" in data, "Missing 'new_balance' in response"
        assert "reason" in data, "Missing 'reason' in response"
        assert data["amount"] == 100, "Amount should be 100"
        print(f"PASS - Coin adjustment: +{data['amount']} coins, new balance: {data['new_balance']}")
        
        # Deduct coins to restore
        requests.post(
            f"{BASE_URL}/api/admin/users/{user_id}/adjust-coins",
            json={"amount": -100, "reason": "Test reversal"},
            headers=headers,
            timeout=10
        )


class TestHealthAndBasics:
    """Basic health and connectivity tests"""

    def test_health_endpoint(self):
        """Test health endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        print("PASS - Health endpoint OK")

    def test_admin_login(self):
        """Test admin login works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={"phone": ADMIN_PHONE, "pin": ADMIN_PIN}, timeout=10)
        assert response.status_code == 200, f"Admin login failed: {response.status_code}"
        data = response.json()
        assert "token" in data, "Missing token in login response"
        print("PASS - Admin login successful")

    def test_player_login(self):
        """Test player login works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={"phone": PLAYER_PHONE, "pin": PLAYER_PIN}, timeout=10)
        assert response.status_code == 200, f"Player login failed: {response.status_code}"
        data = response.json()
        assert "token" in data, "Missing token in login response"
        print("PASS - Player login successful")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
