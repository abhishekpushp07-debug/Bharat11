#!/usr/bin/env python3
"""
CrickPredict Backend API Testing
Tests all Stage 1 Foundation APIs and database connections.
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

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all backend tests"""
        print("🚀 Starting CrickPredict Backend API Tests")
        print("=" * 50)
        
        # Test API endpoints
        self.test_api_root()
        self.test_health_check()
        self.test_readiness_probe()
        self.test_liveness_probe()
        self.test_cors_headers()
        
        print("\n" + "=" * 50)
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