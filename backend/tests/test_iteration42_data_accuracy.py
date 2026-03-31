"""
Iteration 42 - IPL Data Accuracy Tests
Tests for:
1. Only IPL teams in matches (MI, CSK, RCB, KKR, DC, PBKS, RR, SRH, GT, LSG)
2. Completed matches have non-zero scores and match_winner
3. Score normalization (both r/w/o AND runs/wickets/overs)
4. MI vs CSK status fix (live -> upcoming)
5. No duplicate matches (total = 70)
6. Status counts: 67 upcoming, 0 live, 3 completed
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# All 10 IPL team short names
IPL_TEAMS = {"MI", "CSK", "RCB", "KKR", "DC", "PBKS", "RR", "SRH", "GT", "LSG"}


class TestIPLDataAccuracy:
    """Tests for IPL data accuracy and completeness"""

    def test_api_health(self):
        """Test API is accessible"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("API health check passed")

    def test_total_matches_count(self):
        """Total matches should be exactly 70"""
        response = requests.get(f"{BASE_URL}/api/matches?limit=50")
        assert response.status_code == 200
        data = response.json()
        total = data.get("total", 0)
        assert total == 70, f"Expected 70 matches, got {total}"
        print(f"Total matches: {total} (expected 70)")

    def test_only_ipl_teams(self):
        """All matches should have only IPL teams"""
        response = requests.get(f"{BASE_URL}/api/matches?limit=50")
        assert response.status_code == 200
        data = response.json()
        
        teams_found = set()
        non_ipl_teams = set()
        
        for match in data.get("matches", []):
            team_a = match.get("team_a", {}).get("short_name", "")
            team_b = match.get("team_b", {}).get("short_name", "")
            teams_found.add(team_a)
            teams_found.add(team_b)
            
            if team_a not in IPL_TEAMS:
                non_ipl_teams.add(team_a)
            if team_b not in IPL_TEAMS:
                non_ipl_teams.add(team_b)
        
        assert len(non_ipl_teams) == 0, f"Non-IPL teams found: {non_ipl_teams}"
        assert teams_found == IPL_TEAMS, f"Expected all 10 IPL teams, found: {teams_found}"
        print(f"All 10 IPL teams found: {sorted(teams_found)}")

    def test_completed_matches_count(self):
        """Should have exactly 3 completed matches"""
        response = requests.get(f"{BASE_URL}/api/matches?status=completed&limit=10")
        assert response.status_code == 200
        data = response.json()
        total = data.get("total", 0)
        assert total == 3, f"Expected 3 completed matches, got {total}"
        print(f"Completed matches: {total}")

    def test_upcoming_matches_count(self):
        """Should have exactly 67 upcoming matches"""
        response = requests.get(f"{BASE_URL}/api/matches?status=upcoming&limit=10")
        assert response.status_code == 200
        data = response.json()
        total = data.get("total", 0)
        assert total == 67, f"Expected 67 upcoming matches, got {total}"
        print(f"Upcoming matches: {total}")

    def test_live_matches_count(self):
        """Should have 0 live matches"""
        response = requests.get(f"{BASE_URL}/api/matches?status=live&limit=10")
        assert response.status_code == 200
        data = response.json()
        total = data.get("total", 0)
        assert total == 0, f"Expected 0 live matches, got {total}"
        print(f"Live matches: {total}")

    def test_completed_matches_have_nonzero_scores(self):
        """All completed matches should have non-zero scores"""
        response = requests.get(f"{BASE_URL}/api/matches?status=completed&limit=10")
        assert response.status_code == 200
        data = response.json()
        
        for match in data.get("matches", []):
            team_a = match.get("team_a", {}).get("short_name", "")
            team_b = match.get("team_b", {}).get("short_name", "")
            scores = match.get("live_score", {}).get("scores", [])
            
            assert len(scores) >= 2, f"{team_a} vs {team_b}: Expected at least 2 innings scores"
            
            for score in scores:
                runs = score.get("r", 0) or score.get("runs", 0)
                assert runs > 0, f"{team_a} vs {team_b}: Score has 0 runs - {score}"
            
            print(f"{team_a} vs {team_b}: Scores verified (non-zero)")

    def test_completed_matches_have_match_winner(self):
        """All completed matches should have match_winner populated"""
        response = requests.get(f"{BASE_URL}/api/matches?status=completed&limit=10")
        assert response.status_code == 200
        data = response.json()
        
        for match in data.get("matches", []):
            team_a = match.get("team_a", {}).get("short_name", "")
            team_b = match.get("team_b", {}).get("short_name", "")
            winner = match.get("match_winner", "")
            
            assert winner and winner != "N/A", f"{team_a} vs {team_b}: match_winner not populated"
            print(f"{team_a} vs {team_b}: Winner = {winner}")

    def test_score_normalization_both_formats(self):
        """Scores should have BOTH r/w/o AND runs/wickets/overs fields"""
        response = requests.get(f"{BASE_URL}/api/matches?status=completed&limit=10")
        assert response.status_code == 200
        data = response.json()
        
        for match in data.get("matches", []):
            team_a = match.get("team_a", {}).get("short_name", "")
            team_b = match.get("team_b", {}).get("short_name", "")
            scores = match.get("live_score", {}).get("scores", [])
            
            for score in scores:
                # Check short form (r/w/o)
                assert "r" in score, f"{team_a} vs {team_b}: Missing 'r' field"
                assert "w" in score, f"{team_a} vs {team_b}: Missing 'w' field"
                assert "o" in score, f"{team_a} vs {team_b}: Missing 'o' field"
                
                # Check long form (runs/wickets/overs)
                assert "runs" in score, f"{team_a} vs {team_b}: Missing 'runs' field"
                assert "wickets" in score, f"{team_a} vs {team_b}: Missing 'wickets' field"
                assert "overs" in score, f"{team_a} vs {team_b}: Missing 'overs' field"
                
                # Values should match
                assert score["r"] == score["runs"], f"r != runs: {score['r']} != {score['runs']}"
                assert score["w"] == score["wickets"], f"w != wickets: {score['w']} != {score['wickets']}"
                assert score["o"] == score["overs"], f"o != overs: {score['o']} != {score['overs']}"
            
            print(f"{team_a} vs {team_b}: Score normalization verified")

    def test_mi_vs_csk_status_is_upcoming(self):
        """MI vs CSK match should be 'upcoming' not 'live'"""
        response = requests.get(f"{BASE_URL}/api/matches?limit=50")
        assert response.status_code == 200
        data = response.json()
        
        mi_csk_match = None
        for match in data.get("matches", []):
            team_a = match.get("team_a", {}).get("short_name", "")
            team_b = match.get("team_b", {}).get("short_name", "")
            if (team_a == "MI" and team_b == "CSK") or (team_a == "CSK" and team_b == "MI"):
                mi_csk_match = match
                break
        
        assert mi_csk_match is not None, "MI vs CSK match not found"
        status = mi_csk_match.get("status", "")
        assert status == "upcoming", f"MI vs CSK status should be 'upcoming', got '{status}'"
        print(f"MI vs CSK status: {status} (correct)")

    def test_no_duplicate_matches(self):
        """No duplicate matches by cricketdata_id"""
        response = requests.get(f"{BASE_URL}/api/matches?limit=50")
        assert response.status_code == 200
        data = response.json()
        
        cricketdata_ids = []
        for match in data.get("matches", []):
            cd_id = match.get("cricketdata_id") or match.get("external_match_id")
            if cd_id:
                cricketdata_ids.append(cd_id)
        
        unique_ids = set(cricketdata_ids)
        assert len(cricketdata_ids) == len(unique_ids), f"Duplicate cricketdata_ids found: {len(cricketdata_ids)} total, {len(unique_ids)} unique"
        print(f"No duplicates: {len(unique_ids)} unique cricketdata_ids")


class TestLiveSyncEndpoints:
    """Tests for live sync endpoints"""

    @pytest.fixture
    def auth_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": "7004186276",
            "pin": "5524"
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("token", {}).get("access_token", "")
        pytest.skip("Authentication failed")

    def test_live_status_endpoint(self):
        """Test /api/matches/live/status returns API info"""
        response = requests.get(f"{BASE_URL}/api/matches/live/status")
        assert response.status_code == 200
        data = response.json()
        
        assert "cricketdata_key_set" in data
        assert data["cricketdata_key_set"] == True, "Cricket API key not set"
        print(f"Cricket API status: key_set={data['cricketdata_key_set']}, hits_today={data.get('api_hits_today', 0)}")

    def test_sync_live_matches_ipl_only(self, auth_token):
        """POST /api/matches/live/sync?ipl_only=true should return only IPL matches"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BASE_URL}/api/matches/live/sync?ipl_only=true", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        total_from_source = data.get("total_from_source", 0)
        # IPL-only should return <= 5 matches (only current/recent IPL matches)
        assert total_from_source <= 5, f"Expected <= 5 IPL matches from source, got {total_from_source}"
        print(f"Live sync IPL only: {total_from_source} matches from source")

    def test_sync_ipl_schedule(self, auth_token):
        """POST /api/matches/live/sync-ipl-schedule should sync 70 matches"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BASE_URL}/api/matches/live/sync-ipl-schedule", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        total_from_api = data.get("total_from_api", 0)
        synced = data.get("synced", 0)
        errors = data.get("errors", [])
        
        assert total_from_api == 70, f"Expected 70 matches from API, got {total_from_api}"
        assert len(errors) == 0, f"Sync errors: {errors}"
        print(f"IPL schedule sync: {total_from_api} from API, {synced} synced, {len(errors)} errors")


class TestMatchDetailEndpoints:
    """Tests for match detail endpoints"""

    def test_get_completed_match_detail(self):
        """Get detail of a completed match"""
        # First get a completed match ID
        response = requests.get(f"{BASE_URL}/api/matches?status=completed&limit=1")
        assert response.status_code == 200
        data = response.json()
        
        matches = data.get("matches", [])
        assert len(matches) > 0, "No completed matches found"
        
        match_id = matches[0].get("id")
        
        # Get match detail
        response = requests.get(f"{BASE_URL}/api/matches/{match_id}")
        assert response.status_code == 200
        match = response.json()
        
        assert match.get("status") == "completed"
        assert match.get("match_winner"), "match_winner not populated"
        print(f"Match detail: {match.get('team_a',{}).get('short_name')} vs {match.get('team_b',{}).get('short_name')}, winner={match.get('match_winner')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
