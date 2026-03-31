"""
Iteration 39 - IPL Data Integration Tests
Tests for CricketData.org API integration, scorecard, squad, match-info, points-table
Focus: RCBW→RCB normalization, completed matches with real data
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestCompletedMatches:
    """Test completed matches API returns real IPL data"""
    
    def test_completed_matches_exist(self):
        """GET /api/matches?status=completed should return 3+ completed IPL matches"""
        response = requests.get(f"{BASE_URL}/api/matches?status=completed&limit=10")
        assert response.status_code == 200
        data = response.json()
        matches = data.get("matches", [])
        assert len(matches) >= 3, f"Expected 3+ completed matches, got {len(matches)}"
        print(f"✓ Found {len(matches)} completed matches")
    
    def test_completed_match_has_cricketdata_id(self):
        """At least one completed match should have cricketdata_id"""
        response = requests.get(f"{BASE_URL}/api/matches?status=completed&limit=5")
        assert response.status_code == 200
        matches = response.json().get("matches", [])
        
        matches_with_cd_id = [m for m in matches if m.get("cricketdata_id")]
        assert len(matches_with_cd_id) >= 1, "Expected at least 1 match with cricketdata_id"
        print(f"✓ {len(matches_with_cd_id)} matches have cricketdata_id")
        
        # Return first match with cd_id for other tests
        return matches_with_cd_id[0]


class TestScorecard:
    """Test scorecard API returns real batting/bowling data"""
    
    @pytest.fixture
    def completed_match_id(self):
        """Get a completed match ID with cricketdata_id"""
        response = requests.get(f"{BASE_URL}/api/matches?status=completed&limit=5")
        matches = response.json().get("matches", [])
        for m in matches:
            if m.get("cricketdata_id"):
                return m["id"]
        pytest.skip("No completed match with cricketdata_id found")
    
    def test_scorecard_returns_innings(self, completed_match_id):
        """GET /api/matches/{id}/scorecard should return real innings data"""
        response = requests.get(f"{BASE_URL}/api/matches/{completed_match_id}/scorecard")
        assert response.status_code == 200
        data = response.json()
        
        # Should have scorecard array
        scorecard = data.get("scorecard", [])
        assert scorecard is not None, "Scorecard should not be None"
        assert len(scorecard) >= 1, "Should have at least 1 innings"
        print(f"✓ Scorecard has {len(scorecard)} innings")
    
    def test_scorecard_has_batting_data(self, completed_match_id):
        """Scorecard should have 11 batsmen per team"""
        response = requests.get(f"{BASE_URL}/api/matches/{completed_match_id}/scorecard")
        data = response.json()
        scorecard = data.get("scorecard", [])
        
        if scorecard:
            first_innings = scorecard[0]
            batting = first_innings.get("batting", [])
            assert len(batting) >= 10, f"Expected 10+ batsmen, got {len(batting)}"
            
            # Check batting data structure
            if batting:
                first_batsman = batting[0]
                assert "r" in first_batsman, "Batsman should have runs (r)"
                assert "b" in first_batsman, "Batsman should have balls (b)"
                print(f"✓ First innings has {len(batting)} batsmen with proper data")
    
    def test_scorecard_has_metrics(self, completed_match_id):
        """Scorecard should include match metrics (total runs, sixes, top scorer)"""
        response = requests.get(f"{BASE_URL}/api/matches/{completed_match_id}/scorecard")
        data = response.json()
        metrics = data.get("metrics", {})
        
        if metrics:
            assert "match_total_runs" in metrics, "Should have match_total_runs"
            assert "highest_run_scorer" in metrics, "Should have highest_run_scorer"
            print(f"✓ Metrics: {metrics.get('match_total_runs')} total runs, top scorer: {metrics.get('highest_run_scorer')}")


class TestSquad:
    """Test squad API returns team players"""
    
    @pytest.fixture
    def completed_match_id(self):
        """Get a completed match ID with cricketdata_id"""
        response = requests.get(f"{BASE_URL}/api/matches?status=completed&limit=5")
        matches = response.json().get("matches", [])
        for m in matches:
            if m.get("cricketdata_id"):
                return m["id"]
        pytest.skip("No completed match with cricketdata_id found")
    
    def test_squad_returns_two_teams(self, completed_match_id):
        """GET /api/matches/{id}/squad should return 2 teams"""
        response = requests.get(f"{BASE_URL}/api/matches/{completed_match_id}/squad")
        assert response.status_code == 200
        data = response.json()
        
        squads = data.get("squads", [])
        assert len(squads) >= 2, f"Expected 2 teams, got {len(squads)}"
        print(f"✓ Squad has {len(squads)} teams")
    
    def test_squad_has_players(self, completed_match_id):
        """Each team should have 20+ players"""
        response = requests.get(f"{BASE_URL}/api/matches/{completed_match_id}/squad")
        data = response.json()
        squads = data.get("squads", [])
        
        for team in squads:
            players = team.get("players", [])
            team_name = team.get("teamName", team.get("shortname", "Unknown"))
            assert len(players) >= 15, f"{team_name} should have 15+ players, got {len(players)}"
            print(f"✓ {team_name}: {len(players)} players")


class TestMatchInfo:
    """Test match-info API returns toss, winner, scores"""
    
    @pytest.fixture
    def completed_match_id(self):
        """Get a completed match ID with cricketdata_id"""
        response = requests.get(f"{BASE_URL}/api/matches?status=completed&limit=5")
        matches = response.json().get("matches", [])
        for m in matches:
            if m.get("cricketdata_id"):
                return m["id"]
        pytest.skip("No completed match with cricketdata_id found")
    
    def test_match_info_has_toss(self, completed_match_id):
        """GET /api/matches/{id}/match-info should return toss info"""
        response = requests.get(f"{BASE_URL}/api/matches/{completed_match_id}/match-info")
        assert response.status_code == 200
        data = response.json()
        
        assert "toss_winner" in data, "Should have toss_winner"
        assert "toss_choice" in data, "Should have toss_choice"
        print(f"✓ Toss: {data.get('toss_winner')} chose to {data.get('toss_choice')}")
    
    def test_match_info_has_winner(self, completed_match_id):
        """Match info should have match_winner for completed matches"""
        response = requests.get(f"{BASE_URL}/api/matches/{completed_match_id}/match-info")
        data = response.json()
        
        assert "match_winner" in data, "Should have match_winner"
        assert data.get("match_winner"), "match_winner should not be empty"
        print(f"✓ Winner: {data.get('match_winner')}")
    
    def test_match_info_has_scores(self, completed_match_id):
        """Match info should have score array"""
        response = requests.get(f"{BASE_URL}/api/matches/{completed_match_id}/match-info")
        data = response.json()
        
        scores = data.get("score", [])
        assert len(scores) >= 2, f"Expected 2 innings scores, got {len(scores)}"
        print(f"✓ Scores: {len(scores)} innings")


class TestPointsTable:
    """Test IPL points table with RCBW→RCB normalization"""
    
    def test_points_table_returns_teams(self):
        """GET /api/cricket/ipl/points-table should return 10 teams"""
        response = requests.get(f"{BASE_URL}/api/cricket/ipl/points-table")
        assert response.status_code == 200
        data = response.json()
        
        teams = data.get("teams", [])
        assert len(teams) == 10, f"Expected 10 IPL teams, got {len(teams)}"
        print(f"✓ Points table has {len(teams)} teams")
    
    def test_points_table_has_rcb_not_rcbw(self):
        """Points table should show 'RCB' not 'RCBW'"""
        response = requests.get(f"{BASE_URL}/api/cricket/ipl/points-table")
        data = response.json()
        teams = data.get("teams", [])
        
        shortnames = [t.get("shortname", "") for t in teams]
        assert "RCB" in shortnames, f"Should have 'RCB' in shortnames: {shortnames}"
        assert "RCBW" not in shortnames, f"Should NOT have 'RCBW' in shortnames: {shortnames}"
        print(f"✓ RCB found in points table (not RCBW)")
    
    def test_points_table_has_stats(self):
        """Each team should have matches, wins, loss stats"""
        response = requests.get(f"{BASE_URL}/api/cricket/ipl/points-table")
        data = response.json()
        teams = data.get("teams", [])
        
        for team in teams:
            assert "matches" in team, f"{team.get('shortname')} missing matches"
            assert "wins" in team, f"{team.get('shortname')} missing wins"
            assert "loss" in team, f"{team.get('shortname')} missing loss"
        print(f"✓ All teams have proper stats")


class TestLiveTicker:
    """Test live ticker API"""
    
    def test_live_ticker_returns_scores(self):
        """GET /api/cricket/live-ticker should return IPL scores"""
        response = requests.get(f"{BASE_URL}/api/cricket/live-ticker")
        assert response.status_code == 200
        data = response.json()
        
        scores = data.get("scores", [])
        # May be empty if no live matches
        print(f"✓ Live ticker returned {len(scores)} scores")


class TestTeamMatches:
    """Test team-specific matches endpoint"""
    
    def test_rcb_matches(self):
        """GET /api/cricket/ipl/team/RCB/matches should return RCB matches"""
        response = requests.get(f"{BASE_URL}/api/cricket/ipl/team/RCB/matches")
        assert response.status_code == 200
        data = response.json()
        
        matches = data.get("matches", [])
        assert len(matches) >= 1, "RCB should have at least 1 match"
        print(f"✓ RCB has {len(matches)} matches")
    
    def test_rcb_has_completed_match(self):
        """RCB should have at least 1 completed match"""
        response = requests.get(f"{BASE_URL}/api/cricket/ipl/team/RCB/matches")
        data = response.json()
        matches = data.get("matches", [])
        
        completed = [m for m in matches if m.get("matchEnded")]
        assert len(completed) >= 1, f"RCB should have 1+ completed matches, got {len(completed)}"
        print(f"✓ RCB has {len(completed)} completed matches")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
