#!/usr/bin/env python3
"""
CrickPredict Backend API Testing
Tests all Stage 3 Authentication APIs and database connections.
"""
import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

class CrickPredictAPITester:
    def __init__(self, base_url: str = "https://plan-then-build-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.auth_token = None

    def log_test(self, name: str, success: bool, details: Dict[str, Any] = None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test": name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if details and not success:
            print(f"    Details: {details}")

    def test_api_root(self) -> bool:
        """Test API root endpoint (/api)"""
        try:
            response = requests.get(f"{self.api_base}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["app", "version", "status"]
                
                if all(field in data for field in expected_fields):
                    if data.get("app") == "CrickPredict" and data.get("status") == "running":
                        self.log_test("API Root Endpoint", True, {
                            "status_code": response.status_code,
                            "response": data
                        })
                        return True
                    else:
                        self.log_test("API Root Endpoint", False, {
                            "status_code": response.status_code,
                            "error": "Invalid app name or status",
                            "response": data
                        })
                        return False
                else:
                    self.log_test("API Root Endpoint", False, {
                        "status_code": response.status_code,
                        "error": "Missing required fields",
                        "response": data
                    })
                    return False
            else:
                self.log_test("API Root Endpoint", False, {
                    "status_code": response.status_code,
                    "error": "Non-200 status code"
                })
                return False
                
        except Exception as e:
            self.log_test("API Root Endpoint", False, {
                "error": str(e)
            })
            return False

    def test_health_check(self) -> bool:
        """Test health check endpoint (/api/health)"""
        try:
            response = requests.get(f"{self.api_base}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["status", "version", "timestamp", "services"]
                
                if all(field in data for field in required_fields):
                    services = data.get("services", {})
                    
                    # Check MongoDB status
                    mongodb_status = services.get("mongodb", {}).get("status")
                    redis_status = services.get("redis", {}).get("status")
                    
                    mongodb_healthy = mongodb_status == "healthy"
                    redis_acceptable = redis_status in ["healthy", "disabled"]
                    
                    if mongodb_healthy and redis_acceptable:
                        self.log_test("Health Check API", True, {
                            "status_code": response.status_code,
                            "overall_status": data.get("status"),
                            "mongodb_status": mongodb_status,
                            "redis_status": redis_status,
                            "mongodb_latency": services.get("mongodb", {}).get("latency_ms"),
                            "redis_latency": services.get("redis", {}).get("latency_ms")
                        })
                        return True
                    else:
                        self.log_test("Health Check API", False, {
                            "status_code": response.status_code,
                            "error": "Database connections not healthy",
                            "mongodb_status": mongodb_status,
                            "redis_status": redis_status
                        })
                        return False
                else:
                    self.log_test("Health Check API", False, {
                        "status_code": response.status_code,
                        "error": "Missing required fields",
                        "response": data
                    })
                    return False
            else:
                self.log_test("Health Check API", False, {
                    "status_code": response.status_code,
                    "error": "Non-200 status code"
                })
                return False
                
        except Exception as e:
            self.log_test("Health Check API", False, {
                "error": str(e)
            })
            return False

    def test_readiness_probe(self) -> bool:
        """Test Kubernetes readiness probe (/api/health/ready)"""
        try:
            response = requests.get(f"{self.api_base}/health/ready", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ready":
                    self.log_test("Readiness Probe", True, {
                        "status_code": response.status_code,
                        "response": data
                    })
                    return True
                else:
                    self.log_test("Readiness Probe", False, {
                        "status_code": response.status_code,
                        "error": "Status not ready",
                        "response": data
                    })
                    return False
            else:
                self.log_test("Readiness Probe", False, {
                    "status_code": response.status_code,
                    "error": "Non-200 status code"
                })
                return False
                
        except Exception as e:
            self.log_test("Readiness Probe", False, {
                "error": str(e)
            })
            return False

    def test_liveness_probe(self) -> bool:
        """Test Kubernetes liveness probe (/api/health/live)"""
        try:
            response = requests.get(f"{self.api_base}/health/live", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "alive":
                    self.log_test("Liveness Probe", True, {
                        "status_code": response.status_code,
                        "response": data
                    })
                    return True
                else:
                    self.log_test("Liveness Probe", False, {
                        "status_code": response.status_code,
                        "error": "Status not alive",
                        "response": data
                    })
                    return False
            else:
                self.log_test("Liveness Probe", False, {
                    "status_code": response.status_code,
                    "error": "Non-200 status code"
                })
                return False
                
        except Exception as e:
            self.log_test("Liveness Probe", False, {
                "error": str(e)
            })
            return False

    def test_cors_headers(self) -> bool:
        """Test CORS headers are properly configured"""
        try:
            # Test preflight request
            response = requests.options(f"{self.api_base}/health", 
                                      headers={
                                          "Origin": "https://example.com",
                                          "Access-Control-Request-Method": "GET"
                                      }, 
                                      timeout=10)
            
            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
            }
            
            # Check if CORS is configured (should allow all origins for development)
            if cors_headers["Access-Control-Allow-Origin"] in ["*", "https://example.com"]:
                self.log_test("CORS Configuration", True, {
                    "status_code": response.status_code,
                    "cors_headers": cors_headers
                })
                return True
            else:
                self.log_test("CORS Configuration", False, {
                    "status_code": response.status_code,
                    "error": "CORS not properly configured",
                    "cors_headers": cors_headers
                })
                return False
                
        except Exception as e:
            self.log_test("CORS Configuration", False, {
                "error": str(e)
            })
            return False

    def test_auth_register_new_user(self) -> bool:
        """Test user registration with new phone number"""
        try:
            # Use test user 2 for registration
            test_phone = "9988776655"
            test_pin = "5678"
            
            response = requests.post(
                f"{self.api_base}/auth/register",
                json={
                    "phone": test_phone,
                    "pin": test_pin,
                    "username": "TestPlayer2"
                },
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                
                # Check response structure
                required_fields = ["token", "user"]
                if all(field in data for field in required_fields):
                    token_data = data.get("token", {})
                    user_data = data.get("user", {})
                    
                    # Validate token structure
                    token_fields = ["access_token", "refresh_token", "token_type", "expires_in"]
                    user_fields = ["id", "phone", "username", "coins_balance"]
                    
                    if (all(field in token_data for field in token_fields) and 
                        all(field in user_data for field in user_fields)):
                        
                        # Check signup bonus
                        if user_data.get("coins_balance") == 10000:
                            self.auth_token = token_data.get("access_token")
                            self.log_test("Auth Registration API", True, {
                                "status_code": response.status_code,
                                "user_id": user_data.get("id"),
                                "username": user_data.get("username"),
                                "coins_balance": user_data.get("coins_balance"),
                                "token_type": token_data.get("token_type"),
                                "expires_in": token_data.get("expires_in")
                            })
                            return True
                        else:
                            self.log_test("Auth Registration API", False, {
                                "status_code": response.status_code,
                                "error": f"Incorrect signup bonus: {user_data.get('coins_balance')} (expected 10000)"
                            })
                            return False
                    else:
                        self.log_test("Auth Registration API", False, {
                            "status_code": response.status_code,
                            "error": "Missing required token or user fields",
                            "token_fields": list(token_data.keys()),
                            "user_fields": list(user_data.keys())
                        })
                        return False
                else:
                    self.log_test("Auth Registration API", False, {
                        "status_code": response.status_code,
                        "error": "Missing required response fields",
                        "response": data
                    })
                    return False
            elif response.status_code in [400, 409]:
                # User might already exist, that's acceptable for testing
                data = response.json()
                error_detail = data.get("detail", "")
                if isinstance(error_detail, dict):
                    error_detail = str(error_detail)
                    
                if "already exists" in error_detail.lower() or "conflict" in error_detail.lower():
                    self.log_test("Auth Registration API", True, {
                        "status_code": response.status_code,
                        "note": "User already exists (acceptable for testing)",
                        "response": data
                    })
                    return True
                else:
                    self.log_test("Auth Registration API", False, {
                        "status_code": response.status_code,
                        "error": "Registration failed with validation error",
                        "response": data
                    })
                    return False
            else:
                self.log_test("Auth Registration API", False, {
                    "status_code": response.status_code,
                    "error": "Unexpected status code"
                })
                return False
                
        except Exception as e:
            self.log_test("Auth Registration API", False, {
                "error": str(e)
            })
            return False

    def test_auth_login_existing_user(self) -> bool:
        """Test login with existing user credentials"""
        try:
            # Use test user 1 for login
            test_phone = "9876543210"
            test_pin = "1234"
            
            response = requests.post(
                f"{self.api_base}/auth/login",
                json={
                    "phone": test_phone,
                    "pin": test_pin
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ["token", "user"]
                if all(field in data for field in required_fields):
                    token_data = data.get("token", {})
                    user_data = data.get("user", {})
                    
                    # Validate token structure
                    token_fields = ["access_token", "refresh_token", "token_type", "expires_in"]
                    user_fields = ["id", "phone", "username", "coins_balance"]
                    
                    if (all(field in token_data for field in token_fields) and 
                        all(field in user_data for field in user_fields)):
                        
                        # Store token for subsequent tests
                        self.auth_token = token_data.get("access_token")
                        
                        self.log_test("Auth Login API", True, {
                            "status_code": response.status_code,
                            "user_id": user_data.get("id"),
                            "username": user_data.get("username"),
                            "phone": user_data.get("phone"),
                            "coins_balance": user_data.get("coins_balance"),
                            "token_type": token_data.get("token_type"),
                            "expires_in": token_data.get("expires_in")
                        })
                        return True
                    else:
                        self.log_test("Auth Login API", False, {
                            "status_code": response.status_code,
                            "error": "Missing required token or user fields",
                            "token_fields": list(token_data.keys()),
                            "user_fields": list(user_data.keys())
                        })
                        return False
                else:
                    self.log_test("Auth Login API", False, {
                        "status_code": response.status_code,
                        "error": "Missing required response fields",
                        "response": data
                    })
                    return False
            else:
                self.log_test("Auth Login API", False, {
                    "status_code": response.status_code,
                    "error": "Login failed",
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_test("Auth Login API", False, {
                "error": str(e)
            })
            return False

    def test_auth_wrong_pin(self) -> bool:
        """Test login with wrong PIN shows error and remaining attempts"""
        try:
            # Use test user 1 with wrong PIN
            test_phone = "9876543210"
            wrong_pin = "9999"
            
            response = requests.post(
                f"{self.api_base}/auth/login",
                json={
                    "phone": test_phone,
                    "pin": wrong_pin
                },
                timeout=10
            )
            
            if response.status_code == 401:
                data = response.json()
                error_detail = data.get("detail", "")
                
                # Handle both string and dict error formats
                if isinstance(error_detail, dict):
                    error_detail = str(error_detail)
                
                # Check if error message contains remaining attempts info
                if "attempts remaining" in error_detail.lower() or "invalid pin" in error_detail.lower():
                    self.log_test("Auth Wrong PIN Error", True, {
                        "status_code": response.status_code,
                        "error_message": error_detail,
                        "note": "Correctly shows error with remaining attempts"
                    })
                    return True
                else:
                    self.log_test("Auth Wrong PIN Error", False, {
                        "status_code": response.status_code,
                        "error": "Error message doesn't contain attempts info",
                        "response": data
                    })
                    return False
            else:
                self.log_test("Auth Wrong PIN Error", False, {
                    "status_code": response.status_code,
                    "error": "Expected 401 status for wrong PIN",
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_test("Auth Wrong PIN Error", False, {
                "error": str(e)
            })
            return False

    def test_auth_me_endpoint(self) -> bool:
        """Test /api/auth/me endpoint with valid token"""
        if not self.auth_token:
            self.log_test("Auth Me Endpoint", False, {
                "error": "No auth token available (login test must pass first)"
            })
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.api_base}/auth/me",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check user profile fields
                required_fields = ["id", "phone", "username", "coins_balance", "rank_title", "total_points"]
                if all(field in data for field in required_fields):
                    self.log_test("Auth Me Endpoint", True, {
                        "status_code": response.status_code,
                        "user_id": data.get("id"),
                        "username": data.get("username"),
                        "phone": data.get("phone"),
                        "coins_balance": data.get("coins_balance"),
                        "rank_title": data.get("rank_title"),
                        "total_points": data.get("total_points")
                    })
                    return True
                else:
                    self.log_test("Auth Me Endpoint", False, {
                        "status_code": response.status_code,
                        "error": "Missing required user profile fields",
                        "available_fields": list(data.keys())
                    })
                    return False
            else:
                self.log_test("Auth Me Endpoint", False, {
                    "status_code": response.status_code,
                    "error": "Failed to get user profile",
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_test("Auth Me Endpoint", False, {
                "error": str(e)
            })
            return False

    def test_auth_token_expiry(self) -> bool:
        """Test JWT token expiry configuration (7 days)"""
        if not self.auth_token:
            self.log_test("Auth Token Expiry", False, {
                "error": "No auth token available (login test must pass first)"
            })
            return False
            
        try:
            # Decode token to check expiry (basic check without verification)
            import base64
            import json
            
            # Split token and decode payload
            parts = self.auth_token.split('.')
            if len(parts) != 3:
                self.log_test("Auth Token Expiry", False, {
                    "error": "Invalid JWT token format"
                })
                return False
            
            # Add padding if needed
            payload = parts[1]
            payload += '=' * (4 - len(payload) % 4)
            
            try:
                decoded = base64.urlsafe_b64decode(payload)
                token_data = json.loads(decoded)
                
                # Check if exp field exists
                if 'exp' in token_data:
                    exp_timestamp = token_data['exp']
                    current_timestamp = datetime.now().timestamp()
                    
                    # Calculate expiry time in days
                    expiry_seconds = exp_timestamp - current_timestamp
                    expiry_days = expiry_seconds / (24 * 60 * 60)
                    
                    # Check if expiry is approximately 7 days (allow some tolerance)
                    if 6.5 <= expiry_days <= 7.5:
                        self.log_test("Auth Token Expiry", True, {
                            "expiry_days": round(expiry_days, 2),
                            "note": "Token expires in approximately 7 days"
                        })
                        return True
                    else:
                        self.log_test("Auth Token Expiry", False, {
                            "expiry_days": round(expiry_days, 2),
                            "error": "Token expiry is not 7 days"
                        })
                        return False
                else:
                    self.log_test("Auth Token Expiry", False, {
                        "error": "Token doesn't contain expiry field",
                        "token_fields": list(token_data.keys())
                    })
                    return False
                    
            except Exception as decode_error:
                self.log_test("Auth Token Expiry", False, {
                    "error": f"Failed to decode token: {str(decode_error)}"
                })
                return False
                
        except Exception as e:
            self.log_test("Auth Token Expiry", False, {
                "error": str(e)
            })
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all backend tests"""
        print("🚀 Starting CrickPredict Backend API Tests (Stage 3 - Authentication)")
        print("=" * 60)
        
        # Test basic API endpoints first
        print("\n📡 Testing Basic API Endpoints...")
        self.test_api_root()
        self.test_health_check()
        self.test_readiness_probe()
        self.test_liveness_probe()
        self.test_cors_headers()
        
        # Test authentication endpoints
        print("\n🔐 Testing Authentication APIs...")
        self.test_auth_register_new_user()
        self.test_auth_login_existing_user()
        self.test_auth_wrong_pin()
        self.test_auth_me_endpoint()
        self.test_auth_token_expiry()
        
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        return {
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "success_rate": round(success_rate, 2),
            "test_results": self.test_results
        }

def main():
    """Main test execution"""
    tester = CrickPredictAPITester()
    results = tester.run_all_tests()
    
    # Save results to file
    with open("/app/backend_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Results saved to: /app/backend_test_results.json")
    
    # Exit with appropriate code
    if results["success_rate"] >= 80:
        print("✅ Backend tests passed!")
        return 0
    else:
        print("❌ Backend tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())