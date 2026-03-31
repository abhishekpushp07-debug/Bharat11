"""
IPL Records Expansion Testing - Iteration 36
Tests 115 records across 8 categories: batting, bowling, fielding, team, controversy, fun, champions, auction
Verifies category filtering, record counts, and specific record content
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestIPLRecordsExpansion:
    """Tests for the expanded IPL records (115 total across 8 categories)"""

    def test_total_records_count(self):
        """Verify total records count is 115"""
        response = requests.get(f"{BASE_URL}/api/ipl/records")
        assert response.status_code == 200
        data = response.json()
        assert data['total'] == 115, f"Expected 115 records, got {data['total']}"
        print(f"✓ Total records: {data['total']}")

    def test_batting_records_count(self):
        """Verify batting category has 25 records"""
        response = requests.get(f"{BASE_URL}/api/ipl/records?category=batting")
        assert response.status_code == 200
        data = response.json()
        assert data['total'] == 25, f"Expected 25 batting records, got {data['total']}"
        print(f"✓ Batting records: {data['total']}")

    def test_bowling_records_count(self):
        """Verify bowling category has 15 records"""
        response = requests.get(f"{BASE_URL}/api/ipl/records?category=bowling")
        assert response.status_code == 200
        data = response.json()
        assert data['total'] == 15, f"Expected 15 bowling records, got {data['total']}"
        print(f"✓ Bowling records: {data['total']}")

    def test_fielding_records_count(self):
        """Verify fielding category has 8 records"""
        response = requests.get(f"{BASE_URL}/api/ipl/records?category=fielding")
        assert response.status_code == 200
        data = response.json()
        assert data['total'] == 8, f"Expected 8 fielding records, got {data['total']}"
        print(f"✓ Fielding records: {data['total']}")

    def test_team_records_count(self):
        """Verify team category has 15 records"""
        response = requests.get(f"{BASE_URL}/api/ipl/records?category=team")
        assert response.status_code == 200
        data = response.json()
        assert data['total'] == 15, f"Expected 15 team records, got {data['total']}"
        print(f"✓ Team records: {data['total']}")

    def test_controversy_records_count(self):
        """Verify controversy category has 12 records"""
        response = requests.get(f"{BASE_URL}/api/ipl/records?category=controversy")
        assert response.status_code == 200
        data = response.json()
        assert data['total'] == 12, f"Expected 12 controversy records, got {data['total']}"
        print(f"✓ Controversy records: {data['total']}")

    def test_fun_records_count(self):
        """Verify fun category has 12 records"""
        response = requests.get(f"{BASE_URL}/api/ipl/records?category=fun")
        assert response.status_code == 200
        data = response.json()
        assert data['total'] == 12, f"Expected 12 fun records, got {data['total']}"
        print(f"✓ Fun records: {data['total']}")

    def test_champions_records_count(self):
        """Verify champions category has 18 records (IPL 2008-2025)"""
        response = requests.get(f"{BASE_URL}/api/ipl/records?category=champions")
        assert response.status_code == 200
        data = response.json()
        assert data['total'] == 18, f"Expected 18 champions records, got {data['total']}"
        print(f"✓ Champions records: {data['total']}")

    def test_auction_records_count(self):
        """Verify auction category has 10 records"""
        response = requests.get(f"{BASE_URL}/api/ipl/records?category=auction")
        assert response.status_code == 200
        data = response.json()
        assert data['total'] == 10, f"Expected 10 auction records, got {data['total']}"
        print(f"✓ Auction records: {data['total']}")


class TestControversyRecordsContent:
    """Tests for specific controversy/drama records"""

    def test_slapgate_record(self):
        """Verify Slapgate (2008) record exists"""
        response = requests.get(f"{BASE_URL}/api/ipl/records?category=controversy")
        assert response.status_code == 200
        records = response.json()['records']
        slapgate = next((r for r in records if 'Slapgate' in r['title']), None)
        assert slapgate is not None, "Slapgate record not found"
        assert 'Harbhajan' in slapgate['value'], "Slapgate should mention Harbhajan"
        print(f"✓ Slapgate record: {slapgate['title']} - {slapgate['value']}")

    def test_spot_fixing_record(self):
        """Verify Spot-Fixing Scandal (2013) record exists"""
        response = requests.get(f"{BASE_URL}/api/ipl/records?category=controversy")
        assert response.status_code == 200
        records = response.json()['records']
        spot_fixing = next((r for r in records if 'Spot-Fixing' in r['title']), None)
        assert spot_fixing is not None, "Spot-Fixing record not found"
        assert 'Sreesanth' in spot_fixing['value'], "Should mention Sreesanth"
        print(f"✓ Spot-Fixing record: {spot_fixing['title']} - {spot_fixing['value']}")

    def test_csk_ban_record(self):
        """Verify CSK & RR Ban record exists"""
        response = requests.get(f"{BASE_URL}/api/ipl/records?category=controversy")
        assert response.status_code == 200
        records = response.json()['records']
        csk_ban = next((r for r in records if 'CSK' in r['title'] and 'Banned' in r['title']), None)
        assert csk_ban is not None, "CSK Ban record not found"
        assert '2016-2017' in csk_ban['value'], "Should mention 2016-2017 suspension"
        print(f"✓ CSK Ban record: {csk_ban['title']} - {csk_ban['value']}")

    def test_mankading_record(self):
        """Verify Mankading (2019) record exists"""
        response = requests.get(f"{BASE_URL}/api/ipl/records?category=controversy")
        assert response.status_code == 200
        records = response.json()['records']
        mankading = next((r for r in records if 'Mankading' in r['title']), None)
        assert mankading is not None, "Mankading record not found"
        assert 'Ashwin' in mankading['value'] or 'Buttler' in mankading['value'], "Should mention Ashwin or Buttler"
        print(f"✓ Mankading record: {mankading['title']} - {mankading['value']}")


class TestChampionsRecordsContent:
    """Tests for IPL champions history (2008-2025)"""

    def test_ipl_2008_champion_rr(self):
        """Verify IPL 2008 Champion is Rajasthan Royals"""
        response = requests.get(f"{BASE_URL}/api/ipl/records?category=champions")
        assert response.status_code == 200
        records = response.json()['records']
        ipl_2008 = next((r for r in records if '2008' in r['title']), None)
        assert ipl_2008 is not None, "IPL 2008 record not found"
        assert 'Rajasthan Royals' in ipl_2008['value'], "2008 champion should be RR"
        print(f"✓ IPL 2008: {ipl_2008['value']}")

    def test_ipl_2025_champion_rcb(self):
        """Verify IPL 2025 Champion is Royal Challengers Bengaluru"""
        response = requests.get(f"{BASE_URL}/api/ipl/records?category=champions")
        assert response.status_code == 200
        records = response.json()['records']
        ipl_2025 = next((r for r in records if '2025' in r['title']), None)
        assert ipl_2025 is not None, "IPL 2025 record not found"
        assert 'Royal Challengers' in ipl_2025['value'] or 'RCB' in ipl_2025['value'], "2025 champion should be RCB"
        print(f"✓ IPL 2025: {ipl_2025['value']}")

    def test_all_18_champions_present(self):
        """Verify all 18 IPL seasons (2008-2025) have champions"""
        response = requests.get(f"{BASE_URL}/api/ipl/records?category=champions")
        assert response.status_code == 200
        records = response.json()['records']
        years = [str(y) for y in range(2008, 2026)]
        for year in years:
            champion = next((r for r in records if year in r['title']), None)
            assert champion is not None, f"IPL {year} champion not found"
        print(f"✓ All 18 IPL champions (2008-2025) present")


class TestAuctionRecordsContent:
    """Tests for auction milestone records"""

    def test_pant_27cr_record(self):
        """Verify Rishabh Pant Rs 27 Cr record exists"""
        response = requests.get(f"{BASE_URL}/api/ipl/records?category=auction")
        assert response.status_code == 200
        records = response.json()['records']
        pant_record = next((r for r in records if 'Pant' in r['title'] or '27 Cr' in r['value']), None)
        assert pant_record is not None, "Pant Rs 27 Cr record not found"
        assert '27' in pant_record['value'], "Should mention Rs 27 Cr"
        print(f"✓ Pant auction record: {pant_record['title']} - {pant_record['value']}")

    def test_dhoni_first_auction_record(self):
        """Verify MS Dhoni first mega auction record exists"""
        response = requests.get(f"{BASE_URL}/api/ipl/records?category=auction")
        assert response.status_code == 200
        records = response.json()['records']
        dhoni_record = next((r for r in records if '2008' in r['title'] and 'Dhoni' in r['value']), None)
        assert dhoni_record is not None, "Dhoni 2008 auction record not found"
        print(f"✓ Dhoni 2008 auction: {dhoni_record['title']} - {dhoni_record['value']}")


class TestFieldingRecordsContent:
    """Tests for fielding records"""

    def test_dhoni_201_dismissals(self):
        """Verify Dhoni 201 dismissals record exists"""
        response = requests.get(f"{BASE_URL}/api/ipl/records?category=fielding")
        assert response.status_code == 200
        records = response.json()['records']
        dhoni_dismissals = next((r for r in records if 'Dismissals' in r['title'] and 'Dhoni' in r['holder']), None)
        assert dhoni_dismissals is not None, "Dhoni dismissals record not found"
        assert '201' in dhoni_dismissals['value'], "Should show 201 dismissals"
        print(f"✓ Dhoni dismissals: {dhoni_dismissals['title']} - {dhoni_dismissals['value']}")


class TestTeamRecordsContent:
    """Tests for team records"""

    def test_srh_287_highest_total(self):
        """Verify SRH 287/3 highest team total record"""
        response = requests.get(f"{BASE_URL}/api/ipl/records?category=team")
        assert response.status_code == 200
        records = response.json()['records']
        highest = next((r for r in records if 'Highest Team Total' in r['title']), None)
        assert highest is not None, "Highest team total record not found"
        assert '287' in highest['value'], "Should show 287/3"
        assert 'SRH' in highest['holder'] or 'SRH' in highest['team'], "Should be SRH"
        print(f"✓ Highest team total: {highest['value']} by {highest['holder']}")

    def test_mi_vs_csk_h2h(self):
        """Verify MI vs CSK Head-to-Head record"""
        response = requests.get(f"{BASE_URL}/api/ipl/records?category=team")
        assert response.status_code == 200
        records = response.json()['records']
        h2h = next((r for r in records if 'MI vs CSK' in r['title'] or 'Head-to-Head' in r['title']), None)
        assert h2h is not None, "MI vs CSK H2H record not found"
        assert '21-18' in h2h['value'], "Should show 21-18"
        print(f"✓ MI vs CSK H2H: {h2h['value']}")


class TestFunRecordsContent:
    """Tests for fun/unique records"""

    def test_srh_top_3_totals(self):
        """Verify SRH owns top 3 team totals record"""
        response = requests.get(f"{BASE_URL}/api/ipl/records?category=fun")
        assert response.status_code == 200
        records = response.json()['records']
        srh_totals = next((r for r in records if 'SRH' in r['title'] and 'Top 3' in r['title']), None)
        assert srh_totals is not None, "SRH top 3 totals record not found"
        assert '287' in srh_totals['value'] and '286' in srh_totals['value'] and '278' in srh_totals['value'], "Should show all 3 totals"
        print(f"✓ SRH top 3 totals: {srh_totals['value']}")


class TestIPLPlayersEndpoint:
    """Tests for IPL players endpoint"""

    def test_players_endpoint_returns_data(self):
        """Verify players endpoint returns player data"""
        response = requests.get(f"{BASE_URL}/api/ipl/players?limit=50")
        assert response.status_code == 200
        data = response.json()
        assert 'players' in data
        assert len(data['players']) > 0
        print(f"✓ Players endpoint: {len(data['players'])} players returned")

    def test_kohli_stats_present(self):
        """Verify Virat Kohli stats are present"""
        response = requests.get(f"{BASE_URL}/api/ipl/players?limit=50")
        assert response.status_code == 200
        players = response.json()['players']
        kohli = next((p for p in players if 'Kohli' in p['name']), None)
        assert kohli is not None, "Kohli not found"
        assert kohli['ipl_stats']['runs'] == 8661, f"Kohli runs should be 8661, got {kohli['ipl_stats']['runs']}"
        print(f"✓ Kohli stats: {kohli['ipl_stats']['runs']} runs")


class TestHeadToHeadEndpoint:
    """Tests for head-to-head comparison endpoint"""

    def test_head_to_head_returns_both_players(self):
        """Verify head-to-head endpoint returns both players"""
        response = requests.get(f"{BASE_URL}/api/ipl/head-to-head?player1=Virat%20Kohli&player2=Rohit%20Sharma")
        assert response.status_code == 200
        data = response.json()
        assert 'player1' in data and 'player2' in data
        assert data['player1']['name'] == 'Virat Kohli'
        assert data['player2']['name'] == 'Rohit Sharma'
        print(f"✓ Head-to-head: {data['player1']['name']} vs {data['player2']['name']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
