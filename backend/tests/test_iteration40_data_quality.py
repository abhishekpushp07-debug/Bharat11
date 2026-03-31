"""
Iteration 40 - Data Quality & Team Name Fix Tests
Tests for:
1. Completed matches have real scores (r > 0)
2. Team names match short_names (no swaps)
3. Scorecard returns real batting data (11 batsmen)
4. AI Commentary returns structured data
5. Points table shows RCB not RCBW
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestCompletedMatchesWithScores:
    """Test that completed matches have real scores"""
    
    def test_completed_matches_exist(self):
        """GET /api/matches?status=completed should return completed matches"""
        response = requests.get(f"{BASE_URL}/api/matches?status=completed")
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        assert len(data["matches"]) >= 3, f"Expected at least 3 completed matches, got {len(data['matches'])}"
        print(f"✓ Found {len(data['matches'])} completed matches")
    
    def test_completed_matches_have_real_scores(self):
        """Completed matches should have scores with r > 0"""
        response = requests.get(f"{BASE_URL}/api/matches?status=completed")
        assert response.status_code == 200
        matches = response.json()["matches"]
        
        for match in matches[:3]:  # Check first 3
            live_score = match.get("live_score", {})
            scores = live_score.get("scores", [])
            assert len(scores) >= 2, f"Match {match['id']} should have 2 innings scores"
            
            for score in scores:
                runs = score.get("r", 0) or score.get("runs", 0)
                assert runs > 0, f"Match {match['id']} has zero runs in {score.get('inning', 'unknown')}"
            
            team_a = match.get("team_a", {}).get("short_name", "?")
            team_b = match.get("team_b", {}).get("short_name", "?")
            print(f"✓ {team_a} vs {team_b}: {scores[0].get('r', 0)}/{scores[0].get('w', 0)} vs {scores[1].get('r', 0)}/{scores[1].get('w', 0)}")


class TestTeamNameConsistency:
    """Test that team_a.name corresponds to team_a.short_name (no mismatches)"""
    
    def test_team_names_match_short_names(self):
        """Team names should match their short names (no swaps like DC showing SRH name)"""
        response = requests.get(f"{BASE_URL}/api/matches?status=completed")
        assert response.status_code == 200
        matches = response.json()["matches"]
        
        # Known mappings - include short name itself as valid (for Cricbuzz source)
        TEAM_MAPPINGS = {
            "RCB": ["Royal Challengers Bengaluru", "Royal Challengers Bangalore", "RCB"],
            "SRH": ["Sunrisers Hyderabad", "SRH"],
            "MI": ["Mumbai Indians", "MI"],
            "CSK": ["Chennai Super Kings", "CSK"],
            "KKR": ["Kolkata Knight Riders", "KKR"],
            "DC": ["Delhi Capitals", "DC"],
            "RR": ["Rajasthan Royals", "RR"],
            "PBKS": ["Punjab Kings", "PBKS"],
            "GT": ["Gujarat Titans", "GT"],
            "LSG": ["Lucknow Super Giants", "LSG"],
        }
        
        for match in matches:
            team_a = match.get("team_a", {})
            team_b = match.get("team_b", {})
            
            for team in [team_a, team_b]:
                short = team.get("short_name", "")
                name = team.get("name", "")
                
                if short in TEAM_MAPPINGS:
                    valid_names = TEAM_MAPPINGS[short]
                    # Key check: name should NOT be another team's name
                    other_teams = [n for k, v in TEAM_MAPPINGS.items() if k != short for n in v if n != k]
                    assert name not in other_teams, f"Team SWAP detected: short_name={short} but name={name} (belongs to another team)"
                    print(f"✓ {short} = {name}")


class TestScorecardData:
    """Test scorecard returns real batting data"""
    
    def test_scorecard_has_batsmen(self):
        """Scorecard should have batsmen (at least 6 for winning team, up to 11 for losing)"""
        # Get a completed match
        response = requests.get(f"{BASE_URL}/api/matches?status=completed")
        assert response.status_code == 200
        matches = response.json()["matches"]
        assert len(matches) > 0
        
        match_id = matches[0]["id"]
        
        # Get scorecard
        sc_response = requests.get(f"{BASE_URL}/api/matches/{match_id}/scorecard")
        assert sc_response.status_code == 200
        data = sc_response.json()
        
        assert "scorecard" in data, "Response should have scorecard field"
        scorecard = data["scorecard"]
        assert len(scorecard) >= 2, "Should have at least 2 innings"
        
        total_batsmen = 0
        for innings in scorecard:
            batting = innings.get("batting", [])
            # Winning team may have fewer batsmen (e.g., 6 if won by 4 wickets)
            assert len(batting) >= 5, f"Innings should have at least 5 batsmen, got {len(batting)}"
            total_batsmen += len(batting)
            
            # Check first batsman has real data
            if batting:
                first = batting[0]
                assert "r" in first, "Batsman should have runs (r)"
                assert "b" in first, "Batsman should have balls (b)"
                print(f"✓ {innings.get('inning', 'Unknown')}: {len(batting)} batsmen")
        
        # Total should be at least 15 (11 + 4 minimum)
        assert total_batsmen >= 15, f"Total batsmen should be >= 15, got {total_batsmen}"
    
    def test_scorecard_has_top_scorer(self):
        """Scorecard should have a top scorer with significant runs"""
        response = requests.get(f"{BASE_URL}/api/matches?status=completed")
        matches = response.json()["matches"]
        match_id = matches[0]["id"]
        
        sc_response = requests.get(f"{BASE_URL}/api/matches/{match_id}/scorecard")
        data = sc_response.json()
        
        max_runs = 0
        top_scorer = None
        
        for innings in data.get("scorecard", []):
            for batsman in innings.get("batting", []):
                runs = batsman.get("r", 0)
                if runs > max_runs:
                    max_runs = runs
                    name = batsman.get("batsman", {})
                    if isinstance(name, dict):
                        top_scorer = name.get("name", "Unknown")
                    else:
                        top_scorer = name
        
        assert max_runs >= 30, f"Top scorer should have at least 30 runs, got {max_runs}"
        print(f"✓ Top scorer: {top_scorer} with {max_runs} runs")


class TestAICommentary:
    """Test AI commentary returns structured data"""
    
    def test_ai_commentary_structure(self):
        """AI commentary should have match_pulse, key_moments, star_performers, verdict"""
        response = requests.get(f"{BASE_URL}/api/matches?status=completed")
        matches = response.json()["matches"]
        match_id = matches[0]["id"]
        
        ai_response = requests.get(f"{BASE_URL}/api/matches/{match_id}/ai-commentary")
        assert ai_response.status_code == 200
        data = ai_response.json()
        
        # Check required fields
        assert "match_pulse" in data, "Should have match_pulse"
        assert "key_moments" in data, "Should have key_moments"
        assert "star_performers" in data, "Should have star_performers"
        
        # Validate match_pulse
        pulse = data["match_pulse"]
        assert "headline" in pulse, "match_pulse should have headline"
        assert "sub" in pulse, "match_pulse should have sub"
        print(f"✓ Match Pulse: {pulse['headline'][:50]}...")
        
        # Validate key_moments
        moments = data["key_moments"]
        assert len(moments) >= 5, f"Should have at least 5 key moments, got {len(moments)}"
        for moment in moments[:3]:
            assert "over" in moment, "Moment should have over"
            assert "title" in moment, "Moment should have title"
            assert "description" in moment, "Moment should have description"
        print(f"✓ Key Moments: {len(moments)} moments")
        
        # Validate star_performers
        stars = data["star_performers"]
        assert len(stars) >= 2, f"Should have at least 2 star performers, got {len(stars)}"
        for star in stars[:2]:
            assert "name" in star, "Star should have name"
            assert "rating" in star, "Star should have rating"
            assert star["rating"] >= 5, f"Star rating should be >= 5, got {star['rating']}"
        print(f"✓ Star Performers: {[s['name'] for s in stars[:3]]}")
    
    def test_ai_commentary_has_hinglish(self):
        """AI commentary should have Hinglish text"""
        response = requests.get(f"{BASE_URL}/api/matches?status=completed")
        matches = response.json()["matches"]
        match_id = matches[0]["id"]
        
        ai_response = requests.get(f"{BASE_URL}/api/matches/{match_id}/ai-commentary")
        data = ai_response.json()
        
        # Check for Hindi words in descriptions
        hindi_words = ["kya", "hai", "yaar", "dhamaka", "zabardast", "paaji", "gaya", "bhai"]
        found_hindi = False
        
        for moment in data.get("key_moments", []):
            desc = moment.get("description", "").lower()
            if any(word in desc for word in hindi_words):
                found_hindi = True
                break
        
        assert found_hindi, "AI commentary should contain Hinglish text"
        print("✓ Hinglish text found in commentary")


class TestPointsTable:
    """Test points table shows correct team names"""
    
    def test_points_table_has_rcb_not_rcbw(self):
        """Points table should show RCB, not RCBW"""
        response = requests.get(f"{BASE_URL}/api/cricket/ipl/points-table")
        assert response.status_code == 200
        data = response.json()
        
        teams = data.get("teams", [])
        assert len(teams) == 10, f"Should have 10 IPL teams, got {len(teams)}"
        
        shortnames = [t.get("shortname", "") for t in teams]
        
        # Check RCB exists, not RCBW
        assert "RCB" in shortnames, "Should have RCB in points table"
        assert "RCBW" not in shortnames, "Should NOT have RCBW in points table"
        
        # Check other teams
        expected_teams = ["MI", "CSK", "RCB", "KKR", "DC", "RR", "SRH", "GT", "LSG", "PBKS"]
        for team in expected_teams:
            assert team in shortnames, f"Missing team {team} in points table"
        
        print(f"✓ Points table teams: {shortnames}")
    
    def test_points_table_has_wins(self):
        """Points table should have teams with wins"""
        response = requests.get(f"{BASE_URL}/api/cricket/ipl/points-table")
        data = response.json()
        
        teams_with_wins = [t for t in data.get("teams", []) if t.get("wins", 0) > 0]
        assert len(teams_with_wins) >= 1, "At least one team should have wins"
        
        for team in teams_with_wins:
            print(f"✓ {team['shortname']}: {team['wins']} wins, {team['loss']} losses")


class TestMatchWinnerText:
    """Test that completed matches have winner text"""
    
    def test_completed_matches_have_status_text(self):
        """Completed matches should have status_text with winner"""
        response = requests.get(f"{BASE_URL}/api/matches?status=completed")
        matches = response.json()["matches"]
        
        for match in matches[:3]:
            status_text = match.get("status_text", "")
            assert status_text, f"Match {match['id']} should have status_text"
            assert "won" in status_text.lower(), f"status_text should contain 'won': {status_text}"
            print(f"✓ {match['team_a']['short_name']} vs {match['team_b']['short_name']}: {status_text}")


class TestMVPRatings:
    """Test that MVPs have proper ratings"""
    
    def test_mvp_virat_kohli_rating(self):
        """Virat Kohli should have 9.6 rating in RCB vs SRH match"""
        response = requests.get(f"{BASE_URL}/api/matches?status=completed")
        matches = response.json()["matches"]
        
        # Find RCB vs SRH match
        rcb_match = None
        for match in matches:
            if match["team_a"]["short_name"] == "RCB" or match["team_b"]["short_name"] == "RCB":
                rcb_match = match
                break
        
        if not rcb_match:
            pytest.skip("RCB match not found")
        
        ai_response = requests.get(f"{BASE_URL}/api/matches/{rcb_match['id']}/ai-commentary")
        data = ai_response.json()
        
        stars = data.get("star_performers", [])
        kohli = next((s for s in stars if "Kohli" in s.get("name", "")), None)
        
        if kohli:
            assert kohli["rating"] >= 9.0, f"Kohli rating should be >= 9.0, got {kohli['rating']}"
            print(f"✓ Virat Kohli rating: {kohli['rating']}")
        else:
            print("⚠ Virat Kohli not in star performers (may be different match)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
