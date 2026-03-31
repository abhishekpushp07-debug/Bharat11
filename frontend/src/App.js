/**
 * Bharat 11 - Main App Component
 * Complete separation: Admin sees AdminApp, Player sees PlayerApp
 */
import { useEffect, useState, useCallback, useRef, lazy, Suspense } from "react";
import "@/App.css";
import { useAuthStore } from "@/stores/authStore";
import { useSocketStore } from "@/stores/socketStore";
import { AuthFlow } from "@/components/auth";
import BottomNav from "@/components/BottomNav";
import HomePage from "@/pages/HomePage";
import { COLORS } from "@/constants/design";
import CelebrationOverlay from "@/components/CelebrationOverlay";
import apiClient from "@/api/client";

// Lazy load heavy pages for performance
const WalletPage = lazy(() => import("@/pages/WalletPage"));
const ProfilePage = lazy(() => import("@/pages/ProfilePage"));
const MatchDetailPage = lazy(() => import("@/pages/MatchDetailPage"));
const MyContestsPage = lazy(() => import("@/pages/MyContestsPage"));
const PredictionPage = lazy(() => import("@/pages/PredictionPage"));
const LeaderboardPage = lazy(() => import("@/pages/LeaderboardPage"));
const AdminApp = lazy(() => import("@/pages/AdminApp"));
const SearchPage = lazy(() => import("@/pages/SearchPage"));

const PageLoader = () => (
  <div className="flex items-center justify-center h-40">
    <div className="w-6 h-6 border-2 rounded-full animate-spin" style={{ borderColor: `${COLORS.primary.main}30`, borderTopColor: COLORS.primary.main }} />
  </div>
);

// Splash Screen
const SplashScreen = () => (
  <div className="fixed inset-0 flex flex-col items-center justify-center z-50" style={{ background: COLORS.background.primary }}>
    <div className="text-3xl font-bold tracking-wider mb-4" style={{ color: COLORS.primary.main, fontFamily: "'Orbitron', sans-serif" }}>
      BHARAT 11
    </div>
    <div className="w-10 h-10 border-3 rounded-full animate-spin" style={{ borderColor: `${COLORS.primary.main}30`, borderTopColor: COLORS.primary.main }} />
    <p className="mt-4 text-sm" style={{ color: COLORS.text.secondary }}>Loading...</p>
  </div>
);

// ====== PLAYER APP - Zero admin traces ======
const PlayerApp = () => {
  const [activeTab, setActiveTab] = useState('home');
  const [selectedMatch, setSelectedMatch] = useState(null);
  const [selectedContestId, setSelectedContestId] = useState(null);
  const [globalCelebration, setGlobalCelebration] = useState(null);
  const triggerCelebration = useCallback((type) => {
    console.log('GLOBAL CELEBRATION TRIGGERED:', type);
    setGlobalCelebration(type);
  }, []);
  const lastScoreRef = useRef(null);
  const liveMatchIdRef = useRef(null);
  const { fetchUser } = useAuthStore();
  const { connect, disconnect } = useSocketStore();

  // Connect to Socket.IO on mount
  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  // ===== GLOBAL LIVE MATCH POLLING — celebrations on ANY screen =====
  useEffect(() => {
    let pollInterval = null;
    let cancelled = false;

    const findLiveMatchAndPoll = async () => {
      try {
        // Find any live match
        const res = await apiClient.get('/matches?status=live&limit=1');
        const matches = res.data?.matches || [];
        if (matches.length === 0) {
          liveMatchIdRef.current = null;
          return;
        }
        const liveMatchId = matches[0]?.id;
        liveMatchIdRef.current = liveMatchId;

        // Now start polling scorecard for this match
        const pollScorecard = async () => {
          if (cancelled || !liveMatchIdRef.current) return;
          try {
            const scRes = await apiClient.get(`/matches/${liveMatchIdRef.current}/scorecard`);
            const sc = scRes.data;
            if (!sc || sc.error) return;

            const allInnings = sc?.scorecard || [];
            let totalFours = 0, totalSixes = 0, totalWickets = 0;
            for (const inn of allInnings) {
              for (const b of (inn?.batting || [])) {
                totalSixes += parseInt(b['6s']) || 0;
                totalFours += parseInt(b['4s']) || 0;
                if (b.dismissal && b.dismissal !== 'not out' && b.dismissal !== '') totalWickets++;
              }
            }

            const prev = lastScoreRef.current;
            if (prev && prev.matchId === liveMatchIdRef.current) {
              if (totalWickets > prev.wickets) {
                triggerCelebration('wicket');
              } else if (totalSixes > prev.sixes) {
                triggerCelebration('six');
              } else if (totalFours > prev.fours) {
                triggerCelebration('four');
              }
            }
            lastScoreRef.current = { matchId: liveMatchIdRef.current, wickets: totalWickets, sixes: totalSixes, fours: totalFours };
          } catch (e) { /* silent */ }
        };

        // Initial poll
        await pollScorecard();

        // Clear old interval if any
        if (pollInterval) clearInterval(pollInterval);
        pollInterval = setInterval(pollScorecard, 30000);
      } catch (e) { /* silent */ }
    };

    findLiveMatchAndPoll();

    // Re-check for live matches every 2 minutes
    const matchCheck = setInterval(findLiveMatchAndPoll, 120000);

    return () => {
      cancelled = true;
      if (pollInterval) clearInterval(pollInterval);
      clearInterval(matchCheck);
    };
  }, []);

  const handleMatchClick = useCallback((match) => {
    setSelectedMatch(match);
    setActiveTab('matchDetail');
  }, []);

  const handleBackFromMatch = useCallback(() => {
    setSelectedMatch(null);
    setActiveTab('home');
  }, []);

  const handleOpenPrediction = useCallback((contestId) => {
    setSelectedContestId(contestId);
    setActiveTab('prediction');
  }, []);

  const handleOpenLeaderboard = useCallback((contestId) => {
    setSelectedContestId(contestId);
    setActiveTab('leaderboard');
  }, []);

  const handleBackFromPrediction = useCallback(() => {
    setSelectedContestId(null);
    if (selectedMatch) {
      setActiveTab('matchDetail');
    } else {
      setActiveTab('contests');
    }
  }, [selectedMatch]);

  const handleBackFromLeaderboard = useCallback(() => {
    setSelectedContestId(null);
    setActiveTab('contests');
  }, []);

  const handleContestClick = useCallback(({ entry, contest }) => {
    const cid = contest?.id || entry?.contest_id;
    if (!cid) return;
    if (contest?.status === 'completed') {
      handleOpenLeaderboard(cid);
    } else {
      handleOpenPrediction(cid);
    }
  }, [handleOpenLeaderboard, handleOpenPrediction]);

  const handleAfterJoin = useCallback((contestId) => {
    fetchUser();
    handleOpenPrediction(contestId);
  }, [fetchUser, handleOpenPrediction]);

  const renderPage = () => {
    const content = (() => {
      switch (activeTab) {
        case 'home': return <HomePage onMatchClick={handleMatchClick} />;
        case 'matchDetail': return <MatchDetailPage match={selectedMatch} onBack={handleBackFromMatch} onJoinContest={handleAfterJoin} onOpenPrediction={handleOpenPrediction} onOpenLeaderboard={handleOpenLeaderboard} onCelebrate={triggerCelebration} />;
        case 'contests': return <MyContestsPage onContestClick={handleContestClick} />;
        case 'prediction': return <PredictionPage contestId={selectedContestId} onBack={handleBackFromPrediction} onViewLeaderboard={handleOpenLeaderboard} />;
        case 'leaderboard': return <LeaderboardPage contestId={selectedContestId} match={selectedMatch} onBack={handleBackFromLeaderboard} />;
        case 'wallet': return <WalletPage />;
        case 'profile': return <ProfilePage />;
        case 'search': return <SearchPage onMatchClick={handleMatchClick} onBack={() => setActiveTab('home')} />;
        default: return <HomePage onMatchClick={handleMatchClick} />;
      }
    })();
    return <Suspense fallback={<PageLoader />}>{content}</Suspense>;
  };

  const handleTabChange = (tab) => {
    setSelectedMatch(null);
    setSelectedContestId(null);
    setActiveTab(tab);
  };

  const hiddenNavTabs = ['matchDetail', 'prediction', 'leaderboard'];

  return (
    <div className="min-h-screen" style={{ background: COLORS.background.primary }}>
      {/* GLOBAL CELEBRATION OVERLAY — fires on ANY screen */}
      {globalCelebration && (
        <CelebrationOverlay type={globalCelebration} onComplete={() => setGlobalCelebration(null)} />
      )}

      <header className="sticky top-0 z-40 px-4 py-3 safe-top" style={{ background: `${COLORS.background.primary}F0`, backdropFilter: 'blur(12px)', borderBottom: `1px solid ${COLORS.border.light}` }}>
        <div className="flex items-center justify-between max-w-lg mx-auto">
          <h1 data-testid="app-title" className="text-lg font-bold tracking-wider" style={{ color: COLORS.primary.main, fontFamily: "'Orbitron', sans-serif" }}>
            BHARAT 11
          </h1>
        </div>
      </header>

      <main className="px-4 pt-3 max-w-lg mx-auto" style={{ paddingBottom: 'calc(70px + env(safe-area-inset-bottom, 0px))' }}>
        {renderPage()}
      </main>

      <BottomNav active={hiddenNavTabs.includes(activeTab) ? 'home' : activeTab} onChange={handleTabChange} />
    </div>
  );
};

// ====== MAIN APP - Routes Admin vs Player ======
function App() {
  const [isLoading, setIsLoading] = useState(true);
  const { fetchUser, isAuthenticated, user } = useAuthStore();

  useEffect(() => {
    const initApp = async () => {
      try {
        await fetchUser();
      } catch (error) {
        console.error('Init error:', error);
      } finally {
        setTimeout(() => setIsLoading(false), 800);
      }
    };
    initApp();
  }, [fetchUser]);

  if (isLoading) return <SplashScreen />;

  if (!isAuthenticated) {
    return (
      <div className="App min-h-screen" style={{ background: COLORS.background.primary }}>
        <AuthFlow />
      </div>
    );
  }

  // COMPLETE SEPARATION: Admin gets AdminApp, Player gets PlayerApp
  if (user?.is_admin) {
    return <Suspense fallback={<SplashScreen />}><AdminApp /></Suspense>;
  }

  return <PlayerApp />;
}

export default App;
