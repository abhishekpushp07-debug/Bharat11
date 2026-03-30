import { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';
import apiClient from '../api/client';
import { COLORS } from '../constants/design';
import { Flame, Zap, Crown, TrendingUp } from 'lucide-react';

function FireIcon({ size = 20, className = '' }) {
  return <Flame size={size} className={className} />;
}

function getStreakTier(streak) {
  if (streak >= 10) return { label: 'LEGENDARY', color: '#FF69B4', glow: '#FF69B4', multiplier: '4x', bg: 'linear-gradient(135deg, #FF69B422, #C88CFF22)' };
  if (streak >= 5) return { label: 'HOT STREAK', color: '#E040A0', glow: '#E040A0', multiplier: '2x', bg: 'linear-gradient(135deg, #E040A022, #FF69B411)' };
  if (streak >= 3) return { label: 'WARMING UP', color: '#C88CFF', glow: '#C88CFF', multiplier: '1x', bg: 'linear-gradient(135deg, #C88CFF15, #FF69B408)' };
  return { label: 'BUILD IT', color: '#C88CFF', glow: 'transparent', multiplier: '1x', bg: COLORS.background.card };
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
          background: 'linear-gradient(135deg, #1a0a1e, #2d0f38, #1a0a20, #2d0f38)',
          border: isHot ? 'none' : 'none',
        }}>

        {/* Diamond sparkle overlay */}
        <div className="absolute inset-0 pointer-events-none streak-diamond-sparkle" />
        <div className="absolute inset-0 pointer-events-none" style={{
          background: 'radial-gradient(ellipse at 30% 20%, rgba(255,105,180,0.08) 0%, transparent 50%), radial-gradient(ellipse at 70% 80%, rgba(200,140,255,0.06) 0%, transparent 50%)',
        }} />

        {/* Floating diamond particles */}
        <div className="streak-diamond-particles">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="diamond-particle"
              style={{
                '--delay': `${i * 0.6}s`,
                '--x': `${8 + i * 11}%`,
                '--size': `${2 + (i % 3)}px`,
              }} />
          ))}
        </div>

        {/* Hot streak fire particles */}
        {isHot && (
          <>
            <div className="absolute inset-0 pointer-events-none" style={{
              background: 'linear-gradient(180deg, transparent 0%, rgba(255,105,180,0.06) 40%, rgba(200,140,255,0.08) 70%, rgba(255,105,180,0.03) 100%)',
              animation: 'streakFireBg 4s ease-in-out infinite',
            }} />
          </>
        )}

        <div className="relative p-3.5 flex items-center gap-3.5">
          {/* Streak Fire Icon */}
          <div className={`shrink-0 w-12 h-12 rounded-xl flex items-center justify-center ${isHot ? 'streak-icon-glow' : ''}`}
            style={{ background: isHot ? 'rgba(255,105,180,0.15)' : 'rgba(255,105,180,0.08)' }}>
            <FireIcon
              size={isHot ? 28 : 22}
              className={`transition-all ${isHot ? 'streak-fire-icon' : ''}`}
            />
            {currentStreak >= 10 && (
              <div className="absolute inset-0 rounded-xl animate-live-pulse" style={{
                background: 'radial-gradient(circle, rgba(255,105,180,0.2), transparent 70%)'
              }} />
            )}
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
              <div className="flex items-baseline gap-1">
                <span className={`text-2xl font-black ${isHot ? 'streak-number-glow' : ''}`}
                  style={{
                    color: currentStreak >= 1 ? tier.color : COLORS.text.tertiary,
                    fontFamily: "'Rajdhani', sans-serif",
                    textShadow: isHot ? `0 0 12px ${tier.color}55` : 'none',
                  }}>
                  {currentStreak}
                </span>
                <span className="text-[10px] font-medium" style={{ color: COLORS.text.tertiary }}>
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
          <div className="px-3.5 py-2 text-center" style={{ borderTop: '1px solid rgba(255,105,180,0.08)', background: 'rgba(255,105,180,0.03)' }}>
            <span className="text-[8px] font-bold uppercase tracking-[0.15em]" style={{ color: 'rgba(255,105,180,0.4)' }}>
              Get 5 consecutive correct predictions for 2x bonus
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
