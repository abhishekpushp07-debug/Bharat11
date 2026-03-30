"""
Iteration 21 - Cricket Data APIs Testing (LOT1-5)
Tests IPL Points Table, Live Ticker, Squads, Player Info, Match Squad, Fantasy Points, Match Info
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test match with cricketdata_id (KKR vs MI completed match)
KKR_MI_MATCH_ID = "e06a8963-410c-4901-bb96-807a3f258fe3"
IPL_SERIES_ID = "87c62aac-bc3c-4738-ab93-19da0690488f"
VIRAT_KOHLI_PLAYER_ID = "c61d247d-7f77-452c-b495-2813a9cd0ac4"


class TestCricketIPLEndpoints:
    """IPL-level endpoints from cricket.py router"""

    def test_ipl_points_table(self):
        """GET /api/cricket/ipl/points-table - IPL team standings"""
        response = requests.get(f"{BASE_URL}/api/cricket/ipl/points-table")
        assert response.status_code == 200
        
        data = response.json()
        assert "teams" in data
        assert "series_id" in data
        assert data["series_id"] == IPL_SERIES_ID
        
        teams = data["teams"]
        assert len(teams) == 10, f"Expected 10 IPL teams, got {len(teams)}"
        
        # Verify team structure
        for team in teams:
            assert "teamname" in team
            assert "shortname" in team
            assert "img" in team
            assert "matches" in team
            assert "wins" in team
            assert "loss" in team
            assert "nr" in team  # No Result
        
        # Verify known teams exist
        shortnames = [t["shortname"] for t in teams]
        assert "MI" in shortnames, "Mumbai Indians missing"
        assert "CSK" in shortnames, "Chennai Super Kings missing"
        assert "KKR" in shortnames, "Kolkata Knight Riders missing"
        print(f"PASS: IPL Points Table - {len(teams)} teams with P/W/L/NR columns")

    def test_live_ticker(self):
        """GET /api/cricket/live-ticker - Live score feed"""
        response = requests.get(f"{BASE_URL}/api/cricket/live-ticker")
        assert response.status_code == 200
        
        data = response.json()
        assert "scores" in data
        assert "count" in data
        
        scores = data["scores"]
        assert len(scores) > 0, "Expected at least 1 match in ticker"
        
        # Verify score structure
        for score in scores[:3]:  # Check first 3
            assert "id" in score
            assert "t1" in score  # Team 1 name
            assert "t2" in score  # Team 2 name
            assert "t1img" in score  # Team 1 logo
            assert "t2img" in score  # Team 2 logo
            assert "status" in score
            assert "ms" in score  # Match status: fixture/result/live
        
        print(f"PASS: Live Ticker - {data['count']} IPL matches with team names/scores/status")

    def test_ipl_squads(self):
        """GET /api/cricket/ipl/squads - All IPL team squads"""
        response = requests.get(f"{BASE_URL}/api/cricket/ipl/squads")
        assert response.status_code == 200
        
        data = response.json()
        assert "teams" in data
        assert "series_id" in data
        
        teams = data["teams"]
        assert len(teams) == 10, f"Expected 10 IPL teams, got {len(teams)}"
        
        # Verify team squad structure
        for team in teams[:2]:  # Check first 2 teams
            assert "teamName" in team
            assert "shortname" in team
            assert "players" in team
            assert len(team["players"]) > 0, f"No players for {team['teamName']}"
            
            # Verify player structure
            player = team["players"][0]
            assert "id" in player
            assert "name" in player
            assert "role" in player or "country" in player
        
        print(f"PASS: IPL Squads - {len(teams)} teams with player details")

    def test_player_profile(self):
        """GET /api/cricket/player/{player_id} - Player profile + career stats"""
        response = requests.get(f"{BASE_URL}/api/cricket/player/{VIRAT_KOHLI_PLAYER_ID}")
        assert response.status_code == 200
        
        data = response.json()
        assert "player" in data
        assert "stats" in data
        
        player = data["player"]
        assert player["name"] == "Virat Kohli"
        assert player["role"] == "Batsman"
        assert player["country"] == "India"
        assert "playerImg" in player
        
        stats = data["stats"]
        assert len(stats) > 0, "Expected career stats"
        
        # Verify stats structure
        stat = stats[0]
        assert "fn" in stat  # Function: batting/bowling
        assert "matchtype" in stat  # test/odi/t20i/ipl
        assert "stat" in stat  # runs/avg/sr etc
        assert "value" in stat
        
        print(f"PASS: Player Profile - {player['name']} with {len(stats)} career stats")


class TestMatchSpecificEndpoints:
    """Match-specific endpoints from matches.py router"""

    def test_match_squad(self):
        """GET /api/matches/{match_id}/squad - Match squad with 2 teams"""
        response = requests.get(f"{BASE_URL}/api/matches/{KKR_MI_MATCH_ID}/squad")
        assert response.status_code == 200
        
        data = response.json()
        assert "match_id" in data
        assert "squads" in data
        
        squads = data["squads"]
        assert len(squads) == 2, f"Expected 2 teams, got {len(squads)}"
        
        # Verify both teams
        team_names = [s.get("teamName") or s.get("shortname") for s in squads]
        assert any("Kolkata" in str(t) or "KKR" in str(t) for t in team_names), "KKR missing"
        assert any("Mumbai" in str(t) or "MI" in str(t) for t in team_names), "MI missing"
        
        # Verify player structure
        for team in squads:
            assert "players" in team
            assert len(team["players"]) > 0
            player = team["players"][0]
            assert "id" in player
            assert "name" in player
        
        print(f"PASS: Match Squad - 2 teams with player lists")

    def test_match_fantasy_points(self):
        """GET /api/matches/{match_id}/fantasy-points - Fantasy points per player"""
        response = requests.get(f"{BASE_URL}/api/matches/{KKR_MI_MATCH_ID}/fantasy-points")
        assert response.status_code == 200
        
        data = response.json()
        assert "match_id" in data
        assert "innings" in data
        assert "totals" in data
        
        innings = data["innings"]
        assert len(innings) == 2, f"Expected 2 innings, got {len(innings)}"
        
        # Verify innings structure
        for inn in innings:
            assert "inning" in inn
            assert "batting" in inn
            assert "bowling" in inn
            
            # Verify player points
            if inn["batting"]:
                batter = inn["batting"][0]
                assert "id" in batter
                assert "name" in batter
                assert "points" in batter
        
        # Verify totals
        totals = data["totals"]
        assert len(totals) > 0, "Expected player totals"
        
        # Check top performer
        top = totals[0]
        assert "name" in top
        assert "points" in top
        
        print(f"PASS: Fantasy Points - {len(innings)} innings, {len(totals)} player totals")

    def test_match_info(self):
        """GET /api/matches/{match_id}/match-info - Toss winner/choice, match winner"""
        response = requests.get(f"{BASE_URL}/api/matches/{KKR_MI_MATCH_ID}/match-info")
        assert response.status_code == 200
        
        data = response.json()
        assert "match_id" in data
        assert "name" in data
        assert "venue" in data
        assert "status" in data
        
        # Verify toss info
        assert "toss_winner" in data
        assert "toss_choice" in data
        assert data["toss_winner"].lower() == "mumbai indians"
        assert data["toss_choice"] == "bowl"
        
        # Verify match winner
        assert "match_winner" in data
        assert data["match_winner"] == "Mumbai Indians"
        
        # Verify score
        assert "score" in data
        assert len(data["score"]) == 2
        
        print(f"PASS: Match Info - Toss: {data['toss_winner']} chose to {data['toss_choice']}, Winner: {data['match_winner']}")

    def test_match_scorecard(self):
        """GET /api/matches/{match_id}/scorecard - Full scorecard"""
        response = requests.get(f"{BASE_URL}/api/matches/{KKR_MI_MATCH_ID}/scorecard")
        assert response.status_code == 200
        
        data = response.json()
        assert "match_id" in data
        
        # Scorecard may or may not be available
        if data.get("scorecard"):
            assert len(data["scorecard"]) > 0
            print(f"PASS: Scorecard - Available with {len(data['scorecard'])} innings")
        else:
            print(f"PASS: Scorecard endpoint working (data may be cached/unavailable)")


class TestMatchWithoutCricketDataId:
    """Test match without cricketdata_id returns graceful empty response"""

    def test_squad_without_cricketdata_id(self):
        """Squad returns empty array for match without cricketdata_id"""
        # Use a match that might not have cricketdata_id
        response = requests.get(f"{BASE_URL}/api/matches")
        matches = response.json().get("matches", [])
        
        # Find a match without cricketdata_id
        match_without_cd = None
        for m in matches:
            if not m.get("cricketdata_id"):
                match_without_cd = m
                break
        
        if match_without_cd:
            resp = requests.get(f"{BASE_URL}/api/matches/{match_without_cd['id']}/squad")
            assert resp.status_code == 200
            data = resp.json()
            # Should return empty squads or error message
            assert "squads" in data or "error" in data
            print(f"PASS: Squad gracefully handles match without cricketdata_id")
        else:
            print("SKIP: All matches have cricketdata_id")


class TestHealthAndStatus:
    """Health and status endpoints"""

    def test_health(self):
        """GET /api/health - Backend health check"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("PASS: Health check")

    def test_cricket_status(self):
        """GET /api/matches/live/status - Cricket data service status"""
        response = requests.get(f"{BASE_URL}/api/matches/live/status")
        assert response.status_code == 200
        data = response.json()
        assert "cricketdata_key_set" in data
        assert data["cricketdata_key_set"] == True, "CRICKET_API_KEY not set"
        print(f"PASS: Cricket service status - API key set: {data['cricketdata_key_set']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
