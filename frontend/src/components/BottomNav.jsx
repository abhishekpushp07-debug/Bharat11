import { COLORS } from '../constants/design';
import { Home, Trophy, Scale, User, Search } from 'lucide-react';

const tabs = [
  { id: 'home', label: 'Home', Icon: Home },
  { id: 'contests', label: 'Contest', Icon: Trophy },
  { id: 'search', label: '', Icon: Search, isCenter: true },
  { id: 'wallet', label: 'Legal', Icon: Scale },
  { id: 'profile', label: 'Profile', Icon: User },
];

export default function BottomNav({ active, onChange }) {
  return (
    <nav data-testid="bottom-nav" className="fixed bottom-0 left-0 right-0 z-50" style={{ background: COLORS.background.primary, borderTop: `1px solid ${COLORS.border.light}`, paddingBottom: 'env(safe-area-inset-bottom)' }}>
      <div className="flex items-center justify-around max-w-lg mx-auto relative">
        {tabs.map(({ id, label, Icon, isCenter }) => {
          const isActive = active === id;

          if (isCenter) {
            // Protruding center search button
            return (
              <button
                data-testid="nav-search"
                key={id}
                onClick={() => onChange(id)}
                className="relative -mt-7 flex items-center justify-center transition-all active:scale-90"
                style={{ width: '52px', height: '52px' }}
              >
                {/* Glow effect */}
                <div className="absolute inset-0 rounded-full opacity-60" style={{
                  background: COLORS.primary.main,
                  filter: 'blur(10px)',
                  transform: 'scale(0.8)'
                }} />
                {/* Button */}
                <div className="relative w-12 h-12 rounded-full flex items-center justify-center shadow-lg"
                  style={{
                    background: `linear-gradient(135deg, ${COLORS.primary.main}, #ff2020)`,
                    boxShadow: `0 4px 20px ${COLORS.primary.main}55`,
                    border: `3px solid ${COLORS.background.primary}`
                  }}>
                  <Search size={20} color="#fff" strokeWidth={2.5} />
                </div>
              </button>
            );
          }

          return (
            <button
              data-testid={`nav-${id}`}
              key={id}
              onClick={() => onChange(id)}
              className="flex flex-col items-center py-2 px-4 transition-all relative"
              style={{ opacity: isActive ? 1 : 0.5 }}
            >
              {isActive && <div className="absolute top-0 left-1/2 -translate-x-1/2 w-6 h-0.5 rounded-full" style={{ background: COLORS.primary.main }} />}
              <Icon size={20} color={isActive ? COLORS.primary.main : COLORS.text.secondary} strokeWidth={isActive ? 2.5 : 1.5} />
              <span className="text-[10px] mt-0.5 font-medium" style={{ color: isActive ? COLORS.primary.main : COLORS.text.secondary }}>{label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
