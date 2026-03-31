/**
 * PlayerView - Admin can "View as Player" to test player experience
 * Shows the full player app with a floating "Back to Admin" button
 */
import { useState, useCallback } from 'react';
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
import { Shield } from 'lucide-react';

export default function PlayerView({ onBackToAdmin }) {
  const [activeTab, setActiveTab] = useState('home');
  const [selectedMatch, setSelectedMatch] = useState(null);
  const [selectedContestId, setSelectedContestId] = useState(null);
  const { fetchUser } = useAuthStore();

  const handleMatchClick = useCallback((match) => { setSelectedMatch(match); setActiveTab('matchDetail'); }, []);
  const handleBackFromMatch = useCallback(() => { setSelectedMatch(null); setActiveTab('home'); }, []);
  const handleOpenPrediction = useCallback((cid) => { setSelectedContestId(cid); setActiveTab('prediction'); }, []);
  const handleOpenLeaderboard = useCallback((cid) => { setSelectedContestId(cid); setActiveTab('leaderboard'); }, []);
  const handleBackFromPrediction = useCallback(() => { setSelectedContestId(null); setActiveTab(selectedMatch ? 'matchDetail' : 'contests'); }, [selectedMatch]);
  const handleBackFromLeaderboard = useCallback(() => { setSelectedContestId(null); setActiveTab('contests'); }, []);

  const handleContestClick = useCallback(({ entry, contest, match: contestMatch }) => {
    const cid = contest?.id || entry?.contest_id;
    if (!cid) return;
    // Store match data from contest entry for leaderboard usage
    if (contestMatch) setSelectedMatch(contestMatch);
    // Only live contests go to prediction page, everything else goes to leaderboard
    contest?.status === 'live' ? handleOpenPrediction(cid) : handleOpenLeaderboard(cid);
  }, [handleOpenLeaderboard, handleOpenPrediction]);

  const handleAfterJoin = useCallback((cid) => { fetchUser(); handleOpenPrediction(cid); }, [fetchUser, handleOpenPrediction]);

  const renderPage = () => {
    switch (activeTab) {
      case 'home': return <HomePage onMatchClick={handleMatchClick} />;
      case 'matchDetail': return <MatchDetailPage match={selectedMatch} onBack={handleBackFromMatch} onJoinContest={handleAfterJoin} onOpenPrediction={handleOpenPrediction} onOpenLeaderboard={handleOpenLeaderboard} />;
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
