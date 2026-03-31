import { useState, useEffect, useCallback, useRef } from 'react';
import { useAuthStore } from '../stores/authStore';
import { useSocketStore } from '../stores/socketStore';
import apiClient from '../api/client';
import { COLORS } from '../constants/design';
import { TEAM_COLORS, TEAM_CARD_IMAGES, getTeamLogo, getTeamGradient, getTeamCardImage, normalizeTeam } from '../constants/teams';
import { Coins, ChevronRight, Clock, Trophy, Zap, RefreshCw, Activity, ChevronLeft, MapPin, Wifi, WifiOff, Bell, BellOff, X, Calendar, Award, Users, BarChart3, Loader2 } from 'lucide-react';
import PredictionBadge from '../components/PredictionBadge';
import StreakBanner from '../components/StreakBanner';
import { usePushNotifications } from '../hooks/usePushNotifications';

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
  const { on, off, isConnected } = useSocketStore();
  const { isSupported: pushSupported, isSubscribed: pushSubscribed, subscribe: subscribePush } = usePushNotifications();
  const [matches, setMatches] = useState([]);
  const [hotContests, setHotContests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [liveTicker, setLiveTicker] = useState([]);
  const [pointsTable, setPointsTable] = useState([]);
  const [showFullTable, setShowFullTable] = useState(false);
  const [selectedTeam, setSelectedTeam] = useState(null);
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

  // Socket.IO: Live score updates
  useEffect(() => {
    const handleLiveScore = (data) => {
      setMatches(prev => prev.map(m => {
        if (m.id === data.match_id) {
          return {
            ...m,
            live_score: {
              scores: data.scores || m.live_score?.scores,
              status_text: data.status_text || m.live_score?.status_text,
              match_winner: data.match_winner || m.live_score?.match_winner,
              updated_at: data.updated_at,
            }
          };
        }
        return m;
      }));
    };

    const handleContestCreated = (data) => {
      // Refresh contests list when a new one is auto-created
      fetchAll();
    };

    const handleContestFinalized = (data) => {
      // Refresh to show updated results
      fetchAll();
    };

    on('live_score', handleLiveScore);
    on('contest_created', handleContestCreated);
    on('contest_finalized', handleContestFinalized);

    return () => {
      off('live_score', handleLiveScore);
      off('contest_created', handleContestCreated);
      off('contest_finalized', handleContestFinalized);
    };
  }, [on, off, fetchAll]);

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
          {/* Live connection indicator */}
          <div data-testid="socket-status" className="flex items-center gap-1 px-2 py-1 rounded-full" style={{
            background: isConnected ? 'rgba(34,197,94,0.12)' : 'rgba(239,68,68,0.12)',
            border: `1px solid ${isConnected ? 'rgba(34,197,94,0.2)' : 'rgba(239,68,68,0.2)'}`,
          }}>
            {isConnected ? <Wifi size={9} color="#22c55e" /> : <WifiOff size={9} color="#ef4444" />}
            <span className="text-[8px] font-bold" style={{ color: isConnected ? '#22c55e' : '#ef4444' }}>
              {isConnected ? 'LIVE' : 'OFFLINE'}
            </span>
          </div>
          {/* Push notification toggle */}
          {pushSupported && (
            <button data-testid="push-toggle" onClick={subscribePush}
              className="p-1.5 rounded-full" style={{ background: pushSubscribed ? 'rgba(34,197,94,0.12)' : COLORS.background.card }}>
              {pushSubscribed
                ? <Bell size={12} color="#22c55e" />
                : <BellOff size={12} color={COLORS.text.tertiary} />}
            </button>
          )}
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

      {/* Prediction Accuracy Badge */}
      <PredictionBadge />

      {/* Prediction Streak */}
      <StreakBanner />

      {/* Dual Points Banner - Vibrant */}
      <div data-testid="dual-banner" className="grid grid-cols-2 gap-2.5">
        <div className="p-3.5 rounded-2xl relative overflow-hidden animate-gradient-shift"
          style={{ background: 'linear-gradient(135deg, #1a3a8a, #1e40af, #2563eb, #1a3a8a)', backgroundSize: '200% 200%', boxShadow: '0 4px 24px rgba(30,64,175,0.3)' }}>
          <div className="absolute -top-4 -right-4 w-20 h-20 rounded-full opacity-20" style={{ background: 'radial-gradient(circle, #60a5fa, transparent)' }} />
          <div className="absolute bottom-0 left-0 w-full h-[1px] opacity-30" style={{ background: 'linear-gradient(90deg, transparent, #60a5fa, transparent)' }} />
          <div className="relative">
            <div className="text-[9px] font-black uppercase tracking-[0.15em]" style={{ color: '#ffffffcc' }}>Fantasy Points</div>
            <div className="text-2xl font-black text-white mt-0.5 animate-count" style={{ fontFamily: "'Rajdhani', sans-serif" }}>
              {(user?.total_fantasy_points || 0).toLocaleString()}
            </div>
            <div className="text-[9px] mt-0.5" style={{ color: '#ffffff88' }}>From correct predictions</div>
          </div>
        </div>
        <div className="p-3.5 rounded-2xl relative overflow-hidden animate-gradient-shift"
          style={{ background: 'linear-gradient(135deg, #f59e0b, #d97706, #f59e0b)', backgroundSize: '200% 200%', boxShadow: '0 4px 24px #f59e0b33', animationDelay: '1.5s' }}>
          <div className="absolute -top-4 -right-4 w-20 h-20 rounded-full opacity-20" style={{ background: 'radial-gradient(circle, #fff, transparent)' }} />
          <div className="absolute bottom-0 left-0 w-full h-[1px] opacity-20" style={{ background: 'linear-gradient(90deg, transparent, #fff, transparent)' }} />
          <div className="relative">
            <div className="text-[9px] font-black uppercase tracking-[0.15em]" style={{ color: '#ffffffbb' }}>Contest Coins</div>
            <div className="text-2xl font-black text-white mt-0.5 animate-count" style={{ fontFamily: "'Rajdhani', sans-serif" }}>
              {(user?.coins_balance || 0).toLocaleString()}
            </div>
            <div className="text-[9px] mt-0.5" style={{ color: '#ffffff88' }}>Win by playing contests</div>
          </div>
        </div>
      </div>

      {/* Live Score Ticker (horizontal scroll) */}
      {liveTicker.length > 0 && (
        <div data-testid="live-ticker">
          <div className="flex items-center gap-2 mb-2">
            <div className="relative">
              <Activity size={14} color="#FF3B3B" className="animate-pulse" />
              <div className="absolute inset-0 animate-ping" style={{ opacity: 0.3 }}>
                <Activity size={14} color="#FF3B3B" />
              </div>
            </div>
            <span className="text-xs font-black tracking-wider" style={{ color: '#FF3B3B', textShadow: '0 0 8px rgba(255,59,59,0.4)' }}>IPL LIVE</span>
            <div className="h-3 w-px" style={{ background: 'rgba(255,255,255,0.1)' }} />
            <span className="text-[10px] font-bold" style={{ color: COLORS.text.secondary }}>{liveTicker.length} matches</span>
          </div>
          <div ref={tickerRef} className="flex gap-2.5 overflow-x-auto pb-2 scrollbar-hide" style={{ scrollbarWidth: 'none' }}>
            {liveTicker.map((s, i) => {
              const t1Short = (s.t1.match(/\[(\w+)\]/)?.[1]) || s.t1.split(' ')[0];
              const t2Short = (s.t2.match(/\[(\w+)\]/)?.[1]) || s.t2.split(' ')[0];
              const t1Norm = normalizeTeam(t1Short);
              const t2Norm = normalizeTeam(t2Short);
              const t1Color = (TEAM_COLORS[t1Norm] || { primary: '#888' }).primary;
              const t2Color = (TEAM_COLORS[t2Norm] || { primary: '#888' }).primary;
              const isLiveMatch = s.ms === 'live';
              const isResult = s.ms === 'result';
              return (
                <div key={s.id || i} data-testid={`ticker-${i}`}
                  className="shrink-0 rounded-xl p-2.5 min-w-[175px] relative overflow-hidden transition-all duration-300"
                  style={{
                    background: isLiveMatch
                      ? `linear-gradient(135deg, rgba(220,40,60,0.12), rgba(180,20,40,0.06), rgba(0,0,0,0.9))`
                      : isResult
                        ? `linear-gradient(135deg, rgba(34,197,94,0.08), rgba(0,0,0,0.95))`
                        : `linear-gradient(135deg, ${t1Color}12, #0d0d14, ${t2Color}08)`,
                    border: `1px solid ${isLiveMatch ? 'rgba(255,50,50,0.4)' : isResult ? 'rgba(34,197,94,0.25)' : 'rgba(255,255,255,0.1)'}`,
                    boxShadow: isLiveMatch
                      ? '0 0 20px rgba(255,50,50,0.12), inset 0 0 20px rgba(255,50,50,0.03)'
                      : isResult ? '0 0 10px rgba(34,197,94,0.08)' : 'none',
                  }}>
                  {isLiveMatch && (
                    <div className="absolute top-0 left-0 right-0 h-px" style={{
                      background: 'linear-gradient(90deg, transparent, rgba(255,50,50,0.6), transparent)',
                    }} />
                  )}
                  <div className="flex items-center justify-between mb-1.5">
                    <div className="flex items-center gap-1.5">
                      {s.t1img && <img src={s.t1img} alt="" className="w-4 h-4 rounded-sm" style={{ filter: 'drop-shadow(0 0 2px rgba(255,255,255,0.3))' }} />}
                      <span className="text-[10px] font-black text-white">{t1Norm}</span>
                    </div>
                    {s.t1s && <span className="text-[10px] font-black" style={{ color: t1Color, textShadow: `0 0 6px ${t1Color}44` }}>{s.t1s}</span>}
                  </div>
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-1.5">
                      {s.t2img && <img src={s.t2img} alt="" className="w-4 h-4 rounded-sm" style={{ filter: 'drop-shadow(0 0 2px rgba(255,255,255,0.3))' }} />}
                      <span className="text-[10px] font-black text-white">{t2Norm}</span>
                    </div>
                    {s.t2s && <span className="text-[10px] font-black" style={{ color: t2Color, textShadow: `0 0 6px ${t2Color}44` }}>{s.t2s}</span>}
                  </div>
                  <div className="text-[8px] truncate font-bold" style={{
                    color: isResult ? '#4ade80' : isLiveMatch ? '#FF5555' : COLORS.text.tertiary,
                    textShadow: isResult ? '0 0 4px rgba(34,197,94,0.3)' : isLiveMatch ? '0 0 4px rgba(255,50,50,0.3)' : 'none',
                  }}>
                    {s.status}
                  </div>
                  {isLiveMatch && (
                    <div className="absolute top-1.5 right-1.5 flex items-center gap-1 px-1.5 py-0.5 rounded-full" style={{ background: 'rgba(255,50,50,0.2)' }}>
                      <div className="w-1 h-1 rounded-full bg-red-500 animate-pulse" />
                      <span className="text-[7px] font-black text-red-400">LIVE</span>
                    </div>
                  )}
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
              <h2 className="text-base font-black text-white tracking-tight">IPL 2026 Standings</h2>
            </div>
            <button onClick={() => setShowFullTable(f => !f)} className="text-[10px] font-semibold" style={{ color: COLORS.primary.main }}>
              {showFullTable ? 'Show Less' : 'View All'}
            </button>
          </div>
          <div className="rounded-xl overflow-hidden" style={{ border: `1px solid rgba(255,255,255,0.06)` }}>
            {/* Header */}
            <div className="flex items-center px-3 py-2" style={{ background: 'rgba(255,255,255,0.04)' }}>
              <span className="w-6 text-[9px] font-bold" style={{ color: COLORS.text.tertiary }}>#</span>
              <span className="flex-1 text-[9px] font-bold" style={{ color: COLORS.text.tertiary }}>TEAM</span>
              <span className="w-7 text-center text-[9px] font-bold" style={{ color: COLORS.text.tertiary }}>P</span>
              <span className="w-7 text-center text-[9px] font-bold" style={{ color: '#4ade80' }}>W</span>
              <span className="w-7 text-center text-[9px] font-bold" style={{ color: '#f87171' }}>L</span>
              <span className="w-7 text-center text-[9px] font-bold" style={{ color: COLORS.text.tertiary }}>NR</span>
              <span className="w-6"></span>
            </div>
            {(showFullTable ? sortedTable : sortedTable.slice(0, 4)).map((team, i) => {
              const teamShort = normalizeTeam((team.shortname || '').toUpperCase());
              const tc = TEAM_COLORS[teamShort] || TEAM_COLORS[(team.shortname || '').toUpperCase()] || { primary: '#666', secondary: '#444' };
              const teamPrimary = tc.primary;
              const teamSecondary = tc.secondary;
              return (
              <div key={team.shortname || i} data-testid={`pt-row-${team.shortname}`}
                className="flex items-center px-3 py-2.5 relative overflow-hidden cursor-pointer transition-all duration-200 active:scale-[0.98]"
                onClick={() => setSelectedTeam({ shortname: teamShort, ...team })}
                style={{
                  borderTop: '1px solid rgba(0,0,0,0.3)',
                  background: `linear-gradient(90deg, ${teamPrimary}40, ${teamPrimary}25, ${teamSecondary}15, transparent)`,
                  borderLeft: `3px solid ${teamPrimary}`,
                }}>
                {/* Full row team color wash */}
                <div className="absolute inset-0 pointer-events-none" style={{
                  background: `linear-gradient(90deg, ${teamPrimary}18, ${teamPrimary}08, transparent 70%)`,
                }} />
                <span className="w-6 text-[11px] font-black relative z-10" style={{ color: '#fff', textShadow: `0 0 10px ${teamPrimary}` }}>{i + 1}</span>
                <div className="flex-1 flex items-center gap-2 relative z-10">
                  {team.img && <img src={team.img} alt={team.shortname} className="w-5 h-5 rounded-sm" style={{ filter: 'drop-shadow(0 0 3px rgba(255,255,255,0.4))' }} />}
                  <span className="text-xs font-black" style={{ color: '#fff', textShadow: `0 0 8px ${teamPrimary}66` }}>{teamShort}</span>
                </div>
                <span className="w-7 text-center text-xs font-bold relative z-10" style={{ color: 'rgba(255,255,255,0.85)' }}>{team.matches}</span>
                <span className="w-7 text-center text-xs font-black relative z-10" style={{ color: '#4ade80' }}>{team.wins}</span>
                <span className="w-7 text-center text-xs font-bold relative z-10" style={{ color: '#f87171' }}>{team.loss}</span>
                <span className="w-7 text-center text-xs font-medium relative z-10" style={{ color: 'rgba(255,255,255,0.5)' }}>{team.nr}</span>
                <ChevronRight size={12} className="relative z-10" color="rgba(255,255,255,0.3)" />
              </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Team Matches Drawer */}
      {selectedTeam && (
        <TeamMatchesDrawer
          team={selectedTeam}
          onClose={() => setSelectedTeam(null)}
        />
      )}

      {/* Upcoming Matches */}
      {loading ? (
        <div className="space-y-3"><MatchSkeleton /><MatchSkeleton /></div>
      ) : upcomingMatches.length > 0 ? (
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-base font-black text-white tracking-tight">Upcoming Matches</h2>
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

      {/* Hot Contests - Instagram Stories Style */}
      {hotContests.length > 0 && (() => {
        const now = new Date();
        const cutoff = new Date(now.getTime() + 24 * 60 * 60 * 1000);
        const liveContests = hotContests.filter(c => {
          if (c.status !== 'open') return false;
          const match = matches.find(m => m.id === c.match_id);
          if (!match) return true;
          const matchStart = new Date(match.start_time || match.dateTimeGMT || '');
          if (isNaN(matchStart.getTime())) return true;
          return matchStart <= cutoff;
        });
        if (liveContests.length === 0) return null;
        return (
        <div data-testid="hot-contests-section">
          <div className="flex items-center gap-2 mb-3">
            <Zap size={16} color={COLORS.accent.gold} />
            <h2 className="text-base font-black text-white tracking-tight">Hot Contests</h2>
          </div>
          <div className="flex gap-4 overflow-x-auto pb-3 scrollbar-hide" style={{ scrollbarWidth: 'none' }}>
            {liveContests.slice(0, 8).map((c, i) => {
              const match = matches.find(m => m.id === c.match_id);
              const matchName = c.name || '';
              const teams = matchName.split(' vs ');
              const t1 = (teams[0] || '').replace(' Mega Contest', '').replace(' - Mega Contest', '').trim();
              const t2 = (teams[1] || '').replace(' Mega Contest', '').replace(' - Mega Contest', '').replace('- Mega Contest','').trim();
              const t1Short = normalizeTeam(t1.split(' ')[0]);
              const t2Short = normalizeTeam(t2.split(' ')[0]);
              const t1Color = (TEAM_COLORS[t1Short] || { primary: '#C134EA' }).primary;
              const t2Color = (TEAM_COLORS[t2Short] || { primary: '#FF6B35' }).primary;
              return (
                <div key={c.id} data-testid={`contest-story-${i}`}
                  className="shrink-0 flex flex-col items-center gap-1.5 cursor-pointer active:scale-95 transition-transform"
                  onClick={() => { if (match && onMatchClick) onMatchClick(match); }}
                  style={{ width: '72px' }}>
                  <div className="relative w-[68px] h-[68px]">
                    <svg className="absolute inset-0 w-full h-full contest-ring-spin" viewBox="0 0 68 68">
                      <defs>
                        <linearGradient id={`ring-${i}`} x1="0%" y1="0%" x2="100%" y2="100%">
                          <stop offset="0%" stopColor={t1Color} />
                          <stop offset="33%" stopColor={COLORS.accent.gold} />
                          <stop offset="66%" stopColor={t2Color} />
                          <stop offset="100%" stopColor={t1Color} />
                        </linearGradient>
                      </defs>
                      <circle cx="34" cy="34" r="31" fill="none" stroke={`url(#ring-${i})`}
                        strokeWidth="2.5" strokeLinecap="round"
                        strokeDasharray="8 4" />
                    </svg>
                    <div className="absolute inset-[4px] rounded-full overflow-hidden flex items-center justify-center"
                      style={{
                        background: `linear-gradient(135deg, ${t1Color}20, #0d0d14, ${t2Color}20)`,
                        border: '2px solid rgba(0,0,0,0.8)',
                      }}>
                      <div className="flex items-center gap-0.5">
                        <span className="text-[9px] font-black text-white" style={{ textShadow: `0 0 4px ${t1Color}` }}>{t1Short || '?'}</span>
                        <span className="text-[7px] font-bold" style={{ color: COLORS.accent.gold }}>v</span>
                        <span className="text-[9px] font-black text-white" style={{ textShadow: `0 0 4px ${t2Color}` }}>{t2Short || '?'}</span>
                      </div>
                    </div>
                    <div className="absolute -bottom-0.5 left-1/2 -translate-x-1/2 px-1.5 py-0.5 rounded-full text-[7px] font-black"
                      style={{
                        background: c.entry_fee === 0 ? 'rgba(34,197,94,0.9)' : `linear-gradient(135deg, ${t1Color}, ${t2Color})`,
                        color: '#fff',
                        boxShadow: '0 2px 6px rgba(0,0,0,0.5)',
                      }}>
                      {c.entry_fee === 0 ? 'FREE' : `${c.entry_fee}`}
                    </div>
                  </div>
                  <span className="text-[9px] font-bold text-center leading-tight truncate w-full" style={{ color: COLORS.text.secondary }}>
                    {t1Short} vs {t2Short}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
        );
      })()}

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
  const cardImg = getTeamCardImage(teamA.short_name) || getTeamCardImage(teamB.short_name);

  return (
    <div data-testid={`match-card-${match.id}`}
      className={`rounded-2xl overflow-hidden cursor-pointer transition-all active:scale-[0.97] ${isLive ? 'animate-border-glow' : 'card-hover'} match-card-sparkle`}
      style={{
        background: 'linear-gradient(135deg, #0d0d0d, #1a0a0f, #0d0d0d, #150810)',
        border: `1px solid ${isLive ? COLORS.primary.main + '55' : 'rgba(180,30,50,0.15)'}`,
        opacity: isCompleted ? 0.75 : 1
      }}
      onClick={() => onClick?.(match)}>

      {/* Team Card Image Hero (if available) */}
      {cardImg && !isCompleted && (
        <div className="relative h-20 overflow-hidden">
          <img src={cardImg} alt="" className="w-full h-full object-cover" style={{ filter: 'brightness(0.4) saturate(1.2)' }} />
          <div className="absolute inset-0" style={{ background: 'linear-gradient(to bottom, transparent 30%, #0D0D0D 100%)' }} />
          <div className="absolute top-2 left-3 flex items-center gap-2">
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded glass" style={{ color: '#fff' }}>
              {match.tournament || 'IPL 2026'}
            </span>
            {isLive && (
              <span className="px-2 py-0.5 rounded text-[9px] font-black text-white flex items-center gap-1" style={{ background: COLORS.primary.main }}>
                <span className="w-1.5 h-1.5 rounded-full bg-white animate-live-pulse" /> LIVE
              </span>
            )}
          </div>
        </div>
      )}

      {/* Fallback header if no image or completed */}
      {(!cardImg || isCompleted) && (
        <div className="px-4 py-2.5 flex items-center justify-between" style={{ borderBottom: `1px solid ${COLORS.border.light}` }}>
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium" style={{ color: COLORS.text.secondary }}>{match.tournament || match.venue || 'IPL 2026'}</span>
            {isLive && (
              <span className="px-1.5 py-0.5 rounded text-[10px] font-bold text-white flex items-center gap-1" style={{ background: COLORS.primary.main }}>
                <span className="w-1.5 h-1.5 rounded-full bg-white animate-live-pulse" /> LIVE
              </span>
            )}
            {isCompleted && <span className="text-[10px] font-semibold" style={{ color: COLORS.text.tertiary }}>ENDED</span>}
          </div>
          <div className="flex items-center gap-1.5">
            <Clock size={12} color={isLive ? COLORS.primary.main : COLORS.warning.main} />
            <span className="text-xs font-semibold" style={{ color: isLive ? COLORS.primary.main : COLORS.warning.main }}>
              {isLive ? 'In Progress' : isCompleted ? 'Finished' : <Countdown time={match.start_time} />}
            </span>
          </div>
        </div>
      )}

      <div className={`px-4 ${cardImg && !isCompleted ? 'pt-0 -mt-4 relative z-10' : 'pt-4'} pb-4 flex items-center justify-between`}>
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl flex items-center justify-center text-xs font-black text-white overflow-hidden shadow-lg"
            style={{ background: getTeamGrad(teamA.short_name) }}>
            {getTeamLogo(teamA.short_name) ? <img src={getTeamLogo(teamA.short_name)} alt={teamA.short_name} className="w-9 h-9 object-contain" /> : (teamA.short_name || '?')}
          </div>
          <div>
            <div className="text-sm font-bold text-white">{teamA.short_name || 'TBD'}</div>
            {scores[0] ? (
              <div className="text-sm font-bold animate-count" style={{ color: COLORS.primary.main, fontFamily: "'Rajdhani', sans-serif" }}>
                {scores[0].r || scores[0].runs}/{scores[0].w || scores[0].wickets} <span className="text-[10px]">({scores[0].o || scores[0].overs})</span>
              </div>
            ) : (
              <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>{teamA.name || ''}</div>
            )}
          </div>
        </div>

        <div className={`px-3 py-1.5 rounded-xl text-xs font-black ${isLive ? 'animate-live-pulse' : ''}`}
          style={{ background: isLive ? COLORS.primary.gradient : `${COLORS.primary.main}15`, color: isLive ? '#fff' : COLORS.primary.main }}>
          VS
        </div>

        <div className="flex items-center gap-3 flex-row-reverse">
          <div className="w-12 h-12 rounded-xl flex items-center justify-center text-xs font-black text-white overflow-hidden shadow-lg"
            style={{ background: getTeamGrad(teamB.short_name) }}>
            {getTeamLogo(teamB.short_name) ? <img src={getTeamLogo(teamB.short_name)} alt={teamB.short_name} className="w-9 h-9 object-contain" /> : (teamB.short_name || '?')}
          </div>
          <div className="text-right">
            <div className="text-sm font-bold text-white">{teamB.short_name || 'TBD'}</div>
            {scores[1] ? (
              <div className="text-sm font-bold animate-count" style={{ color: COLORS.primary.main, fontFamily: "'Rajdhani', sans-serif" }}>
                {scores[1].r || scores[1].runs}/{scores[1].w || scores[1].wickets} <span className="text-[10px]">({scores[1].o || scores[1].overs})</span>
              </div>
            ) : (
              <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>{teamB.name || ''}</div>
            )}
          </div>
        </div>
      </div>

      {/* Bottom action strip */}
      <div className="px-4 py-2.5 flex items-center justify-between" style={{ background: COLORS.background.tertiary, borderTop: `1px solid ${COLORS.border.light}` }}>
        <div className="flex items-center gap-1.5">
          <MapPin size={11} color={COLORS.text.tertiary} />
          <span className="text-[10px] truncate max-w-[150px]" style={{ color: COLORS.text.tertiary }}>{match.venue || ''}</span>
        </div>
        <div className="flex items-center gap-1 text-xs font-bold" style={{ color: COLORS.primary.main }}>
          {isLive ? 'Live Score' : isCompleted ? 'View Results' : 'Predict Now'} <ChevronRight size={14} />
        </div>
      </div>
    </div>
  );
}


// ==================== TEAM MATCHES DRAWER ====================
function TeamMatchesDrawer({ team, onClose }) {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMatch, setSelectedMatch] = useState(null);
  const teamShort = normalizeTeam((team.shortname || '').toUpperCase());
  const tc = TEAM_COLORS[teamShort] || { primary: '#888', secondary: '#666' };

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await apiClient.get(`/cricket/ipl/team/${teamShort}/matches`);
        setMatches(res.data.matches || []);
      } catch (_) {}
      finally { setLoading(false); }
    };
    fetch();
  }, [teamShort]);

  if (selectedMatch) {
    return <MatchFullDataView match={selectedMatch} onBack={() => setSelectedMatch(null)} onClose={onClose} teamColor={tc.primary} />;
  }

  return (
    <div data-testid="team-drawer" className="fixed inset-0 z-50 flex flex-col" style={{ background: '#0a0a0f' }}>
      {/* Header */}
      <div className="flex items-center gap-3 p-4 relative" style={{
        background: `linear-gradient(135deg, ${tc.primary}30, ${tc.primary}10, transparent)`,
        borderBottom: `1px solid ${tc.primary}30`,
      }}>
        <button onClick={onClose} className="p-1.5 rounded-full" style={{ background: 'rgba(255,255,255,0.08)' }}>
          <X size={16} color="#fff" />
        </button>
        {team.img && <img src={team.img} alt="" className="w-8 h-8 rounded-lg" style={{ filter: 'drop-shadow(0 0 4px rgba(255,255,255,0.3))' }} />}
        <div>
          <h2 className="text-base font-black text-white">{teamShort} Matches</h2>
          <span className="text-[10px]" style={{ color: `${tc.primary}cc` }}>{matches.length} matches in IPL 2026</span>
        </div>
      </div>

      {/* Match List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 size={24} className="animate-spin" color={tc.primary} />
          </div>
        ) : matches.map((m, i) => {
          const teams = m.teamInfo || [];
          const t1 = teams[0] || {};
          const t2 = teams[1] || {};
          const isEnded = m.matchEnded;
          const isStarted = m.matchStarted && !m.matchEnded;
          return (
            <div key={m.id || i} data-testid={`team-match-${i}`}
              className="rounded-xl p-3 cursor-pointer transition-all active:scale-[0.97]"
              onClick={() => setSelectedMatch(m)}
              style={{
                background: isStarted ? `linear-gradient(135deg, rgba(255,50,50,0.08), #111)` : `linear-gradient(135deg, ${tc.primary}0a, #111)`,
                border: `1px solid ${isStarted ? 'rgba(255,50,50,0.25)' : isEnded ? `${tc.primary}20` : 'rgba(255,255,255,0.06)'}`,
              }}>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Calendar size={10} color={COLORS.text.tertiary} />
                  <span className="text-[10px] font-bold" style={{ color: COLORS.text.secondary }}>{m.date || ''}</span>
                </div>
                <span className="text-[8px] font-black px-1.5 py-0.5 rounded" style={{
                  background: isStarted ? 'rgba(255,50,50,0.2)' : isEnded ? 'rgba(34,197,94,0.15)' : 'rgba(255,255,255,0.05)',
                  color: isStarted ? '#FF5555' : isEnded ? '#4ade80' : COLORS.text.tertiary,
                }}>
                  {isStarted ? 'LIVE' : isEnded ? 'COMPLETED' : 'UPCOMING'}
                </span>
              </div>
              <div className="flex items-center gap-2">
                {t1.img && <img src={t1.img} alt="" className="w-5 h-5 rounded-sm" />}
                <span className="text-xs font-black text-white flex-1">{normalizeTeam(t1.shortname || t1.name || '?')}</span>
                <span className="text-[10px] font-bold" style={{ color: COLORS.text.secondary }}>vs</span>
                <span className="text-xs font-black text-white flex-1 text-right">{normalizeTeam(t2.shortname || t2.name || '?')}</span>
                {t2.img && <img src={t2.img} alt="" className="w-5 h-5 rounded-sm" />}
              </div>
              {m.venue && (
                <div className="flex items-center gap-1 mt-1.5">
                  <MapPin size={8} color={COLORS.text.tertiary} />
                  <span className="text-[8px] truncate" style={{ color: COLORS.text.tertiary }}>{m.venue}</span>
                </div>
              )}
              <div className="text-[9px] mt-1 truncate" style={{ color: isEnded ? '#4ade80' : COLORS.text.tertiary }}>{m.status || ''}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ==================== MATCH FULL DATA VIEW ====================
function MatchFullDataView({ match, onBack, onClose, teamColor }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('info');
  const [commentary, setCommentary] = useState(null);
  const [commentaryLoading, setCommentaryLoading] = useState(false);

  const cricApiId = match.id || '';

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await apiClient.get(`/cricket/match/${cricApiId}/full-data`);
        setData(res.data);
      } catch (_) {}
      finally { setLoading(false); }
    };
    if (cricApiId) fetch();
  }, [cricApiId]);

  const loadCommentary = async () => {
    if (commentary) return;
    setCommentaryLoading(true);
    try {
      // Find internal match_id from our DB
      const matchesRes = await apiClient.get('/matches?limit=50');
      const ourMatches = matchesRes.data.matches || [];
      const ourMatch = ourMatches.find(m =>
        m.cricketdata_id === cricApiId || m.external_match_id === cricApiId
      );
      if (ourMatch) {
        const res = await apiClient.get(`/matches/${ourMatch.id}/ai-commentary`);
        setCommentary(res.data);
      }
    } catch (_) {}
    finally { setCommentaryLoading(false); }
  };

  const tabs = [
    { id: 'info', label: 'Info', icon: Award },
    { id: 'scorecard', label: 'Scorecard', icon: BarChart3 },
    { id: 'squad', label: 'Squad', icon: Users },
    { id: 'points', label: 'Fantasy', icon: Trophy },
    { id: 'commentary', label: 'AI Commentary', icon: Zap },
  ];

  const info = data?.match_info;
  const teams = info?.teamInfo || [];
  const t1 = teams[0] || {};
  const t2 = teams[1] || {};

  return (
    <div data-testid="match-full-data" className="fixed inset-0 z-50 flex flex-col" style={{ background: '#0a0a0f' }}>
      {/* Header */}
      <div className="p-3 relative" style={{
        background: `linear-gradient(135deg, ${teamColor}20, transparent)`,
        borderBottom: `1px solid ${teamColor}25`,
      }}>
        <div className="flex items-center gap-2 mb-2">
          <button onClick={onBack} className="p-1.5 rounded-full" style={{ background: 'rgba(255,255,255,0.08)' }}>
            <ChevronLeft size={16} color="#fff" />
          </button>
          <button onClick={onClose} className="p-1.5 rounded-full ml-auto" style={{ background: 'rgba(255,255,255,0.08)' }}>
            <X size={14} color="#fff" />
          </button>
        </div>
        {info && (
          <div className="text-center">
            <div className="flex items-center justify-center gap-4 mb-1">
              <div className="flex items-center gap-2">
                {t1.img && <img src={t1.img} alt="" className="w-6 h-6 rounded" />}
                <span className="text-sm font-black text-white">{normalizeTeam(t1.shortname || '?')}</span>
              </div>
              <span className="text-[10px] font-bold" style={{ color: teamColor }}>VS</span>
              <div className="flex items-center gap-2">
                <span className="text-sm font-black text-white">{normalizeTeam(t2.shortname || '?')}</span>
                {t2.img && <img src={t2.img} alt="" className="w-6 h-6 rounded" />}
              </div>
            </div>
            {info.score && info.score.length > 0 && (
              <div className="flex items-center justify-center gap-4 text-xs font-bold" style={{ color: teamColor }}>
                {info.score.map((s, i) => (
                  <span key={i}>{s.r}/{s.w} ({s.o} ov)</span>
                ))}
              </div>
            )}
            <div className="text-[9px] mt-1 font-bold" style={{ color: info.matchEnded ? '#4ade80' : '#FF5555' }}>{info.status}</div>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 px-2 py-1.5 overflow-x-auto" style={{ background: 'rgba(255,255,255,0.02)', scrollbarWidth: 'none' }}>
        {tabs.map(t => (
          <button key={t.id} data-testid={`tab-${t.id}`}
            onClick={() => { setActiveTab(t.id); if (t.id === 'commentary') loadCommentary(); }}
            className="shrink-0 flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-[10px] font-bold transition-all"
            style={{
              background: activeTab === t.id ? `${teamColor}25` : 'transparent',
              color: activeTab === t.id ? teamColor : COLORS.text.tertiary,
              border: `1px solid ${activeTab === t.id ? `${teamColor}40` : 'transparent'}`,
            }}>
            <t.icon size={10} />
            {t.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-3">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 size={24} className="animate-spin" color={teamColor} />
          </div>
        ) : !data ? (
          <div className="text-center py-10 text-sm" style={{ color: COLORS.text.tertiary }}>Data not available</div>
        ) : (
          <>
            {activeTab === 'info' && <MatchInfoTab data={data} teamColor={teamColor} />}
            {activeTab === 'scorecard' && <ScorecardTab data={data} teamColor={teamColor} />}
            {activeTab === 'squad' && <SquadTab data={data} teamColor={teamColor} />}
            {activeTab === 'points' && <FantasyPointsTab data={data} teamColor={teamColor} />}
            {activeTab === 'commentary' && <CommentaryTab commentary={commentary} loading={commentaryLoading} teamColor={teamColor} />}
          </>
        )}
      </div>
    </div>
  );
}

// ---- Sub-tabs ----
function MatchInfoTab({ data, teamColor }) {
  const info = data.match_info;
  const metrics = data.metrics;
  if (!info) return <div className="text-center text-sm py-10" style={{ color: COLORS.text.tertiary }}>Match info not available</div>;

  return (
    <div className="space-y-3">
      <InfoRow label="Match" value={info.name} color={teamColor} />
      <InfoRow label="Venue" value={info.venue} color={teamColor} />
      <InfoRow label="Date" value={info.date} color={teamColor} />
      <InfoRow label="Toss" value={info.tossWinner ? `${info.tossWinner} chose to ${info.tossChoice}` : '—'} color={teamColor} />
      <InfoRow label="Winner" value={info.matchWinner || '—'} color={teamColor} highlight />
      <InfoRow label="Status" value={info.status} color={teamColor} />
      {metrics && (
        <div className="mt-3">
          <div className="text-[10px] font-black uppercase tracking-wider mb-2" style={{ color: teamColor }}>Match Metrics</div>
          <div className="grid grid-cols-2 gap-2">
            <MetricCard label="Total Runs" value={metrics.match_total_runs} color={teamColor} />
            <MetricCard label="Total Wickets" value={metrics.match_total_wickets} color={teamColor} />
            <MetricCard label="Total Sixes" value={metrics.match_total_sixes} color={teamColor} />
            <MetricCard label="Total Fours" value={metrics.match_total_fours} color={teamColor} />
            <MetricCard label="Top Scorer" value={metrics.highest_run_scorer || '—'} sub={`${metrics.highest_run_scorer_runs} runs`} color={teamColor} />
            <MetricCard label="Best Bowler" value={metrics.best_bowler || '—'} sub={`${metrics.best_bowler_wickets} wickets`} color={teamColor} />
          </div>
        </div>
      )}
      {data.available_sections && (
        <div className="mt-3 flex flex-wrap gap-1">
          {data.available_sections.map(s => (
            <span key={s} className="text-[8px] font-bold px-1.5 py-0.5 rounded" style={{ background: `${teamColor}15`, color: teamColor }}>{s}</span>
          ))}
        </div>
      )}
    </div>
  );
}

function ScorecardTab({ data, teamColor }) {
  const sc = data.scorecard;
  if (!sc || !sc.innings || sc.innings.length === 0) return <div className="text-center text-sm py-10" style={{ color: COLORS.text.tertiary }}>Scorecard not available</div>;

  return (
    <div className="space-y-4">
      {sc.innings.map((inn, idx) => (
        <div key={idx}>
          <div className="text-[10px] font-black uppercase tracking-wider mb-2 px-1" style={{ color: teamColor }}>{inn.inning}</div>
          {/* Batting */}
          <div className="rounded-lg overflow-hidden mb-2" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.05)' }}>
            <div className="flex px-2 py-1.5" style={{ background: 'rgba(255,255,255,0.04)' }}>
              <span className="flex-1 text-[8px] font-bold" style={{ color: COLORS.text.tertiary }}>BATTER</span>
              <span className="w-7 text-center text-[8px] font-bold" style={{ color: COLORS.text.tertiary }}>R</span>
              <span className="w-7 text-center text-[8px] font-bold" style={{ color: COLORS.text.tertiary }}>B</span>
              <span className="w-6 text-center text-[8px] font-bold" style={{ color: COLORS.text.tertiary }}>4s</span>
              <span className="w-6 text-center text-[8px] font-bold" style={{ color: COLORS.text.tertiary }}>6s</span>
              <span className="w-8 text-center text-[8px] font-bold" style={{ color: COLORS.text.tertiary }}>SR</span>
            </div>
            {(inn.batting || []).map((b, bi) => {
              const name = typeof b.batsman === 'object' ? b.batsman.name : b.batsman;
              const isHighScore = b.r >= 50;
              return (
                <div key={bi} className="flex px-2 py-1.5" style={{ borderTop: '1px solid rgba(255,255,255,0.03)', background: isHighScore ? `${teamColor}08` : 'transparent' }}>
                  <div className="flex-1 min-w-0">
                    <span className="text-[10px] font-bold text-white truncate block">{name || '?'}</span>
                    <span className="text-[7px]" style={{ color: COLORS.text.tertiary }}>{b['dismissal-text'] || b.dismissal || ''}</span>
                  </div>
                  <span className="w-7 text-center text-[10px] font-black" style={{ color: isHighScore ? teamColor : '#fff' }}>{b.r}</span>
                  <span className="w-7 text-center text-[10px]" style={{ color: COLORS.text.secondary }}>{b.b}</span>
                  <span className="w-6 text-center text-[10px]" style={{ color: b['4s'] > 0 ? '#60a5fa' : COLORS.text.tertiary }}>{b['4s']}</span>
                  <span className="w-6 text-center text-[10px]" style={{ color: b['6s'] > 0 ? '#f59e0b' : COLORS.text.tertiary }}>{b['6s']}</span>
                  <span className="w-8 text-center text-[10px] font-bold" style={{ color: b.sr >= 150 ? '#4ade80' : COLORS.text.secondary }}>{b.sr}</span>
                </div>
              );
            })}
          </div>
          {/* Bowling */}
          <div className="rounded-lg overflow-hidden" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.05)' }}>
            <div className="flex px-2 py-1.5" style={{ background: 'rgba(255,255,255,0.04)' }}>
              <span className="flex-1 text-[8px] font-bold" style={{ color: COLORS.text.tertiary }}>BOWLER</span>
              <span className="w-6 text-center text-[8px] font-bold" style={{ color: COLORS.text.tertiary }}>O</span>
              <span className="w-6 text-center text-[8px] font-bold" style={{ color: COLORS.text.tertiary }}>M</span>
              <span className="w-7 text-center text-[8px] font-bold" style={{ color: COLORS.text.tertiary }}>R</span>
              <span className="w-6 text-center text-[8px] font-bold" style={{ color: COLORS.text.tertiary }}>W</span>
              <span className="w-8 text-center text-[8px] font-bold" style={{ color: COLORS.text.tertiary }}>ECO</span>
            </div>
            {(inn.bowling || []).map((bw, bwi) => {
              const name = typeof bw.bowler === 'object' ? bw.bowler.name : bw.bowler;
              const isGood = bw.w >= 2;
              return (
                <div key={bwi} className="flex px-2 py-1.5" style={{ borderTop: '1px solid rgba(255,255,255,0.03)', background: isGood ? `${teamColor}08` : 'transparent' }}>
                  <span className="flex-1 text-[10px] font-bold text-white truncate">{name || '?'}</span>
                  <span className="w-6 text-center text-[10px]" style={{ color: COLORS.text.secondary }}>{bw.o}</span>
                  <span className="w-6 text-center text-[10px]" style={{ color: COLORS.text.tertiary }}>{bw.m}</span>
                  <span className="w-7 text-center text-[10px]" style={{ color: COLORS.text.secondary }}>{bw.r}</span>
                  <span className="w-6 text-center text-[10px] font-black" style={{ color: isGood ? '#4ade80' : '#fff' }}>{bw.w}</span>
                  <span className="w-8 text-center text-[10px] font-bold" style={{ color: bw.eco <= 7 ? '#4ade80' : bw.eco >= 10 ? '#f87171' : COLORS.text.secondary }}>{bw.eco}</span>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}

function SquadTab({ data, teamColor }) {
  const squads = data.squad;
  if (!squads || squads.length === 0) return <div className="text-center text-sm py-10" style={{ color: COLORS.text.tertiary }}>Squad not available</div>;

  return (
    <div className="space-y-4">
      {squads.map((team, ti) => (
        <div key={ti}>
          <div className="flex items-center gap-2 mb-2">
            {team.img && <img src={team.img} alt="" className="w-5 h-5 rounded" />}
            <span className="text-[11px] font-black text-white">{normalizeTeam(team.teamName || team.shortname || '')}</span>
            <span className="text-[9px]" style={{ color: COLORS.text.tertiary }}>{(team.players || []).length} players</span>
          </div>
          <div className="grid grid-cols-2 gap-1.5">
            {(team.players || []).map((p, pi) => (
              <div key={pi} className="flex items-center gap-2 p-2 rounded-lg" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.04)' }}>
                {p.playerImg && <img src={p.playerImg} alt="" className="w-6 h-6 rounded-full object-cover" style={{ background: '#222' }} />}
                <div className="min-w-0 flex-1">
                  <div className="text-[9px] font-bold text-white truncate">{p.name}</div>
                  <div className="text-[7px]" style={{ color: teamColor }}>{p.role || '—'}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function FantasyPointsTab({ data, teamColor }) {
  const fp = data.fantasy_points;
  if (!fp || !fp.totals || fp.totals.length === 0) return <div className="text-center text-sm py-10" style={{ color: COLORS.text.tertiary }}>Fantasy points not available</div>;

  return (
    <div className="space-y-3">
      <div className="text-[10px] font-black uppercase tracking-wider" style={{ color: teamColor }}>Top Fantasy Performers</div>
      <div className="rounded-lg overflow-hidden" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.05)' }}>
        <div className="flex px-2 py-1.5" style={{ background: 'rgba(255,255,255,0.04)' }}>
          <span className="w-5 text-[8px] font-bold" style={{ color: COLORS.text.tertiary }}>#</span>
          <span className="flex-1 text-[8px] font-bold" style={{ color: COLORS.text.tertiary }}>PLAYER</span>
          <span className="w-12 text-center text-[8px] font-bold" style={{ color: teamColor }}>POINTS</span>
        </div>
        {fp.totals.slice(0, 15).map((p, i) => (
          <div key={i} className="flex items-center px-2 py-1.5" style={{
            borderTop: '1px solid rgba(255,255,255,0.03)',
            background: i < 3 ? `${teamColor}0${8 - i * 2}` : 'transparent',
          }}>
            <span className="w-5 text-[10px] font-black" style={{ color: i < 3 ? teamColor : COLORS.text.tertiary }}>{i + 1}</span>
            <span className="flex-1 text-[10px] font-bold text-white truncate">{p.name}</span>
            <span className="w-12 text-center text-[11px] font-black" style={{
              color: p.points >= 0 ? teamColor : '#f87171',
              fontFamily: "'Rajdhani', sans-serif",
            }}>{p.points}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function CommentaryTab({ commentary, loading, teamColor }) {
  if (loading) return <div className="flex items-center justify-center py-20"><Loader2 size={24} className="animate-spin" color={teamColor} /></div>;
  if (!commentary) return <div className="text-center text-sm py-10" style={{ color: COLORS.text.tertiary }}>AI commentary not available. Match scorecard needed.</div>;

  const { match_pulse, key_moments, star_performers, turning_point, verdict } = commentary;

  return (
    <div className="space-y-4">
      {match_pulse && (
        <div className="p-3 rounded-xl" style={{ background: `${teamColor}10`, border: `1px solid ${teamColor}25` }}>
          <div className="text-sm font-black text-white">{match_pulse.headline}</div>
          <div className="text-[10px] mt-1" style={{ color: COLORS.text.secondary }}>{match_pulse.sub}</div>
        </div>
      )}
      {verdict && (
        <div className="p-3 rounded-xl" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)' }}>
          <div className="text-[10px] font-black uppercase tracking-wider mb-1" style={{ color: teamColor }}>Verdict</div>
          <div className="text-xs font-bold text-white">{verdict.headline}</div>
          <div className="text-[10px] mt-1" style={{ color: COLORS.text.secondary }}>{verdict.description}</div>
        </div>
      )}
      {star_performers && star_performers.length > 0 && (
        <div>
          <div className="text-[10px] font-black uppercase tracking-wider mb-2" style={{ color: teamColor }}>Star Performers</div>
          {star_performers.map((sp, i) => (
            <div key={i} className="flex items-center gap-2 p-2 rounded-lg mb-1.5" style={{ background: 'rgba(255,255,255,0.03)' }}>
              <div className="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-black" style={{ background: `${teamColor}20`, color: teamColor }}>{(sp.rating || 0).toFixed(1)}</div>
              <div className="flex-1 min-w-0">
                <div className="text-[10px] font-black text-white">{sp.name}</div>
                <div className="text-[8px]" style={{ color: COLORS.text.secondary }}>{sp.stats}</div>
                <div className="text-[8px] italic" style={{ color: teamColor }}>{sp.headline}</div>
              </div>
            </div>
          ))}
        </div>
      )}
      {key_moments && key_moments.length > 0 && (
        <div>
          <div className="text-[10px] font-black uppercase tracking-wider mb-2" style={{ color: teamColor }}>Key Moments</div>
          {key_moments.slice(0, 10).map((km, i) => (
            <div key={i} className="flex gap-2 mb-1.5 p-2 rounded-lg" style={{ background: km.impact === 'high' ? `${teamColor}08` : 'transparent' }}>
              <span className="text-[9px] font-bold shrink-0 w-8" style={{ color: teamColor }}>{km.over || '—'}</span>
              <div className="min-w-0">
                <div className="text-[10px] font-bold text-white">{km.title}</div>
                <div className="text-[9px]" style={{ color: COLORS.text.secondary }}>{km.description}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ---- Helper Components ----
function InfoRow({ label, value, color, highlight }) {
  return (
    <div className="flex items-start gap-2 px-1">
      <span className="text-[9px] font-bold uppercase w-16 shrink-0" style={{ color: COLORS.text.tertiary }}>{label}</span>
      <span className={`text-[10px] ${highlight ? 'font-black' : 'font-bold'}`} style={{ color: highlight ? color : '#fff' }}>{value || '—'}</span>
    </div>
  );
}

function MetricCard({ label, value, sub, color }) {
  return (
    <div className="p-2.5 rounded-lg" style={{ background: `${color}08`, border: `1px solid ${color}15` }}>
      <div className="text-[8px] font-bold uppercase" style={{ color: COLORS.text.tertiary }}>{label}</div>
      <div className="text-base font-black" style={{ color, fontFamily: "'Rajdhani', sans-serif" }}>{value}</div>
      {sub && <div className="text-[8px]" style={{ color: COLORS.text.secondary }}>{sub}</div>}
    </div>
  );
}
