import { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';
import apiClient from '../api/client';
import { COLORS, RANKS } from '../constants/design';
import { User, Wallet, Trophy, Gift, ChevronRight, Copy, Check, LogOut } from 'lucide-react';

export default function ProfilePage() {
  const { user, logout } = useAuthStore();
  const [rankProgress, setRankProgress] = useState(null);
  const [referralStats, setReferralStats] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [rankRes, refRes] = await Promise.all([
        apiClient.get('/user/rank-progress'),
        apiClient.get('/user/referral-stats')
      ]);
      setRankProgress(rankRes.data);
      setReferralStats(refRes.data);
    } catch (e) { /* silent */ }
  };

  const copyReferral = () => {
    if (referralStats?.referral_code) {
      navigator.clipboard.writeText(referralStats.referral_code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const rankKey = (user?.rank_title || 'Rookie').toUpperCase();
  const rankColor = RANKS[rankKey]?.color || '#B0B0B0';

  return (
    <div data-testid="profile-page" className="pb-6 space-y-4">
      {/* Profile Card */}
      <div data-testid="profile-card" className="rounded-2xl p-5" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold" style={{ background: COLORS.primary.gradient, color: '#fff' }}>
            {(user?.username || 'P')[0].toUpperCase()}
          </div>
          <div className="flex-1">
            <h2 data-testid="profile-username" className="text-lg font-bold text-white">{user?.username}</h2>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full" style={{ background: `${rankColor}22`, color: rankColor }}>{user?.rank_title || 'Rookie'}</span>
              <span className="text-xs" style={{ color: COLORS.text.secondary }}>{user?.phone}</span>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-3 gap-3 mt-5">
          {[
            { label: 'Matches', value: user?.matches_played || 0, icon: '🏏' },
            { label: 'Won', value: user?.contests_won || 0, icon: '🏆' },
            { label: 'Points', value: user?.total_points || 0, icon: '⭐' },
          ].map(s => (
            <div key={s.label} className="text-center p-3 rounded-xl" style={{ background: COLORS.background.tertiary }}>
              <div className="text-xl">{s.icon}</div>
              <div className="text-lg font-bold text-white" style={{ fontFamily: "'Rajdhani', sans-serif" }}>{s.value}</div>
              <div className="text-xs" style={{ color: COLORS.text.secondary }}>{s.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Rank Progress */}
      {rankProgress && (
        <div data-testid="rank-progress" className="rounded-2xl p-5" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
          <div className="flex justify-between items-center mb-3">
            <span className="text-sm font-semibold text-white">Rank Progress</span>
            {rankProgress.next_rank && (
              <span className="text-xs" style={{ color: COLORS.text.secondary }}>
                {rankProgress.points_to_next} pts to {rankProgress.next_rank}
              </span>
            )}
          </div>
          <div className="h-2.5 rounded-full overflow-hidden" style={{ background: COLORS.background.tertiary }}>
            <div className="h-full rounded-full transition-all duration-700" style={{ width: `${rankProgress.progress_percent}%`, background: rankColor, boxShadow: `0 0 8px ${rankColor}66` }} />
          </div>
          <div className="flex justify-between mt-2">
            <span className="text-xs font-semibold" style={{ color: rankColor }}>{rankProgress.current_rank}</span>
            {rankProgress.next_rank && <span className="text-xs" style={{ color: COLORS.text.tertiary }}>{rankProgress.next_rank}</span>}
          </div>
        </div>
      )}

      {/* Referral Card */}
      {referralStats && (
        <div data-testid="referral-card" className="rounded-2xl p-5" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
          <div className="flex items-center gap-2 mb-3">
            <Gift size={18} style={{ color: COLORS.primary.main }} />
            <span className="text-sm font-semibold text-white">Invite Friends</span>
          </div>
          <p className="text-xs mb-3" style={{ color: COLORS.text.secondary }}>Share your code & earn {referralStats.bonus_per_referral} coins per referral!</p>
          <div className="flex items-center gap-2">
            <div data-testid="referral-code" className="flex-1 text-center py-2.5 rounded-xl font-mono text-lg font-bold tracking-widest" style={{ background: COLORS.background.tertiary, color: COLORS.primary.main, letterSpacing: '0.2em' }}>
              {referralStats.referral_code}
            </div>
            <button data-testid="copy-referral-btn" onClick={copyReferral} className="p-2.5 rounded-xl transition-colors" style={{ background: copied ? COLORS.success.bg : COLORS.primary.gradient }}>
              {copied ? <Check size={20} color={COLORS.success.main} /> : <Copy size={20} color="#fff" />}
            </button>
          </div>
          <div className="text-xs mt-2" style={{ color: COLORS.text.tertiary }}>
            {referralStats.total_referrals} friend{referralStats.total_referrals !== 1 ? 's' : ''} invited
          </div>
        </div>
      )}

      {/* Logout */}
      <button data-testid="logout-btn" onClick={logout} className="w-full py-3 rounded-xl text-sm font-semibold flex items-center justify-center gap-2 transition-colors" style={{ background: COLORS.error.bg, color: COLORS.error.main, border: `1px solid ${COLORS.error.main}33` }}>
        <LogOut size={16} /> Logout
      </button>
    </div>
  );
}
