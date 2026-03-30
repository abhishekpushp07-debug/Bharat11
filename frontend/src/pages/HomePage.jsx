import { useState, useEffect, useCallback, useRef } from 'react';
import { useAuthStore } from '../stores/authStore';
import apiClient from '../api/client';
import { COLORS } from '../constants/design';
import { TEAM_COLORS, TEAM_CARD_IMAGES, getTeamLogo, getTeamGradient, getTeamCardImage, normalizeTeam } from '../constants/teams';
import { Coins, ChevronRight, Clock, Trophy, Zap, RefreshCw, Activity, ChevronLeft } from 'lucide-react';

const getTeamGrad = (short) => getTeamGradient(short);

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

function Countdown({ time }) {
  const remaining = useCountdown(time);
  return <span>{remaining}</span>;
}

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
          <div className="space-y-1.5"><div className="h-3 w-8 rounded" style={{ background: COLORS.background.tertiary }} /></div>
        </div>
        <div className="h-6 w-8 rounded-lg" style={{ background: COLORS.background.tertiary }} />
        <div className="flex items-center gap-3 flex-row-reverse">
          <div className="w-11 h-11 rounded-xl" style={{ background: COLORS.background.tertiary }} />
          <div className="space-y-1.5"><div className="h-3 w-8 rounded" style={{ background: COLORS.background.tertiary }} /></div>
        </div>
      </div>
    </div>
  );
}

export default function HomePage({ onMatchClick }) {
  const { user } = useAuthStore();
  const [matches, setMatches] = useState([]);
  const [hotContests, setHotContests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [liveTicker, setLiveTicker] = useState([]);
  const [pointsTable, setPointsTable] = useState([]);
  const [showFullTable, setShowFullTable] = useState(false);
  const refreshTimer = useRef(null);
  const tickerRef = useRef(null);

  const fetchAll = useCallback(async (showRefresh = false) => {
    if (showRefresh) setRefreshing(true);
    try {
      const [matchRes, contestRes, tickerRes, ptRes] = await Promise.allSettled([
        apiClient.get('/matches?limit=10'),
        apiClient.get('/contests?limit=5'),
        apiClient.get('/cricket/live-ticker'),
        apiClient.get('/cricket/ipl/points-table'),
      ]);
      if (matchRes.status === 'fulfilled') setMatches(matchRes.value.data.matches || []);
      if (contestRes.status === 'fulfilled') setHotContests(contestRes.value.data.contests || []);
      if (tickerRes.status === 'fulfilled') setLiveTicker(tickerRes.value.data.scores || []);
      if (ptRes.status === 'fulfilled') setPointsTable(ptRes.value.data.teams || []);
    } catch (_) {}
    finally { setLoading(false); setRefreshing(false); }
  }, []);

  useEffect(() => {
    fetchAll();
    refreshTimer.current = setInterval(() => fetchAll(), 30000);
    return () => clearInterval(refreshTimer.current);
  }, [fetchAll]);

  const liveMatches = matches.filter(m => m.status === 'live');
  const upcomingMatches = matches.filter(m => m.status === 'upcoming');
  const completedMatches = matches.filter(m => m.status === 'completed');

  // Sort points table by wins desc
  const sortedTable = [...pointsTable].sort((a, b) => b.wins - a.wins || a.loss - b.loss);

  return (
    <div data-testid="home-page" className="pb-4 space-y-5">
      {/* Greeting + Balance */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Hey, {user?.username || 'Player'}!</h1>
          <p className="text-xs mt-0.5" style={{ color: COLORS.text.secondary }}>Predict & Win Virtual Coins</p>
        </div>
        <div className="flex items-center gap-2">
          <button data-testid="refresh-btn" onClick={() => fetchAll(true)} disabled={refreshing}
            className="p-2 rounded-full" style={{ background: COLORS.background.card }}>
            <RefreshCw size={14} color={COLORS.text.secondary} className={refreshing ? 'animate-spin' : ''} />
          </button>
          <div data-testid="home-balance" className="flex items-center gap-1.5 px-3 py-1.5 rounded-full" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
            <Coins size={14} color="#FFD700" />
            <span className="text-sm font-bold text-white" style={{ fontFamily: "'Rajdhani', sans-serif" }}>{(user?.coins_balance || 0).toLocaleString()}</span>
          </div>
        </div>
      </div>

      {/* Dual Points Banner */}
      <div data-testid="dual-banner" className="grid grid-cols-2 gap-2.5">
        <div className="p-3.5 rounded-2xl relative overflow-hidden"
          style={{ background: 'linear-gradient(135deg, #10b981, #059669)', boxShadow: '0 4px 20px #10b98133' }}>
          <div className="absolute top-0 right-0 w-16 h-16 rounded-full opacity-10" style={{ background: '#fff', transform: 'translate(30%, -30%)' }} />
          <div className="text-[9px] font-bold uppercase tracking-wider" style={{ color: '#ffffffaa' }}>Fantasy Points</div>
          <div className="text-2xl font-black text-white mt-0.5" style={{ fontFamily: "'Rajdhani', sans-serif" }}>
            {(user?.total_fantasy_points || 0).toLocaleString()}
          </div>
          <div className="text-[9px] mt-0.5" style={{ color: '#ffffffaa' }}>From correct predictions</div>
        </div>
        <div className="p-3.5 rounded-2xl relative overflow-hidden"
          style={{ background: 'linear-gradient(135deg, #f59e0b, #d97706)', boxShadow: '0 4px 20px #f59e0b33' }}>
          <div className="absolute top-0 right-0 w-16 h-16 rounded-full opacity-10" style={{ background: '#fff', transform: 'translate(30%, -30%)' }} />
          <div className="text-[9px] font-bold uppercase tracking-wider" style={{ color: '#ffffffaa' }}>Contest Coins</div>
          <div className="text-2xl font-black text-white mt-0.5" style={{ fontFamily: "'Rajdhani', sans-serif" }}>
            {(user?.coins_balance || 0).toLocaleString()}
          </div>
          <div className="text-[9px] mt-0.5" style={{ color: '#ffffffaa' }}>Win by playing contests</div>
        </div>
      </div>

      {/* Live Score Ticker (horizontal scroll) */}
      {liveTicker.length > 0 && (
        <div data-testid="live-ticker">
          <div className="flex items-center gap-2 mb-2">
            <Activity size={14} color={COLORS.primary.main} className="animate-pulse" />
            <span className="text-xs font-bold" style={{ color: COLORS.primary.main }}>IPL LIVE</span>
            <span className="text-[10px]" style={{ color: COLORS.text.tertiary }}>{liveTicker.length} matches</span>
          </div>
          <div ref={tickerRef} className="flex gap-2.5 overflow-x-auto pb-2 scrollbar-hide" style={{ scrollbarWidth: 'none' }}>
            {liveTicker.map((s, i) => {
              const t1Short = (s.t1.match(/\[(\w+)\]/)?.[1]) || s.t1.split(' ')[0];
              const t2Short = (s.t2.match(/\[(\w+)\]/)?.[1]) || s.t2.split(' ')[0];
              const isLive = s.ms === 'result' || s.t1s;
              return (
                <div key={s.id || i} data-testid={`ticker-${i}`}
                  className="shrink-0 rounded-xl p-2.5 min-w-[170px]"
                  style={{ background: COLORS.background.card, border: `1px solid ${s.ms === 'result' ? COLORS.success.main + '33' : COLORS.border.light}` }}>
                  <div className="flex items-center justify-between mb-1.5">
                    <div className="flex items-center gap-1.5">
                      {s.t1img && <img src={s.t1img} alt="" className="w-4 h-4 rounded-sm" />}
                      <span className="text-[10px] font-bold text-white">{t1Short}</span>
                    </div>
                    {s.t1s && <span className="text-[10px] font-bold" style={{ color: COLORS.primary.main }}>{s.t1s}</span>}
                  </div>
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-1.5">
                      {s.t2img && <img src={s.t2img} alt="" className="w-4 h-4 rounded-sm" />}
                      <span className="text-[10px] font-bold text-white">{t2Short}</span>
                    </div>
                    {s.t2s && <span className="text-[10px] font-bold" style={{ color: COLORS.primary.main }}>{s.t2s}</span>}
                  </div>
                  <div className="text-[8px] truncate" style={{ color: s.ms === 'result' ? COLORS.success.main : s.ms === 'live' ? COLORS.primary.main : COLORS.text.tertiary }}>
                    {s.status}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Live Matches */}
      {liveMatches.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <div className="w-2 h-2 rounded-full animate-pulse" style={{ background: COLORS.primary.main }} />
            <h2 className="text-base font-semibold text-white">Live Now</h2>
          </div>
          <div className="space-y-3">
            {liveMatches.map(match => <MatchCard key={match.id} match={match} isLive onClick={onMatchClick} />)}
          </div>
        </div>
      )}

      {/* IPL Points Table */}
      {sortedTable.length > 0 && (
        <div data-testid="ipl-points-table">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Trophy size={16} color={COLORS.accent.gold} />
              <h2 className="text-base font-semibold text-white">IPL 2026 Standings</h2>
            </div>
            <button onClick={() => setShowFullTable(f => !f)} className="text-[10px] font-semibold" style={{ color: COLORS.primary.main }}>
              {showFullTable ? 'Show Less' : 'View All'}
            </button>
          </div>
          <div className="rounded-xl overflow-hidden" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
            {/* Header */}
            <div className="flex items-center px-3 py-2" style={{ background: COLORS.background.tertiary }}>
              <span className="w-6 text-[9px] font-bold" style={{ color: COLORS.text.tertiary }}>#</span>
              <span className="flex-1 text-[9px] font-bold" style={{ color: COLORS.text.tertiary }}>TEAM</span>
              <span className="w-7 text-center text-[9px] font-bold" style={{ color: COLORS.text.tertiary }}>P</span>
              <span className="w-7 text-center text-[9px] font-bold" style={{ color: COLORS.success.main }}>W</span>
              <span className="w-7 text-center text-[9px] font-bold" style={{ color: COLORS.error.main }}>L</span>
              <span className="w-7 text-center text-[9px] font-bold" style={{ color: COLORS.text.tertiary }}>NR</span>
            </div>
            {(showFullTable ? sortedTable : sortedTable.slice(0, 4)).map((team, i) => (
              <div key={team.shortname || i} data-testid={`pt-row-${team.shortname}`}
                className="flex items-center px-3 py-2"
                style={{ borderTop: `1px solid ${COLORS.border.light}`, background: i < 4 ? `${COLORS.success.main}06` : 'transparent' }}>
                <span className="w-6 text-[10px] font-bold" style={{ color: i < 4 ? COLORS.success.main : COLORS.text.tertiary }}>{i + 1}</span>
                <div className="flex-1 flex items-center gap-2">
                  {team.img && <img src={team.img} alt={team.shortname} className="w-5 h-5 rounded-sm" />}
                  <span className="text-xs font-semibold text-white">{team.shortname}</span>
                </div>
                <span className="w-7 text-center text-xs" style={{ color: COLORS.text.secondary }}>{team.matches}</span>
                <span className="w-7 text-center text-xs font-bold" style={{ color: COLORS.success.main }}>{team.wins}</span>
                <span className="w-7 text-center text-xs" style={{ color: COLORS.error.main }}>{team.loss}</span>
                <span className="w-7 text-center text-xs" style={{ color: COLORS.text.tertiary }}>{team.nr}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upcoming Matches */}
      {loading ? (
        <div className="space-y-3"><MatchSkeleton /><MatchSkeleton /></div>
      ) : upcomingMatches.length > 0 ? (
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-base font-semibold text-white">Upcoming Matches</h2>
            <span className="text-xs" style={{ color: COLORS.text.tertiary }}>{upcomingMatches.length} matches</span>
          </div>
          <div className="space-y-3">
            {upcomingMatches.map(match => <MatchCard key={match.id} match={match} onClick={onMatchClick} />)}
          </div>
        </div>
      ) : liveMatches.length === 0 ? (
        <div className="text-center py-10 rounded-2xl" style={{ background: COLORS.background.card }}>
          <Trophy size={36} color={COLORS.text.tertiary} className="mx-auto mb-2" />
          <p className="text-sm" style={{ color: COLORS.text.secondary }}>No matches available right now</p>
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
                <div className="px-3 py-1.5 rounded-lg text-xs font-bold" style={{ background: c.entry_fee === 0 ? COLORS.success.bg : COLORS.primary.gradient, color: c.entry_fee === 0 ? COLORS.success.main : '#fff' }}>
                  {c.entry_fee === 0 ? 'FREE' : `${c.entry_fee}`}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Completed */}
      {completedMatches.length > 0 && (
        <div>
          <h2 className="text-base font-semibold mb-3" style={{ color: COLORS.text.tertiary }}>Completed</h2>
          <div className="space-y-2">
            {completedMatches.slice(0, 3).map(match => <MatchCard key={match.id} match={match} onClick={onMatchClick} isCompleted />)}
          </div>
        </div>
      )}
    </div>
  );
}

function MatchCard({ match, isLive, isCompleted, onClick }) {
  const teamA = match.team_a || {};
  const teamB = match.team_b || {};
  const score = match.live_score;
  const scores = score?.scores || [];

  return (
    <div data-testid={`match-card-${match.id}`}
      className="rounded-2xl overflow-hidden cursor-pointer transition-transform active:scale-[0.98]"
      style={{ background: COLORS.background.card, border: `1px solid ${isLive ? COLORS.primary.main + '44' : COLORS.border.light}`, boxShadow: isLive ? `0 0 12px ${COLORS.primary.main}22` : 'none', opacity: isCompleted ? 0.7 : 1 }}
      onClick={() => onClick?.(match)}>
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

      <div className="px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-xl flex items-center justify-center text-xs font-black text-white overflow-hidden" style={{ background: getTeamGrad(teamA.short_name) }}>
            {getTeamLogo(teamA.short_name) ? <img src={getTeamLogo(teamA.short_name)} alt={teamA.short_name} className="w-8 h-8 object-contain" /> : (teamA.short_name || '?')}
          </div>
          <div>
            <div className="text-sm font-bold text-white">{teamA.short_name || 'TBD'}</div>
            {scores[0] ? (
              <div className="text-xs font-semibold" style={{ color: COLORS.primary.main }}>{scores[0].runs}/{scores[0].wickets} ({scores[0].overs})</div>
            ) : (
              <div className="text-xs" style={{ color: COLORS.text.tertiary }}>{teamA.name || ''}</div>
            )}
          </div>
        </div>

        <div className="px-3 py-1 rounded-lg text-xs font-bold" style={{ background: isLive ? COLORS.primary.gradient : `${COLORS.primary.main}22`, color: isLive ? '#fff' : COLORS.primary.main }}>
          VS
        </div>

        <div className="flex items-center gap-3 flex-row-reverse">
          <div className="w-11 h-11 rounded-xl flex items-center justify-center text-xs font-black text-white overflow-hidden" style={{ background: getTeamGrad(teamB.short_name) }}>
            {getTeamLogo(teamB.short_name) ? <img src={getTeamLogo(teamB.short_name)} alt={teamB.short_name} className="w-8 h-8 object-contain" /> : (teamB.short_name || '?')}
          </div>
          <div className="text-right">
            <div className="text-sm font-bold text-white">{teamB.short_name || 'TBD'}</div>
            {scores[1] ? (
              <div className="text-xs font-semibold" style={{ color: COLORS.primary.main }}>{scores[1].runs}/{scores[1].wickets} ({scores[1].overs})</div>
            ) : (
              <div className="text-xs" style={{ color: COLORS.text.tertiary }}>{teamB.name || ''}</div>
            )}
          </div>
        </div>
      </div>

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
