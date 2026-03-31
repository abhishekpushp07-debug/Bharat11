import { useState, useEffect } from 'react';
import apiClient from '../api/client';
import { COLORS } from '../constants/design';
import { TEAM_COLORS, getTeamLogo, normalizeTeam } from '../constants/teams';
import { Trophy, Clock, Users, ChevronRight, CheckCircle, XCircle, Coins, Target, ArrowLeft, Medal, Flame, Lock, TrendingUp } from 'lucide-react';
import { motion } from 'framer-motion';

const STATUS_CONFIG = {
  open: { label: 'OPEN', color: '#22c55e', bg: 'rgba(34,197,94,0.1)', border: 'rgba(34,197,94,0.25)' },
  live: { label: 'LIVE', color: '#FF3B3B', bg: 'rgba(255,59,59,0.1)', border: 'rgba(255,59,59,0.3)' },
  locked: { label: 'LOCKED', color: '#F59E0B', bg: 'rgba(245,158,11,0.1)', border: 'rgba(245,158,11,0.25)' },
  completed: { label: 'COMPLETED', color: '#94a3b8', bg: 'rgba(148,163,184,0.08)', border: 'rgba(148,163,184,0.15)' },
};

export default function MyContestsPage({ onContestClick, onViewLeaderboard }) {
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

  const stats = {
    total: contests.length,
    active: contests.filter(c => ['open', 'live'].includes(c.contest?.status)).length,
    completed: contests.filter(c => c.contest?.status === 'completed').length,
    totalPoints: contests.reduce((s, c) => s + (c.entry?.total_points || 0), 0),
    totalCorrect: contests.reduce((s, c) => s + (c.entry?.predictions || []).filter(p => p.is_correct).length, 0),
  };

  const filters = [
    { key: 'all', label: 'All', count: stats.total },
    { key: 'live', label: 'Live', count: contests.filter(c => c.contest?.status === 'live').length },
    { key: 'open', label: 'Open', count: contests.filter(c => c.contest?.status === 'open').length },
    { key: 'completed', label: 'Done', count: stats.completed },
  ];

  return (
    <div data-testid="my-contests-page" className="pb-6 space-y-5">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight">My Contests</h1>
        <p className="text-xs mt-0.5" style={{ color: COLORS.text.secondary }}>Track your predictions & performance</p>
      </div>

      {/* Stats Strip */}
      <div className="grid grid-cols-3 gap-2">
        <div className="p-3 rounded-xl text-center" style={{ background: 'rgba(255,59,59,0.08)', border: '1px solid rgba(255,59,59,0.15)' }}>
          <div className="text-lg font-black" style={{ color: COLORS.primary.main, fontFamily: "'Rajdhani', sans-serif" }}>{stats.total}</div>
          <div className="text-[9px] font-semibold uppercase tracking-wider" style={{ color: COLORS.text.tertiary }}>Joined</div>
        </div>
        <div className="p-3 rounded-xl text-center" style={{ background: 'rgba(34,197,94,0.08)', border: '1px solid rgba(34,197,94,0.15)' }}>
          <div className="text-lg font-black" style={{ color: '#22c55e', fontFamily: "'Rajdhani', sans-serif" }}>{stats.totalCorrect}</div>
          <div className="text-[9px] font-semibold uppercase tracking-wider" style={{ color: COLORS.text.tertiary }}>Correct</div>
        </div>
        <div className="p-3 rounded-xl text-center" style={{ background: 'rgba(255,215,0,0.08)', border: '1px solid rgba(255,215,0,0.15)' }}>
          <div className="text-lg font-black" style={{ color: '#FFD700', fontFamily: "'Rajdhani', sans-serif" }}>{stats.totalPoints}</div>
          <div className="text-[9px] font-semibold uppercase tracking-wider" style={{ color: COLORS.text.tertiary }}>Points</div>
        </div>
      </div>

      {/* Filter Pills */}
      <div className="flex gap-2 overflow-x-auto pb-1" style={{ scrollbarWidth: 'none' }}>
        {filters.map(f => (
          <button key={f.key} data-testid={`filter-${f.key}`} onClick={() => setFilter(f.key)}
            className="px-3.5 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all flex items-center gap-1.5"
            style={{
              background: filter === f.key
                ? (f.key === 'live' ? 'rgba(255,59,59,0.15)' : f.key === 'open' ? 'rgba(34,197,94,0.15)' : `${COLORS.primary.main}20`)
                : COLORS.background.card,
              color: filter === f.key
                ? (f.key === 'live' ? '#FF3B3B' : f.key === 'open' ? '#22c55e' : COLORS.primary.main)
                : COLORS.text.secondary,
              border: `1px solid ${filter === f.key
                ? (f.key === 'live' ? 'rgba(255,59,59,0.3)' : f.key === 'open' ? 'rgba(34,197,94,0.3)' : `${COLORS.primary.main}33`)
                : COLORS.border.light}`,
            }}>
            {f.label}
            {f.count > 0 && (
              <span className="w-5 h-5 rounded-full flex items-center justify-center text-[9px] font-black"
                style={{ background: filter === f.key ? 'rgba(255,255,255,0.15)' : 'rgba(255,255,255,0.05)' }}>
                {f.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="w-10 h-10 border-2 rounded-full animate-spin" style={{ borderColor: `${COLORS.primary.main}20`, borderTopColor: COLORS.primary.main }} />
        </div>
      ) : filtered.length === 0 ? (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center py-16 rounded-2xl"
          style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
          <div className="w-16 h-16 rounded-2xl mx-auto mb-4 flex items-center justify-center" style={{ background: `${COLORS.primary.main}12` }}>
            <Trophy size={28} color={COLORS.text.tertiary} />
          </div>
          <p className="text-sm font-bold text-white mb-1">No Contests Yet</p>
          <p className="text-xs px-8" style={{ color: COLORS.text.secondary }}>
            {filter === 'all'
              ? 'Join a contest from any match to start predicting!'
              : `No ${filter} contests right now`}
          </p>
        </motion.div>
      ) : (
        <div className="space-y-3">
          {filtered.map(({ entry, contest, match }, idx) => (
            <ContestCard
              key={entry?.id || idx}
              entry={entry}
              contest={contest}
              match={match}
              index={idx}
              onClick={() => onContestClick?.({ entry, contest, match })}
              onViewLeaderboard={() => onViewLeaderboard?.(contest?.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function ContestCard({ entry, contest, match, index, onClick, onViewLeaderboard }) {
  const teamA = match?.team_a || {};
  const teamB = match?.team_b || {};
  const tA = normalizeTeam(teamA.short_name);
  const tB = normalizeTeam(teamB.short_name);
  const tcA = TEAM_COLORS[tA] || { primary: '#555' };
  const tcB = TEAM_COLORS[tB] || { primary: '#555' };
  const status = contest?.status || 'open';
  const sc = STATUS_CONFIG[status] || STATUS_CONFIG.open;
  const isCompleted = status === 'completed';
  const isLive = status === 'live';
  const predictions = entry?.predictions || [];
  const answered = predictions.length;
  const correct = predictions.filter(p => p.is_correct).length;
  const totalQ = contest?.question_count || contest?.total_questions || 16;
  const currentRank = entry?.current_rank || entry?.final_rank;

  return (
    <motion.div
      data-testid={`my-contest-${entry?.id}`}
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06, duration: 0.35, ease: [0.22, 0.61, 0.36, 1] }}
      className="rounded-2xl overflow-hidden cursor-pointer transition-all active:scale-[0.98]"
      style={{
        background: isLive
          ? 'linear-gradient(135deg, rgba(255,59,59,0.06), #0D0D0D, rgba(255,59,59,0.03))'
          : COLORS.background.card,
        border: `1px solid ${isLive ? 'rgba(255,59,59,0.2)' : isCompleted ? 'rgba(148,163,184,0.12)' : COLORS.border.light}`,
        boxShadow: isLive ? '0 0 20px rgba(255,59,59,0.08)' : 'none',
      }}
      onClick={onClick}>

      {/* Match Header */}
      <div className="px-4 py-3 flex items-center gap-3" style={{ borderBottom: `1px solid ${COLORS.border.light}` }}>
        {/* Team Logos */}
        <div className="flex items-center gap-1.5 flex-1 min-w-0">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center overflow-hidden shrink-0"
            style={{ background: `linear-gradient(135deg, ${tcA.primary}30, ${tcA.primary}10)` }}>
            {getTeamLogo(tA)
              ? <img src={getTeamLogo(tA)} alt={tA} className="w-6 h-6 object-contain" />
              : <span className="text-[9px] font-black text-white">{tA}</span>}
          </div>
          <span className="text-[10px] font-bold" style={{ color: COLORS.text.tertiary }}>vs</span>
          <div className="w-8 h-8 rounded-lg flex items-center justify-center overflow-hidden shrink-0"
            style={{ background: `linear-gradient(135deg, ${tcB.primary}30, ${tcB.primary}10)` }}>
            {getTeamLogo(tB)
              ? <img src={getTeamLogo(tB)} alt={tB} className="w-6 h-6 object-contain" />
              : <span className="text-[9px] font-black text-white">{tB}</span>}
          </div>
          <div className="ml-1 min-w-0 flex-1">
            <div className="text-xs font-bold text-white truncate">{tA} vs {tB}</div>
            <div className="text-[9px] truncate" style={{ color: COLORS.text.tertiary }}>
              {match?.start_time_ist || new Date(match?.start_time).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Kolkata' })}
            </div>
          </div>
        </div>

        {/* Status Badge */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg shrink-0"
          style={{ background: sc.bg, border: `1px solid ${sc.border}` }}>
          {isLive && <div className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: sc.color }} />}
          <span className="text-[10px] font-black" style={{ color: sc.color }}>{sc.label}</span>
        </div>
      </div>

      {/* Body */}
      <div className="px-4 py-3 flex items-center justify-between">
        <div className="flex-1">
          <div className="text-[10px] font-semibold mb-1" style={{ color: COLORS.text.tertiary }}>
            {contest?.name?.replace(/- Mega Contest/i, '').trim() || 'Contest'}
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1">
              <Coins size={11} color="#FFD700" />
              <span className="text-[10px] font-bold" style={{ color: COLORS.accent.gold }}>{contest?.entry_fee || 0}</span>
            </div>
            <div className="flex items-center gap-1">
              <Users size={10} color={COLORS.text.tertiary} />
              <span className="text-[10px]" style={{ color: COLORS.text.secondary }}>{contest?.current_participants || 0}</span>
            </div>
            {answered > 0 && (
              <div className="flex items-center gap-1">
                <Target size={10} color={COLORS.primary.main} />
                <span className="text-[10px] font-bold" style={{ color: COLORS.text.secondary }}>{answered}/{totalQ}</span>
              </div>
            )}
          </div>
        </div>

        {/* Rank Shortcut + Points */}
        <div className="flex items-center gap-2.5">
          {currentRank && (
            <button
              data-testid={`rank-shortcut-${entry?.id}`}
              onClick={(e) => { e.stopPropagation(); onViewLeaderboard?.(); }}
              className="flex items-center gap-1 px-2 py-1.5 rounded-lg transition-all active:scale-95"
              style={{
                background: isLive ? 'rgba(255,59,59,0.12)' : 'rgba(255,215,0,0.1)',
                border: `1px solid ${isLive ? 'rgba(255,59,59,0.25)' : 'rgba(255,215,0,0.2)'}`,
              }}>
              <TrendingUp size={10} color={isLive ? '#FF3B3B' : COLORS.accent.gold} />
              <span className="text-[10px] font-black" style={{ color: isLive ? '#FF3B3B' : COLORS.accent.gold }}>
                #{currentRank}
              </span>
            </button>
          )}
          <div className="text-right">
            <div className="text-xl font-black" style={{ color: COLORS.primary.main, fontFamily: "'Rajdhani', sans-serif" }}>
              {entry?.total_points || 0}
            </div>
            <div className="text-[8px] font-semibold uppercase tracking-wider" style={{ color: COLORS.text.tertiary }}>Points</div>
          </div>
          <ChevronRight size={16} color={COLORS.text.tertiary} />
        </div>
      </div>

      {/* Progress Footer */}
      {(answered > 0 || isCompleted) && (
        <div className="px-4 py-2.5 flex items-center justify-between" style={{ background: COLORS.background.tertiary, borderTop: `1px solid ${COLORS.border.light}` }}>
          {isCompleted ? (
            <>
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1">
                  <CheckCircle size={11} color="#22c55e" />
                  <span className="text-[10px] font-bold" style={{ color: '#22c55e' }}>{correct} correct</span>
                </div>
                {correct < answered && (
                  <div className="flex items-center gap-1">
                    <XCircle size={11} color="#ef4444" />
                    <span className="text-[10px] font-bold" style={{ color: '#ef4444' }}>{answered - correct} wrong</span>
                  </div>
                )}
              </div>
              {entry?.final_rank && (
                <div className="flex items-center gap-1">
                  <Medal size={12} color={COLORS.accent.gold} />
                  <span className="text-xs font-black" style={{ color: COLORS.accent.gold }}>#{entry.final_rank}</span>
                  {entry.prize_won > 0 && (
                    <span className="text-[10px] font-bold ml-1" style={{ color: '#22c55e' }}>+{entry.prize_won}</span>
                  )}
                </div>
              )}
            </>
          ) : (
            <>
              <div className="flex-1 mr-3">
                <div className="h-1.5 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.06)' }}>
                  <div className="h-full rounded-full transition-all" style={{ width: `${(answered / totalQ) * 100}%`, background: COLORS.primary.main }} />
                </div>
              </div>
              <span className="text-[10px] font-bold shrink-0" style={{ color: COLORS.primary.main }}>
                {answered}/{totalQ} answered
              </span>
            </>
          )}
        </div>
      )}
    </motion.div>
  );
}
