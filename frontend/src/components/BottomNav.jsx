import { COLORS } from '../constants/design';
import { Home, Trophy, Scale, User } from 'lucide-react';

const tabs = [
  { id: 'home', label: 'Home', Icon: Home },
  { id: 'contests', label: 'Contest', Icon: Trophy },
  { id: 'search', label: 'IPL', isCenter: true },
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
            return (
              <button
                data-testid="nav-ipl"
                key={id}
                onClick={() => onChange(id)}
                className="relative -mt-8 flex items-center justify-center transition-all active:scale-90"
                style={{ width: '56px', height: '56px' }}
              >
                {/* Outer glow */}
                <div className="absolute inset-0" style={{
                  transform: 'rotate(45deg)',
                  borderRadius: '12px',
                  background: '#1e3a8a',
                  filter: 'blur(12px)',
                  opacity: 0.5,
                }} />
                {/* Shadow ring */}
                <div className="absolute" style={{
                  width: '50px', height: '50px',
                  transform: 'rotate(45deg)',
                  borderRadius: '13px',
                  background: 'transparent',
                  boxShadow: `0 0 20px #3b82f644, 0 0 40px #1e3a8a33`,
                }} />
                {/* Rhombus shape */}
                <div className="relative flex items-center justify-center shadow-xl"
                  style={{
                    width: '46px', height: '46px',
                    transform: 'rotate(45deg)',
                    borderRadius: '12px',
                    background: 'linear-gradient(135deg, #1e3a8a, #1e40af, #2563eb)',
                    border: `2.5px solid ${COLORS.background.primary}`,
                    boxShadow: '0 4px 16px rgba(30,58,138,0.6), inset 0 1px 0 rgba(255,255,255,0.15)',
                  }}>
                  {/* Inner highlight */}
                  <div className="absolute inset-[3px] rounded-[9px] opacity-20" style={{
                    background: 'linear-gradient(135deg, rgba(255,255,255,0.3), transparent 60%)'
                  }} />
                  {/* IPL text - counter-rotate */}
                  <span className="relative font-black text-[13px] tracking-[1px] select-none"
                    style={{
                      transform: 'rotate(-45deg)',
                      color: '#ffffff',
                      textShadow: '0 1px 4px rgba(0,0,0,0.4)',
                      fontFamily: "'Orbitron', sans-serif",
                      letterSpacing: '2px',
                    }}>
                    IPL
                  </span>
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
