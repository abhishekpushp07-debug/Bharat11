import { useState, useEffect, useCallback, useRef } from 'react';
import { useAuthStore } from '../stores/authStore';
import apiClient from '../api/client';
import { COLORS } from '../constants/design';
import { Coins, ChevronRight, Clock, Trophy, Zap, RefreshCw } from 'lucide-react';

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

// Live countdown hook
function useCountdown(targetTime) {
  const [remaining, setRemaining] = useState('');

  useEffect(() => {
    const update = () => {
      const diff = new Date(targetTime) - new Date();
      if (diff <= 0) { setRemaining('Starting...'); return; }
      const d = Math.floor(diff / 86400000);
      const h = Math.floor((diff % 86400000) / 3600000);
      const m = Math.floor((diff % 3600000) / 60000);
      const s = Math.floor((diff % 60000) / 1000);
      if (d > 0) setRemaining(`${d}d ${h}h`);
      else if (h > 0) setRemaining(`${h}h ${m}m`);
      else setRemaining(`${m}m ${s}s`);
    };
    update();
    const interval = setInterval(update, 1000);
    return () => clearInterval(interval);
  }, [targetTime]);

  return remaining;
}

// Countdown display component
function Countdown({ time }) {
  const remaining = useCountdown(time);
  return <span>{remaining}</span>;
}

// Skeleton loader for match cards
function MatchSkeleton() {
  return (
    <div className="rounded-2xl overflow-hidden animate-pulse" style={{ background: COLORS.background.card }}>
      <div className="px-4 py-2.5 flex justify-between" style={{ borderBottom: `1px solid ${COLORS.border.light}` }}>
        <div className="h-3 w-24 rounded" style={{ background: COLORS.background.tertiary }} />
        <div className="h-3 w-16 rounded" style={{ background: COLORS.background.tertiary }} />
      </div>
      <div className="px-4 py-5 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-xl" style={{ background: COLORS.background.tertiary }} />
          <div className="space-y-1.5"><div className="h-3 w-8 rounded" style={{ background: COLORS.background.tertiary }} /><div className="h-2 w-16 rounded" style={{ background: COLORS.background.tertiary }} /></div>
        </div>
        <div className="h-6 w-8 rounded-lg" style={{ background: COLORS.background.tertiary }} />
        <div className="flex items-center gap-3 flex-row-reverse">
          <div className="w-11 h-11 rounded-xl" style={{ background: COLORS.background.tertiary }} />
          <div className="space-y-1.5"><div className="h-3 w-8 rounded" style={{ background: COLORS.background.tertiary }} /><div className="h-2 w-16 rounded" style={{ background: COLORS.background.tertiary }} /></div>
        </div>
      </div>
      <div className="px-4 py-2.5" style={{ background: COLORS.background.tertiary }}><div className="h-3 w-full rounded" style={{ background: COLORS.background.card }} /></div>
    </div>
  );
}

export default function HomePage({ onMatchClick }) {
  const { user } = useAuthStore();
  const [matches, setMatches] = useState([]);
  const [hotContests, setHotContests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const refreshTimer = useRef(null);

  const fetchAll = useCallback(async (showRefresh = false) => {
    if (showRefresh) setRefreshing(true);
    try {
      const [matchRes, contestRes] = await Promise.allSettled([
        apiClient.get('/matches?limit=10'),
        apiClient.get('/contests?limit=5')
      ]);
      if (matchRes.status === 'fulfilled') setMatches(matchRes.value.data.matches || []);
      if (contestRes.status === 'fulfilled') setHotContests(contestRes.value.data.contests || []);
    } catch (_) { /* silent */ }
    finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchAll();
    // Auto-refresh every 30s for live matches
    refreshTimer.current = setInterval(() => fetchAll(), 30000);
    return () => clearInterval(refreshTimer.current);
  }, [fetchAll]);

  const liveMatches = matches.filter(m => m.status === 'live');
  const upcomingMatches = matches.filter(m => m.status === 'upcoming');
  const completedMatches = matches.filter(m => m.status === 'completed');

  return (
    <div data-testid="home-page" className="pb-4 space-y-5">
      {/* Greeting + Balance */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Hey, {user?.username || 'Player'}!</h1>
          <p className="text-xs mt-0.5" style={{ color: COLORS.text.secondary }}>Predict & Win Virtual Coins</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            data-testid="refresh-btn"
            onClick={() => fetchAll(true)}
            disabled={refreshing}
            className="p-2 rounded-full"
            style={{ background: COLORS.background.card }}>
            <RefreshCw size={14} color={COLORS.text.secondary} className={refreshing ? 'animate-spin' : ''} />
          </button>
          <div data-testid="home-balance" className="flex items-center gap-1.5 px-3 py-1.5 rounded-full" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
            <Coins size={14} color="#FFD700" />
            <span className="text-sm font-bold text-white" style={{ fontFamily: "'Rajdhani', sans-serif" }}>{(user?.coins_balance || 0).toLocaleString()}</span>
          </div>
        </div>
      </div>

      {/* Live Matches (Priority Section) */}
      {liveMatches.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <div className="w-2 h-2 rounded-full animate-pulse" style={{ background: COLORS.primary.main }} />
            <h2 className="text-base font-semibold text-white">Live Now</h2>
          </div>
          <div className="space-y-3">
            {liveMatches.map(match => (
              <MatchCard key={match.id} match={match} isLive onClick={onMatchClick} />
            ))}
          </div>
        </div>
      )}

      {/* Upcoming Matches */}
      {loading ? (
        <div className="space-y-3">
          <MatchSkeleton />
          <MatchSkeleton />
        </div>
      ) : upcomingMatches.length > 0 ? (
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-base font-semibold text-white">Upcoming Matches</h2>
            <span className="text-xs" style={{ color: COLORS.text.tertiary }}>{upcomingMatches.length} matches</span>
          </div>
          <div className="space-y-3">
            {upcomingMatches.map(match => (
              <MatchCard key={match.id} match={match} onClick={onMatchClick} />
            ))}
          </div>
        </div>
      ) : liveMatches.length === 0 ? (
        <div className="text-center py-10 rounded-2xl" style={{ background: COLORS.background.card }}>
          <Trophy size={36} color={COLORS.text.tertiary} className="mx-auto mb-2" />
          <p className="text-sm" style={{ color: COLORS.text.secondary }}>No matches available right now</p>
          <p className="text-xs mt-1" style={{ color: COLORS.text.tertiary }}>Check back soon!</p>
        </div>
      ) : null}

      {/* Hot Contests */}
      {hotContests.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Zap size={16} color={COLORS.accent.gold} />
            <h2 className="text-base font-semibold text-white">Hot Contests</h2>
          </div>
          <div className="space-y-2">
            {hotContests.filter(c => c.status === 'open').slice(0, 4).map((c, i) => (
              <div data-testid={`contest-card-${i}`} key={c.id} className="flex items-center justify-between p-3.5 rounded-xl" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
                <div>
                  <div className="text-sm font-semibold text-white">{c.name}</div>
                  <div className="flex items-center gap-3 mt-1">
                    <span className="text-xs" style={{ color: COLORS.text.secondary }}>Entry: {c.entry_fee === 0 ? 'FREE' : `${c.entry_fee} coins`}</span>
                    <span className="text-xs" style={{ color: COLORS.accent.gold }}>Pool: {(c.prize_pool || 0).toLocaleString()}</span>
                  </div>
                </div>
                <div className="px-3 py-1.5 rounded-lg text-xs font-bold" style={{
                  background: c.entry_fee === 0 ? COLORS.success.bg : COLORS.primary.gradient,
                  color: c.entry_fee === 0 ? COLORS.success.main : '#fff'
                }}>
                  {c.entry_fee === 0 ? 'FREE' : `${c.entry_fee}`}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Completed (Collapsible) */}
      {completedMatches.length > 0 && (
        <div>
          <h2 className="text-base font-semibold mb-3" style={{ color: COLORS.text.tertiary }}>Completed</h2>
          <div className="space-y-2">
            {completedMatches.slice(0, 3).map(match => (
              <MatchCard key={match.id} match={match} onClick={onMatchClick} isCompleted />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// Match Card Component
function MatchCard({ match, isLive, isCompleted, onClick }) {
  const teamA = match.team_a || {};
  const teamB = match.team_b || {};
  const score = match.live_score;

  return (
    <div
      data-testid={`match-card-${match.id}`}
      className="rounded-2xl overflow-hidden cursor-pointer transition-transform active:scale-[0.98]"
      style={{
        background: COLORS.background.card,
        border: `1px solid ${isLive ? COLORS.primary.main + '44' : COLORS.border.light}`,
        boxShadow: isLive ? `0 0 12px ${COLORS.primary.main}22` : 'none',
        opacity: isCompleted ? 0.7 : 1
      }}
      onClick={() => onClick?.(match)}>
      {/* Header */}
      <div className="px-4 py-2.5 flex items-center justify-between" style={{ borderBottom: `1px solid ${COLORS.border.light}` }}>
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium" style={{ color: COLORS.text.secondary }}>{match.tournament || match.venue || 'Cricket'}</span>
          {isLive && <span className="px-1.5 py-0.5 rounded text-[10px] font-bold text-white animate-pulse" style={{ background: COLORS.primary.main }}>LIVE</span>}
          {isCompleted && <span className="text-[10px] font-semibold" style={{ color: COLORS.text.tertiary }}>ENDED</span>}
        </div>
        <div className="flex items-center gap-1.5">
          <Clock size={12} color={isLive ? COLORS.primary.main : COLORS.warning.main} />
          <span className="text-xs font-semibold" style={{ color: isLive ? COLORS.primary.main : COLORS.warning.main }}>
            {isLive ? 'In Progress' : isCompleted ? 'Finished' : <Countdown time={match.start_time} />}
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
        <div className="flex items-center gap-1">
          <Trophy size={12} color={COLORS.accent.gold} />
          <span className="text-xs" style={{ color: COLORS.text.secondary }}>{match.venue || match.tournament || ''}</span>
        </div>
        <div className="flex items-center gap-1 text-xs font-semibold" style={{ color: COLORS.primary.main }}>
          {isLive ? 'Live Score' : isCompleted ? 'View Results' : 'Predict Now'} <ChevronRight size={14} />
        </div>
      </div>
    </div>
  );
}
