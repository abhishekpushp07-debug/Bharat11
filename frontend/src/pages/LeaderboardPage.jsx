import { useState, useEffect, useCallback } from 'react';
import apiClient from '../api/client';
import { COLORS } from '../constants/design';
import { ArrowLeft, Trophy, Crown, Medal, Award, Star } from 'lucide-react';

export default function LeaderboardPage({ contestId, onBack }) {
  const [data, setData] = useState(null);
  const [myPos, setMyPos] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      const [lbRes, meRes] = await Promise.allSettled([
        apiClient.get(`/contests/${contestId}/leaderboard?limit=50`),
        apiClient.get(`/contests/${contestId}/leaderboard/me`)
      ]);
      if (lbRes.status === 'fulfilled') setData(lbRes.value.data);
      if (meRes.status === 'fulfilled') setMyPos(meRes.value.data);
    } catch (e) { /* silent */ }
  }, [contestId]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const rankIcon = (rank) => {
    if (rank === 1) return <Crown size={18} color="#FFD700" />;
    if (rank === 2) return <Medal size={18} color="#C0C0C0" />;
    if (rank === 3) return <Medal size={18} color="#CD7F32" />;
    return <span className="text-xs font-bold" style={{ color: COLORS.text.secondary }}>#{rank}</span>;
  };

  const rankBg = (rank) => {
    if (rank === 1) return 'linear-gradient(135deg, #FFD70022, #FFA50011)';
    if (rank === 2) return 'linear-gradient(135deg, #C0C0C022, #A0A0A011)';
    if (rank === 3) return 'linear-gradient(135deg, #CD7F3222, #8B451311)';
    return COLORS.background.card;
  };

  return (
    <div data-testid="leaderboard-page" className="pb-6 space-y-4">
      <button data-testid="lb-back-btn" onClick={onBack} className="flex items-center gap-2 text-sm" style={{ color: COLORS.text.secondary }}>
        <ArrowLeft size={16} /> Back
      </button>

      {/* Header */}
      <div className="text-center">
        <Trophy size={32} color={COLORS.accent.gold} className="mx-auto mb-2" />
        <h1 className="text-lg font-bold text-white">{data?.contest_name || 'Leaderboard'}</h1>
        <div className="flex items-center justify-center gap-4 mt-2">
          <span className="text-xs" style={{ color: COLORS.text.secondary }}>{data?.total_participants || 0} Players</span>
          <span className="text-xs" style={{ color: COLORS.accent.gold }}>Pool: {(data?.prize_pool || 0).toLocaleString()}</span>
        </div>
      </div>

      {/* My Position */}
      {myPos && (
        <div data-testid="my-position" className="rounded-xl p-4 flex items-center justify-between" style={{ background: `${COLORS.primary.main}15`, border: `1px solid ${COLORS.primary.main}33` }}>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ background: COLORS.primary.gradient }}>
              <Star size={18} color="#fff" />
            </div>
            <div>
              <div className="text-sm font-semibold text-white">Your Position</div>
              <div className="text-xs" style={{ color: COLORS.text.secondary }}>{myPos.team_name}</div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-xl font-bold" style={{ color: COLORS.primary.main, fontFamily: "'Rajdhani', sans-serif" }}>
              #{myPos.rank}
            </div>
            <div className="text-xs font-semibold" style={{ color: COLORS.accent.gold }}>{myPos.total_points} pts</div>
          </div>
        </div>
      )}

      {/* Leaderboard List */}
      <div className="rounded-2xl overflow-hidden" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
        {(data?.leaderboard || []).map((entry, i) => (
          <div key={entry.user_id}
            className="flex items-center gap-3 px-4 py-3"
            style={{
              background: rankBg(entry.rank),
              borderBottom: i < (data?.leaderboard || []).length - 1 ? `1px solid ${COLORS.border.light}` : 'none'
            }}>
            <div className="w-8 flex justify-center">{rankIcon(entry.rank)}</div>
            <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white" style={{ background: COLORS.primary.main + '44' }}>
              {(entry.username || 'U')[0].toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-white truncate">{entry.username}</div>
              <div className="text-xs" style={{ color: COLORS.text.tertiary }}>{entry.team_name}</div>
            </div>
            <div className="text-right">
              <div className="text-sm font-bold" style={{ fontFamily: "'Rajdhani', sans-serif", color: entry.rank <= 3 ? COLORS.accent.gold : '#fff' }}>
                {entry.total_points}
              </div>
              {entry.prize_won > 0 && (
                <div className="text-[10px] font-semibold" style={{ color: COLORS.success.main }}>+{entry.prize_won}</div>
              )}
            </div>
          </div>
        ))}
        {(!data?.leaderboard || data.leaderboard.length === 0) && (
          <div className="py-10 text-center text-sm" style={{ color: COLORS.text.tertiary }}>No entries yet</div>
        )}
      </div>
    </div>
  );
}
