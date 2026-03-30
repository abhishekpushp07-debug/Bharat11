/**
 * CrickPredict - Main App Component
 * Fantasy Cricket Prediction PWA
 */
import { useEffect, useState, useCallback } from "react";
import "@/App.css";
import { useAuthStore } from "@/stores/authStore";
import { AuthFlow } from "@/components/auth";
import BottomNav from "@/components/BottomNav";
import HomePage from "@/pages/HomePage";
import WalletPage from "@/pages/WalletPage";
import ProfilePage from "@/pages/ProfilePage";
import MatchDetailPage from "@/pages/MatchDetailPage";
import MyContestsPage from "@/pages/MyContestsPage";
import PredictionPage from "@/pages/PredictionPage";
import LeaderboardPage from "@/pages/LeaderboardPage";
import AdminPage from "@/pages/AdminPage";
import { COLORS } from "@/constants/design";

// Splash Screen
const SplashScreen = () => (
  <div className="fixed inset-0 flex flex-col items-center justify-center z-50" style={{ background: COLORS.background.primary }}>
    <div className="text-3xl font-bold tracking-wider mb-4" style={{ color: COLORS.primary.main, fontFamily: "'Orbitron', sans-serif" }}>
      CRICKPREDICT
    </div>
    <div className="w-10 h-10 border-3 rounded-full animate-spin" style={{ borderColor: `${COLORS.primary.main}30`, borderTopColor: COLORS.primary.main }} />
    <p className="mt-4 text-sm" style={{ color: COLORS.text.secondary }}>Loading...</p>
  </div>
);

// Main App Shell (after login)
const AppShell = () => {
  const [activeTab, setActiveTab] = useState('home');
  const [selectedMatch, setSelectedMatch] = useState(null);
  const [selectedContestId, setSelectedContestId] = useState(null);
  const { fetchUser } = useAuthStore();

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
    switch (activeTab) {
      case 'home': return <HomePage onMatchClick={handleMatchClick} />;
      case 'matchDetail': return <MatchDetailPage match={selectedMatch} onBack={handleBackFromMatch} onJoinContest={handleAfterJoin} onOpenPrediction={handleOpenPrediction} onOpenLeaderboard={handleOpenLeaderboard} />;
      case 'contests': return <MyContestsPage onContestClick={handleContestClick} />;
      case 'prediction': return <PredictionPage contestId={selectedContestId} onBack={handleBackFromPrediction} onViewLeaderboard={handleOpenLeaderboard} />;
      case 'leaderboard': return <LeaderboardPage contestId={selectedContestId} onBack={handleBackFromLeaderboard} />;
      case 'admin': return <AdminPage onBack={() => setActiveTab('profile')} />;
      case 'wallet': return <WalletPage />;
      case 'profile': return <ProfilePage onAdminClick={() => setActiveTab('admin')} />;
      default: return <HomePage onMatchClick={handleMatchClick} />;
    }
  };

  const handleTabChange = (tab) => {
    setSelectedMatch(null);
    setSelectedContestId(null);
    setActiveTab(tab);
  };

  const hiddenNavTabs = ['matchDetail', 'prediction', 'leaderboard', 'admin'];

  return (
    <div className="min-h-screen" style={{ background: COLORS.background.primary }}>
      {/* Header */}
      <header className="sticky top-0 z-40 px-4 py-3 safe-top" style={{ background: `${COLORS.background.primary}F0`, backdropFilter: 'blur(12px)', borderBottom: `1px solid ${COLORS.border.light}` }}>
        <div className="flex items-center justify-between max-w-lg mx-auto">
          <h1 data-testid="app-title" className="text-lg font-bold tracking-wider" style={{ color: COLORS.primary.main, fontFamily: "'Orbitron', sans-serif" }}>
            CRICKPREDICT
          </h1>
        </div>
      </header>

      {/* Page Content */}
      <main className="px-4 pt-3 pb-20 max-w-lg mx-auto">
        {renderPage()}
      </main>

      {/* Bottom Navigation */}
      <BottomNav active={hiddenNavTabs.includes(activeTab) ? 'home' : activeTab} onChange={handleTabChange} />
    </div>
  );
};

// Main App
function App() {
  const [isLoading, setIsLoading] = useState(true);
  const { fetchUser, isAuthenticated } = useAuthStore();

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

  return (
    <div className="App min-h-screen" style={{ background: COLORS.background.primary }}>
      {isAuthenticated ? <AppShell /> : <AuthFlow />}
    </div>
  );
}

export default App;
