/**
 * CrickPredict - Main App Component
 * Fantasy Cricket Prediction PWA
 */
import { useEffect, useState } from "react";
import "@/App.css";
import { api } from "@/api/client";
import { useAuthStore } from "@/stores/authStore";
import { useAppStore } from "@/stores/appStore";
import { AuthFlow } from "@/components/auth";

// Splash Screen Component
const SplashScreen = () => (
  <div className="fixed inset-0 bg-bg-primary flex flex-col items-center justify-center z-50">
    <div className="font-display text-3xl font-bold text-primary tracking-wider mb-4">
      CRICKPREDICT
    </div>
    <div className="w-10 h-10 border-3 border-primary/30 border-t-primary rounded-full animate-spin" />
    <p className="mt-4 text-text-secondary text-sm">Loading...</p>
  </div>
);

// Home Screen Component (After Login)
const HomeScreen = () => {
  const { user, logout } = useAuthStore();
  const [healthStatus, setHealthStatus] = useState(null);
  const [matches, setMatches] = useState([]);
  const [contests, setContests] = useState([]);

  useEffect(() => {
    const loadData = async () => {
      try {
        const health = await api.health();
        setHealthStatus(health.data);
      } catch (error) {
        console.error('Health check failed:', error);
      }
    };
    loadData();
  }, []);

  return (
    <div className="min-h-screen bg-bg-primary pb-20" data-testid="home-screen">
      {/* Header */}
      <header className="sticky top-0 z-20 bg-bg-primary/95 backdrop-blur-md border-b border-bg-elevated px-4 py-3 safe-top">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-display text-xl font-bold text-primary tracking-wide">
              CRICKPREDICT
            </h1>
          </div>
          <button 
            onClick={() => logout()}
            className="w-9 h-9 rounded-full bg-bg-card border border-primary/30 flex items-center justify-center"
            data-testid="profile-btn"
          >
            <svg className="w-5 h-5 text-primary" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
      </header>

      {/* Banner */}
      <div className="px-4 py-3">
        <div className="bg-gradient-to-r from-primary/20 to-primary/5 border border-primary/30 rounded-xl p-4 text-center">
          <p className="text-primary font-medium font-hindi">
            🏏 Revolution in Fantasy Cricket is here
          </p>
        </div>
      </div>

      {/* Balance Card */}
      <div className="px-4 py-2">
        <div className="flex gap-3">
          <div className="flex-1 bg-bg-card border border-bg-elevated rounded-xl p-4">
            <p className="text-text-tertiary text-xs mb-1">My Balance</p>
            <p className="font-numbers text-2xl font-bold text-gold flex items-center gap-1">
              {user?.coins_balance?.toLocaleString() || 0}
              <span className="text-base">🪙</span>
            </p>
          </div>
          <button className="flex-1 bg-gradient-primary rounded-xl p-4 flex items-center justify-center gap-2 text-white font-semibold">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Deposit
          </button>
        </div>
      </div>

      {/* Live Matches Section */}
      <div className="px-4 py-4">
        <h2 className="text-lg font-semibold text-text-primary mb-3 flex items-center gap-2">
          <span className="text-primary">⚡</span>
          Live Matches
        </h2>
        <div className="flex gap-3 overflow-x-auto no-scrollbar pb-2">
          {/* Sample Match Cards */}
          {[
            { teamA: 'MI', teamB: 'CSK', colorA: 'blue', colorB: 'yellow' },
            { teamA: 'RCB', teamB: 'KKR', colorA: 'red', colorB: 'purple' },
            { teamA: 'DC', teamB: 'PBKS', colorA: 'blue', colorB: 'red' },
          ].map((match, idx) => (
            <div 
              key={idx}
              className={`flex-shrink-0 w-40 rounded-xl p-4 bg-team-${match.colorA} border-2 border-primary/50`}
              data-testid={`match-card-${idx}`}
            >
              <p className="text-white font-semibold text-center mb-2">
                {match.teamA} VS {match.teamB}
              </p>
              <div className="live-indicator mx-auto w-fit">
                LIVE
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Hot Contests Section */}
      <div className="px-4 py-4">
        <h2 className="text-lg font-semibold text-text-primary mb-3 flex items-center gap-2">
          <span className="text-gold">🏆</span>
          Hot Contests
        </h2>
        
        {/* Contest Card */}
        <div className="card p-4 flex items-center justify-between">
          <div>
            <p className="text-text-primary font-semibold">MI VS CSK</p>
            <p className="text-primary text-sm font-numbers">
              1000 real cash
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-text-tertiary">🔥</span>
            <button className="btn btn-primary py-2 px-4 text-sm">
              JOIN <span className="font-numbers">🪙 100</span>
            </button>
          </div>
        </div>
      </div>

      {/* User Info Card */}
      <div className="px-4 py-4">
        <div className="card p-4">
          <h3 className="text-md font-semibold text-text-primary mb-3">Your Profile</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-text-tertiary">Username</span>
              <span className="text-text-primary">{user?.username}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-tertiary">Rank</span>
              <span className="text-primary font-medium">{user?.rank_title}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-tertiary">Total Points</span>
              <span className="text-gold font-numbers">{user?.total_points}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-tertiary">Referral Code</span>
              <span className="text-info font-mono">{user?.referral_code}</span>
            </div>
          </div>
        </div>
      </div>

      {/* System Status (Dev Mode) */}
      <div className="px-4 py-4">
        <div className="card p-4 opacity-75">
          <h3 className="text-xs font-semibold text-text-tertiary mb-2">System Status</h3>
          <div className="flex gap-4 text-xs">
            <span className={`flex items-center gap-1 ${healthStatus?.services?.mongodb?.status === 'healthy' ? 'text-success' : 'text-warning'}`}>
              <span className="w-2 h-2 rounded-full bg-current" />
              MongoDB
            </span>
            <span className={`flex items-center gap-1 ${healthStatus?.services?.redis?.status === 'healthy' ? 'text-success' : 'text-text-tertiary'}`}>
              <span className="w-2 h-2 rounded-full bg-current" />
              Redis
            </span>
          </div>
        </div>
      </div>

      {/* Bottom Navigation */}
      <nav className="bottom-nav" data-testid="bottom-nav">
        <a href="#" className="bottom-nav-item active">
          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
          </svg>
          <span>Home</span>
        </a>
        <a href="#" className="bottom-nav-item">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
          </svg>
          <span>My Contest</span>
        </a>
        <div className="bottom-nav-center">
          <svg className="w-7 h-7" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z" clipRule="evenodd" />
          </svg>
        </div>
        <a href="#" className="bottom-nav-item">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
          </svg>
          <span>Wallet</span>
        </a>
        <a href="#" className="bottom-nav-item">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
          </svg>
          <span>Legal</span>
        </a>
      </nav>
    </div>
  );
};

// Main App Component
function App() {
  const [isLoading, setIsLoading] = useState(true);
  const { fetchUser, isAuthenticated } = useAuthStore();
  const { showToast } = useAppStore();

  useEffect(() => {
    const initApp = async () => {
      try {
        // Check for existing auth
        await fetchUser();
      } catch (error) {
        console.error('Init error:', error);
      } finally {
        // Minimum splash time for UX
        setTimeout(() => setIsLoading(false), 1000);
      }
    };

    initApp();
  }, [fetchUser]);

  if (isLoading) {
    return <SplashScreen />;
  }

  return (
    <div className="App min-h-screen bg-bg-primary">
      {isAuthenticated ? <HomeScreen /> : <AuthFlow />}
    </div>
  );
}

export default App;
