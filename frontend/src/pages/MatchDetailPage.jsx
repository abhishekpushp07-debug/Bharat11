import { useState, useEffect } from 'react';
import apiClient from '../api/client';
import { COLORS } from '../constants/design';
import { ArrowLeft, Clock, MapPin, Trophy, Users, ChevronRight } from 'lucide-react';

const TEAM_COLORS = {
  MI: ['#004BA0', '#00599E'], CSK: ['#F9CD05', '#F3A012'],
  RCB: ['#D4213D', '#A0171F'], KKR: ['#3A225D', '#552583'],
  DC: ['#0078BC', '#17479E'], PBKS: ['#ED1B24', '#AA1019'],
  SRH: ['#FF822A', '#E35205'], RR: ['#EA1A85', '#C51D70'],
  GT: ['#1C1C2B', '#0B4F6C'], LSG: ['#2E90A8', '#1B7B93'],
};

export default function MatchDetailPage({ match, onBack }) {
  const [contests, setContests] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (match?.id) fetchContests();
  }, [match?.id]);

  const fetchContests = async () => {
    try {
      const res = await apiClient.get(`/matches/${match.id}/contests`);
      setContests(res.data.contests || []);
    } catch (e) { /* silent */ }
    finally { setLoading(false); }
  };

  const teamA = match?.team_a || {};
  const teamB = match?.team_b || {};
  const isLive = match?.status === 'live';
  const score = match?.live_score;
  const getGrad = (s) => { const c = TEAM_COLORS[s] || ['#555','#333']; return `linear-gradient(135deg, ${c[0]}, ${c[1]})`; };

  return (
    <div data-testid="match-detail-page" className="pb-6 space-y-4">
      {/* Back Button */}
      <button data-testid="match-back-btn" onClick={onBack} className="flex items-center gap-2 text-sm" style={{ color: COLORS.text.secondary }}>
        <ArrowLeft size={16} /> Back to Matches
      </button>

      {/* Match Hero Card */}
      <div className="rounded-2xl overflow-hidden" style={{ background: COLORS.background.card, border: `1px solid ${isLive ? COLORS.primary.main + '44' : COLORS.border.light}` }}>
        {/* Tournament/Status bar */}
        <div className="px-4 py-3 flex items-center justify-between" style={{ background: isLive ? `${COLORS.primary.main}15` : COLORS.background.tertiary }}>
          <span className="text-xs font-medium" style={{ color: COLORS.text.secondary }}>{match?.tournament || 'IPL 2026'}</span>
          {isLive && <span className="px-2 py-0.5 rounded text-xs font-bold text-white animate-pulse" style={{ background: COLORS.primary.main }}>LIVE</span>}
        </div>

        {/* Teams */}
        <div className="px-6 py-6 flex items-center justify-between">
          <div className="flex flex-col items-center gap-2 flex-1">
            <div className="w-16 h-16 rounded-2xl flex items-center justify-center text-lg font-black text-white shadow-lg" style={{ background: getGrad(teamA.short_name) }}>
              {teamA.short_name || '?'}
            </div>
            <div className="text-center">
              <div className="text-sm font-bold text-white">{teamA.short_name}</div>
              <div className="text-xs" style={{ color: COLORS.text.tertiary }}>{teamA.name}</div>
              {isLive && score?.batting_team === teamA.short_name && (
                <div className="text-lg font-bold mt-1" style={{ color: COLORS.primary.main, fontFamily: "'Rajdhani', sans-serif" }}>
                  {score.score}
                </div>
              )}
            </div>
          </div>

          <div className="flex flex-col items-center">
            <div className="text-xs font-bold px-3 py-1 rounded-lg" style={{ background: `${COLORS.primary.main}22`, color: COLORS.primary.main }}>VS</div>
            {isLive && <div className="text-xs mt-1" style={{ color: COLORS.text.tertiary }}>{score?.overs} ov</div>}
          </div>

          <div className="flex flex-col items-center gap-2 flex-1">
            <div className="w-16 h-16 rounded-2xl flex items-center justify-center text-lg font-black text-white shadow-lg" style={{ background: getGrad(teamB.short_name) }}>
              {teamB.short_name || '?'}
            </div>
            <div className="text-center">
              <div className="text-sm font-bold text-white">{teamB.short_name}</div>
              <div className="text-xs" style={{ color: COLORS.text.tertiary }}>{teamB.name}</div>
              {isLive && score?.batting_team === teamB.short_name && (
                <div className="text-lg font-bold mt-1" style={{ color: COLORS.primary.main, fontFamily: "'Rajdhani', sans-serif" }}>
                  {score.score}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Match Info */}
        <div className="px-4 py-3 flex items-center justify-around" style={{ borderTop: `1px solid ${COLORS.border.light}` }}>
          <div className="flex items-center gap-1.5">
            <MapPin size={14} color={COLORS.text.tertiary} />
            <span className="text-xs" style={{ color: COLORS.text.secondary }}>{match?.venue || 'TBD'}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Clock size={14} color={COLORS.warning.main} />
            <span className="text-xs" style={{ color: COLORS.warning.main }}>
              {isLive ? 'In Progress' : new Date(match?.start_time).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
        </div>
      </div>

      {/* Contests */}
      <div>
        <h2 className="text-base font-semibold text-white mb-3">Contests</h2>
        {loading ? (
          <div className="flex justify-center py-8">
            <div className="w-6 h-6 border-2 rounded-full animate-spin" style={{ borderColor: `${COLORS.primary.main}30`, borderTopColor: COLORS.primary.main }} />
          </div>
        ) : contests.length === 0 ? (
          <div className="text-center py-8 rounded-2xl" style={{ background: COLORS.background.card }}>
            <Trophy size={32} color={COLORS.text.tertiary} className="mx-auto mb-2" />
            <p className="text-sm" style={{ color: COLORS.text.secondary }}>No contests yet for this match</p>
          </div>
        ) : (
          <div className="space-y-2">
            {contests.map(c => (
              <div key={c.id} className="p-4 rounded-xl" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-semibold text-white">{c.name}</div>
                    <div className="flex items-center gap-3 mt-1">
                      <span className="text-xs" style={{ color: COLORS.text.secondary }}>Entry: {c.entry_fee === 0 ? 'FREE' : `${c.entry_fee} coins`}</span>
                      <span className="text-xs" style={{ color: COLORS.accent.gold }}>Pool: {(c.prize_pool || 0).toLocaleString()}</span>
                    </div>
                    <div className="flex items-center gap-1 mt-1">
                      <Users size={12} color={COLORS.info.main} />
                      <span className="text-xs" style={{ color: COLORS.text.tertiary }}>{c.current_participants || 0}/{c.max_participants || 0}</span>
                    </div>
                  </div>
                  <button className="px-4 py-2 rounded-xl text-xs font-bold" style={{ background: COLORS.primary.gradient, color: '#fff' }}>
                    Join <ChevronRight size={12} className="inline" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
