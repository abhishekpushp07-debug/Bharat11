/**
 * AdminApp - Complete Admin Shell
 * Separate app experience for Super Admin
 * Gold-accented header, dedicated nav, power dashboard
 */
import { useState, useCallback } from 'react';
import { useAuthStore } from '@/stores/authStore';
import { COLORS } from '@/constants/design';
import { LayoutDashboard, FileText, Calendar, CheckCircle, Eye, LogOut, Shield } from 'lucide-react';
import AdminDashboard from './admin/AdminDashboard';
import AdminContentPage from './admin/AdminContentPage';
import AdminMatchPage from './admin/AdminMatchPage';
import AdminResolvePage from './admin/AdminResolvePage';
import PlayerView from './PlayerView';

const ADMIN_TABS = [
  { id: 'dashboard', label: 'Dashboard', Icon: LayoutDashboard },
  { id: 'content', label: 'Content', Icon: FileText },
  { id: 'matches', label: 'Matches', Icon: Calendar },
  { id: 'resolve', label: 'Resolve', Icon: CheckCircle },
];

export default function AdminApp() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [viewAsPlayer, setViewAsPlayer] = useState(false);
  const { user, logout } = useAuthStore();

  const handleLogout = useCallback(() => { logout(); }, [logout]);

  // "View as Player" mode
  if (viewAsPlayer) {
    return <PlayerView onBackToAdmin={() => setViewAsPlayer(false)} />;
  }

  const renderPage = () => {
    switch (activeTab) {
      case 'dashboard': return <AdminDashboard onNavigate={setActiveTab} />;
      case 'content': return <AdminContentPage />;
      case 'matches': return <AdminMatchPage />;
      case 'resolve': return <AdminResolvePage />;
      default: return <AdminDashboard onNavigate={setActiveTab} />;
    }
  };

  return (
    <div data-testid="admin-app" className="min-h-screen" style={{ background: COLORS.background.primary }}>
      {/* Admin Header - Gold accent */}
      <header className="sticky top-0 z-40 px-4 py-3 safe-top" style={{
        background: `${COLORS.background.primary}F0`,
        backdropFilter: 'blur(12px)',
        borderBottom: `1px solid ${COLORS.accent.gold}33`
      }}>
        <div className="flex items-center justify-between max-w-lg mx-auto">
          <div className="flex items-center gap-2">
            <Shield size={20} color={COLORS.accent.gold} />
            <div>
              <h1 data-testid="admin-title" className="text-base font-bold tracking-wider" style={{ color: COLORS.accent.gold, fontFamily: "'Orbitron', sans-serif" }}>
                BHARAT 11
              </h1>
              <span className="text-[9px] font-semibold tracking-widest uppercase" style={{ color: COLORS.accent.gold + '99' }}>
                Super Admin
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button data-testid="view-as-player-btn" onClick={() => setViewAsPlayer(true)}
              className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-[10px] font-semibold transition-all"
              style={{ background: COLORS.background.card, color: COLORS.text.secondary, border: `1px solid ${COLORS.border.light}` }}>
              <Eye size={12} /> Player View
            </button>
            <button data-testid="admin-logout-btn" onClick={handleLogout}
              className="p-2 rounded-lg" style={{ background: COLORS.background.card }}>
              <LogOut size={16} color={COLORS.error.main} />
            </button>
          </div>
        </div>
      </header>

      {/* Page Content */}
      <main className="px-4 pt-3 pb-24 max-w-lg mx-auto">
        {renderPage()}
      </main>

      {/* Admin Bottom Nav - Gold themed */}
      <nav className="fixed bottom-0 left-0 right-0 z-40 safe-bottom" style={{
        background: `${COLORS.background.primary}F8`,
        backdropFilter: 'blur(16px)',
        borderTop: `1px solid ${COLORS.accent.gold}22`
      }}>
        <div className="flex items-center justify-around max-w-lg mx-auto py-2 px-2">
          {ADMIN_TABS.map(({ id, label, Icon }) => {
            const isActive = activeTab === id;
            return (
              <button key={id} data-testid={`admin-nav-${id}`}
                onClick={() => setActiveTab(id)}
                className="flex flex-col items-center gap-0.5 py-1.5 px-3 rounded-xl transition-all"
                style={{
                  background: isActive ? `${COLORS.accent.gold}15` : 'transparent',
                  minWidth: '64px'
                }}>
                <Icon size={20} color={isActive ? COLORS.accent.gold : COLORS.text.tertiary} strokeWidth={isActive ? 2.5 : 1.5} />
                <span className="text-[10px] font-semibold" style={{ color: isActive ? COLORS.accent.gold : COLORS.text.tertiary }}>
                  {label}
                </span>
                {isActive && <div className="w-4 h-0.5 rounded-full mt-0.5" style={{ background: COLORS.accent.gold }} />}
              </button>
            );
          })}
        </div>
      </nav>
    </div>
  );
}
