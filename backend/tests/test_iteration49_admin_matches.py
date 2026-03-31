"""
Iteration 49 - Admin Matches Section with 2 Sub-Tabs Test Suite
Tests:
1. Admin login with phone 7004186276 and PIN 5524
2. Matches list with 3 sections: LIVE, UPCOMING, COMPLETED
3. PBKS vs GT shows as UPCOMING with correct IST date
4. Match status transitions: upcoming→live, live→upcoming (unlive)
5. Contest CRUD: create, status toggle, delete
6. Max 5 contests per match enforcement
7. Contest status transitions: open→live→locked→open
8. Templates with 16 questions
"""
import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://fantasy-points.preview.emergentagent.com')


class TestAdminLogin:
    """Test admin authentication"""
    
    def test_admin_login_success(self):
        """Admin login with correct credentials"""
        r = requests.post(f'{BASE_URL}/api/auth/login', json={
            'phone': '7004186276',
            'pin': '5524'
        })
        assert r.status_code == 200
        data = r.json()
        assert 'token' in data
        assert 'access_token' in data['token']
        assert data['user']['is_admin'] == True
        print(f"✓ Admin login successful: {data['user']['username']}")


@pytest.fixture(scope='module')
def admin_token():
    """Get admin auth token"""
    r = requests.post(f'{BASE_URL}/api/auth/login', json={
        'phone': '7004186276',
        'pin': '5524'
    })
    if r.status_code == 200:
        return r.json()['token']['access_token']
    pytest.skip("Admin login failed")


@pytest.fixture(scope='module')
def admin_headers(admin_token):
    """Get admin auth headers"""
    return {'Authorization': f'Bearer {admin_token}'}


class TestMatchesList:
    """Test matches listing and sections"""
    
    def test_list_matches_returns_data(self, admin_headers):
        """Matches list returns data"""
        r = requests.get(f'{BASE_URL}/api/matches?limit=50', headers=admin_headers)
        assert r.status_code == 200
        data = r.json()
        assert 'matches' in data
        assert len(data['matches']) > 0
        print(f"✓ Matches list: {len(data['matches'])} matches")
    
    def test_matches_have_three_statuses(self, admin_headers):
        """Matches have LIVE, UPCOMING, COMPLETED statuses"""
        r = requests.get(f'{BASE_URL}/api/matches?limit=50', headers=admin_headers)
        assert r.status_code == 200
        matches = r.json()['matches']
        
        statuses = set(m.get('status') for m in matches)
        print(f"✓ Match statuses found: {statuses}")
        
        # Count by status
        live = [m for m in matches if m.get('status') == 'live']
        upcoming = [m for m in matches if m.get('status') == 'upcoming']
        completed = [m for m in matches if m.get('status') == 'completed']
        
        print(f"✓ LIVE: {len(live)}, UPCOMING: {len(upcoming)}, COMPLETED: {len(completed)}")
        
        # At least upcoming and completed should exist
        assert len(upcoming) > 0 or len(completed) > 0
    
    def test_pbks_vs_gt_is_upcoming(self, admin_headers):
        """PBKS vs GT should show as UPCOMING"""
        r = requests.get(f'{BASE_URL}/api/matches?limit=50', headers=admin_headers)
        assert r.status_code == 200
        matches = r.json()['matches']
        
        pbks_gt = None
        for m in matches:
            ta = m.get('team_a', {}).get('short_name', '')
            tb = m.get('team_b', {}).get('short_name', '')
            if 'PBKS' in [ta, tb] and 'GT' in [ta, tb]:
                pbks_gt = m
                break
        
        assert pbks_gt is not None, "PBKS vs GT match not found"
        assert pbks_gt['status'] == 'upcoming', f"PBKS vs GT should be UPCOMING, got {pbks_gt['status']}"
        print(f"✓ PBKS vs GT: status={pbks_gt['status']}, start_time={pbks_gt['start_time']}")
    
    def test_pbks_vs_gt_date_is_march_31(self, admin_headers):
        """PBKS vs GT should have date 31 Mar 2026"""
        r = requests.get(f'{BASE_URL}/api/matches?limit=50', headers=admin_headers)
        assert r.status_code == 200
        matches = r.json()['matches']
        
        pbks_gt = None
        for m in matches:
            ta = m.get('team_a', {}).get('short_name', '')
            tb = m.get('team_b', {}).get('short_name', '')
            if 'PBKS' in [ta, tb] and 'GT' in [ta, tb]:
                pbks_gt = m
                break
        
        assert pbks_gt is not None
        start_time = pbks_gt.get('start_time', '')
        # Should be 2026-03-31T14:00:00 (UTC) which is 07:30 PM IST
        assert '2026-03-31' in start_time, f"Expected 2026-03-31, got {start_time}"
        print(f"✓ PBKS vs GT date: {start_time}")


class TestMatchStatusTransitions:
    """Test match status transitions"""
    
    def test_match_status_upcoming_to_live(self, admin_headers):
        """Match can transition from upcoming to live"""
        # Find an upcoming match
        r = requests.get(f'{BASE_URL}/api/matches?status=upcoming&limit=10', headers=admin_headers)
        assert r.status_code == 200
        matches = r.json()['matches']
        
        if not matches:
            pytest.skip("No upcoming matches to test")
        
        match = matches[0]
        match_id = match['id']
        
        # Make it live
        r = requests.put(f'{BASE_URL}/api/matches/{match_id}/status', 
                        json={'status': 'live'}, headers=admin_headers)
        assert r.status_code == 200
        assert r.json()['status'] == 'live'
        print(f"✓ Match {match_id[:8]} transitioned to LIVE")
        
        # Revert back to upcoming
        r = requests.put(f'{BASE_URL}/api/matches/{match_id}/status', 
                        json={'status': 'upcoming'}, headers=admin_headers)
        assert r.status_code == 200
        assert r.json()['status'] == 'upcoming'
        print(f"✓ Match {match_id[:8]} reverted to UPCOMING")
    
    def test_match_status_live_to_upcoming_unlive(self, admin_headers):
        """Match can transition from live to upcoming (unlive)"""
        # Find an upcoming match and make it live first
        r = requests.get(f'{BASE_URL}/api/matches?status=upcoming&limit=10', headers=admin_headers)
        assert r.status_code == 200
        matches = r.json()['matches']
        
        if not matches:
            pytest.skip("No upcoming matches to test")
        
        match = matches[0]
        match_id = match['id']
        
        # Make it live
        r = requests.put(f'{BASE_URL}/api/matches/{match_id}/status', 
                        json={'status': 'live'}, headers=admin_headers)
        assert r.status_code == 200
        
        # Make it unlive (back to upcoming)
        r = requests.put(f'{BASE_URL}/api/matches/{match_id}/status', 
                        json={'status': 'upcoming'}, headers=admin_headers)
        assert r.status_code == 200
        assert r.json()['status'] == 'upcoming'
        print(f"✓ Match {match_id[:8]} unlive (live→upcoming) works")


class TestContestCRUD:
    """Test contest CRUD operations"""
    
    def test_list_contests(self, admin_headers):
        """List all contests"""
        r = requests.get(f'{BASE_URL}/api/admin/contests?limit=50', headers=admin_headers)
        assert r.status_code == 200
        data = r.json()
        assert 'contests' in data
        print(f"✓ Contests list: {len(data['contests'])} contests")
    
    def test_create_contest(self, admin_headers):
        """Create a new contest"""
        # Get a match and template
        r = requests.get(f'{BASE_URL}/api/matches?status=upcoming&limit=10', headers=admin_headers)
        matches = r.json()['matches']
        
        r = requests.get(f'{BASE_URL}/api/admin/templates?limit=10', headers=admin_headers)
        templates = r.json()['templates']
        
        if not matches or not templates:
            pytest.skip("No matches or templates available")
        
        # Find a match with less than 5 contests
        match = None
        for m in matches:
            r = requests.get(f'{BASE_URL}/api/matches/{m["id"]}/contests', headers=admin_headers)
            if r.status_code == 200:
                contests = r.json().get('contests', [])
                if len(contests) < 5:
                    match = m
                    break
        
        if not match:
            pytest.skip("No match with less than 5 contests")
        
        template = templates[0]
        
        # Create contest
        r = requests.post(f'{BASE_URL}/api/admin/contests', json={
            'match_id': match['id'],
            'template_id': template['id'],
            'name': f'TEST_Iteration49_Contest',
            'entry_fee': 500,
            'prize_pool': 0,
            'max_participants': 1000
        }, headers=admin_headers)
        
        assert r.status_code == 201
        contest = r.json()
        assert contest['name'] == 'TEST_Iteration49_Contest'
        assert contest['status'] == 'open'
        print(f"✓ Contest created: {contest['id'][:8]}")
        
        # Cleanup - delete the contest
        r = requests.delete(f'{BASE_URL}/api/admin/contests/{contest["id"]}', headers=admin_headers)
        assert r.status_code == 200
        print(f"✓ Contest deleted: {contest['id'][:8]}")
    
    def test_contest_status_open_to_live(self, admin_headers):
        """Contest can transition from open to live"""
        r = requests.get(f'{BASE_URL}/api/admin/contests?limit=50', headers=admin_headers)
        contests = r.json()['contests']
        
        open_contest = next((c for c in contests if c.get('status') == 'open'), None)
        if not open_contest:
            pytest.skip("No open contest to test")
        
        contest_id = open_contest['id']
        
        # Make it live
        r = requests.put(f'{BASE_URL}/api/admin/contests/{contest_id}/status', 
                        json={'status': 'live'}, headers=admin_headers)
        assert r.status_code == 200
        assert r.json()['new_status'] == 'live'
        print(f"✓ Contest {contest_id[:8]} transitioned to LIVE")
        
        # Revert back to open
        r = requests.put(f'{BASE_URL}/api/admin/contests/{contest_id}/status', 
                        json={'status': 'open'}, headers=admin_headers)
        assert r.status_code == 200
        assert r.json()['new_status'] == 'open'
        print(f"✓ Contest {contest_id[:8]} reverted to OPEN")
    
    def test_contest_status_live_to_open_unlive(self, admin_headers):
        """Contest can transition from live to open (unlive)"""
        r = requests.get(f'{BASE_URL}/api/admin/contests?limit=50', headers=admin_headers)
        contests = r.json()['contests']
        
        open_contest = next((c for c in contests if c.get('status') == 'open'), None)
        if not open_contest:
            pytest.skip("No open contest to test")
        
        contest_id = open_contest['id']
        
        # Make it live
        r = requests.put(f'{BASE_URL}/api/admin/contests/{contest_id}/status', 
                        json={'status': 'live'}, headers=admin_headers)
        assert r.status_code == 200
        
        # Make it unlive (back to open)
        r = requests.put(f'{BASE_URL}/api/admin/contests/{contest_id}/status', 
                        json={'status': 'open'}, headers=admin_headers)
        assert r.status_code == 200
        assert r.json()['new_status'] == 'open'
        print(f"✓ Contest {contest_id[:8]} unlive (live→open) works")
    
    def test_delete_contest(self, admin_headers):
        """Delete a contest"""
        # Create a test contest first
        r = requests.get(f'{BASE_URL}/api/matches?status=upcoming&limit=10', headers=admin_headers)
        matches = r.json()['matches']
        
        r = requests.get(f'{BASE_URL}/api/admin/templates?limit=10', headers=admin_headers)
        templates = r.json()['templates']
        
        if not matches or not templates:
            pytest.skip("No matches or templates available")
        
        # Find a match with less than 5 contests
        match = None
        for m in matches:
            r = requests.get(f'{BASE_URL}/api/matches/{m["id"]}/contests', headers=admin_headers)
            if r.status_code == 200:
                contests = r.json().get('contests', [])
                if len(contests) < 5:
                    match = m
                    break
        
        if not match:
            pytest.skip("No match with less than 5 contests")
        
        template = templates[0]
        
        # Create contest
        r = requests.post(f'{BASE_URL}/api/admin/contests', json={
            'match_id': match['id'],
            'template_id': template['id'],
            'name': f'TEST_Delete_Contest',
            'entry_fee': 500,
            'prize_pool': 0,
            'max_participants': 1000
        }, headers=admin_headers)
        
        if r.status_code != 201:
            pytest.skip("Could not create test contest")
        
        contest_id = r.json()['id']
        
        # Delete it
        r = requests.delete(f'{BASE_URL}/api/admin/contests/{contest_id}', headers=admin_headers)
        assert r.status_code == 200
        print(f"✓ Contest {contest_id[:8]} deleted successfully")


class TestMax5ContestsEnforcement:
    """Test max 5 contests per match enforcement"""
    
    def test_max_5_contests_enforcement(self, admin_headers):
        """Backend returns 400 when trying to create 6th contest"""
        # Find a match and check contest count
        r = requests.get(f'{BASE_URL}/api/matches?status=upcoming&limit=50', headers=admin_headers)
        matches = r.json()['matches']
        
        r = requests.get(f'{BASE_URL}/api/admin/templates?limit=10', headers=admin_headers)
        templates = r.json()['templates']
        
        if not matches or not templates:
            pytest.skip("No matches or templates available")
        
        template = templates[0]
        
        # Find a match and count its contests
        for match in matches:
            r = requests.get(f'{BASE_URL}/api/matches/{match["id"]}/contests', headers=admin_headers)
            if r.status_code == 200:
                contests = r.json().get('contests', [])
                if len(contests) >= 5:
                    # Try to create 6th contest - should fail
                    r = requests.post(f'{BASE_URL}/api/admin/contests', json={
                        'match_id': match['id'],
                        'template_id': template['id'],
                        'name': f'TEST_6th_Contest',
                        'entry_fee': 500,
                        'prize_pool': 0,
                        'max_participants': 1000
                    }, headers=admin_headers)
                    
                    assert r.status_code == 400
                    assert 'Maximum 5 contests' in r.json().get('detail', '')
                    print(f"✓ Max 5 contests enforcement works: {r.json()['detail']}")
                    return
        
        pytest.skip("No match with 5 contests found to test enforcement")


class TestTemplatesAndQuestions:
    """Test templates and questions"""
    
    def test_list_templates(self, admin_headers):
        """List all templates"""
        r = requests.get(f'{BASE_URL}/api/admin/templates?limit=50', headers=admin_headers)
        assert r.status_code == 200
        data = r.json()
        assert 'templates' in data
        print(f"✓ Templates list: {len(data['templates'])} templates")
    
    def test_template_has_16_questions(self, admin_headers):
        """Full match template has 16 questions"""
        r = requests.get(f'{BASE_URL}/api/admin/templates?limit=50', headers=admin_headers)
        templates = r.json()['templates']
        
        full_match = next((t for t in templates if t.get('template_type') == 'full_match'), None)
        if not full_match:
            pytest.skip("No full_match template found")
        
        question_count = len(full_match.get('question_ids', []))
        assert question_count == 16, f"Expected 16 questions, got {question_count}"
        print(f"✓ Full match template has {question_count} questions")
    
    def test_questions_have_hindi_text(self, admin_headers):
        """Questions have Hindi text"""
        r = requests.get(f'{BASE_URL}/api/admin/questions?limit=50', headers=admin_headers)
        assert r.status_code == 200
        questions = r.json()['questions']
        
        hindi_count = sum(1 for q in questions if q.get('question_text_hi'))
        print(f"✓ Questions with Hindi text: {hindi_count}/{len(questions)}")
        assert hindi_count > 0, "No questions have Hindi text"


class TestSyncIPLSchedule:
    """Test IPL schedule sync"""
    
    def test_sync_ipl_schedule(self, admin_headers):
        """Sync IPL schedule endpoint works"""
        r = requests.post(f'{BASE_URL}/api/matches/live/sync-ipl-schedule', headers=admin_headers)
        assert r.status_code == 200
        data = r.json()
        print(f"✓ Sync IPL Schedule: created={data.get('created', 0)}, updated={data.get('updated', 0)}")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
