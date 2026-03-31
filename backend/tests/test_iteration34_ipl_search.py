"""
Iteration 34 - IPL Search & Data Testing
Tests: IPL search, records, players, caps endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://fantasy-points.preview.emergentagent.com')


class TestIPLRecords:
    """Test IPL Records endpoint"""
    
    def test_get_all_records(self):
        """GET /api/ipl/records returns 18 IPL records"""
        response = requests.get(f"{BASE_URL}/api/ipl/records")
        assert response.status_code == 200
        data = response.json()
        assert "records" in data
        assert "total" in data
        assert data["total"] >= 18, f"Expected at least 18 records, got {data['total']}"
        
        # Verify record structure
        record = data["records"][0]
        assert "title" in record
        assert "value" in record
        assert "holder" in record
        assert "category" in record
        assert "color" in record
        print(f"PASS: Got {data['total']} IPL records")
    
    def test_records_have_categories(self):
        """Records should have batting, bowling, team, special categories"""
        response = requests.get(f"{BASE_URL}/api/ipl/records")
        assert response.status_code == 200
        data = response.json()
        
        categories = set(r["category"] for r in data["records"])
        expected = {"batting", "bowling", "team", "special"}
        assert expected.issubset(categories), f"Missing categories: {expected - categories}"
        print(f"PASS: Records have all categories: {categories}")


class TestIPLPlayers:
    """Test IPL Players endpoint"""
    
    def test_get_all_players(self):
        """GET /api/ipl/players returns 20 IPL player profiles"""
        response = requests.get(f"{BASE_URL}/api/ipl/players?limit=50")
        assert response.status_code == 200
        data = response.json()
        assert "players" in data
        assert "total" in data
        assert data["total"] >= 20, f"Expected at least 20 players, got {data['total']}"
        print(f"PASS: Got {data['total']} IPL players")
    
    def test_player_structure(self):
        """Player profiles should have required fields"""
        response = requests.get(f"{BASE_URL}/api/ipl/players?limit=1")
        assert response.status_code == 200
        data = response.json()
        
        player = data["players"][0]
        required_fields = ["name", "name_hi", "role", "current_team", "ipl_stats", "bio", "bio_hi", "achievements"]
        for field in required_fields:
            assert field in player, f"Missing field: {field}"
        
        # Verify ipl_stats structure
        stats = player["ipl_stats"]
        stat_fields = ["matches", "runs", "avg", "sr"]
        for field in stat_fields:
            assert field in stats, f"Missing stat field: {field}"
        print(f"PASS: Player {player['name']} has all required fields")
    
    def test_filter_by_role(self):
        """Filter players by role"""
        response = requests.get(f"{BASE_URL}/api/ipl/players?role=Bowler")
        assert response.status_code == 200
        data = response.json()
        
        for player in data["players"]:
            assert "bowler" in player["role"].lower() or "all-rounder" in player["role"].lower()
        print(f"PASS: Filtered {data['total']} bowlers/all-rounders")
    
    def test_filter_by_team(self):
        """Filter players by team"""
        response = requests.get(f"{BASE_URL}/api/ipl/players?team=MI")
        assert response.status_code == 200
        data = response.json()
        
        assert data["total"] >= 1, "Expected at least 1 MI player"
        print(f"PASS: Found {data['total']} MI players")


class TestIPLCaps:
    """Test IPL Cap Winners endpoint"""
    
    def test_get_cap_winners(self):
        """GET /api/ipl/caps returns 9 years of cap winners"""
        response = requests.get(f"{BASE_URL}/api/ipl/caps")
        assert response.status_code == 200
        data = response.json()
        assert "cap_winners" in data
        assert "total" in data
        assert data["total"] >= 9, f"Expected at least 9 cap winner years, got {data['total']}"
        print(f"PASS: Got {data['total']} years of cap winners")
    
    def test_cap_winner_structure(self):
        """Cap winners should have orange_cap and purple_cap"""
        response = requests.get(f"{BASE_URL}/api/ipl/caps")
        assert response.status_code == 200
        data = response.json()
        
        cap = data["cap_winners"][0]
        assert "year" in cap
        assert "orange_cap" in cap
        assert "purple_cap" in cap
        
        # Verify orange cap structure
        orange = cap["orange_cap"]
        assert "player" in orange
        assert "runs" in orange
        assert "team" in orange
        
        # Verify purple cap structure
        purple = cap["purple_cap"]
        assert "player" in purple
        assert "wickets" in purple
        assert "team" in purple
        print(f"PASS: Cap winner {cap['year']} has correct structure")


class TestIPLSearch:
    """Test IPL Search endpoint"""
    
    def test_search_player_kohli(self):
        """Search for Kohli returns player + record results"""
        response = requests.get(f"{BASE_URL}/api/ipl/search?q=Kohli")
        assert response.status_code == 200
        data = response.json()
        
        assert "query" in data
        assert data["query"] == "Kohli"
        assert "total" in data
        assert "results" in data
        
        results = data["results"]
        assert "players" in results
        assert "records" in results
        
        # Should find Virat Kohli
        player_names = [p["name"] for p in results["players"]]
        assert any("Kohli" in name for name in player_names), "Kohli not found in players"
        
        # Should find records held by Kohli
        assert len(results["records"]) >= 1, "Expected at least 1 record for Kohli"
        print(f"PASS: Search 'Kohli' returned {data['total']} results")
    
    def test_search_team_csk(self):
        """Search for CSK returns team results"""
        response = requests.get(f"{BASE_URL}/api/ipl/search?q=CSK")
        assert response.status_code == 200
        data = response.json()
        
        results = data["results"]
        assert "teams" in results
        assert len(results["teams"]) >= 1, "CSK team not found"
        
        team = results["teams"][0]
        assert team["short"] == "CSK"
        assert "Chennai" in team["name"]
        print(f"PASS: Search 'CSK' found team: {team['name']}")
    
    def test_search_bumrah(self):
        """Search for Bumrah returns player"""
        response = requests.get(f"{BASE_URL}/api/ipl/search?q=Bumrah")
        assert response.status_code == 200
        data = response.json()
        
        results = data["results"]
        player_names = [p["name"] for p in results["players"]]
        assert any("Bumrah" in name for name in player_names), "Bumrah not found"
        print(f"PASS: Search 'Bumrah' found player")
    
    def test_search_most_runs(self):
        """Search for 'Most Runs' returns records"""
        response = requests.get(f"{BASE_URL}/api/ipl/search?q=Most%20Runs")
        assert response.status_code == 200
        data = response.json()
        
        results = data["results"]
        assert len(results["records"]) >= 1, "No records found for 'Most Runs'"
        print(f"PASS: Search 'Most Runs' found {len(results['records'])} records")
    
    def test_search_empty_query(self):
        """Empty query should return error or empty results"""
        response = requests.get(f"{BASE_URL}/api/ipl/search?q=")
        # Should return 422 (validation error) for empty query
        assert response.status_code in [400, 422], f"Expected 400/422 for empty query, got {response.status_code}"
        print(f"PASS: Empty query returns {response.status_code}")


class TestIPLPlayerProfile:
    """Test individual player profile endpoint"""
    
    def test_get_player_by_name(self):
        """GET /api/ipl/players/{name} returns player profile"""
        response = requests.get(f"{BASE_URL}/api/ipl/players/Virat%20Kohli")
        assert response.status_code == 200
        data = response.json()
        
        assert "player" in data
        player = data["player"]
        assert player["name"] == "Virat Kohli"
        assert player["current_team"] == "RCB"
        assert "ipl_stats" in player
        assert "achievements" in player
        assert "bio" in player
        assert "bio_hi" in player
        print(f"PASS: Got player profile for Virat Kohli")
    
    def test_get_nonexistent_player(self):
        """GET /api/ipl/players/{name} returns error for unknown player"""
        response = requests.get(f"{BASE_URL}/api/ipl/players/Unknown%20Player")
        assert response.status_code == 200  # Returns 200 with error in body
        data = response.json()
        assert data.get("player") is None or data.get("error") is not None
        print(f"PASS: Unknown player returns appropriate response")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
