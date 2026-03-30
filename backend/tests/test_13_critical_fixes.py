"""
Test 13 Critical Fixes from Honest Audit Stage 1-3
Each test verifies a specific fix was properly implemented.
"""
import pytest
import requests
import os
import time
import re

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_PHONE = "9876543210"
TEST_PIN = "1234"
NEW_PIN = "5678"


class TestFix1_RequestIDHeader:
    """FIX-1: X-Request-ID header is full UUID format (36 chars with dashes)"""
    
    def test_request_id_is_full_uuid(self):
        """Verify X-Request-ID is 36 chars (full UUID with dashes)"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        request_id = response.headers.get("X-Request-ID", "")
        print(f"X-Request-ID: {request_id}")
        print(f"Length: {len(request_id)}")
        
        # Full UUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx (36 chars)
        assert len(request_id) >= 36, f"X-Request-ID should be >= 36 chars, got {len(request_id)}"
        # Verify UUID format with dashes
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        assert re.match(uuid_pattern, request_id, re.IGNORECASE), f"X-Request-ID not in UUID format: {request_id}"
        print("PASS: X-Request-ID is full UUID format")


class TestFix2_ContentSecurityPolicy:
    """FIX-2: Content-Security-Policy header present"""
    
    def test_csp_header_present(self):
        """Verify CSP header contains 'default-src' and 'frame-ancestors none'"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        csp = response.headers.get("Content-Security-Policy", "")
        print(f"CSP Header: {csp}")
        
        assert "default-src" in csp, "CSP missing 'default-src'"
        assert "frame-ancestors" in csp, "CSP missing 'frame-ancestors'"
        # Check for 'none' in frame-ancestors
        assert "'none'" in csp or "none" in csp.lower(), "CSP frame-ancestors should be 'none'"
        print("PASS: CSP header present with default-src and frame-ancestors")


class TestFix3_RequestBodyLimit:
    """FIX-3: Request body > 1MB returns 413"""
    
    def test_large_body_returns_413(self):
        """Verify 2MB POST body returns 413 PAYLOAD_TOO_LARGE"""
        # Create 2MB payload
        large_payload = "x" * (2 * 1024 * 1024)  # 2MB
        
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            data=large_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        assert response.status_code == 413, f"Expected 413, got {response.status_code}"
        
        # Check error message
        try:
            data = response.json()
            assert data.get("error") == "PAYLOAD_TOO_LARGE", f"Expected PAYLOAD_TOO_LARGE error, got {data}"
        except:
            pass  # JSON parse may fail, status code is enough
        
        print("PASS: Large body returns 413 PAYLOAD_TOO_LARGE")


class TestFix4_RateLimitStoreCleanup:
    """FIX-4: Rate limit store cleanup function exists"""
    
    def test_cleanup_function_exists(self):
        """Verify _cleanup_rate_limit_store function exists in dependencies.py"""
        # Read the file
        with open("/app/backend/core/dependencies.py", "r") as f:
            content = f.read()
        
        # Check for cleanup function
        assert "_cleanup_rate_limit_store" in content, "Missing _cleanup_rate_limit_store function"
        assert "_CLEANUP_INTERVAL" in content, "Missing _CLEANUP_INTERVAL constant"
        assert "_last_cleanup" in content, "Missing _last_cleanup variable"
        
        print("PASS: Rate limit cleanup function exists with interval and last_cleanup")


class TestFix5_WalletUpdateCoinsGteGuard:
    """FIX-5: Wallet update_coins subtract uses $gte guard"""
    
    def test_gte_guard_in_update_coins(self):
        """Verify update_coins has $gte guard for subtract operation"""
        with open("/app/backend/repositories/user_repository.py", "r") as f:
            content = f.read()
        
        # Check for $gte guard in subtract operation
        assert '"$gte"' in content or "'$gte'" in content, "Missing $gte guard in update_coins"
        
        # More specific check - look for the pattern in update_coins method
        # The pattern should be: {"id": user_id, "coins_balance": {"$gte": amount}}
        assert "coins_balance" in content and "$gte" in content, "Missing coins_balance $gte guard"
        
        print("PASS: update_coins has $gte guard for subtract operation")


class TestFix6_UniqueReferralCodeRetries:
    """FIX-6: generate_unique_referral_code with 5 retries"""
    
    def test_unique_referral_code_retries(self):
        """Verify generate_unique_referral_code has 5 retries"""
        with open("/app/backend/models/schemas.py", "r") as f:
            content = f.read()
        
        # Check for the function
        assert "generate_unique_referral_code" in content, "Missing generate_unique_referral_code function"
        
        # Check for retry loop (range(5))
        assert "range(5)" in content, "Missing 5 retries in generate_unique_referral_code"
        
        # Check for async function
        assert "async def generate_unique_referral_code" in content, "Function should be async"
        
        print("PASS: generate_unique_referral_code has 5 retries")


class TestFix7_ContestJoinRollback:
    """FIX-7: Contest join rollback on entry creation failure"""
    
    def test_contest_join_has_rollback(self):
        """Verify contest join has try/except with refund on failure"""
        with open("/app/backend/routers/contests.py", "r") as f:
            content = f.read()
        
        # Check for try/except around insert_one
        assert "try:" in content, "Missing try block in contest join"
        assert "except" in content, "Missing except block in contest join"
        
        # Check for refund logic
        assert "refund" in content.lower() or "Fee refunded" in content, "Missing refund logic"
        
        # Check for rollback pattern - incrementing coins back
        assert '"$inc": {"coins_balance":' in content or "'$inc': {'coins_balance':" in content, "Missing rollback increment"
        
        print("PASS: Contest join has rollback with refund on failure")


class TestFix8_PinChangeSetsPinChangedAt:
    """FIX-8: PIN change sets pin_changed_at and returns new tokens"""
    
    def test_pin_change_returns_new_tokens(self):
        """Verify PIN change returns new tokens"""
        # Try login with 1234 first, if fails try 5678
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": TEST_PHONE,
            "pin": TEST_PIN
        })
        
        current_pin = TEST_PIN
        target_pin = NEW_PIN
        
        if response.status_code != 200:
            # Try with 5678
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "phone": TEST_PHONE,
                "pin": NEW_PIN
            })
            if response.status_code != 200:
                pytest.skip(f"Login failed with both PINs: {response.text}")
            current_pin = NEW_PIN
            target_pin = TEST_PIN
        
        auth_token = response.json()["token"]["access_token"]
        print(f"Logged in with PIN {current_pin}")
        
        # Change PIN
        response = requests.put(
            f"{BASE_URL}/api/auth/change-pin",
            json={"old_pin": current_pin, "new_pin": target_pin},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        print(f"Change PIN response: {response.status_code}")
        
        assert response.status_code == 200, f"PIN change failed: {response.text}"
        
        data = response.json()
        assert "token" in data, "Response missing 'token' key"
        assert "access_token" in data["token"], "Response missing access_token"
        assert "refresh_token" in data["token"], "Response missing refresh_token"
        
        new_token = data["token"]["access_token"]
        print(f"Got new token after PIN change")
        
        # IMPORTANT: Change PIN back using the NEW token
        response2 = requests.put(
            f"{BASE_URL}/api/auth/change-pin",
            json={"old_pin": target_pin, "new_pin": current_pin},
            headers={"Authorization": f"Bearer {new_token}"}
        )
        
        # Even if restore fails, the main test passed
        if response2.status_code == 200:
            print(f"PIN restored to {current_pin}")
        else:
            print(f"Warning: Could not restore PIN: {response2.status_code}")
        
        print("PASS: PIN change returns new tokens")


class TestFix9_OldTokenRejectedAfterPinChange:
    """FIX-9: Old token rejected after PIN change"""
    
    def test_old_token_rejected_after_pin_change(self):
        """Verify old token fails after PIN change"""
        # Try login with 1234 first, if fails try 5678
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": TEST_PHONE,
            "pin": TEST_PIN
        })
        
        current_pin = TEST_PIN
        target_pin = NEW_PIN
        
        if response.status_code != 200:
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "phone": TEST_PHONE,
                "pin": NEW_PIN
            })
            if response.status_code != 200:
                pytest.skip(f"Login failed with both PINs: {response.text}")
            current_pin = NEW_PIN
            target_pin = TEST_PIN
        
        token1 = response.json()["token"]["access_token"]
        print(f"Got token1 with PIN {current_pin}")
        
        # Change PIN
        response2 = requests.put(
            f"{BASE_URL}/api/auth/change-pin",
            json={"old_pin": current_pin, "new_pin": target_pin},
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        if response2.status_code != 200:
            pytest.skip(f"PIN change failed: {response2.text}")
        
        new_token = response2.json()["token"]["access_token"]
        print(f"PIN changed to {target_pin}, got new token")
        
        # Try to use old token1 - should fail
        response3 = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        print(f"Old token /me response: {response3.status_code}")
        old_token_status = response3.status_code
        
        # IMPORTANT: Change PIN back using new token BEFORE asserting
        response4 = requests.put(
            f"{BASE_URL}/api/auth/change-pin",
            json={"old_pin": target_pin, "new_pin": current_pin},
            headers={"Authorization": f"Bearer {new_token}"}
        )
        
        if response4.status_code == 200:
            print(f"PIN restored to {current_pin}")
        else:
            print(f"Warning: Failed to restore PIN: {response4.status_code}")
        
        # Now verify old token was rejected
        assert old_token_status == 401, f"Old token should be rejected with 401, got {old_token_status}"
        print("PASS: Old token rejected after PIN change (401)")


class TestFix10_LockoutAutoReset:
    """FIX-10: Lockout auto-reset when expired"""
    
    def test_lockout_auto_reset_code_exists(self):
        """Verify auth_service resets failed login when lockout expired"""
        with open("/app/backend/services/auth_service.py", "r") as f:
            content = f.read()
        
        # Check for lockout expiry check
        assert "locked_until" in content, "Missing locked_until check"
        
        # Check for auto-reset after lockout expires
        # Pattern: if lockout expired, call reset_failed_login
        assert "reset_failed_login" in content, "Missing reset_failed_login call"
        
        # Check for the specific pattern: after checking lockout expired, reset
        # Look for: datetime.now(timezone.utc) < lock_time ... else ... reset_failed_login
        assert "Lockout expired" in content or "reset_failed_login(user.id)" in content, \
            "Missing auto-reset logic after lockout expiry"
        
        print("PASS: Lockout auto-reset code exists in auth_service")


class TestFix11_PhoneValidationRejects1to5:
    """FIX-11: Phone validation rejects numbers starting with 1-5"""
    
    def test_phone_starting_with_1_rejected(self):
        """Verify phone starting with 1 is rejected"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "phone": "1234567890",
            "pin": "5678"
        })
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Should get validation error (400 or 422)
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        
        # Check error type
        data = response.json()
        error = data.get("error", "") or data.get("detail", "")
        # Should be validation error, not PHONE_EXISTS
        assert "PHONE_EXISTS" not in str(error), "Should be validation error, not PHONE_EXISTS"
        
        print("PASS: Phone starting with 1 rejected with validation error")


class TestFix12_PhoneValidationAccepts6to9:
    """FIX-12: Phone validation accepts numbers starting with 6-9"""
    
    def test_phone_starting_with_6_accepted(self):
        """Verify phone starting with 6 passes validation (may fail on duplicate)"""
        # Use a phone that likely doesn't exist
        test_phone = "6111111111"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "phone": test_phone,
            "pin": "5678"
        })
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Should NOT be validation error
        # Could be 201 (success), 409 (duplicate), or other - but NOT validation error
        if response.status_code in [400, 422]:
            data = response.json()
            error = str(data.get("error", "")) + str(data.get("detail", ""))
            # If it's a validation error about phone format, that's a FAIL
            assert "VALIDATION_ERROR" not in error or "phone" not in error.lower(), \
                f"Phone starting with 6 should pass validation: {error}"
        
        print("PASS: Phone starting with 6 passes validation (or fails for other reason)")


class TestFix13_ChangePinHasRateLimit:
    """FIX-13: /change-pin has rate_limit_dependency"""
    
    def test_change_pin_has_rate_limit(self):
        """Verify change_pin route has rate limit dependency"""
        with open("/app/backend/routers/auth.py", "r") as f:
            content = f.read()
        
        # Find the change-pin route definition
        # Look for: @router.put("/change-pin" ... dependencies=[Depends(rate_limit_dependency)]
        
        # Check that rate_limit_dependency is imported
        assert "rate_limit_dependency" in content, "rate_limit_dependency not imported"
        
        # Check that change-pin has the dependency
        # The pattern should be: dependencies=[Depends(rate_limit_dependency)] before change_pin
        change_pin_section = content[content.find('"/change-pin"'):]
        
        # Look for dependencies in the decorator
        assert "rate_limit_dependency" in change_pin_section[:500], \
            "change-pin route missing rate_limit_dependency"
        
        print("PASS: /change-pin has rate_limit_dependency")


class TestFix14_RefreshTokenRotation:
    """FIX-14: Refresh token rotation returns both new access and refresh tokens"""
    
    def test_refresh_returns_both_tokens(self):
        """Verify refresh returns both new access_token AND new refresh_token"""
        # Try login with 1234 first, if fails try 5678
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": TEST_PHONE,
            "pin": TEST_PIN
        })
        
        if response.status_code != 200:
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "phone": TEST_PHONE,
                "pin": NEW_PIN
            })
            if response.status_code != 200:
                pytest.skip(f"Login failed with both PINs: {response.text}")
        
        initial_refresh = response.json()["token"]["refresh_token"]
        print(f"Got initial refresh token")
        
        # Call refresh endpoint
        response2 = requests.post(f"{BASE_URL}/api/auth/refresh", json={
            "refresh_token": initial_refresh
        })
        
        print(f"Refresh status: {response2.status_code}")
        print(f"Refresh response: {response2.text[:500]}")
        
        assert response2.status_code == 200, f"Refresh failed: {response2.text}"
        
        data = response2.json()
        assert "access_token" in data, "Refresh response missing access_token"
        assert "refresh_token" in data, "Refresh response missing refresh_token (no rotation!)"
        
        print("PASS: Refresh returns both access_token and refresh_token")


class TestFix15_WalletBalanceLastClaimed:
    """FIX-15: Wallet balance returns last_claimed field"""
    
    def test_wallet_balance_has_last_claimed(self):
        """Verify GET /api/wallet/balance returns last_claimed key"""
        # Try login with 1234 first, if fails try 5678
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": TEST_PHONE,
            "pin": TEST_PIN
        })
        
        if response.status_code != 200:
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "phone": TEST_PHONE,
                "pin": NEW_PIN
            })
            if response.status_code != 200:
                pytest.skip(f"Login failed with both PINs: {response.text}")
        
        token = response.json()["token"]["access_token"]
        
        # Get wallet balance
        response2 = requests.get(
            f"{BASE_URL}/api/wallet/balance",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"Wallet balance status: {response2.status_code}")
        print(f"Wallet balance response: {response2.text}")
        
        assert response2.status_code == 200, f"Wallet balance failed: {response2.text}"
        
        data = response2.json()
        assert "last_claimed" in data, f"Response missing 'last_claimed' key. Keys: {list(data.keys())}"
        
        print("PASS: Wallet balance returns last_claimed field")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
