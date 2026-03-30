import { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';
import apiClient from '../api/client';
import { COLORS } from '../constants/design';
import { Trophy, Clock, Users, ChevronRight, CheckCircle, XCircle, Coins } from 'lucide-react';

const TEAM_COLORS = {
  MI: '#004BA0', CSK: '#F9CD05', RCB: '#D4213D', KKR: '#3A225D',
  DC: '#0078BC', PBKS: '#ED1B24', SRH: '#FF822A', RR: '#EA1A85',
  GT: '#1C1C2B', LSG: '#2E90A8',
};

export default function MyContestsPage({ onContestClick }) {
  const [contests, setContests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => { fetchMyContests(); }, []);

  const fetchMyContests = async () => {
    try {
      const res = await apiClient.get('/contests/user/my-contests?limit=50');
      setContests(res.data.my_contests || []);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const filtered = filter === 'all' ? contests :
    contests.filter(c => c.contest?.status === filter);

  const statusColor = (s) => ({
    open: COLORS.success.main, locked: COLORS.warning.main,
    live: COLORS.primary.main, completed: COLORS.text.tertiary
  }[s] || COLORS.text.secondary);

  return (
    <div data-testid="my-contests-page" className="pb-4 space-y-4">
      <h1 className="text-xl font-bold text-white">My Contests</h1>

      {/* Filter Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-1 no-scrollbar">
        {['all', 'open', 'live', 'completed'].map(f => (
          <button key={f} data-testid={`filter-${f}`} onClick={() => setFilter(f)}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors"
            style={{
              background: filter === f ? COLORS.primary.main : COLORS.background.card,
              color: filter === f ? '#fff' : COLORS.text.secondary,
              border: `1px solid ${filter === f ? COLORS.primary.main : COLORS.border.light}`
            }}>
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex justify-center py-10">
          <div className="w-8 h-8 border-2 rounded-full animate-spin" style={{ borderColor: `${COLORS.primary.main}30`, borderTopColor: COLORS.primary.main }} />
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-12 rounded-2xl" style={{ background: COLORS.background.card }}>
          <Trophy size={36} color={COLORS.text.tertiary} className="mx-auto mb-3" />
          <p className="text-sm font-medium text-white mb-1">No Contests Yet</p>
          <p className="text-xs" style={{ color: COLORS.text.secondary }}>Join a contest from the Home page!</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map(({ entry, contest, match }) => {
            const teamA = match?.team_a || {};
            const teamB = match?.team_b || {};
            const isCompleted = contest?.status === 'completed';
            const predictions = entry?.predictions || [];
            const answered = predictions.length;
            const correct = predictions.filter(p => p.is_correct).length;

            return (
              <div key={entry?.id} data-testid={`my-contest-${entry?.id}`}
                className="rounded-2xl overflow-hidden cursor-pointer transition-transform active:scale-[0.98]"
                style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}
                onClick={() => onContestClick?.({ entry, contest, match })}>

                {/* Header */}
                <div className="px-4 py-2.5 flex items-center justify-between" style={{ borderBottom: `1px solid ${COLORS.border.light}` }}>
                  <span className="text-sm font-semibold text-white">{contest?.name}</span>
                  <span className="text-xs font-semibold px-2 py-0.5 rounded" style={{ color: statusColor(contest?.status), background: `${statusColor(contest?.status)}15` }}>
                    {contest?.status?.toUpperCase()}
                  </span>
                </div>

                {/* Teams row */}
                <div className="px-4 py-3 flex items-center gap-3">
                  <div className="flex items-center gap-2 flex-1">
                    <div className="w-8 h-8 rounded-lg flex items-center justify-center text-[10px] font-black text-white"
                      style={{ background: (TEAM_COLORS[teamA.short_name] || {primary: '#555'}).primary }}>
                      {teamA.short_name || '?'}
                    </div>
                    <span className="text-xs font-medium text-white">vs</span>
                    <div className="w-8 h-8 rounded-lg flex items-center justify-center text-[10px] font-black text-white"
                      style={{ background: (TEAM_COLORS[teamB.short_name] || {primary: '#555'}).primary }}>
                      {teamB.short_name || '?'}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold" style={{ color: COLORS.primary.main, fontFamily: "'Rajdhani', sans-serif" }}>
                      {entry?.total_points || 0} pts
                    </div>
                    {isCompleted && entry?.final_rank && (
                      <div className="text-xs" style={{ color: COLORS.accent.gold }}>
                        Rank #{entry.final_rank} {entry.prize_won > 0 ? `| +${entry.prize_won}` : ''}
                      </div>
                    )}
                  </div>
                </div>

                {/* Progress */}
                {answered > 0 && (
                  <div className="px-4 py-2 flex items-center justify-between" style={{ background: COLORS.background.tertiary }}>
                    <span className="text-xs" style={{ color: COLORS.text.secondary }}>
                      {answered} predictions {isCompleted ? `| ${correct} correct` : ''}
                    </span>
                    {isCompleted ? (
                      <div className="flex items-center gap-1">
                        <CheckCircle size={12} color={COLORS.success.main} />
                        <span className="text-xs font-semibold" style={{ color: COLORS.success.main }}>{correct}/{answered}</span>
                      </div>
                    ) : (
                      <span className="text-xs" style={{ color: COLORS.primary.main }}>
                        View <ChevronRight size={12} className="inline" />
                      </span>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
