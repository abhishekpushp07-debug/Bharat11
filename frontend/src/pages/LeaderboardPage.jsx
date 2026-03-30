import { useState, useEffect, useCallback } from 'react';
import apiClient from '../api/client';
import { COLORS } from '../constants/design';
import { ArrowLeft, Trophy, Crown, Medal, Star, X, Check, AlertCircle, ChevronDown, ChevronUp, Share2 } from 'lucide-react';
import ShareCard from '../components/ShareCard';
import { useSocketStore } from '../stores/socketStore';

// User Answer Detail Modal
function UserAnswerModal({ contestId, userId, onClose }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await apiClient.get(`/contests/${contestId}/leaderboard/${userId}`);
        setData(res.data);
      } catch (e) {
        setError(e?.response?.data?.detail || e?.message || 'Failed to load answers');
      }
      finally { setLoading(false); }
    };
    fetch();
  }, [contestId, userId]);

  if (loading) {
    return (
      <div className="fixed inset-0 z-50 flex items-end justify-center" style={{ background: 'rgba(0,0,0,0.7)' }}>
        <div className="w-full max-w-lg rounded-t-3xl p-6" style={{ background: COLORS.background.secondary, maxHeight: '80vh' }}>
          <div className="flex justify-center py-10">
            <div className="w-8 h-8 border-2 rounded-full animate-spin" style={{ borderColor: `${COLORS.primary.main}30`, borderTopColor: COLORS.primary.main }} />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 z-50 flex items-end justify-center" style={{ background: 'rgba(0,0,0,0.7)' }} onClick={onClose}>
        <div className="w-full max-w-lg rounded-t-3xl p-6 text-center" style={{ background: COLORS.background.secondary }} onClick={e => e.stopPropagation()}>
          <AlertCircle size={32} color={COLORS.error.main} className="mx-auto mb-2" />
          <p className="text-sm mb-3" style={{ color: COLORS.error.main }}>{error}</p>
          <button onClick={onClose} className="px-4 py-2 rounded-lg text-sm" style={{ background: COLORS.background.card, color: COLORS.text.secondary }}>Close</button>
        </div>
      </div>
    );
  }

  if (!data) return null;

  const correct = data.predictions?.filter(p => p.is_correct === true).length || 0;
  const total = data.predictions?.length || 0;

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center" style={{ background: 'rgba(0,0,0,0.7)' }} onClick={onClose}>
      <div
        data-testid="user-answer-modal"
        className="w-full max-w-lg rounded-t-3xl overflow-hidden"
        style={{ background: COLORS.background.secondary, maxHeight: '85vh' }}
        onClick={e => e.stopPropagation()}>

        {/* Header */}
        <div className="sticky top-0 px-5 pt-5 pb-3 flex items-center justify-between" style={{ background: COLORS.background.secondary, borderBottom: `1px solid ${COLORS.border.light}` }}>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold text-white" style={{ background: COLORS.primary.main + '44' }}>
              {(data.username || 'U')[0].toUpperCase()}
            </div>
            <div>
              <div className="text-sm font-semibold text-white">{data.username}</div>
              <div className="text-xs" style={{ color: COLORS.text.tertiary }}>{data.team_name} - {data.rank_title}</div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-right">
              <div className="text-lg font-bold" style={{ color: COLORS.primary.main, fontFamily: "'Rajdhani', sans-serif" }}>{data.total_points} pts</div>
              {data.final_rank && <div className="text-xs" style={{ color: COLORS.accent.gold }}>Rank #{data.final_rank}</div>}
            </div>
            <button data-testid="close-modal-btn" onClick={onClose} className="p-1.5 rounded-lg" style={{ background: COLORS.background.tertiary }}>
              <X size={16} color={COLORS.text.secondary} />
            </button>
          </div>
        </div>

        {/* Stats Bar */}
        <div className="px-5 py-2.5 flex items-center gap-4" style={{ background: COLORS.background.tertiary }}>
          <span className="text-xs" style={{ color: COLORS.text.secondary }}>{total} Predictions</span>
          <span className="text-xs flex items-center gap-1" style={{ color: COLORS.success.main }}>
            <Check size={11} /> {correct} Correct
          </span>
          <span className="text-xs flex items-center gap-1" style={{ color: COLORS.error.main }}>
            <AlertCircle size={11} /> {total - correct} Wrong
          </span>
          {data.prize_won > 0 && (
            <span className="text-xs font-semibold" style={{ color: COLORS.accent.gold }}>+{data.prize_won} coins</span>
          )}
        </div>

        {/* Predictions List */}
        <div className="overflow-y-auto px-5 py-3 space-y-2" style={{ maxHeight: 'calc(85vh - 140px)' }}>
          {(data.predictions || []).map((pred, i) => {
            const isCorrect = pred.is_correct === true;
            const isWrong = pred.is_correct === false;
            const isUnresolved = pred.is_correct === null || pred.is_correct === undefined;

            const selectedOpt = (pred.options || []).find(o => o.key === pred.selected_option);
            const correctOpt = pred.correct_option ? (pred.options || []).find(o => o.key === pred.correct_option) : null;

            return (
              <div key={i} data-testid={`user-pred-${i}`} className="rounded-xl p-3.5"
                style={{
                  background: COLORS.background.card,
                  borderLeft: `3px solid ${isCorrect ? COLORS.success.main : isWrong ? COLORS.error.main : COLORS.text.tertiary}`
                }}>
                {/* Question */}
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="flex-1">
                    <span className="text-[10px] font-medium px-1.5 py-0.5 rounded mr-2"
                      style={{ background: COLORS.primary.main + '22', color: COLORS.primary.main }}>
                      Q{i + 1}
                    </span>
                    <span className="text-xs" style={{ color: COLORS.text.secondary }}>
                      {pred.question_text_hi || pred.question_text_en}
                    </span>
                  </div>
                  <span className="text-xs font-bold shrink-0" style={{
                    color: isCorrect ? COLORS.success.main : isWrong ? COLORS.error.main : COLORS.text.tertiary
                  }}>
                    {isCorrect ? `+${pred.points_earned}` : isWrong ? '0' : `${pred.points}`} pts
                  </span>
                </div>

                {/* Answer */}
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium"
                    style={{
                      background: isCorrect ? COLORS.success.bg : isWrong ? COLORS.error.bg : COLORS.background.tertiary,
                      color: isCorrect ? COLORS.success.main : isWrong ? COLORS.error.main : COLORS.text.secondary
                    }}>
                    {isCorrect ? <Check size={11} /> : isWrong ? <AlertCircle size={11} /> : null}
                    <span className="font-bold">{pred.selected_option}</span>
                    <span>{selectedOpt?.text_hi || selectedOpt?.text_en || ''}</span>
                  </div>

                  {isWrong && correctOpt && (
                    <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs"
                      style={{ background: COLORS.success.bg, color: COLORS.success.main }}>
                      <Check size={11} /> {pred.correct_option}: {correctOpt.text_hi || correctOpt.text_en}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default function LeaderboardPage({ contestId, match, onBack }) {
  const [data, setData] = useState(null);
  const [myPos, setMyPos] = useState(null);
  const [selectedUserId, setSelectedUserId] = useState(null);
  const [expanded, setExpanded] = useState(false);
  const [loading, setLoading] = useState(true);
  const [showShare, setShowShare] = useState(false);
  const [moodData, setMoodData] = useState(null);
  const [badgeData, setBadgeData] = useState(null);
  const { joinContest, leaveContest, on, off } = useSocketStore();

  const fetchData = useCallback(async () => {
    try {
      const [lbRes, meRes] = await Promise.allSettled([
        apiClient.get(`/contests/${contestId}/leaderboard?limit=50`),
        apiClient.get(`/contests/${contestId}/leaderboard/me`)
      ]);
      if (lbRes.status === 'fulfilled') setData(lbRes.value.data);
      if (meRes.status === 'fulfilled') setMyPos(meRes.value.data);

      // Fetch mood data for ShareCard
      if (match?.id) {
        try {
          const moodRes = await apiClient.get(`/matches/${match.id}/mood-meter`);
          setMoodData(moodRes.data);
        } catch (_) {}
      }
      // Fetch badge data
      try {
        const badgeRes = await apiClient.get('/contests/global/my-badge');
        setBadgeData(badgeRes.data);
      } catch (_) {}
    } catch (_) { /* silent */ }
    finally { setLoading(false); }
  }, [contestId, match?.id]);

  useEffect(() => { fetchData(); }, [fetchData]);

  // Socket.IO: Real-time leaderboard updates
  useEffect(() => {
    if (!contestId) return;
    joinContest(contestId);

    const handleLeaderboardUpdate = (data) => {
      if (data.contest_id === contestId) {
        fetchData(); // Refresh leaderboard when scores change
      }
    };

    const handleQuestionResolved = (data) => {
      if (data.contest_id === contestId) {
        fetchData(); // Refresh when a question is resolved
      }
    };

    const handleContestFinalized = (data) => {
      if (data.contest_id === contestId) {
        fetchData();
      }
    };

    on('leaderboard_update', handleLeaderboardUpdate);
    on('question_resolved', handleQuestionResolved);
    on('contest_finalized', handleContestFinalized);

    return () => {
      leaveContest(contestId);
      off('leaderboard_update', handleLeaderboardUpdate);
      off('question_resolved', handleQuestionResolved);
      off('contest_finalized', handleContestFinalized);
    };
  }, [contestId, joinContest, leaveContest, on, off, fetchData]);

  const rankIcon = (rank) => {
    if (rank === 1) return <Crown size={18} color="#FFD700" />;
    if (rank === 2) return <Medal size={18} color="#C0C0C0" />;
    if (rank === 3) return <Medal size={18} color="#CD7F32" />;
    return <span className="text-xs font-bold" style={{ color: COLORS.text.secondary }}>#{rank}</span>;
  };

  const rankBg = (rank) => {
    if (rank === 1) return 'linear-gradient(135deg, #FFD70015, #FFA50008)';
    if (rank === 2) return 'linear-gradient(135deg, #C0C0C015, #A0A0A008)';
    if (rank === 3) return 'linear-gradient(135deg, #CD7F3215, #8B451308)';
    return COLORS.background.card;
  };

  const leaderboard = data?.leaderboard || [];
  const displayList = expanded ? leaderboard : leaderboard.slice(0, 10);

  return (
    <div data-testid="leaderboard-page" className="pb-6 space-y-4">
      <button data-testid="lb-back-btn" onClick={onBack} className="flex items-center gap-2 text-sm" style={{ color: COLORS.text.secondary }}>
        <ArrowLeft size={16} /> Back
      </button>

      {/* Header */}
      <div className="text-center relative">
        <div className="absolute inset-0 -top-4 opacity-10" style={{ background: 'radial-gradient(circle at 50% 30%, #FFD700, transparent 60%)' }} />
        <div className="relative">
          <Trophy size={36} color={COLORS.accent.gold} className="mx-auto mb-2 animate-float" />
          <h1 className="text-lg font-black text-white" style={{ fontFamily: "'Rajdhani', sans-serif" }}>{data?.contest_name || 'Leaderboard'}</h1>
          <div className="flex items-center justify-center gap-4 mt-2">
            <span className="text-xs" style={{ color: COLORS.text.secondary }}>{data?.total_participants || 0} Players</span>
            <span className="text-xs font-bold" style={{ color: COLORS.accent.gold }}>Pool: {(data?.prize_pool || 0).toLocaleString()}</span>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex justify-center py-10">
          <div className="w-8 h-8 border-2 rounded-full animate-spin" style={{ borderColor: `${COLORS.primary.main}30`, borderTopColor: COLORS.primary.main }} />
        </div>
      )}

      {/* My Position */}
      {myPos && (
        <div data-testid="my-position" className="rounded-2xl p-4 flex items-center justify-between relative overflow-hidden"
          style={{ background: `${COLORS.primary.main}10`, border: `1px solid ${COLORS.primary.main}25` }}>
          <div className="absolute -top-6 -right-6 w-24 h-24 rounded-full opacity-10" style={{ background: `radial-gradient(circle, ${COLORS.primary.main}, transparent)` }} />
          <div className="flex items-center gap-3 relative">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center shadow-lg" style={{ background: COLORS.primary.gradient }}>
              <Star size={18} color="#fff" />
            </div>
            <div>
              <div className="text-sm font-bold text-white">Your Position</div>
              <div className="text-[10px] font-medium" style={{ color: COLORS.text.secondary }}>{myPos.team_name} - {myPos.predictions_count} predictions</div>
            </div>
          </div>
          <div className="text-right relative">
            <div className="text-2xl font-black" style={{ color: COLORS.primary.main, fontFamily: "'Rajdhani', sans-serif" }}>
              #{myPos.rank}
            </div>
            <div className="text-xs font-bold" style={{ color: COLORS.accent.gold }}>{myPos.total_points} pts</div>
          </div>
        </div>
      )}

      {/* Share Button */}
      {myPos && (
        <button data-testid="share-result-btn" onClick={() => setShowShare(true)}
          className="w-full flex items-center justify-center gap-2 py-3.5 rounded-2xl font-bold text-sm text-white transition-transform active:scale-[0.97]"
          style={{ background: 'linear-gradient(135deg, #25D366, #128C7E)', boxShadow: '0 4px 20px rgba(37,211,102,0.25)' }}>
          <Share2 size={16} /> Share Result on WhatsApp
        </button>
      )}

      {/* Leaderboard List */}
      <div className="rounded-2xl overflow-hidden" style={{ background: COLORS.background.card, border: `1px solid rgba(255,255,255,0.06)` }}>
        {displayList.map((entry, i) => (
          <div
            key={entry.user_id}
            data-testid={`lb-entry-${i}`}
            className="flex items-center gap-3 px-4 py-3.5 cursor-pointer transition-all active:opacity-80"
            style={{
              background: rankBg(entry.rank),
              borderBottom: i < displayList.length - 1 ? `1px solid rgba(255,255,255,0.04)` : 'none'
            }}
            onClick={() => setSelectedUserId(entry.user_id)}>
            <div className="w-8 flex justify-center">{rankIcon(entry.rank)}</div>
            <div className="w-9 h-9 rounded-xl flex items-center justify-center text-xs font-black text-white shadow" style={{ background: entry.rank <= 3 ? COLORS.primary.gradient : 'rgba(255,255,255,0.06)' }}>
              {(entry.username || 'U')[0].toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-bold text-white truncate">{entry.username}</div>
              <div className="text-[10px] font-medium" style={{ color: COLORS.text.tertiary }}>{entry.team_name}</div>
            </div>
            <div className="text-right">
              <div className="text-base font-black" style={{ fontFamily: "'Rajdhani', sans-serif", color: entry.rank <= 3 ? COLORS.accent.gold : '#fff' }}>
                {entry.total_points}
              </div>
              {entry.prize_won > 0 && (
                <div className="text-[10px] font-bold" style={{ color: COLORS.success.main }}>+{entry.prize_won}</div>
              )}
            </div>
          </div>
        ))}

        {(!leaderboard || leaderboard.length === 0) && (
          <div className="py-10 text-center text-sm" style={{ color: COLORS.text.tertiary }}>No entries yet</div>
        )}
      </div>

      {/* Show More / Less */}
      {leaderboard.length > 10 && (
        <button
          data-testid="toggle-expand-btn"
          onClick={() => setExpanded(prev => !prev)}
          className="w-full py-2.5 rounded-xl text-xs font-semibold flex items-center justify-center gap-1"
          style={{ background: COLORS.background.card, color: COLORS.text.secondary, border: `1px solid ${COLORS.border.light}` }}>
          {expanded ? <><ChevronUp size={14} /> Show Less</> : <><ChevronDown size={14} /> Show All {leaderboard.length} Players</>}
        </button>
      )}

      {/* User Answer Modal */}
      {selectedUserId && (
        <UserAnswerModal
          contestId={contestId}
          userId={selectedUserId}
          onClose={() => setSelectedUserId(null)}
        />
      )}

      {/* Share Card */}
      {showShare && myPos && (
        <ShareCard
          match={match}
          rank={myPos.rank}
          totalPlayers={data?.total_participants || 0}
          score={myPos.total_points}
          totalPoints={myPos.total_points + 100}
          correctAnswers={myPos.correct_count || 0}
          totalQuestions={myPos.predictions_count || 0}
          moodData={moodData}
          badgeData={badgeData}
          onClose={() => setShowShare(false)}
        />
      )}
    </div>
  );
}
