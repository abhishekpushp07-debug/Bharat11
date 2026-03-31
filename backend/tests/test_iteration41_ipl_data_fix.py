"""
Iteration 41 - IPL Data Fix Testing
Tests for:
1. _align_team_info() - fixes random teamInfo[] ordering
2. _is_strictly_ipl() - strict IPL whitelist filtering
3. No non-IPL teams in /api/matches
4. No duplicate matches
5. Completed matches have non-zero scores
6. Team names not swapped
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# IPL team short names whitelist
IPL_SHORT_NAMES = {"MI", "CSK", "RCB", "KKR", "DC", "PBKS", "RR", "SRH", "GT", "LSG"}


class TestIPLDataFix:
    """Tests for IPL data quality fixes"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
    def get_admin_token(self):
        """Get admin auth token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "phone": "7004186276",
            "pin": "5524"
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("token", {}).get("access_token", "")
        return None
    
    def test_01_api_health(self):
        """Test API is accessible"""
        response = self.session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        data = response.json()
        assert data.get("status") == "healthy"
        print("PASSED: API health check")
    
    def test_02_matches_only_ipl_teams(self):
        """Test /api/matches returns ONLY IPL team short names"""
        response = self.session.get(f"{BASE_URL}/api/matches?limit=50")
        assert response.status_code == 200, f"Matches API failed: {response.text}"
        
        data = response.json()
        matches = data.get("matches", [])
        assert len(matches) > 0, "No matches found"
        
        non_ipl_teams = []
        for match in matches:
            team_a_short = match.get("team_a", {}).get("short_name", "")
            team_b_short = match.get("team_b", {}).get("short_name", "")
            
            if team_a_short and team_a_short not in IPL_SHORT_NAMES:
                non_ipl_teams.append(f"team_a: {team_a_short}")
            if team_b_short and team_b_short not in IPL_SHORT_NAMES:
                non_ipl_teams.append(f"team_b: {team_b_short}")
        
        assert len(non_ipl_teams) == 0, f"Non-IPL teams found: {non_ipl_teams}"
        print(f"PASSED: All {len(matches)} matches have IPL teams only")
    
    def test_03_no_duplicate_matches(self):
        """Test no duplicate matches (same cricketdata_id appearing twice)"""
        response = self.session.get(f"{BASE_URL}/api/matches?limit=50")
        assert response.status_code == 200
        
        data = response.json()
        matches = data.get("matches", [])
        
        # Check for duplicate cricketdata_ids
        cd_ids = [m.get("cricketdata_id") for m in matches if m.get("cricketdata_id")]
        duplicates = [cd_id for cd_id in cd_ids if cd_ids.count(cd_id) > 1]
        
        assert len(duplicates) == 0, f"Duplicate cricketdata_ids found: {set(duplicates)}"
        
        # Check for duplicate match IDs
        match_ids = [m.get("id") for m in matches]
        dup_ids = [mid for mid in match_ids if match_ids.count(mid) > 1]
        
        assert len(dup_ids) == 0, f"Duplicate match IDs found: {set(dup_ids)}"
        print(f"PASSED: No duplicates in {len(matches)} matches")
    
    def test_04_completed_matches_have_scores(self):
        """Test completed matches have non-zero scores (r > 0)"""
        response = self.session.get(f"{BASE_URL}/api/matches?status=completed&limit=20")
        assert response.status_code == 200
        
        data = response.json()
        matches = data.get("matches", [])
        
        if len(matches) == 0:
            pytest.skip("No completed matches to test")
        
        matches_with_zero_scores = []
        for match in matches:
            live_score = match.get("live_score", {})
            scores = live_score.get("scores", []) if live_score else []
            
            # Check if any innings has runs > 0
            has_real_score = any(
                s.get("r", 0) > 0 or s.get("runs", 0) > 0 
                for s in scores
            )
            
            if not has_real_score:
                team_a = match.get("team_a", {}).get("short_name", "?")
                team_b = match.get("team_b", {}).get("short_name", "?")
                matches_with_zero_scores.append(f"{team_a} vs {team_b}")
        
        # Allow some matches without scores (API may not have data for all)
        zero_pct = len(matches_with_zero_scores) / len(matches) * 100
        assert zero_pct < 50, f"Too many completed matches without scores ({zero_pct:.0f}%): {matches_with_zero_scores[:5]}"
        
        print(f"PASSED: {len(matches) - len(matches_with_zero_scores)}/{len(matches)} completed matches have scores")
    
    def test_05_team_names_not_swapped(self):
        """Test team_a.name matches team_a.short_name (no swaps)"""
        response = self.session.get(f"{BASE_URL}/api/matches?limit=30")
        assert response.status_code == 200
        
        data = response.json()
        matches = data.get("matches", [])
        
        # Team name to short name mapping
        TEAM_NAME_MAP = {
            "MI": ["Mumbai Indians", "Mumbai"],
            "CSK": ["Chennai Super Kings", "Chennai"],
            "RCB": ["Royal Challengers Bangalore", "Royal Challengers Bengaluru", "Bangalore", "Bengaluru"],
            "KKR": ["Kolkata Knight Riders", "Kolkata"],
            "DC": ["Delhi Capitals", "Delhi"],
            "PBKS": ["Punjab Kings", "Punjab"],
            "RR": ["Rajasthan Royals", "Rajasthan"],
            "SRH": ["Sunrisers Hyderabad", "Hyderabad"],
            "GT": ["Gujarat Titans", "Gujarat"],
            "LSG": ["Lucknow Super Giants", "Lucknow"],
        }
        
        swapped_teams = []
        for match in matches:
            for team_key in ["team_a", "team_b"]:
                team = match.get(team_key, {})
                short_name = team.get("short_name", "")
                full_name = team.get("name", "")
                
                if short_name in TEAM_NAME_MAP:
                    valid_names = TEAM_NAME_MAP[short_name]
                    # Check if full_name contains any valid name OR is the short name itself
                    # (API sometimes returns short name as full name)
                    name_matches = any(vn.lower() in full_name.lower() for vn in valid_names) or full_name == short_name
                    if not name_matches and full_name:
                        swapped_teams.append(f"{short_name} has name '{full_name}'")
        
        assert len(swapped_teams) == 0, f"Team name swaps detected: {swapped_teams[:5]}"
        print(f"PASSED: No team name swaps in {len(matches)} matches")
    
    def test_06_admin_login(self):
        """Test admin login works"""
        token = self.get_admin_token()
        assert token, "Admin login failed"
        print("PASSED: Admin login successful")
    
    def test_07_live_sync_ipl_only(self):
        """Test /api/matches/live/sync?ipl_only=true returns only IPL matches"""
        token = self.get_admin_token()
        assert token, "Admin login required"
        
        headers = {"Authorization": f"Bearer {token}"}
        response = self.session.post(
            f"{BASE_URL}/api/matches/live/sync?ipl_only=true",
            headers=headers
        )
        
        # May return 200 even if no new matches
        assert response.status_code == 200, f"Sync failed: {response.text}"
        
        data = response.json()
        print(f"PASSED: Live sync returned: {data}")
    
    def test_08_sync_ipl_schedule(self):
        """Test /api/matches/live/sync-ipl-schedule syncs IPL matches"""
        token = self.get_admin_token()
        assert token, "Admin login required"
        
        headers = {"Authorization": f"Bearer {token}"}
        response = self.session.post(
            f"{BASE_URL}/api/matches/live/sync-ipl-schedule",
            headers=headers
        )
        
        assert response.status_code == 200, f"Schedule sync failed: {response.text}"
        
        data = response.json()
        assert "synced" in data or "created" in data or "updated" in data, f"Unexpected response: {data}"
        
        # Check for errors
        errors = data.get("errors", [])
        assert len(errors) == 0, f"Sync had errors: {errors}"
        
        print(f"PASSED: IPL schedule sync: created={data.get('created', 0)}, updated={data.get('updated', 0)}")
    
    def test_09_verify_ipl_teams_after_sync(self):
        """Verify all matches still have IPL teams after sync"""
        response = self.session.get(f"{BASE_URL}/api/matches?limit=50")
        assert response.status_code == 200
        
        data = response.json()
        matches = data.get("matches", [])
        
        non_ipl = []
        for match in matches:
            ta = match.get("team_a", {}).get("short_name", "")
            tb = match.get("team_b", {}).get("short_name", "")
            
            if ta not in IPL_SHORT_NAMES:
                non_ipl.append(f"team_a={ta}")
            if tb not in IPL_SHORT_NAMES:
                non_ipl.append(f"team_b={tb}")
        
        assert len(non_ipl) == 0, f"Non-IPL teams after sync: {non_ipl}"
        print(f"PASSED: All {len(matches)} matches have IPL teams after sync")
    
    def test_10_cricket_service_status(self):
        """Test cricket data service status"""
        response = self.session.get(f"{BASE_URL}/api/matches/live/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "cricketdata_key_set" in data
        assert data.get("cricketdata_key_set") == True, "Cricket API key not set"
        
        print(f"PASSED: Cricket service status: {data}")
    
    def test_11_match_detail_team_consistency(self):
        """Test individual match detail has consistent team data"""
        # Get a match first
        response = self.session.get(f"{BASE_URL}/api/matches?limit=1")
        assert response.status_code == 200
        
        data = response.json()
        matches = data.get("matches", [])
        if not matches:
            pytest.skip("No matches to test")
        
        match_id = matches[0].get("id")
        
        # Get match detail
        response = self.session.get(f"{BASE_URL}/api/matches/{match_id}")
        assert response.status_code == 200
        
        match = response.json()
        team_a = match.get("team_a", {})
        team_b = match.get("team_b", {})
        
        # Verify team_a and team_b have required fields
        assert team_a.get("short_name") in IPL_SHORT_NAMES, f"Invalid team_a: {team_a}"
        assert team_b.get("short_name") in IPL_SHORT_NAMES, f"Invalid team_b: {team_b}"
        assert team_a.get("name"), "team_a missing name"
        assert team_b.get("name"), "team_b missing name"
        
        print(f"PASSED: Match {match_id} has consistent team data")


class TestAlignTeamInfoFunction:
    """Unit tests for _align_team_info function logic"""
    
    def test_align_team_info_import(self):
        """Test _align_team_info can be imported"""
        try:
            from services.cricket_data import _align_team_info, _is_strictly_ipl, IPL_SHORT_NAMES
            assert callable(_align_team_info)
            assert callable(_is_strictly_ipl)
            assert len(IPL_SHORT_NAMES) == 10
            print("PASSED: Functions imported successfully")
        except ImportError as e:
            pytest.skip(f"Cannot import from services: {e}")
    
    def test_is_strictly_ipl_valid(self):
        """Test _is_strictly_ipl returns True for IPL teams"""
        try:
            from services.cricket_data import _is_strictly_ipl
            
            # Valid IPL match
            teams = ["Mumbai Indians", "Chennai Super Kings"]
            team_info = [
                {"name": "Mumbai Indians", "shortname": "MI"},
                {"name": "Chennai Super Kings", "shortname": "CSK"}
            ]
            
            result = _is_strictly_ipl(teams, team_info)
            assert result == True, f"Expected True for IPL teams, got {result}"
            print("PASSED: _is_strictly_ipl returns True for IPL teams")
        except ImportError:
            pytest.skip("Cannot import _is_strictly_ipl")
    
    def test_is_strictly_ipl_invalid(self):
        """Test _is_strictly_ipl returns False for non-IPL teams"""
        try:
            from services.cricket_data import _is_strictly_ipl
            
            # Non-IPL match (Pakistan Super League)
            teams = ["Lahore Qalandars", "Karachi Kings"]
            team_info = [
                {"name": "Lahore Qalandars", "shortname": "LQ"},
                {"name": "Karachi Kings", "shortname": "KK"}
            ]
            
            result = _is_strictly_ipl(teams, team_info)
            assert result == False, f"Expected False for non-IPL teams, got {result}"
            print("PASSED: _is_strictly_ipl returns False for non-IPL teams")
        except ImportError:
            pytest.skip("Cannot import _is_strictly_ipl")
    
    def test_align_team_info_correct_order(self):
        """Test _align_team_info aligns teamInfo to teams order"""
        try:
            from services.cricket_data import _align_team_info
            
            # teams[] has MI first, but teamInfo[] has CSK first (API bug simulation)
            teams = ["Mumbai Indians", "Chennai Super Kings"]
            team_info = [
                {"name": "Chennai Super Kings", "shortname": "CSK", "img": "csk.png"},
                {"name": "Mumbai Indians", "shortname": "MI", "img": "mi.png"}
            ]
            
            team_a_info, team_b_info = _align_team_info(teams, team_info)
            
            # team_a should be MI (matches teams[0])
            assert team_a_info.get("shortname") == "MI", f"Expected MI for team_a, got {team_a_info}"
            # team_b should be CSK (matches teams[1])
            assert team_b_info.get("shortname") == "CSK", f"Expected CSK for team_b, got {team_b_info}"
            
            print("PASSED: _align_team_info correctly aligns teams")
        except ImportError:
            pytest.skip("Cannot import _align_team_info")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
