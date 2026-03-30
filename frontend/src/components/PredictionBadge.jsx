import { useState, useEffect } from 'react';
import apiClient from '../api/client';
import { COLORS } from '../constants/design';

const BADGES = {
  pink_diamond: {
    label: 'Pink Diamond',
    icon: (sz) => (
      <svg width={sz} height={sz} viewBox="0 0 40 40" fill="none">
        <defs>
          <linearGradient id="pd" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#FF69B4" />
            <stop offset="50%" stopColor="#FF1493" />
            <stop offset="100%" stopColor="#C71585" />
          </linearGradient>
          <filter id="pdg"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
        </defs>
        <polygon points="20,2 35,14 28,38 12,38 5,14" fill="url(#pd)" filter="url(#pdg)" />
        <polygon points="20,6 31,15 26,35 14,35 9,15" fill="none" stroke="#fff" strokeWidth="0.5" opacity="0.4" />
        <polygon points="20,12 25,18 20,32 15,18" fill="#fff" opacity="0.25" />
      </svg>
    ),
    glow: '#FF1493',
    bg: 'linear-gradient(135deg, #FF149322, #FF69B411)',
    border: '#FF149340',
  },
  gold: {
    label: 'Gold',
    icon: (sz) => (
      <svg width={sz} height={sz} viewBox="0 0 40 40" fill="none">
        <defs>
          <linearGradient id="gd" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#FFD700" />
            <stop offset="50%" stopColor="#FFA500" />
            <stop offset="100%" stopColor="#FF8C00" />
          </linearGradient>
          <filter id="gg"><feGaussianBlur stdDeviation="1.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
        </defs>
        <polygon points="20,2 35,14 28,38 12,38 5,14" fill="url(#gd)" filter="url(#gg)" />
        <polygon points="20,6 31,15 26,35 14,35 9,15" fill="none" stroke="#fff" strokeWidth="0.5" opacity="0.3" />
        <polygon points="20,12 25,18 20,32 15,18" fill="#fff" opacity="0.2" />
      </svg>
    ),
    glow: '#FFD700',
    bg: 'linear-gradient(135deg, #FFD70022, #FFA50011)',
    border: '#FFD70040',
  },
  silver: {
    label: 'Silver',
    icon: (sz) => (
      <svg width={sz} height={sz} viewBox="0 0 40 40" fill="none">
        <defs>
          <linearGradient id="sd" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#E0E0E0" />
            <stop offset="50%" stopColor="#B0B0B0" />
            <stop offset="100%" stopColor="#909090" />
          </linearGradient>
        </defs>
        <polygon points="20,2 35,14 28,38 12,38 5,14" fill="url(#sd)" />
        <polygon points="20,6 31,15 26,35 14,35 9,15" fill="none" stroke="#fff" strokeWidth="0.5" opacity="0.3" />
        <polygon points="20,12 25,18 20,32 15,18" fill="#fff" opacity="0.15" />
      </svg>
    ),
    glow: '#C0C0C0',
    bg: 'linear-gradient(135deg, #C0C0C022, #90909011)',
    border: '#C0C0C040',
  },
  blue_crystal: {
    label: 'Crystal',
    icon: (sz) => (
      <svg width={sz} height={sz} viewBox="0 0 40 40" fill="none">
        <defs>
          <linearGradient id="bc" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#60A5FA" />
            <stop offset="50%" stopColor="#3B82F6" />
            <stop offset="100%" stopColor="#2563EB" />
          </linearGradient>
        </defs>
        <polygon points="20,2 35,14 28,38 12,38 5,14" fill="url(#bc)" />
        <polygon points="20,6 31,15 26,35 14,35 9,15" fill="none" stroke="#fff" strokeWidth="0.5" opacity="0.25" />
        <polygon points="20,12 25,18 20,32 15,18" fill="#fff" opacity="0.15" />
      </svg>
    ),
    glow: '#3B82F6',
    bg: 'linear-gradient(135deg, #3B82F622, #2563EB11)',
    border: '#3B82F640',
  },
};

export default function PredictionBadge({ compact = false }) {
  const [badge, setBadge] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchBadge = async () => {
      try {
        const res = await apiClient.get('/contests/global/my-badge');
        setBadge(res.data);
      } catch (_) {}
      finally { setLoading(false); }
    };
    fetchBadge();
  }, []);

  if (loading || !badge || !badge.badge) return null;

  const b = BADGES[badge.badge] || BADGES.blue_crystal;
  const isTop3 = badge.rank <= 3;

  if (compact) {
    return (
      <div data-testid="badge-compact" className="flex items-center gap-2">
        <div className="shrink-0">{b.icon(24)}</div>
        <span className="text-[10px] font-bold" style={{ color: b.glow }}>#{badge.rank}</span>
        <span className="text-[10px]" style={{ color: COLORS.text.secondary }}>
          {badge.total_correct}/{badge.total_attempted} ({badge.accuracy_pct}%)
        </span>
      </div>
    );
  }

  const accColor = badge.accuracy_pct >= 70 ? '#10B981' : badge.accuracy_pct >= 40 ? '#F59E0B' : '#EF4444';

  return (
    <div data-testid="prediction-badge"
      className="rounded-2xl overflow-hidden relative"
      style={{ background: '#0d1117', border: `1px solid ${b.border}` }}>

      {/* Ambient glow */}
      {isTop3 && (
        <div className="absolute inset-0 pointer-events-none" style={{
          background: `radial-gradient(ellipse at 30% 30%, ${b.glow}12, transparent 60%), radial-gradient(ellipse at 70% 70%, ${b.glow}08, transparent 50%)`
        }} />
      )}

      <div className="relative p-4 flex items-center gap-4">
        {/* Badge Icon */}
        <div className={`shrink-0 relative ${isTop3 ? 'animate-float' : ''}`}>
          {b.icon(48)}
          {isTop3 && (
            <div className="absolute inset-0 rounded-full animate-live-pulse" style={{
              background: `radial-gradient(circle, ${b.glow}30, transparent 70%)`
            }} />
          )}
        </div>

        {/* Stats */}
        <div className="flex-1 min-w-0 space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="text-[9px] font-black uppercase tracking-[0.15em]" style={{ color: b.glow }}>
              {b.label}
            </span>
            <span className="text-lg font-black" style={{ color: '#fff', fontFamily: "'Rajdhani', sans-serif" }}>
              #{badge.rank}
            </span>
          </div>

          {/* Correct / Attempted */}
          <div className="flex items-center gap-3">
            <div>
              <span className="text-sm font-black" style={{ color: '#fff', fontFamily: "'Rajdhani', sans-serif" }}>
                {badge.total_correct}
              </span>
              <span className="text-[10px] font-medium" style={{ color: COLORS.text.tertiary }}>
                /{badge.total_attempted}
              </span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-16 h-1.5 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.06)' }}>
                <div className="h-full rounded-full transition-all" style={{
                  width: `${badge.accuracy_pct}%`,
                  background: `linear-gradient(90deg, ${accColor}88, ${accColor})`
                }} />
              </div>
              <span className="text-xs font-black" style={{ color: accColor, fontFamily: "'Rajdhani', sans-serif" }}>
                {badge.accuracy_pct}%
              </span>
            </div>
          </div>

          {/* Sub stats */}
          <div className="flex items-center gap-3">
            <span className="text-[9px]" style={{ color: COLORS.text.tertiary }}>
              {badge.contests_count} contest{badge.contests_count !== 1 ? 's' : ''}
            </span>
            <span className="text-[9px]" style={{ color: COLORS.text.tertiary }}>
              {badge.total_points_earned} pts earned
            </span>
          </div>
        </div>
      </div>

      {/* Bottom label */}
      <div className="px-4 py-2 text-center" style={{ borderTop: `1px solid rgba(255,255,255,0.04)`, background: 'rgba(255,255,255,0.02)' }}>
        <span className="text-[8px] font-bold uppercase tracking-[0.15em]" style={{ color: 'rgba(255,255,255,0.2)' }}>
          Global Prediction Accuracy Rank
        </span>
      </div>
    </div>
  );
}

// For use in ShareCard (static, receives data as prop)
export function BadgeInline({ badgeData }) {
  if (!badgeData || !badgeData.badge) return null;
  const b = BADGES[badgeData.badge] || BADGES.blue_crystal;
  const accColor = badgeData.accuracy_pct >= 70 ? '#10B981' : badgeData.accuracy_pct >= 40 ? '#F59E0B' : '#EF4444';

  return (
    <div className="flex items-center justify-between px-3 py-2.5 rounded-xl" style={{ background: b.bg, border: `1px solid ${b.border}` }}>
      <div className="flex items-center gap-2">
        {b.icon(28)}
        <div>
          <div className="flex items-center gap-1.5">
            <span className="text-[9px] font-black uppercase" style={{ color: b.glow }}>{b.label}</span>
            <span className="text-sm font-black text-white" style={{ fontFamily: "'Rajdhani', sans-serif" }}>#{badgeData.rank}</span>
          </div>
          <span className="text-[8px]" style={{ color: 'rgba(255,255,255,0.4)' }}>Global Prediction Rank</span>
        </div>
      </div>
      <div className="text-right">
        <div className="text-xs font-black" style={{ color: accColor, fontFamily: "'Rajdhani', sans-serif" }}>
          {badgeData.accuracy_pct}%
        </div>
        <div className="text-[8px]" style={{ color: COLORS.text.tertiary }}>
          {badgeData.total_correct}/{badgeData.total_attempted}
        </div>
      </div>
    </div>
  );
}
