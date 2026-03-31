"""
Iteration 35 - IPL Real Data & Head-to-Head Testing
Tests REAL verified IPL stats from iplt20.com, ESPNcricinfo, CricTracker
Key verifications:
- Kohli 8661 runs (not 8004)
- Chahal 221 wickets (not 187)
- Dhoni 278 matches (not 264)
- Highest Team Total: 287/3 SRH vs RCB 2024 (not RCB vs GL 2016)
- Most Expensive: Rs 27 Cr Rishabh Pant (not Shreyas Iyer Rs 24.75 Cr)
- 2025 Cap Winners: Sai Sudharsan (Orange), Prasidh Krishna (Purple)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://fantasy-points.preview.emergentagent.com')

class TestIPLSeedEndpoint:
    """Test IPL data seeding with force parameter"""
    
    def test_seed_with_force_true(self):
        """Seed should reseed all data when force=true"""
        response = requests.get(f"{BASE_URL}/api/ipl/seed?force=true")
        assert response.status_code == 200
        data = response.json()
        assert data["players"] == 20, f"Expected 20 players, got {data['players']}"
        assert data["records"] == 18, f"Expected 18 records, got {data['records']}"
        assert data["cap_winners"] == 10, f"Expected 10 cap winners, got {data['cap_winners']}"
        assert data["force_reseeded"] == True
        print(f"✅ Seed with force=true: {data['players']} players, {data['records']} records, {data['cap_winners']} caps")


class TestIPLPlayersEndpoint:
    """Test /api/ipl/players with REAL verified stats"""
    
    def test_players_count(self):
        """Should return 20 players"""
        response = requests.get(f"{BASE_URL}/api/ipl/players")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 20, f"Expected 20 players, got {data['total']}"
        print(f"✅ Players count: {data['total']}")
    
    def test_virat_kohli_8661_runs(self):
        """Kohli should have 8661 runs (REAL verified stat)"""
        response = requests.get(f"{BASE_URL}/api/ipl/players")
        assert response.status_code == 200
        players = response.json()["players"]
        kohli = next((p for p in players if p["name"] == "Virat Kohli"), None)
        assert kohli is not None, "Virat Kohli not found"
        assert kohli["ipl_stats"]["runs"] == 8661, f"Expected 8661 runs, got {kohli['ipl_stats']['runs']}"
        assert kohli["ipl_stats"]["matches"] == 267
        assert kohli["ipl_stats"]["fifties"] == 63
        assert kohli["ipl_stats"]["hundreds"] == 8
        print(f"✅ Virat Kohli: {kohli['ipl_stats']['runs']} runs, {kohli['ipl_stats']['matches']} matches")
    
    def test_yuzvendra_chahal_221_wickets(self):
        """Chahal should have 221 wickets (REAL verified stat)"""
        response = requests.get(f"{BASE_URL}/api/ipl/players")
        assert response.status_code == 200
        players = response.json()["players"]
        chahal = next((p for p in players if p["name"] == "Yuzvendra Chahal"), None)
        assert chahal is not None, "Yuzvendra Chahal not found"
        assert chahal["ipl_stats"]["wickets"] == 221, f"Expected 221 wickets, got {chahal['ipl_stats']['wickets']}"
        assert chahal["ipl_stats"]["matches"] == 174
        print(f"✅ Yuzvendra Chahal: {chahal['ipl_stats']['wickets']} wickets, {chahal['ipl_stats']['matches']} matches")
    
    def test_ms_dhoni_278_matches(self):
        """Dhoni should have 278 matches (REAL verified stat)"""
        response = requests.get(f"{BASE_URL}/api/ipl/players")
        assert response.status_code == 200
        players = response.json()["players"]
        dhoni = next((p for p in players if p["name"] == "MS Dhoni"), None)
        assert dhoni is not None, "MS Dhoni not found"
        assert dhoni["ipl_stats"]["matches"] == 278, f"Expected 278 matches, got {dhoni['ipl_stats']['matches']}"
        assert dhoni["ipl_stats"]["runs"] == 5439
        print(f"✅ MS Dhoni: {dhoni['ipl_stats']['matches']} matches, {dhoni['ipl_stats']['runs']} runs")
    
    def test_rohit_sharma_stats(self):
        """Rohit Sharma should have correct stats"""
        response = requests.get(f"{BASE_URL}/api/ipl/players")
        assert response.status_code == 200
        players = response.json()["players"]
        rohit = next((p for p in players if p["name"] == "Rohit Sharma"), None)
        assert rohit is not None, "Rohit Sharma not found"
        assert rohit["ipl_stats"]["runs"] == 7124
        assert rohit["ipl_stats"]["matches"] == 273
        print(f"✅ Rohit Sharma: {rohit['ipl_stats']['runs']} runs, {rohit['ipl_stats']['matches']} matches")


class TestIPLRecordsEndpoint:
    """Test /api/ipl/records with REAL verified records"""
    
    def test_records_count(self):
        """Should return 18 records"""
        response = requests.get(f"{BASE_URL}/api/ipl/records")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 18, f"Expected 18 records, got {data['total']}"
        print(f"✅ Records count: {data['total']}")
    
    def test_most_runs_kohli_8661(self):
        """Most Runs record should be Kohli with 8,661"""
        response = requests.get(f"{BASE_URL}/api/ipl/records")
        assert response.status_code == 200
        records = response.json()["records"]
        most_runs = next((r for r in records if r["title"] == "Most Runs (All-time)"), None)
        assert most_runs is not None, "Most Runs record not found"
        assert most_runs["value"] == "8,661", f"Expected 8,661, got {most_runs['value']}"
        assert most_runs["holder"] == "Virat Kohli"
        print(f"✅ Most Runs: {most_runs['value']} by {most_runs['holder']}")
    
    def test_most_wickets_chahal_221(self):
        """Most Wickets record should be Chahal with 221"""
        response = requests.get(f"{BASE_URL}/api/ipl/records")
        assert response.status_code == 200
        records = response.json()["records"]
        most_wickets = next((r for r in records if r["title"] == "Most Wickets (All-time)"), None)
        assert most_wickets is not None, "Most Wickets record not found"
        assert most_wickets["value"] == "221", f"Expected 221, got {most_wickets['value']}"
        assert most_wickets["holder"] == "Yuzvendra Chahal"
        print(f"✅ Most Wickets: {most_wickets['value']} by {most_wickets['holder']}")
    
    def test_highest_team_total_srh_287(self):
        """Highest Team Total should be SRH 287/3 vs RCB 2024 (NOT RCB vs GL 2016)"""
        response = requests.get(f"{BASE_URL}/api/ipl/records")
        assert response.status_code == 200
        records = response.json()["records"]
        highest_total = next((r for r in records if r["title"] == "Highest Team Total"), None)
        assert highest_total is not None, "Highest Team Total record not found"
        assert highest_total["value"] == "287/3", f"Expected 287/3, got {highest_total['value']}"
        assert "SRH" in highest_total["holder"], f"Expected SRH, got {highest_total['holder']}"
        assert "2024" in highest_total["year"], f"Expected 2024, got {highest_total['year']}"
        print(f"✅ Highest Team Total: {highest_total['value']} by {highest_total['holder']} ({highest_total['year']})")
    
    def test_most_expensive_rishabh_pant_27cr(self):
        """Most Expensive Player should be Rishabh Pant Rs 27 Cr (NOT Shreyas Iyer Rs 24.75 Cr)"""
        response = requests.get(f"{BASE_URL}/api/ipl/records")
        assert response.status_code == 200
        records = response.json()["records"]
        most_expensive = next((r for r in records if r["title"] == "Most Expensive Player (Auction)"), None)
        assert most_expensive is not None, "Most Expensive Player record not found"
        assert most_expensive["value"] == "Rs 27 Cr", f"Expected Rs 27 Cr, got {most_expensive['value']}"
        assert most_expensive["holder"] == "Rishabh Pant", f"Expected Rishabh Pant, got {most_expensive['holder']}"
        print(f"✅ Most Expensive: {most_expensive['value']} - {most_expensive['holder']}")
    
    def test_most_matches_dhoni_278(self):
        """Most Matches should be Dhoni with 278"""
        response = requests.get(f"{BASE_URL}/api/ipl/records")
        assert response.status_code == 200
        records = response.json()["records"]
        most_matches = next((r for r in records if r["title"] == "Most Matches Played"), None)
        assert most_matches is not None, "Most Matches record not found"
        assert most_matches["value"] == "278", f"Expected 278, got {most_matches['value']}"
        assert most_matches["holder"] == "MS Dhoni"
        print(f"✅ Most Matches: {most_matches['value']} by {most_matches['holder']}")


class TestIPLCapsEndpoint:
    """Test /api/ipl/caps with 2025 winners"""
    
    def test_caps_count(self):
        """Should return 10 cap winners (2016-2025)"""
        response = requests.get(f"{BASE_URL}/api/ipl/caps")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 10, f"Expected 10 cap winners, got {data['total']}"
        print(f"✅ Cap winners count: {data['total']}")
    
    def test_2025_orange_cap_sai_sudharsan(self):
        """2025 Orange Cap should be Sai Sudharsan"""
        response = requests.get(f"{BASE_URL}/api/ipl/caps")
        assert response.status_code == 200
        caps = response.json()["cap_winners"]
        cap_2025 = next((c for c in caps if c["year"] == 2025), None)
        assert cap_2025 is not None, "2025 cap winner not found"
        assert cap_2025["orange_cap"]["player"] == "Sai Sudharsan", f"Expected Sai Sudharsan, got {cap_2025['orange_cap']['player']}"
        assert cap_2025["orange_cap"]["runs"] == 759
        assert cap_2025["orange_cap"]["team"] == "GT"
        print(f"✅ 2025 Orange Cap: {cap_2025['orange_cap']['player']} ({cap_2025['orange_cap']['runs']} runs)")
    
    def test_2025_purple_cap_prasidh_krishna(self):
        """2025 Purple Cap should be Prasidh Krishna"""
        response = requests.get(f"{BASE_URL}/api/ipl/caps")
        assert response.status_code == 200
        caps = response.json()["cap_winners"]
        cap_2025 = next((c for c in caps if c["year"] == 2025), None)
        assert cap_2025 is not None, "2025 cap winner not found"
        assert cap_2025["purple_cap"]["player"] == "Prasidh Krishna", f"Expected Prasidh Krishna, got {cap_2025['purple_cap']['player']}"
        assert cap_2025["purple_cap"]["wickets"] == 25
        assert cap_2025["purple_cap"]["team"] == "GT"
        print(f"✅ 2025 Purple Cap: {cap_2025['purple_cap']['player']} ({cap_2025['purple_cap']['wickets']} wickets)")
    
    def test_2016_kohli_973_runs(self):
        """2016 Orange Cap should be Kohli with 973 runs"""
        response = requests.get(f"{BASE_URL}/api/ipl/caps")
        assert response.status_code == 200
        caps = response.json()["cap_winners"]
        cap_2016 = next((c for c in caps if c["year"] == 2016), None)
        assert cap_2016 is not None, "2016 cap winner not found"
        assert cap_2016["orange_cap"]["player"] == "Virat Kohli"
        assert cap_2016["orange_cap"]["runs"] == 973
        print(f"✅ 2016 Orange Cap: {cap_2016['orange_cap']['player']} ({cap_2016['orange_cap']['runs']} runs)")


class TestHeadToHeadEndpoint:
    """Test /api/ipl/head-to-head endpoint"""
    
    def test_head_to_head_kohli_vs_rohit(self):
        """Head-to-head should return both players' complete stats"""
        response = requests.get(f"{BASE_URL}/api/ipl/head-to-head?player1=Virat+Kohli&player2=Rohit+Sharma")
        assert response.status_code == 200
        data = response.json()
        assert "player1" in data, "player1 not in response"
        assert "player2" in data, "player2 not in response"
        assert data["player1"]["name"] == "Virat Kohli"
        assert data["player2"]["name"] == "Rohit Sharma"
        assert data["player1"]["ipl_stats"]["runs"] == 8661
        assert data["player2"]["ipl_stats"]["runs"] == 7124
        print(f"✅ Head-to-Head: {data['player1']['name']} ({data['player1']['ipl_stats']['runs']}) vs {data['player2']['name']} ({data['player2']['ipl_stats']['runs']})")
    
    def test_head_to_head_dhoni_vs_chahal(self):
        """Head-to-head with batsman vs bowler"""
        response = requests.get(f"{BASE_URL}/api/ipl/head-to-head?player1=MS+Dhoni&player2=Yuzvendra+Chahal")
        assert response.status_code == 200
        data = response.json()
        assert data["player1"]["name"] == "MS Dhoni"
        assert data["player2"]["name"] == "Yuzvendra Chahal"
        assert data["player1"]["ipl_stats"]["matches"] == 278
        assert data["player2"]["ipl_stats"]["wickets"] == 221
        print(f"✅ Head-to-Head: {data['player1']['name']} ({data['player1']['ipl_stats']['matches']} matches) vs {data['player2']['name']} ({data['player2']['ipl_stats']['wickets']} wickets)")
    
    def test_head_to_head_invalid_player(self):
        """Head-to-head with invalid player should return error"""
        response = requests.get(f"{BASE_URL}/api/ipl/head-to-head?player1=Invalid+Player&player2=Virat+Kohli")
        assert response.status_code == 200
        data = response.json()
        assert "error" in data, "Expected error for invalid player"
        print(f"✅ Head-to-Head invalid player: {data['error']}")


class TestIPLSearchEndpoint:
    """Test /api/ipl/search endpoint"""
    
    def test_search_kohli(self):
        """Search for Kohli should return player with 8661 runs"""
        response = requests.get(f"{BASE_URL}/api/ipl/search?q=Kohli")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0, "No results found"
        players = data["results"]["players"]
        kohli = next((p for p in players if p["name"] == "Virat Kohli"), None)
        assert kohli is not None, "Virat Kohli not found in search"
        assert kohli["ipl_stats"]["runs"] == 8661
        print(f"✅ Search Kohli: Found {data['total']} results, Kohli has {kohli['ipl_stats']['runs']} runs")
    
    def test_search_most_runs(self):
        """Search for 'Most Runs' should return record"""
        response = requests.get(f"{BASE_URL}/api/ipl/search?q=Most+Runs")
        assert response.status_code == 200
        data = response.json()
        records = data["results"]["records"]
        assert len(records) > 0, "No records found"
        print(f"✅ Search 'Most Runs': Found {len(records)} records")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
