import { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';
import apiClient from '../api/client';
import { COLORS } from '../constants/design';
import { Coins, ChevronRight, Clock, Users, Trophy } from 'lucide-react';

const TEAM_COLORS = {
  MI: ['#004BA0', '#00599E'], CSK: ['#F9CD05', '#F3A012'],
  RCB: ['#D4213D', '#A0171F'], KKR: ['#3A225D', '#552583'],
  DC: ['#0078BC', '#17479E'], PBKS: ['#ED1B24', '#AA1019'],
  SRH: ['#FF822A', '#E35205'], RR: ['#EA1A85', '#C51D70'],
  GT: ['#1C1C2B', '#0B4F6C'], LSG: ['#2E90A8', '#1B7B93'],
};

const getTeamGrad = (short) => {
  const c = TEAM_COLORS[short] || ['#555', '#333'];
  return `linear-gradient(135deg, ${c[0]}, ${c[1]})`;
};

const formatTime = (d) => {
  const date = new Date(d);
  const now = new Date();
  const diff = date - now;
  if (diff < 0) return 'LIVE';
  const hours = Math.floor(diff / 3600000);
  const mins = Math.floor((diff % 3600000) / 60000);
  if (hours > 24) return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
  return `${hours}h ${mins}m`;
};

export default function HomePage({ onMatchClick }) {
  const { user } = useAuthStore();
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchMatches(); }, []);

  const fetchMatches = async () => {
    try {
      const res = await apiClient.get('/matches?limit=10');
      setMatches(res.data.matches || []);
    } catch (e) {
      console.error('Match fetch error:', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div data-testid="home-page" className="pb-4 space-y-4">
      {/* Greeting + Balance */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Hey, {user?.username || 'Player'}!</h1>
          <p className="text-xs mt-0.5" style={{ color: COLORS.text.secondary }}>Predict & Win Virtual Coins</p>
        </div>
        <div data-testid="home-balance" className="flex items-center gap-1.5 px-3 py-1.5 rounded-full" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
          <Coins size={14} color="#FFD700" />
          <span className="text-sm font-bold text-white" style={{ fontFamily: "'Rajdhani', sans-serif" }}>{(user?.coins_balance || 0).toLocaleString()}</span>
        </div>
      </div>

      {/* Matches Section */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-base font-semibold text-white">
            {matches.some(m => m.status === 'live') ? 'Live & Upcoming' : 'Upcoming Matches'}
          </h2>
          <span className="text-xs" style={{ color: COLORS.text.tertiary }}>{matches.length} matches</span>
        </div>

        {loading ? (
          <div className="flex justify-center py-10">
            <div className="w-8 h-8 border-2 rounded-full animate-spin" style={{ borderColor: `${COLORS.primary.main}30`, borderTopColor: COLORS.primary.main }} />
          </div>
        ) : matches.length === 0 ? (
          <div className="text-center py-10 rounded-2xl" style={{ background: COLORS.background.card }}>
            <div className="text-4xl mb-3">🏏</div>
            <p className="text-sm" style={{ color: COLORS.text.secondary }}>No matches available right now</p>
            <p className="text-xs mt-1" style={{ color: COLORS.text.tertiary }}>Check back soon!</p>
          </div>
        ) : (
          <div className="space-y-3">
            {matches.map(match => {
              const teamA = match.team_a || {};
              const teamB = match.team_b || {};
              const isLive = match.status === 'live';
              const score = match.live_score;

              return (
                <div
                  data-testid={`match-card-${match.id}`}
                  key={match.id}
                  className="rounded-2xl overflow-hidden cursor-pointer transition-transform active:scale-[0.98]"
                  style={{
                    background: COLORS.background.card,
                    border: `1px solid ${isLive ? COLORS.primary.main + '44' : COLORS.border.light}`,
                    boxShadow: isLive ? `0 0 12px ${COLORS.primary.main}22` : 'none'
                  }}
                  onClick={() => onMatchClick?.(match)}
                >
                  {/* Header */}
                  <div className="px-4 py-2.5 flex items-center justify-between" style={{ borderBottom: `1px solid ${COLORS.border.light}` }}>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium" style={{ color: COLORS.text.secondary }}>{match.tournament || match.venue}</span>
                      {isLive && <span className="px-1.5 py-0.5 rounded text-[10px] font-bold text-white animate-pulse" style={{ background: COLORS.primary.main }}>LIVE</span>}
                    </div>
                    <div className="flex items-center gap-1.5">
                      <Clock size={12} color={isLive ? COLORS.primary.main : COLORS.warning.main} />
                      <span className="text-xs font-semibold" style={{ color: isLive ? COLORS.primary.main : COLORS.warning.main }}>
                        {isLive ? 'In Progress' : formatTime(match.start_time)}
                      </span>
                    </div>
                  </div>

                  {/* Teams */}
                  <div className="px-4 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-11 h-11 rounded-xl flex items-center justify-center text-xs font-black text-white" style={{ background: getTeamGrad(teamA.short_name) }}>
                        {teamA.short_name || '?'}
                      </div>
                      <div>
                        <div className="text-sm font-bold text-white">{teamA.short_name || 'TBD'}</div>
                        {isLive && score?.batting_team === teamA.short_name ? (
                          <div className="text-xs font-semibold" style={{ color: COLORS.primary.main }}>{score.score} ({score.overs})</div>
                        ) : (
                          <div className="text-xs" style={{ color: COLORS.text.tertiary }}>{teamA.name || ''}</div>
                        )}
                      </div>
                    </div>

                    <div className="px-3 py-1 rounded-lg text-xs font-bold" style={{ background: isLive ? COLORS.primary.gradient : `${COLORS.primary.main}22`, color: isLive ? '#fff' : COLORS.primary.main }}>
                      VS
                    </div>

                    <div className="flex items-center gap-3 flex-row-reverse">
                      <div className="w-11 h-11 rounded-xl flex items-center justify-center text-xs font-black text-white" style={{ background: getTeamGrad(teamB.short_name) }}>
                        {teamB.short_name || '?'}
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-bold text-white">{teamB.short_name || 'TBD'}</div>
                        {isLive && score?.batting_team === teamB.short_name ? (
                          <div className="text-xs font-semibold" style={{ color: COLORS.primary.main }}>{score.score} ({score.overs})</div>
                        ) : (
                          <div className="text-xs" style={{ color: COLORS.text.tertiary }}>{teamB.name || ''}</div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Footer */}
                  <div className="px-4 py-2.5 flex items-center justify-between" style={{ background: COLORS.background.tertiary }}>
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-1">
                        <Trophy size={12} color={COLORS.accent.gold} />
                        <span className="text-xs" style={{ color: COLORS.text.secondary }}>{match.venue}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-1 text-xs font-semibold" style={{ color: COLORS.primary.main }}>
                      {isLive ? 'Live Score' : 'Predict Now'} <ChevronRight size={14} />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Hot Contests */}
      <div>
        <h2 className="text-base font-semibold text-white mb-3">Hot Contests</h2>
        <div className="space-y-2">
          {[
            { name: 'Free Contest', fee: 0, pool: 1000, tag: 'FREE' },
            { name: 'Mini Contest', fee: 100, pool: 5000, tag: 'Popular' },
            { name: 'Mega Contest', fee: 500, pool: 25000, tag: 'Mega' },
          ].map((c, i) => (
            <div data-testid={`contest-card-${i}`} key={i} className="flex items-center justify-between p-3.5 rounded-xl" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
              <div>
                <div className="text-sm font-semibold text-white">{c.name}</div>
                <div className="flex items-center gap-3 mt-1">
                  <span className="text-xs" style={{ color: COLORS.text.secondary }}>Entry: {c.fee === 0 ? 'FREE' : `${c.fee} coins`}</span>
                  <span className="text-xs" style={{ color: COLORS.accent.gold }}>Pool: {c.pool.toLocaleString()}</span>
                </div>
              </div>
              <button className="px-3 py-1.5 rounded-lg text-xs font-bold" style={{ background: c.fee === 0 ? COLORS.success.bg : COLORS.primary.gradient, color: c.fee === 0 ? COLORS.success.main : '#fff' }}>
                {c.tag}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
