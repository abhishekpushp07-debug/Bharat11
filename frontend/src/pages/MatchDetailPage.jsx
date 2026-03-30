import { useState, useEffect, useCallback } from 'react';
import apiClient from '../api/client';
import { COLORS } from '../constants/design';
import { ArrowLeft, Clock, MapPin, Trophy, Users, ChevronRight, Loader2, Check, Coins } from 'lucide-react';

const TEAM_COLORS = {
  MI: ['#004BA0', '#00599E'], CSK: ['#F9CD05', '#F3A012'],
  RCB: ['#D4213D', '#A0171F'], KKR: ['#3A225D', '#552583'],
  DC: ['#0078BC', '#17479E'], PBKS: ['#ED1B24', '#AA1019'],
  SRH: ['#FF822A', '#E35205'], RR: ['#EA1A85', '#C51D70'],
  GT: ['#1C1C2B', '#0B4F6C'], LSG: ['#2E90A8', '#1B7B93'],
};

export default function MatchDetailPage({ match, onBack, onJoinContest, onOpenPrediction, onOpenLeaderboard }) {
  const [contests, setContests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [joiningId, setJoiningId] = useState(null);
  const [joinedIds, setJoinedIds] = useState(new Set());
  const [joinError, setJoinError] = useState('');

  const fetchContests = useCallback(async () => {
    try {
      const res = await apiClient.get(`/matches/${match.id}/contests`);
      setContests(res.data.contests || []);

      // Check which contests user already joined
      try {
        const myRes = await apiClient.get('/contests/user/my-contests?limit=50');
        const myContestIds = new Set(
          (myRes.data.my_contests || []).map(mc => mc.entry?.contest_id).filter(Boolean)
        );
        setJoinedIds(myContestIds);
      } catch (_) { /* silent */ }
    } catch (_) { /* silent */ }
    finally { setLoading(false); }
  }, [match?.id]);

  useEffect(() => {
    if (match?.id) fetchContests();
  }, [match?.id, fetchContests]);

  const handleJoin = async (contestId) => {
    setJoiningId(contestId);
    setJoinError('');
    try {
      await apiClient.post(`/contests/${contestId}/join`, { team_name: `Team_${Date.now().toString(36)}` });
      setJoinedIds(prev => new Set([...prev, contestId]));
      onJoinContest?.(contestId);
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.message || 'Join failed';
      if (msg.includes('Already joined')) {
        setJoinedIds(prev => new Set([...prev, contestId]));
        onOpenPrediction?.(contestId);
      } else {
        setJoinError(msg);
      }
    } finally {
      setJoiningId(null);
    }
  };

  const teamA = match?.team_a || {};
  const teamB = match?.team_b || {};
  const isLive = match?.status === 'live';
  const isCompleted = match?.status === 'completed';
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
          {isCompleted && <span className="px-2 py-0.5 rounded text-xs font-bold" style={{ color: COLORS.text.tertiary, background: COLORS.background.tertiary }}>COMPLETED</span>}
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
              {isLive ? 'In Progress' : isCompleted ? 'Match Over' : new Date(match?.start_time).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
        </div>
      </div>

      {/* Error */}
      {joinError && (
        <div data-testid="join-error" className="text-center text-sm py-2.5 px-3 rounded-xl" style={{ background: COLORS.error.bg, color: COLORS.error.main }}>
          {joinError}
        </div>
      )}

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
          <div className="space-y-2.5">
            {contests.map(c => {
              const isJoined = joinedIds.has(c.id);
              const isJoining = joiningId === c.id;
              const contestCompleted = c.status === 'completed';

              return (
                <div key={c.id} data-testid={`contest-${c.id}`}
                  className="p-4 rounded-xl transition-all"
                  style={{ background: COLORS.background.card, border: `1px solid ${isJoined ? COLORS.success.main + '33' : COLORS.border.light}` }}>
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-semibold text-white">{c.name}</div>
                      <div className="flex items-center gap-3 mt-1">
                        <span className="flex items-center gap-1 text-xs" style={{ color: COLORS.text.secondary }}>
                          <Coins size={11} color="#FFD700" /> {c.entry_fee} coins
                        </span>
                        <span className="text-xs" style={{ color: COLORS.accent.gold }}>Pool: {(c.prize_pool || c.entry_fee * (c.current_participants || 0)).toLocaleString()}</span>
                      </div>
                      <div className="text-[9px] mt-0.5" style={{ color: COLORS.text.tertiary }}>1st: 50% | 2nd: 30% | 3rd: 20%</div>
                      <div className="flex items-center gap-1 mt-1">
                        <Users size={12} color={COLORS.info.main} />
                        <span className="text-xs" style={{ color: COLORS.text.tertiary }}>{c.current_participants || 0}/{c.max_participants || 0}</span>
                        <span className="text-xs font-medium ml-2 px-1.5 py-0.5 rounded" style={{
                          color: c.status === 'open' ? COLORS.success.main : COLORS.text.tertiary,
                          background: c.status === 'open' ? COLORS.success.bg : COLORS.background.tertiary
                        }}>{c.status?.toUpperCase()}</span>
                      </div>
                    </div>

                    <div className="ml-3 shrink-0">
                      {contestCompleted ? (
                        <button
                          data-testid={`leaderboard-btn-${c.id}`}
                          onClick={() => onOpenLeaderboard?.(c.id)}
                          className="px-4 py-2.5 rounded-xl text-xs font-bold flex items-center gap-1"
                          style={{ background: COLORS.background.tertiary, color: COLORS.accent.gold, border: `1px solid ${COLORS.accent.gold}33` }}>
                          <Trophy size={13} /> Results
                        </button>
                      ) : isJoined ? (
                        <button
                          data-testid={`predict-btn-${c.id}`}
                          onClick={() => onOpenPrediction?.(c.id)}
                          className="px-4 py-2.5 rounded-xl text-xs font-bold flex items-center gap-1"
                          style={{ background: COLORS.success.bg, color: COLORS.success.main, border: `1px solid ${COLORS.success.main}33` }}>
                          <Check size={13} /> Predict
                        </button>
                      ) : (
                        <button
                          data-testid={`join-btn-${c.id}`}
                          onClick={() => handleJoin(c.id)}
                          disabled={isJoining || c.status !== 'open'}
                          className="px-4 py-2.5 rounded-xl text-xs font-bold flex items-center gap-1 disabled:opacity-50"
                          style={{ background: COLORS.primary.gradient, color: '#fff' }}>
                          {isJoining ? <Loader2 size={13} className="animate-spin" /> : null}
                          {isJoining ? 'Joining...' : 'Join'}
                          {!isJoining && <ChevronRight size={13} />}
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
