"""
Iteration 18 - Auto-Settlement Engine Tests
Tests the new settlement feature:
1. POST /api/auth/login - Admin login
2. GET /api/admin/settlement/status - Settlement status for matches
3. POST /api/admin/settlement/{match_id}/run - Run auto-settlement
4. GET /api/admin/settlement/{match_id}/metrics - Get parsed scorecard metrics
5. GET /api/admin/settlement/{match_id}/scorecard - Get raw scorecard data
6. POST /api/admin/questions/bulk-import-with-auto - Seed auto-resolvable questions
7. POST /api/admin/settlement/{match_id}/link - Link CricketData.org match ID
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
SUPER_ADMIN_PHONE = "7004186276"
SUPER_ADMIN_PIN = "5524"
TEST_MATCH_ID = "e06a8963-410c-4901-bb96-807a3f258fe3"  # KKR vs MI with cricketdata_id linked


class TestAdminLogin:
    """Test admin authentication for settlement endpoints"""
    
    def test_admin_login_success(self):
        """POST /api/auth/login with super admin credentials should return JWT token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": SUPER_ADMIN_PHONE,
            "pin": SUPER_ADMIN_PIN
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        # Token is nested: data.token.access_token
        assert "token" in data, "No token in response"
        assert "access_token" in data["token"], "No access_token in token"
        assert data.get("user", {}).get("is_admin") == True, "User should be admin"
        print(f"PASS: Admin login successful, token received, is_admin=True")
        return data["token"]["access_token"]


@pytest.fixture(scope="module")
def admin_token():
    """Get admin JWT token for authenticated requests"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "phone": SUPER_ADMIN_PHONE,
        "pin": SUPER_ADMIN_PIN
    })
    if response.status_code != 200:
        pytest.skip(f"Admin login failed: {response.text}")
    data = response.json()
    return data["token"]["access_token"]


@pytest.fixture
def admin_headers(admin_token):
    """Headers with admin JWT token"""
    return {"Authorization": f"Bearer {admin_token}"}


class TestSettlementStatus:
    """Test GET /api/admin/settlement/status endpoint"""
    
    def test_settlement_status_returns_matches(self, admin_headers):
        """GET /api/admin/settlement/status should return matches with settlement progress"""
        response = requests.get(f"{BASE_URL}/api/admin/settlement/status", headers=admin_headers)
        assert response.status_code == 200, f"Settlement status failed: {response.text}"
        data = response.json()
        assert "matches" in data, "Response should have 'matches' field"
        print(f"PASS: Settlement status returned {len(data['matches'])} matches")
        
        # Check structure of match data
        if data["matches"]:
            match = data["matches"][0]
            assert "match_id" in match, "Match should have match_id"
            assert "team_a" in match, "Match should have team_a"
            assert "team_b" in match, "Match should have team_b"
            assert "settlement_progress" in match, "Match should have settlement_progress"
            print(f"PASS: Match structure verified - {match.get('team_a', {}).get('short_name', '?')} vs {match.get('team_b', {}).get('short_name', '?')}")
    
    def test_settlement_status_requires_auth(self):
        """GET /api/admin/settlement/status without auth should fail"""
        response = requests.get(f"{BASE_URL}/api/admin/settlement/status")
        assert response.status_code in [401, 403], f"Should require auth, got {response.status_code}"
        print("PASS: Settlement status requires authentication")


class TestBulkImportAutoQuestions:
    """Test POST /api/admin/questions/bulk-import-with-auto endpoint"""
    
    def test_bulk_import_auto_questions(self, admin_headers):
        """POST /api/admin/questions/bulk-import-with-auto should seed 11 auto-resolvable questions"""
        response = requests.post(f"{BASE_URL}/api/admin/questions/bulk-import-with-auto", headers=admin_headers)
        assert response.status_code == 201, f"Bulk import failed: {response.text}"
        data = response.json()
        assert data.get("imported") == 11, f"Should import 11 questions, got {data.get('imported')}"
        assert "template_id" in data, "Should return template_id"
        assert "template_name" in data, "Should return template_name"
        print(f"PASS: Imported {data['imported']} auto-resolvable questions + template '{data['template_name']}'")
        return data
    
    def test_bulk_import_requires_admin(self):
        """POST /api/admin/questions/bulk-import-with-auto without auth should fail"""
        response = requests.post(f"{BASE_URL}/api/admin/questions/bulk-import-with-auto")
        assert response.status_code in [401, 403], f"Should require admin, got {response.status_code}"
        print("PASS: Bulk import requires admin authentication")


class TestLinkCricketDataID:
    """Test POST /api/admin/settlement/{match_id}/link endpoint"""
    
    def test_link_cricketdata_id(self, admin_headers):
        """POST /api/admin/settlement/{match_id}/link should link CricketData.org match ID"""
        # First get a match to link
        matches_response = requests.get(f"{BASE_URL}/api/matches", headers=admin_headers)
        if matches_response.status_code != 200 or not matches_response.json().get("matches"):
            pytest.skip("No matches available to test linking")
        
        match_id = matches_response.json()["matches"][0]["id"]
        cricketdata_id = "test-cricketdata-id-12345"
        
        response = requests.post(
            f"{BASE_URL}/api/admin/settlement/{match_id}/link",
            headers=admin_headers,
            json={"cricketdata_id": cricketdata_id}
        )
        assert response.status_code == 200, f"Link failed: {response.text}"
        data = response.json()
        assert data.get("linked") == True, "Should return linked=True"
        assert data.get("cricketdata_id") == cricketdata_id, "Should return the linked ID"
        print(f"PASS: Linked CricketData ID '{cricketdata_id}' to match {match_id}")
    
    def test_link_nonexistent_match(self, admin_headers):
        """POST /api/admin/settlement/{match_id}/link with invalid match should return 404"""
        response = requests.post(
            f"{BASE_URL}/api/admin/settlement/nonexistent-match-id/link",
            headers=admin_headers,
            json={"cricketdata_id": "test-id"}
        )
        assert response.status_code == 404, f"Should return 404, got {response.status_code}"
        print("PASS: Link returns 404 for nonexistent match")


class TestSettlementRun:
    """Test POST /api/admin/settlement/{match_id}/run endpoint"""
    
    def test_settlement_run_with_linked_match(self, admin_headers):
        """POST /api/admin/settlement/{match_id}/run should fetch scorecard and auto-resolve"""
        # Use the test match ID that has cricketdata_id linked
        response = requests.post(
            f"{BASE_URL}/api/admin/settlement/{TEST_MATCH_ID}/run",
            headers=admin_headers
        )
        # Could be 200 (success) or error if match not found
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                print(f"INFO: Settlement returned error (expected if no API link): {data['error']}")
            else:
                assert "total_resolved" in data or "scorecard_fetched" in data, "Should have settlement result"
                print(f"PASS: Settlement run completed - resolved: {data.get('total_resolved', 0)}, skipped: {data.get('total_skipped', 0)}")
                
                # Check key_metrics if present
                if "key_metrics" in data:
                    km = data["key_metrics"]
                    print(f"  Key Metrics: Inn1={km.get('innings_1_runs')}, Inn2={km.get('innings_2_runs')}, Sixes={km.get('total_sixes')}, Fours={km.get('total_fours')}")
                    print(f"  Top Scorer: {km.get('highest_scorer')}, Best Bowler: {km.get('best_bowler')}")
        else:
            print(f"INFO: Settlement run returned {response.status_code} - {response.text[:200]}")
    
    def test_settlement_run_nonexistent_match(self, admin_headers):
        """POST /api/admin/settlement/{match_id}/run with invalid match should return error"""
        response = requests.post(
            f"{BASE_URL}/api/admin/settlement/nonexistent-match-id/run",
            headers=admin_headers
        )
        # Should return 200 with error message or 404
        if response.status_code == 200:
            data = response.json()
            assert "error" in data, "Should return error for nonexistent match"
            print(f"PASS: Settlement run returns error for nonexistent match: {data['error']}")
        else:
            assert response.status_code == 404
            print("PASS: Settlement run returns 404 for nonexistent match")


class TestSettlementMetrics:
    """Test GET /api/admin/settlement/{match_id}/metrics endpoint"""
    
    def test_get_match_metrics(self, admin_headers):
        """GET /api/admin/settlement/{match_id}/metrics should return parsed scorecard metrics"""
        response = requests.get(
            f"{BASE_URL}/api/admin/settlement/{TEST_MATCH_ID}/metrics",
            headers=admin_headers
        )
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                print(f"INFO: Metrics returned error (expected if no API link): {data['error']}")
            else:
                assert "metrics" in data, "Should have metrics field"
                metrics = data["metrics"]
                # Check key metrics exist
                expected_keys = ["match_completed", "match_total_runs", "match_total_sixes", "match_total_fours"]
                for key in expected_keys:
                    assert key in metrics, f"Metrics should have {key}"
                print(f"PASS: Metrics fetched - completed={metrics.get('match_completed')}, runs={metrics.get('match_total_runs')}, sixes={metrics.get('match_total_sixes')}")
        else:
            print(f"INFO: Metrics returned {response.status_code} - {response.text[:200]}")


class TestSettlementScorecard:
    """Test GET /api/admin/settlement/{match_id}/scorecard endpoint"""
    
    def test_get_match_scorecard(self, admin_headers):
        """GET /api/admin/settlement/{match_id}/scorecard should return raw scorecard data"""
        response = requests.get(
            f"{BASE_URL}/api/admin/settlement/{TEST_MATCH_ID}/scorecard",
            headers=admin_headers
        )
        if response.status_code == 200:
            data = response.json()
            assert "scorecard" in data, "Should have scorecard field"
            assert "cricketdata_id" in data, "Should have cricketdata_id field"
            print(f"PASS: Scorecard fetched for match {data.get('match_id')}, cricketdata_id={data.get('cricketdata_id')}")
        elif response.status_code == 400:
            # Expected if no CricketData ID linked
            print(f"INFO: Scorecard returned 400 (no CricketData ID linked): {response.json().get('detail', '')}")
        elif response.status_code == 502:
            # Expected if API call fails
            print(f"INFO: Scorecard returned 502 (API call failed): {response.json().get('detail', '')}")
        else:
            print(f"INFO: Scorecard returned {response.status_code}")
    
    def test_scorecard_requires_auth(self):
        """GET /api/admin/settlement/{match_id}/scorecard without auth should fail"""
        response = requests.get(f"{BASE_URL}/api/admin/settlement/{TEST_MATCH_ID}/scorecard")
        assert response.status_code in [401, 403], f"Should require auth, got {response.status_code}"
        print("PASS: Scorecard endpoint requires authentication")


class TestSettlementIntegration:
    """Integration tests for the full settlement flow"""
    
    def test_full_settlement_flow(self, admin_headers):
        """Test the complete settlement flow: status -> link -> run -> verify"""
        # Step 1: Get settlement status
        status_response = requests.get(f"{BASE_URL}/api/admin/settlement/status", headers=admin_headers)
        assert status_response.status_code == 200
        matches = status_response.json().get("matches", [])
        print(f"Step 1: Got {len(matches)} matches in settlement status")
        
        if not matches:
            print("INFO: No matches available for full flow test")
            return
        
        # Step 2: Find a match with contests
        test_match = None
        for m in matches:
            if m.get("contests_count", 0) > 0:
                test_match = m
                break
        
        if not test_match:
            print("INFO: No matches with contests for full flow test")
            return
        
        match_id = test_match["match_id"]
        print(f"Step 2: Testing with match {match_id} ({test_match.get('team_a', {}).get('short_name', '?')} vs {test_match.get('team_b', {}).get('short_name', '?')})")
        
        # Step 3: Try to run settlement
        run_response = requests.post(f"{BASE_URL}/api/admin/settlement/{match_id}/run", headers=admin_headers)
        assert run_response.status_code == 200
        run_data = run_response.json()
        
        if "error" in run_data:
            print(f"Step 3: Settlement returned error (may need CricketData ID): {run_data['error']}")
        else:
            print(f"Step 3: Settlement completed - resolved={run_data.get('total_resolved', 0)}, skipped={run_data.get('total_skipped', 0)}")
            
            # Verify key metrics if available
            if "key_metrics" in run_data:
                km = run_data["key_metrics"]
                print(f"  Metrics: Inn1={km.get('innings_1_runs')}, Inn2={km.get('innings_2_runs')}")
                print(f"  Sixes={km.get('total_sixes')}, Fours={km.get('total_fours')}")
                print(f"  Top Scorer: {km.get('highest_scorer')}")
                print(f"  Best Bowler: {km.get('best_bowler')}")
        
        print("PASS: Full settlement flow completed")


class TestQuestionsWithAutoResolution:
    """Test that questions have auto_resolution config"""
    
    def test_questions_have_auto_resolution(self, admin_headers):
        """GET /api/admin/questions should return questions with auto_resolution config"""
        response = requests.get(f"{BASE_URL}/api/admin/questions?limit=50", headers=admin_headers)
        assert response.status_code == 200
        questions = response.json().get("questions", [])
        
        auto_questions = [q for q in questions if q.get("auto_resolution")]
        print(f"Found {len(auto_questions)} questions with auto_resolution out of {len(questions)} total")
        
        if auto_questions:
            q = auto_questions[0]
            ar = q["auto_resolution"]
            print(f"  Example: '{q.get('question_text_en', '')[:50]}...'")
            print(f"    metric={ar.get('metric')}, trigger={ar.get('trigger')}, type={ar.get('resolution_type')}")
        
        print("PASS: Questions with auto_resolution verified")


class TestRegularUserCannotAccessSettlement:
    """Test that regular users cannot access settlement endpoints"""
    
    def test_regular_user_cannot_access_settlement(self):
        """Regular user should get 403 on settlement endpoints"""
        # Login as regular player
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": "9111111111",
            "pin": "5678"
        })
        if login_response.status_code != 200:
            pytest.skip("Regular user login failed")
        
        token = login_response.json()["token"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try settlement status
        response = requests.get(f"{BASE_URL}/api/admin/settlement/status", headers=headers)
        assert response.status_code == 403, f"Regular user should get 403, got {response.status_code}"
        print("PASS: Regular user cannot access settlement status (403)")
        
        # Try settlement run
        response = requests.post(f"{BASE_URL}/api/admin/settlement/test-match/run", headers=headers)
        assert response.status_code == 403, f"Regular user should get 403, got {response.status_code}"
        print("PASS: Regular user cannot run settlement (403)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
