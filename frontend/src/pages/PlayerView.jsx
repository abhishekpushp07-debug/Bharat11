/**
 * PlayerView - Admin can "View as Player" to test player experience
 * Shows the full player app with a floating "Back to Admin" button
 * Includes global celebration overlay for live match events
 */
import { useState, useCallback, useRef, useEffect } from 'react';
import { useAuthStore } from '@/stores/authStore';
import { COLORS } from '@/constants/design';
import BottomNav from '@/components/BottomNav';
import HomePage from '@/pages/HomePage';
import WalletPage from '@/pages/WalletPage';
import ProfilePage from '@/pages/ProfilePage';
import MatchDetailPage from '@/pages/MatchDetailPage';
import MyContestsPage from '@/pages/MyContestsPage';
import PredictionPage from '@/pages/PredictionPage';
import LeaderboardPage from '@/pages/LeaderboardPage';
import SearchPage from '@/pages/SearchPage';
import CelebrationOverlay from '@/components/CelebrationOverlay';
import apiClient from '@/api/client';
import { Shield } from 'lucide-react';

export default function PlayerView({ onBackToAdmin }) {
  const [activeTab, setActiveTab] = useState('home');
  const [selectedMatch, setSelectedMatch] = useState(null);
  const [selectedContestId, setSelectedContestId] = useState(null);
  const [globalCelebration, setGlobalCelebration] = useState(null);
  const lastScoreRef = useRef(null);
  const liveMatchIdRef = useRef(null);
  const { fetchUser } = useAuthStore();

  const triggerCelebration = useCallback((type) => {
    setGlobalCelebration(type);
  }, []);

  // ===== GLOBAL LIVE MATCH POLLING — celebrations on ANY screen =====
  useEffect(() => {
    let pollInterval = null;
    let cancelled = false;

    const findAndPoll = async () => {
      try {
        const res = await apiClient.get('/matches?status=live&limit=1');
        const matches = res.data?.matches || [];
        if (!matches.length) { liveMatchIdRef.current = null; return; }
        liveMatchIdRef.current = matches[0]?.id;

        const poll = async () => {
          if (cancelled || !liveMatchIdRef.current) return;
          try {
            const scRes = await apiClient.get(`/matches/${liveMatchIdRef.current}/scorecard`);
            const sc = scRes.data;
            if (!sc || sc.error) return;
            let f = 0, s = 0, w = 0;
            for (const inn of (sc?.scorecard || [])) {
              for (const b of (inn?.batting || [])) {
                s += parseInt(b['6s']) || 0;
                f += parseInt(b['4s']) || 0;
                if (b.dismissal && b.dismissal !== 'not out' && b.dismissal !== '') w++;
              }
            }
            const prev = lastScoreRef.current;
            if (prev && prev.mid === liveMatchIdRef.current) {
              if (w > prev.w) triggerCelebration('wicket');
              else if (s > prev.s) triggerCelebration('six');
              else if (f > prev.f) triggerCelebration('four');
            }
            lastScoreRef.current = { mid: liveMatchIdRef.current, w, s, f };
          } catch (e) { /* silent */ }
        };

        await poll();
        if (pollInterval) clearInterval(pollInterval);
        pollInterval = setInterval(poll, 30000);
      } catch (e) { /* silent */ }
    };

    findAndPoll();
    const mc = setInterval(findAndPoll, 120000);
    return () => { cancelled = true; if (pollInterval) clearInterval(pollInterval); clearInterval(mc); };
  }, [triggerCelebration]);

  const handleMatchClick = useCallback((match) => { setSelectedMatch(match); setActiveTab('matchDetail'); }, []);
  const handleBackFromMatch = useCallback(() => { setSelectedMatch(null); setActiveTab('home'); }, []);
  const handleOpenPrediction = useCallback((cid) => { setSelectedContestId(cid); setActiveTab('prediction'); }, []);
  const handleOpenLeaderboard = useCallback((cid) => { setSelectedContestId(cid); setActiveTab('leaderboard'); }, []);
  const handleBackFromPrediction = useCallback(() => { setSelectedContestId(null); setActiveTab(selectedMatch ? 'matchDetail' : 'contests'); }, [selectedMatch]);
  const handleBackFromLeaderboard = useCallback(() => { setSelectedContestId(null); setActiveTab('contests'); }, []);

  const handleContestClick = useCallback(({ entry, contest, match: contestMatch }) => {
    const cid = contest?.id || entry?.contest_id;
    if (!cid) return;
    if (contestMatch) setSelectedMatch(contestMatch);
    contest?.status === 'live' ? handleOpenPrediction(cid) : handleOpenLeaderboard(cid);
  }, [handleOpenLeaderboard, handleOpenPrediction]);

  const handleAfterJoin = useCallback((cid) => { fetchUser(); handleOpenPrediction(cid); }, [fetchUser, handleOpenPrediction]);

  const renderPage = () => {
    switch (activeTab) {
      case 'home': return <HomePage onMatchClick={handleMatchClick} />;
      case 'matchDetail': return <MatchDetailPage match={selectedMatch} onBack={handleBackFromMatch} onJoinContest={handleAfterJoin} onOpenPrediction={handleOpenPrediction} onOpenLeaderboard={handleOpenLeaderboard} onCelebrate={triggerCelebration} />;
      case 'contests': return <MyContestsPage onContestClick={handleContestClick} onViewLeaderboard={handleOpenLeaderboard} />;
      case 'prediction': return <PredictionPage contestId={selectedContestId} onBack={handleBackFromPrediction} onViewLeaderboard={handleOpenLeaderboard} />;
      case 'leaderboard': return <LeaderboardPage contestId={selectedContestId} match={selectedMatch} onBack={handleBackFromLeaderboard} />;
      case 'wallet': return <WalletPage />;
      case 'profile': return <ProfilePage />;
      case 'search': return <SearchPage onMatchClick={handleMatchClick} onBack={() => setActiveTab('home')} />;
      default: return <HomePage onMatchClick={handleMatchClick} />;
    }
  };

  const handleTabChange = (tab) => { setSelectedMatch(null); setSelectedContestId(null); setActiveTab(tab); };
  const hiddenNavTabs = ['matchDetail', 'prediction', 'leaderboard'];

  return (
    <div className="min-h-screen" style={{ background: COLORS.background.primary }}>
      {/* GLOBAL CELEBRATION — fires on ANY screen */}
      {globalCelebration && (
        <CelebrationOverlay type={globalCelebration} onComplete={() => setGlobalCelebration(null)} />
      )}

      <header className="sticky top-0 z-40 px-4 py-3 safe-top" style={{ background: `${COLORS.background.primary}F0`, backdropFilter: 'blur(12px)', borderBottom: `1px solid ${COLORS.border.light}` }}>
        <div className="flex items-center justify-between max-w-lg mx-auto">
          <h1 className="text-lg font-bold tracking-wider" style={{ color: COLORS.primary.main, fontFamily: "'Orbitron', sans-serif" }}>
            BHARAT 11
          </h1>
        </div>
      </header>
      <main className="px-4 pt-3 pb-20 max-w-lg mx-auto">{renderPage()}</main>
      <BottomNav active={hiddenNavTabs.includes(activeTab) ? 'home' : activeTab} onChange={handleTabChange} />

      {/* Floating "Back to Admin" */}
      <button data-testid="back-to-admin-btn" onClick={onBackToAdmin}
        className="fixed top-20 right-3 z-50 flex items-center gap-1.5 px-3 py-2 rounded-full shadow-lg animate-pulse"
        style={{ background: COLORS.accent.gold, color: '#000' }}>
        <Shield size={14} />
        <span className="text-xs font-bold">Admin</span>
      </button>
    </div>
  );
}
