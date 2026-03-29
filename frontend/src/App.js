/**
 * CrickPredict - Main App Component
 * Fantasy Cricket Prediction PWA
 */
import { useEffect, useState } from "react";
import "@/App.css";
import { useAuthStore } from "@/stores/authStore";
import { useAppStore } from "@/stores/appStore";
import { AuthFlow } from "@/components/auth";
import BottomNav from "@/components/BottomNav";
import HomePage from "@/pages/HomePage";
import WalletPage from "@/pages/WalletPage";
import ProfilePage from "@/pages/ProfilePage";
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

// My Contests Placeholder (Stage 7)
const MyContestsPage = () => (
  <div data-testid="contests-page" className="flex flex-col items-center justify-center py-20">
    <div className="text-5xl mb-4">🏆</div>
    <h2 className="text-lg font-semibold text-white mb-2">My Contests</h2>
    <p className="text-sm text-center" style={{ color: COLORS.text.secondary }}>Join a contest to see your entries here.<br />Coming soon in Stage 7!</p>
  </div>
);

// Main App Shell (after login)
const AppShell = () => {
  const [activeTab, setActiveTab] = useState('home');

  const renderPage = () => {
    switch (activeTab) {
      case 'home': return <HomePage />;
      case 'contests': return <MyContestsPage />;
      case 'wallet': return <WalletPage />;
      case 'profile': return <ProfilePage />;
      default: return <HomePage />;
    }
  };

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
      <BottomNav active={activeTab} onChange={setActiveTab} />
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
