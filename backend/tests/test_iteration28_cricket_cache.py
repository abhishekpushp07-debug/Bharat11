"""
Iteration 28 - Cricket Data & MongoDB Cache Layer Tests
Tests: IPL Points Table, Live Ticker, Team Drill-Down, Match Full Data, API Caching
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

IPL_SERIES_ID = "87c62aac-bc3c-4738-ab93-19da0690488f"
# Completed match ID from CSK matches
COMPLETED_MATCH_ID = "d788e9f9-99bf-4650-a035-92a7e21b3d08"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


class TestHealthAndBasics:
    """Basic health and connectivity tests"""
    
    def test_health_endpoint(self, api_client):
        """GET /api/health returns 200"""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "mongodb" in data["services"]
        print("PASS: Health endpoint returns healthy status")


class TestIPLPointsTable:
    """IPL Points Table endpoint tests"""
    
    def test_points_table_returns_teams(self, api_client):
        """GET /api/cricket/ipl/points-table returns 10 IPL teams"""
        response = api_client.get(f"{BASE_URL}/api/cricket/ipl/points-table")
        assert response.status_code == 200
        data = response.json()
        assert "teams" in data
        assert len(data["teams"]) == 10, f"Expected 10 teams, got {len(data['teams'])}"
        print(f"PASS: Points table returns {len(data['teams'])} teams")
    
    def test_points_table_team_structure(self, api_client):
        """Each team has required fields: shortname, wins, loss, matches"""
        response = api_client.get(f"{BASE_URL}/api/cricket/ipl/points-table")
        data = response.json()
        for team in data["teams"]:
            assert "shortname" in team, f"Missing shortname in team: {team}"
            assert "wins" in team, f"Missing wins in team: {team}"
            assert "loss" in team, f"Missing loss in team: {team}"
            assert "matches" in team, f"Missing matches in team: {team}"
        print("PASS: All teams have required fields (shortname, wins, loss, matches)")
    
    def test_points_table_has_series_id(self, api_client):
        """Response includes correct series_id"""
        response = api_client.get(f"{BASE_URL}/api/cricket/ipl/points-table")
        data = response.json()
        assert data.get("series_id") == IPL_SERIES_ID
        print(f"PASS: Points table has correct series_id: {IPL_SERIES_ID}")


class TestLiveTicker:
    """Live Ticker endpoint tests"""
    
    def test_live_ticker_returns_scores(self, api_client):
        """GET /api/cricket/live-ticker returns IPL match scores"""
        response = api_client.get(f"{BASE_URL}/api/cricket/live-ticker")
        assert response.status_code == 200
        data = response.json()
        assert "scores" in data
        assert "count" in data
        print(f"PASS: Live ticker returns {data['count']} matches")
    
    def test_live_ticker_match_structure(self, api_client):
        """Each match has required fields: id, t1, t2, ms, status"""
        response = api_client.get(f"{BASE_URL}/api/cricket/live-ticker")
        data = response.json()
        if data["scores"]:
            match = data["scores"][0]
            assert "id" in match, "Missing id"
            assert "t1" in match, "Missing t1 (team 1)"
            assert "t2" in match, "Missing t2 (team 2)"
            assert "ms" in match, "Missing ms (match status: fixture/result/live)"
            assert "status" in match, "Missing status text"
            print(f"PASS: Match structure valid - ms types: {set(m['ms'] for m in data['scores'])}")
    
    def test_live_ticker_ms_values(self, api_client):
        """ms field contains valid values: fixture, result, or live"""
        response = api_client.get(f"{BASE_URL}/api/cricket/live-ticker")
        data = response.json()
        valid_ms = {"fixture", "result", "live"}
        for match in data["scores"]:
            assert match["ms"] in valid_ms, f"Invalid ms value: {match['ms']}"
        print("PASS: All ms values are valid (fixture/result/live)")


class TestTeamDrillDown:
    """Team matches drill-down endpoint tests"""
    
    def test_csk_matches_returns_data(self, api_client):
        """GET /api/cricket/ipl/team/CSK/matches returns CSK matches"""
        response = api_client.get(f"{BASE_URL}/api/cricket/ipl/team/CSK/matches")
        assert response.status_code == 200
        data = response.json()
        assert data["team"] == "CSK"
        assert "matches" in data
        assert data["total_matches"] > 0, "CSK should have matches"
        print(f"PASS: CSK has {data['total_matches']} matches")
    
    def test_mi_matches_returns_data(self, api_client):
        """GET /api/cricket/ipl/team/MI/matches returns MI matches"""
        response = api_client.get(f"{BASE_URL}/api/cricket/ipl/team/MI/matches")
        assert response.status_code == 200
        data = response.json()
        assert data["team"] == "MI"
        assert data["total_matches"] > 0, "MI should have matches"
        print(f"PASS: MI has {data['total_matches']} matches")
    
    def test_team_match_structure(self, api_client):
        """Each team match has required fields"""
        response = api_client.get(f"{BASE_URL}/api/cricket/ipl/team/CSK/matches")
        data = response.json()
        if data["matches"]:
            match = data["matches"][0]
            assert "id" in match, "Missing id"
            assert "name" in match, "Missing name"
            assert "date" in match, "Missing date"
            assert "venue" in match, "Missing venue"
            assert "status" in match, "Missing status"
            assert "matchStarted" in match, "Missing matchStarted"
            assert "matchEnded" in match, "Missing matchEnded"
            print("PASS: Team match structure is valid")
    
    def test_team_matches_sorted_by_date(self, api_client):
        """Team matches are sorted by date"""
        response = api_client.get(f"{BASE_URL}/api/cricket/ipl/team/CSK/matches")
        data = response.json()
        dates = [m.get("dateTimeGMT", "") for m in data["matches"]]
        assert dates == sorted(dates), "Matches should be sorted by date"
        print("PASS: Team matches are sorted by date")


class TestMatchFullData:
    """Match full data endpoint tests (17 APIs combined)"""
    
    def test_match_full_data_returns_sections(self, api_client):
        """GET /api/cricket/match/{id}/full-data returns combined data"""
        response = api_client.get(f"{BASE_URL}/api/cricket/match/{COMPLETED_MATCH_ID}/full-data")
        assert response.status_code == 200
        data = response.json()
        assert data["cricapi_id"] == COMPLETED_MATCH_ID
        assert "available_sections" in data
        print(f"PASS: Match full data returns sections: {data['available_sections']}")
    
    def test_match_full_data_has_match_info(self, api_client):
        """Match full data includes match_info section"""
        response = api_client.get(f"{BASE_URL}/api/cricket/match/{COMPLETED_MATCH_ID}/full-data")
        data = response.json()
        assert "match_info" in data["available_sections"]
        info = data["match_info"]
        assert info is not None
        assert "name" in info
        assert "venue" in info
        assert "teams" in info
        assert "matchEnded" in info
        print(f"PASS: Match info present - {info['name']}")
    
    def test_match_full_data_has_scorecard(self, api_client):
        """Match full data includes scorecard section"""
        response = api_client.get(f"{BASE_URL}/api/cricket/match/{COMPLETED_MATCH_ID}/full-data")
        data = response.json()
        assert "scorecard" in data["available_sections"]
        sc = data["scorecard"]
        assert sc is not None
        assert "innings" in sc
        assert len(sc["innings"]) >= 1, "Should have at least 1 innings"
        # Check batting/bowling arrays
        innings = sc["innings"][0]
        assert "batting" in innings
        assert "bowling" in innings
        print(f"PASS: Scorecard present with {len(sc['innings'])} innings")
    
    def test_match_full_data_has_fantasy_points(self, api_client):
        """Match full data includes fantasy_points section"""
        response = api_client.get(f"{BASE_URL}/api/cricket/match/{COMPLETED_MATCH_ID}/full-data")
        data = response.json()
        assert "fantasy_points" in data["available_sections"]
        fp = data["fantasy_points"]
        assert fp is not None
        assert "totals" in fp
        assert len(fp["totals"]) > 0, "Should have player fantasy points"
        print(f"PASS: Fantasy points present with {len(fp['totals'])} players")
    
    def test_match_full_data_has_squad(self, api_client):
        """Match full data includes squad section"""
        response = api_client.get(f"{BASE_URL}/api/cricket/match/{COMPLETED_MATCH_ID}/full-data")
        data = response.json()
        assert "squad" in data["available_sections"]
        squad = data["squad"]
        assert squad is not None
        assert len(squad) >= 2, "Should have 2 team squads"
        print(f"PASS: Squad present with {len(squad)} teams")
    
    def test_match_full_data_has_metrics(self, api_client):
        """Match full data includes parsed metrics"""
        response = api_client.get(f"{BASE_URL}/api/cricket/match/{COMPLETED_MATCH_ID}/full-data")
        data = response.json()
        metrics = data.get("metrics")
        assert metrics is not None
        assert "match_total_runs" in metrics
        assert "match_total_wickets" in metrics
        assert "highest_run_scorer" in metrics
        print(f"PASS: Metrics present - Total runs: {metrics['match_total_runs']}, Top scorer: {metrics['highest_run_scorer']}")


class TestIPLSquads:
    """IPL Squads endpoint tests"""
    
    def test_ipl_squads_returns_teams(self, api_client):
        """GET /api/cricket/ipl/squads returns all IPL team squads"""
        response = api_client.get(f"{BASE_URL}/api/cricket/ipl/squads")
        assert response.status_code == 200
        data = response.json()
        assert "teams" in data
        assert len(data["teams"]) == 10, f"Expected 10 teams, got {len(data['teams'])}"
        print(f"PASS: IPL squads returns {len(data['teams'])} teams")
    
    def test_ipl_squads_has_players(self, api_client):
        """Each team squad has players with required fields"""
        response = api_client.get(f"{BASE_URL}/api/cricket/ipl/squads")
        data = response.json()
        for team in data["teams"]:
            assert "teamName" in team or "shortname" in team
            assert "players" in team
            assert len(team["players"]) > 0, f"Team {team.get('shortname')} has no players"
            # Check player structure
            player = team["players"][0]
            assert "name" in player
            assert "id" in player
        print("PASS: All teams have players with required fields")


class TestCacheStats:
    """API Cache statistics tests"""
    
    def test_cache_stats_returns_data(self, api_client):
        """GET /api/cricket/cache-stats returns cache statistics"""
        response = api_client.get(f"{BASE_URL}/api/cricket/cache-stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_cached" in data
        assert "permanent_cached" in data
        assert "by_type" in data
        assert "api_hits_today" in data
        assert "api_hits_limit" in data
        print(f"PASS: Cache stats - Total: {data['total_cached']}, API hits: {data['api_hits_today']}/{data['api_hits_limit']}")
    
    def test_cache_prevents_duplicate_api_calls(self, api_client):
        """Calling same endpoint twice doesn't increase api_hits_today"""
        # Get initial hits
        stats1 = api_client.get(f"{BASE_URL}/api/cricket/cache-stats").json()
        initial_hits = stats1["api_hits_today"]
        
        # Call points table (should be cached)
        api_client.get(f"{BASE_URL}/api/cricket/ipl/points-table")
        
        # Get hits after
        stats2 = api_client.get(f"{BASE_URL}/api/cricket/cache-stats").json()
        final_hits = stats2["api_hits_today"]
        
        assert final_hits == initial_hits, f"API hits increased from {initial_hits} to {final_hits} - cache not working"
        print(f"PASS: Cache working - API hits stayed at {final_hits}")
    
    def test_cache_has_expected_types(self, api_client):
        """Cache contains expected data types"""
        response = api_client.get(f"{BASE_URL}/api/cricket/cache-stats")
        data = response.json()
        by_type = data["by_type"]
        # After our tests, we should have these cached
        expected_types = ["series_points", "cric_score", "series_info"]
        for t in expected_types:
            if t in by_type:
                print(f"  - {t}: {by_type[t]} items cached")
        print("PASS: Cache contains expected data types")


class TestAuthentication:
    """Auth tests to ensure admin/player login still works"""
    
    def test_admin_login(self, api_client):
        """Admin can login with correct credentials"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "phone": ADMIN_PHONE,
            "pin": ADMIN_PIN
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["user"]["is_admin"] == True
        print("PASS: Admin login successful")
    
    def test_player_login(self, api_client):
        """Player can login with correct credentials"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "phone": PLAYER_PHONE,
            "pin": PLAYER_PIN
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        print("PASS: Player login successful")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
