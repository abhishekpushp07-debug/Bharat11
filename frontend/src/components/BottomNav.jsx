import { COLORS } from '../constants/design';
import { Home, Trophy, Wallet, User, Scale } from 'lucide-react';

const tabs = [
  { id: 'home', label: 'Home', Icon: Home },
  { id: 'contests', label: 'My Contest', Icon: Trophy },
  { id: 'wallet', label: 'Wallet', Icon: Wallet },
  { id: 'profile', label: 'Profile', Icon: User },
];

export default function BottomNav({ active, onChange }) {
  return (
    <nav data-testid="bottom-nav" className="fixed bottom-0 left-0 right-0 z-50" style={{ background: COLORS.background.primary, borderTop: `1px solid ${COLORS.border.light}`, paddingBottom: 'env(safe-area-inset-bottom)' }}>
      <div className="flex items-center justify-around max-w-lg mx-auto">
        {tabs.map(({ id, label, Icon }) => {
          const isActive = active === id;
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
