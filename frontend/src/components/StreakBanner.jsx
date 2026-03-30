import { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';
import apiClient from '../api/client';
import { COLORS } from '../constants/design';
import { Flame, Zap, Crown, TrendingUp } from 'lucide-react';

function FireIcon({ size = 20, className = '' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className} xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="fireGrad" x1="12" y1="24" x2="12" y2="0" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#FF4500" />
          <stop offset="35%" stopColor="#FF6600" />
          <stop offset="60%" stopColor="#FFB800" />
          <stop offset="85%" stopColor="#FFD700" />
          <stop offset="100%" stopColor="#FFEE44" />
        </linearGradient>
        <linearGradient id="fireInner" x1="12" y1="22" x2="12" y2="8" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#FF2200" />
          <stop offset="50%" stopColor="#FF5500" />
          <stop offset="100%" stopColor="#FFAA00" />
        </linearGradient>
        <filter id="fireGlow">
          <feGaussianBlur stdDeviation="1.5" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      <path d="M12 2C10.5 6 7 8 7 12.5C7 15.5 9.24 18 12 18C14.76 18 17 15.5 17 12.5C17 8 13.5 6 12 2Z"
        fill="url(#fireGrad)" stroke="url(#fireInner)" strokeWidth="0.5" filter="url(#fireGlow)" />
      <path d="M12 8C11 10.5 9.5 11.5 9.5 13.5C9.5 15 10.62 16.2 12 16.2C13.38 16.2 14.5 15 14.5 13.5C14.5 11.5 13 10.5 12 8Z"
        fill="url(#fireInner)" opacity="0.9" />
      <ellipse cx="12" cy="15" rx="1.5" ry="2" fill="#FFEE44" opacity="0.7" />
    </svg>
  );
}

function getStreakTier(streak) {
  if (streak >= 10) return { label: 'LEGENDARY', color: '#E040FF', glow: '#E040FF', multiplier: '4x', bg: 'linear-gradient(135deg, #E040FF22, #A020F022)' };
  if (streak >= 5) return { label: 'HOT STREAK', color: '#C134EA', glow: '#C134EA', multiplier: '2x', bg: 'linear-gradient(135deg, #C134EA22, #8F00C311)' };
  if (streak >= 3) return { label: 'WARMING UP', color: '#B56CFF', glow: '#B56CFF', multiplier: '1x', bg: 'linear-gradient(135deg, #B56CFF15, #A020F008)' };
  return { label: 'BUILD IT', color: '#B56CFF', glow: 'transparent', multiplier: '1x', bg: COLORS.background.card };
}

export default function StreakBanner() {
  const { user } = useAuthStore();
  const [topStreak, setTopStreak] = useState(null);
  const [myStreak, setMyStreak] = useState(null);

  useEffect(() => {
    const fetchStreaks = async () => {
      try {
        const [topRes, myRes] = await Promise.allSettled([
          apiClient.get('/contests/global/top-streak?limit=1'),
          apiClient.get('/contests/global/my-streak'),
        ]);
        if (topRes.status === 'fulfilled' && topRes.value.data?.streaks?.length) {
          setTopStreak(topRes.value.data.streaks[0]);
        }
        if (myRes.status === 'fulfilled') {
          setMyStreak(myRes.value.data);
        }
      } catch (_) {}
    };
    fetchStreaks();
  }, []);

  const currentStreak = myStreak?.current_streak || user?.prediction_streak || 0;
  const maxStreak = myStreak?.max_streak || user?.max_prediction_streak || 0;
  const tier = getStreakTier(currentStreak);
  const isHot = currentStreak >= 5;
  const nextMilestone = myStreak?.next_milestone || (currentStreak < 5 ? 5 : currentStreak < 10 ? 10 : null);
  const streakToNext = nextMilestone ? nextMilestone - currentStreak : 0;
  const progressPct = nextMilestone ? ((currentStreak % 5) / 5) * 100 : 100;

  // Top streak holder section
  const showTopStreak = topStreak && topStreak.current_streak >= 3 && topStreak.user_id !== user?.id;

  return (
    <div data-testid="streak-banner" className="space-y-2.5">
      {/* Top Streak Holder - "Streak King" */}
      {showTopStreak && (
        <div data-testid="streak-king-banner"
          className="rounded-xl p-3 flex items-center gap-3 relative overflow-hidden"
          style={{
            background: topStreak.is_hot
              ? 'linear-gradient(135deg, #FF3B3B18, #FF690012, #FFD70008)'
              : COLORS.background.card,
            border: `1px solid ${topStreak.is_hot ? '#FF3B3B30' : COLORS.border.light}`,
          }}>
          {/* Fire ambient glow for hot streaks */}
          {topStreak.is_hot && (
            <div className="absolute inset-0 pointer-events-none streak-ambient" />
          )}

          <div className="relative shrink-0">
            <Crown size={18} color="#FFD700" className={topStreak.is_hot ? 'animate-float' : ''} />
          </div>

          <div className="flex-1 min-w-0 relative">
            <div className="flex items-center gap-1.5">
              <span className="text-[9px] font-black uppercase tracking-[0.15em]"
                style={{ color: '#FFD700' }}>Streak King</span>
            </div>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="text-xs font-bold text-white truncate">{topStreak.username}</span>
              <div className="flex items-center gap-1">
                <FireIcon size={12} className={topStreak.is_hot ? 'streak-fire-icon' : ''} />
                <span className="text-sm font-black" style={{
                  color: topStreak.is_hot ? '#FF3B3B' : '#F59E0B',
                  fontFamily: "'Rajdhani', sans-serif",
                  textShadow: topStreak.is_hot ? '0 0 8px #FF3B3B55' : 'none'
                }}>
                  {topStreak.current_streak}
                </span>
              </div>
            </div>
          </div>

          {topStreak.is_hot && (
            <div className="shrink-0 px-2 py-1 rounded-lg text-[9px] font-black"
              style={{ background: '#FF3B3B20', color: '#FF3B3B' }}>
              {topStreak.current_streak >= 10 ? '4x' : '2x'} BONUS
            </div>
          )}
        </div>
      )}

      {/* My Streak Card - Diamond Cut Pink */}
      <div data-testid="my-streak-card"
        className={`rounded-xl overflow-hidden relative ${isHot ? 'streak-hot-border' : 'streak-diamond-border'}`}
        style={{
          background: 'linear-gradient(135deg, #2a0845, #6A0DAD, #3d0d5c, #4a0e78)',
          border: isHot ? 'none' : 'none',
        }}>

        {/* Diamond sparkle overlay */}
        <div className="absolute inset-0 pointer-events-none streak-diamond-sparkle" />
        <div className="absolute inset-0 pointer-events-none" style={{
          background: 'radial-gradient(ellipse at 50% 0%, rgba(193,52,234,0.25) 0%, transparent 60%), radial-gradient(ellipse at 70% 80%, rgba(160,32,240,0.12) 0%, transparent 50%)',
        }} />

        {/* Floating diamond particles */}
        <div className="streak-diamond-particles">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="diamond-particle"
              style={{
                '--delay': `${i * 0.6}s`,
                '--x': `${8 + i * 11}%`,
                '--size': `${2 + (i % 3)}px`,
                '--color': i % 2 === 0 ? '#C134EA' : '#E040FF',
              }} />
          ))}
        </div>

        {/* Hot streak fire particles */}
        {isHot && (
          <>
            <div className="absolute inset-0 pointer-events-none" style={{
              background: 'linear-gradient(180deg, transparent 0%, rgba(160,32,240,0.08) 40%, rgba(193,52,234,0.1) 70%, rgba(224,64,255,0.05) 100%)',
              animation: 'streakFireBg 4s ease-in-out infinite',
            }} />
          </>
        )}

        <div className="relative p-3.5 flex items-center gap-3.5">
          {/* Streak Fire Icon */}
          <div className={`shrink-0 w-14 h-14 rounded-xl flex items-center justify-center streak-fire-box`}
            style={{ background: 'linear-gradient(135deg, rgba(255,69,0,0.2), rgba(255,165,0,0.15), rgba(255,0,0,0.12))' }}>
            <FireIcon
              size={30}
              className="streak-fire-icon-bold"
            />
          </div>

          {/* Streak Info */}
          <div className="flex-1 min-w-0 space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-[9px] font-black uppercase tracking-[0.15em]"
                style={{ color: tier.color }}>{tier.label}</span>
              {isHot && (
                <span className="px-1.5 py-0.5 rounded text-[8px] font-black animate-pulse"
                  style={{ background: `${tier.color}20`, color: tier.color }}>
                  {tier.multiplier} POINTS
                </span>
              )}
            </div>

            <div className="flex items-center gap-3">
              {/* Current Streak Number */}
              <div className="flex items-baseline gap-1.5">
                <span className="text-3xl font-black streak-count-glow"
                  style={{
                    color: '#FF2020',
                    fontFamily: "'Rajdhani', sans-serif",
                    textShadow: '0 0 10px rgba(255,32,32,0.5), 0 0 20px rgba(255,69,0,0.3)',
                    letterSpacing: '-0.5px',
                    WebkitTextStroke: '0.5px rgba(255,69,0,0.3)',
                  }}>
                  {currentStreak}
                </span>
                <span className="text-xs font-black uppercase tracking-wide" style={{ color: 'rgba(255,255,255,0.6)' }}>
                  streak
                </span>
              </div>

              {/* Progress to next milestone */}
              {nextMilestone && currentStreak > 0 && (
                <div className="flex items-center gap-1.5 flex-1">
                  <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.06)' }}>
                    <div className={`h-full rounded-full transition-all duration-500 ${isHot ? 'streak-progress-glow' : ''}`}
                      style={{
                        width: `${progressPct}%`,
                        background: `linear-gradient(90deg, ${tier.color}88, ${tier.color})`
                      }} />
                  </div>
                  <span className="text-[9px] font-bold shrink-0" style={{ color: tier.color }}>
                    {streakToNext} to {nextMilestone >= 10 ? '4x' : '2x'}
                  </span>
                </div>
              )}
            </div>

            {/* Max streak */}
            {maxStreak > 0 && (
              <div className="flex items-center gap-1.5">
                <TrendingUp size={10} color={COLORS.text.tertiary} />
                <span className="text-[9px]" style={{ color: COLORS.text.tertiary }}>
                  Best: {maxStreak} streak
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Bottom info bar */}
        {currentStreak === 0 && (
          <div className="px-3.5 py-2 text-center" style={{ borderTop: '1px solid rgba(160,32,240,0.12)', background: 'rgba(160,32,240,0.05)' }}>
            <span className="text-[8px] font-bold uppercase tracking-[0.15em]" style={{ color: 'rgba(193,52,234,0.5)' }}>
              Get 5 consecutive correct predictions for 2x bonus
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
