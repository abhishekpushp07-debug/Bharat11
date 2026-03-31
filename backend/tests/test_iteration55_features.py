"""
Iteration 55 - New Features Backend Tests
Tests for: Forgot PIN, Change Name, Change PIN, Admin User Management
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_PHONE = "7004186276"
ADMIN_PIN = "5524"


class TestAuthEndpoints:
    """Test new auth endpoints: forgot-pin, change-name, change-pin"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.token = None
        self.user_id = None
    
    def login_admin(self):
        """Login as admin and get token"""
        res = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "phone": ADMIN_PHONE,
            "pin": ADMIN_PIN
        })
        assert res.status_code == 200, f"Admin login failed: {res.text}"
        data = res.json()
        self.token = data.get("token", {}).get("access_token")
        self.user_id = data.get("user", {}).get("id")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        return data
    
    def test_check_phone_exists(self):
        """Test POST /api/auth/check-phone for existing user"""
        res = self.session.post(f"{BASE_URL}/api/auth/check-phone", json={
            "phone": ADMIN_PHONE
        })
        assert res.status_code == 200
        data = res.json()
        assert "exists" in data
        assert data["exists"] == True
        print("✓ check-phone returns exists=True for admin phone")
    
    def test_check_phone_not_exists(self):
        """Test POST /api/auth/check-phone for non-existing user"""
        res = self.session.post(f"{BASE_URL}/api/auth/check-phone", json={
            "phone": "9999999999"
        })
        assert res.status_code == 200
        data = res.json()
        assert "exists" in data
        assert data["exists"] == False
        print("✓ check-phone returns exists=False for unknown phone")
    
    def test_forgot_pin_success(self):
        """Test POST /api/auth/forgot-pin - Reset PIN"""
        # First create a test user
        test_phone = "9876543210"
        test_pin = "1234"
        
        # Check if user exists
        check_res = self.session.post(f"{BASE_URL}/api/auth/check-phone", json={"phone": test_phone})
        if check_res.json().get("exists"):
            # User exists, test forgot-pin
            res = self.session.post(f"{BASE_URL}/api/auth/forgot-pin", json={
                "phone": test_phone,
                "new_pin": "4321"
            })
            assert res.status_code == 200
            data = res.json()
            assert data.get("success") == True
            assert "token" in data
            assert "access_token" in data["token"]
            print("✓ forgot-pin resets PIN and returns token")
            
            # Reset back to original PIN
            self.session.post(f"{BASE_URL}/api/auth/forgot-pin", json={
                "phone": test_phone,
                "new_pin": test_pin
            })
        else:
            # Register user first
            reg_res = self.session.post(f"{BASE_URL}/api/auth/register", json={
                "phone": test_phone,
                "pin": test_pin
            })
            if reg_res.status_code == 201:
                # Now test forgot-pin
                res = self.session.post(f"{BASE_URL}/api/auth/forgot-pin", json={
                    "phone": test_phone,
                    "new_pin": "4321"
                })
                assert res.status_code == 200
                data = res.json()
                assert data.get("success") == True
                print("✓ forgot-pin works for newly registered user")
            else:
                pytest.skip("Could not create test user")
    
    def test_forgot_pin_invalid_phone(self):
        """Test POST /api/auth/forgot-pin with non-existent phone"""
        res = self.session.post(f"{BASE_URL}/api/auth/forgot-pin", json={
            "phone": "1111111111",
            "new_pin": "1234"
        })
        assert res.status_code in [400, 404, 422]  # 422 for validation error is acceptable
        print("✓ forgot-pin returns error for non-existent phone")
    
    def test_forgot_pin_invalid_pin_format(self):
        """Test POST /api/auth/forgot-pin with invalid PIN format"""
        res = self.session.post(f"{BASE_URL}/api/auth/forgot-pin", json={
            "phone": ADMIN_PHONE,
            "new_pin": "12"  # Too short
        })
        assert res.status_code in [400, 422]
        print("✓ forgot-pin validates PIN format")
    
    def test_change_name_success(self):
        """Test PUT /api/auth/change-name"""
        self.login_admin()
        
        new_name = "TestAdmin123"
        res = self.session.put(f"{BASE_URL}/api/auth/change-name", json={
            "username": new_name
        })
        assert res.status_code == 200
        data = res.json()
        assert data.get("success") == True
        assert data.get("username") == new_name
        print(f"✓ change-name updated to: {new_name}")
        
        # Verify via /auth/me
        me_res = self.session.get(f"{BASE_URL}/api/auth/me")
        assert me_res.status_code == 200
        assert me_res.json().get("username") == new_name
        print("✓ change-name persisted correctly")
    
    def test_change_name_validation(self):
        """Test PUT /api/auth/change-name validation"""
        self.login_admin()
        
        # Too short
        res = self.session.put(f"{BASE_URL}/api/auth/change-name", json={
            "username": "A"
        })
        assert res.status_code == 400
        print("✓ change-name rejects names < 2 chars")
        
        # Too long
        res = self.session.put(f"{BASE_URL}/api/auth/change-name", json={
            "username": "A" * 35
        })
        assert res.status_code == 400
        print("✓ change-name rejects names > 30 chars")
    
    def test_change_name_unauthorized(self):
        """Test PUT /api/auth/change-name without auth"""
        res = self.session.put(f"{BASE_URL}/api/auth/change-name", json={
            "username": "Test"
        })
        assert res.status_code == 401
        print("✓ change-name requires authentication")
    
    def test_change_pin_success(self):
        """Test PUT /api/auth/change-pin"""
        # Use test user for PIN change test
        test_phone = "9876543210"
        test_pin = "4321"  # Current PIN after forgot-pin test
        
        # Login as test user
        login_res = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "phone": test_phone,
            "pin": test_pin
        })
        if login_res.status_code != 200:
            # Try original PIN
            login_res = self.session.post(f"{BASE_URL}/api/auth/login", json={
                "phone": test_phone,
                "pin": "1234"
            })
            if login_res.status_code != 200:
                pytest.skip("Test user not available")
            test_pin = "1234"
        
        token = login_res.json().get("token", {}).get("access_token")
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        new_pin = "5678"
        res = self.session.put(f"{BASE_URL}/api/auth/change-pin", json={
            "old_pin": test_pin,
            "new_pin": new_pin
        })
        assert res.status_code == 200
        data = res.json()
        assert data.get("success") == True
        assert "token" in data
        print("✓ change-pin returns success and new tokens")
        
        # Verify new PIN works
        verify_res = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "phone": test_phone,
            "pin": new_pin
        })
        assert verify_res.status_code == 200
        print("✓ new PIN works for login")
        
        # Reset PIN back
        new_token = data["token"]["access_token"]
        self.session.headers.update({"Authorization": f"Bearer {new_token}"})
        self.session.put(f"{BASE_URL}/api/auth/change-pin", json={
            "old_pin": new_pin,
            "new_pin": "1234"
        })
    
    def test_change_pin_wrong_old_pin(self):
        """Test PUT /api/auth/change-pin with wrong old PIN"""
        self.login_admin()
        
        res = self.session.put(f"{BASE_URL}/api/auth/change-pin", json={
            "old_pin": "0000",
            "new_pin": "9999"
        })
        assert res.status_code in [400, 401]
        print("✓ change-pin rejects wrong old PIN")


class TestAdminUserManagement:
    """Test admin user management endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup admin session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.login_admin()
    
    def login_admin(self):
        """Login as admin"""
        res = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "phone": ADMIN_PHONE,
            "pin": ADMIN_PIN
        })
        assert res.status_code == 200
        data = res.json()
        self.token = data.get("token", {}).get("access_token")
        self.admin_id = data.get("user", {}).get("id")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def test_list_users(self):
        """Test GET /api/admin/users"""
        res = self.session.get(f"{BASE_URL}/api/admin/users")
        assert res.status_code == 200
        data = res.json()
        assert "users" in data
        assert "total" in data
        assert isinstance(data["users"], list)
        print(f"✓ admin/users returns {len(data['users'])} users (total: {data['total']})")
    
    def test_list_users_with_search(self):
        """Test GET /api/admin/users with search"""
        res = self.session.get(f"{BASE_URL}/api/admin/users?search=700")
        assert res.status_code == 200
        data = res.json()
        assert "users" in data
        print(f"✓ admin/users search returns {len(data['users'])} results")
    
    def test_list_users_banned_filter(self):
        """Test GET /api/admin/users with banned_only filter"""
        res = self.session.get(f"{BASE_URL}/api/admin/users?banned_only=true")
        assert res.status_code == 200
        data = res.json()
        assert "users" in data
        # All returned users should be banned
        for user in data["users"]:
            assert user.get("is_banned") == True
        print(f"✓ admin/users banned_only filter works ({len(data['users'])} banned)")
    
    def test_get_user_details(self):
        """Test GET /api/admin/users/{user_id}"""
        # First get a user ID
        list_res = self.session.get(f"{BASE_URL}/api/admin/users?limit=1")
        users = list_res.json().get("users", [])
        if not users:
            pytest.skip("No users to test")
        
        user_id = users[0]["id"]
        res = self.session.get(f"{BASE_URL}/api/admin/users/{user_id}")
        assert res.status_code == 200
        data = res.json()
        assert "user" in data
        assert "stats" in data
        assert data["user"]["id"] == user_id
        print(f"✓ admin/users/{user_id[:8]}... returns user details with stats")
    
    def test_get_user_not_found(self):
        """Test GET /api/admin/users/{user_id} with invalid ID"""
        res = self.session.get(f"{BASE_URL}/api/admin/users/invalid-id-12345")
        assert res.status_code == 404
        print("✓ admin/users returns 404 for invalid user ID")
    
    def test_ban_unban_user(self):
        """Test POST /api/admin/users/{user_id}/ban toggle"""
        # Get a non-admin user
        list_res = self.session.get(f"{BASE_URL}/api/admin/users?limit=10")
        users = list_res.json().get("users", [])
        test_user = None
        for u in users:
            if not u.get("is_admin") and u["id"] != self.admin_id:
                test_user = u
                break
        
        if not test_user:
            pytest.skip("No non-admin user to test ban")
        
        user_id = test_user["id"]
        initial_banned = test_user.get("is_banned", False)
        
        # Toggle ban
        res = self.session.post(f"{BASE_URL}/api/admin/users/{user_id}/ban")
        assert res.status_code == 200
        data = res.json()
        assert data["is_banned"] == (not initial_banned)
        print(f"✓ ban toggle: {initial_banned} -> {data['is_banned']}")
        
        # Toggle back
        res2 = self.session.post(f"{BASE_URL}/api/admin/users/{user_id}/ban")
        assert res2.status_code == 200
        assert res2.json()["is_banned"] == initial_banned
        print("✓ ban toggle restored to original state")
    
    def test_ban_admin_fails(self):
        """Test POST /api/admin/users/{user_id}/ban fails for admin users"""
        res = self.session.post(f"{BASE_URL}/api/admin/users/{self.admin_id}/ban")
        assert res.status_code == 403
        print("✓ cannot ban admin users")
    
    def test_adjust_coins(self):
        """Test POST /api/admin/users/{user_id}/adjust-coins"""
        # Get a user
        list_res = self.session.get(f"{BASE_URL}/api/admin/users?limit=5")
        users = list_res.json().get("users", [])
        if not users:
            pytest.skip("No users to test")
        
        user_id = users[0]["id"]
        initial_balance = users[0].get("coins_balance", 0)
        
        # Add coins
        res = self.session.post(f"{BASE_URL}/api/admin/users/{user_id}/adjust-coins", json={
            "amount": 500,
            "reason": "Test bonus"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["amount"] == 500
        assert data["new_balance"] == initial_balance + 500
        print(f"✓ adjust-coins added 500: {initial_balance} -> {data['new_balance']}")
        
        # Deduct coins back
        res2 = self.session.post(f"{BASE_URL}/api/admin/users/{user_id}/adjust-coins", json={
            "amount": -500,
            "reason": "Test deduction"
        })
        assert res2.status_code == 200
        assert res2.json()["new_balance"] == initial_balance
        print("✓ adjust-coins deducted 500 back to original")
    
    def test_adjust_coins_negative_balance_protection(self):
        """Test adjust-coins doesn't go below 0"""
        list_res = self.session.get(f"{BASE_URL}/api/admin/users?limit=1")
        users = list_res.json().get("users", [])
        if not users:
            pytest.skip("No users")
        
        user_id = users[0]["id"]
        
        # Try to deduct more than balance
        res = self.session.post(f"{BASE_URL}/api/admin/users/{user_id}/adjust-coins", json={
            "amount": -999999999,
            "reason": "Test negative protection"
        })
        assert res.status_code == 200
        assert res.json()["new_balance"] >= 0
        print("✓ adjust-coins protects against negative balance")
    
    def test_reset_pin(self):
        """Test POST /api/admin/users/{user_id}/reset-pin"""
        # Get test user
        test_phone = "9876543210"
        check_res = self.session.post(f"{BASE_URL}/api/auth/check-phone", json={"phone": test_phone})
        if not check_res.json().get("exists"):
            pytest.skip("Test user not available")
        
        # Get user ID
        list_res = self.session.get(f"{BASE_URL}/api/admin/users?search={test_phone}")
        users = list_res.json().get("users", [])
        if not users:
            pytest.skip("Test user not found in admin list")
        
        user_id = users[0]["id"]
        
        # Reset PIN
        res = self.session.post(f"{BASE_URL}/api/admin/users/{user_id}/reset-pin", json={
            "new_pin": "1234"
        })
        assert res.status_code == 200
        data = res.json()
        assert "message" in data
        print(f"✓ admin reset-pin successful for user {user_id[:8]}...")
        
        # Verify new PIN works
        verify_res = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "phone": test_phone,
            "pin": "1234"
        })
        assert verify_res.status_code == 200
        print("✓ admin-reset PIN works for login")
    
    def test_reset_pin_invalid_format(self):
        """Test reset-pin with invalid PIN format"""
        list_res = self.session.get(f"{BASE_URL}/api/admin/users?limit=1")
        users = list_res.json().get("users", [])
        if not users:
            pytest.skip("No users")
        
        user_id = users[0]["id"]
        
        res = self.session.post(f"{BASE_URL}/api/admin/users/{user_id}/reset-pin", json={
            "new_pin": "12"  # Too short
        })
        assert res.status_code == 422
        print("✓ reset-pin validates PIN format")


class TestHomepagePointsBanner:
    """Test that homepage shows total_points (not total_fantasy_points)"""
    
    def test_user_profile_has_total_points(self):
        """Verify user profile returns total_points field"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Login
        res = session.post(f"{BASE_URL}/api/auth/login", json={
            "phone": ADMIN_PHONE,
            "pin": ADMIN_PIN
        })
        assert res.status_code == 200
        data = res.json()
        token = data.get("token", {}).get("access_token")
        session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Get profile
        profile_res = session.get(f"{BASE_URL}/api/user/profile")
        assert profile_res.status_code == 200
        profile = profile_res.json()
        
        assert "total_points" in profile
        assert isinstance(profile["total_points"], (int, float))
        print(f"✓ user profile has total_points: {profile['total_points']}")
        
        # Verify auth/me also has it
        me_res = session.get(f"{BASE_URL}/api/auth/me")
        assert me_res.status_code == 200
        me_data = me_res.json()
        assert "total_points" in me_data
        print(f"✓ auth/me has total_points: {me_data['total_points']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
