/**
 * Admin Resolve Page - Auto-Settlement Engine UI
 * Manual resolve + Auto-settle toggle + Live scorecard metrics
 */
import { useState, useEffect, useCallback } from 'react';
import apiClient from '../../api/client';
import { COLORS } from '../../constants/design';
import { ArrowLeft, CheckCircle, Award, AlertCircle, Zap, RefreshCw, Activity, Target, TrendingUp, Clock } from 'lucide-react';

export default function AdminResolvePage() {
  const [contests, setContests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionMsg, setActionMsg] = useState('');
  const [resolvingQ, setResolvingQ] = useState(null);
  const [selectedContest, setSelectedContest] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [resolvedMap, setResolvedMap] = useState({});
  const [finalizing, setFinalizing] = useState(false);
  const [settlementStatus, setSettlementStatus] = useState([]);
  const [settlingMatch, setSettlingMatch] = useState(null);
  const [settlementResult, setSettlementResult] = useState(null);
  const [activeTab, setActiveTab] = useState('contests'); // 'contests' | 'settlement'

  const fetchContests = async () => {
    try {
      const res = await apiClient.get('/contests?limit=100');
      setContests(res.data.contests || []);
    } catch (_) {}
    finally { setLoading(false); }
  };

  const fetchSettlementStatus = useCallback(async () => {
    try {
      const res = await apiClient.get('/admin/settlement/status');
      setSettlementStatus(res.data.matches || []);
    } catch (_) {}
  }, []);

  useEffect(() => {
    fetchContests();
    fetchSettlementStatus();
  }, [fetchSettlementStatus]);

  const loadQuestions = async (contestId) => {
    setActionMsg('Loading questions...');
    try {
      const res = await apiClient.get(`/contests/${contestId}/questions`);
      const qs = res.data.questions || [];
      setQuestions(qs);
      setSelectedContest(contestId);
      const resolved = {};
      qs.forEach(q => { if (q.correct_option) resolved[q.id] = q.correct_option; });
      setResolvedMap(resolved);
      setActionMsg(qs.length > 0 ? '' : 'No questions found');
    } catch (e) {
      setActionMsg(`Error: ${e?.response?.data?.detail || e.message}`);
    }
  };

  const resolveQuestion = async (contestId, questionId, correctOption) => {
    setResolvingQ(questionId);
    try {
      const res = await apiClient.post(`/contests/${contestId}/resolve`, {
        question_id: questionId, correct_option: correctOption
      });
      if (res.data.message === 'Question already resolved') {
        setActionMsg(`Already resolved: ${res.data.correct_option}`);
      } else {
        setActionMsg(`Resolved: ${correctOption} | ${res.data.correct}/${res.data.entries_evaluated} correct`);
      }
      setResolvedMap(prev => ({ ...prev, [questionId]: correctOption }));
    } catch (e) {
      setActionMsg(`Error: ${e?.response?.data?.detail || e.message}`);
    } finally { setResolvingQ(null); }
  };

  const finalizeContest = async (contestId) => {
    setFinalizing(true);
    try {
      const res = await apiClient.post(`/contests/${contestId}/finalize`);
      const topNames = res.data.top_3?.map(t => `#${t.rank} ${t.username}`).join(', ') || 'N/A';
      setActionMsg(`Finalized! ${res.data.prizes_distributed} coins distributed. Winners: ${topNames}`);
      setSelectedContest(null);
      setResolvedMap({});
      fetchContests();
    } catch (e) {
      setActionMsg(`Error: ${e?.response?.data?.detail || e.message}`);
    } finally { setFinalizing(false); }
  };

  // AUTO-SETTLEMENT
  const runAutoSettlement = async (matchId) => {
    setSettlingMatch(matchId);
    setSettlementResult(null);
    try {
      const res = await apiClient.post(`/admin/settlement/${matchId}/run`);
      setSettlementResult(res.data);
      if (res.data.error) {
        setActionMsg(`Settlement: ${res.data.error}`);
      } else {
        setActionMsg(`Auto-settled: ${res.data.total_resolved} resolved, ${res.data.total_skipped} skipped`);
      }
      fetchSettlementStatus();
      fetchContests();
    } catch (e) {
      setActionMsg(`Settlement Error: ${e?.response?.data?.detail || e.message}`);
    } finally { setSettlingMatch(null); }
  };

  const seedAutoQuestions = async () => {
    try {
      const res = await apiClient.post('/admin/questions/bulk-import-with-auto');
      setActionMsg(`${res.data.message}`);
      fetchSettlementStatus();
    } catch (e) {
      setActionMsg(`Error: ${e?.response?.data?.detail || e.message}`);
    }
  };

  const resolvedCount = Object.keys(resolvedMap).length;
  const totalQuestions = questions.length;
  const allResolved = totalQuestions > 0 && resolvedCount >= totalQuestions;
  const progressPct = totalQuestions > 0 ? Math.round((resolvedCount / totalQuestions) * 100) : 0;

  // TAB HEADER
  const TabHeader = () => (
    <div className="flex gap-1 p-1 rounded-xl mb-3" style={{ background: COLORS.background.tertiary }}>
      {[
        { key: 'contests', label: 'Manual Resolve', icon: Target },
        { key: 'settlement', label: 'Auto-Settle', icon: Zap }
      ].map(tab => (
        <button
          key={tab.key}
          data-testid={`tab-${tab.key}`}
          onClick={() => { setActiveTab(tab.key); setSelectedContest(null); setSettlementResult(null); setActionMsg(''); }}
          className="flex-1 py-2.5 rounded-lg text-xs font-bold flex items-center justify-center gap-1.5 transition-all"
          style={{
            background: activeTab === tab.key ? COLORS.accent.gold : 'transparent',
            color: activeTab === tab.key ? '#000' : COLORS.text.tertiary
          }}
        >
          <tab.icon size={14} />
          {tab.label}
        </button>
      ))}
    </div>
  );

  // ==================== RESOLUTION VIEW ====================
  if (selectedContest) {
    const contest = contests.find(c => c.id === selectedContest);
    return (
      <div data-testid="resolve-detail" className="space-y-3">
        <button onClick={() => { setSelectedContest(null); setResolvedMap({}); setActionMsg(''); }}
          className="text-xs flex items-center gap-1" style={{ color: COLORS.text.secondary }}>
          <ArrowLeft size={14} /> Back
        </button>

        <div className="p-3 rounded-xl" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
          <div className="text-sm font-bold text-white mb-2">{contest?.name}</div>
          <div className="flex items-center gap-3">
            <div className="flex-1 h-2 rounded-full overflow-hidden" style={{ background: COLORS.background.tertiary }}>
              <div className="h-full rounded-full transition-all duration-500" style={{ width: `${progressPct}%`, background: allResolved ? COLORS.success.main : COLORS.accent.gold }} />
            </div>
            <span className="text-xs font-bold" style={{ color: allResolved ? COLORS.success.main : COLORS.accent.gold }}>
              {resolvedCount}/{totalQuestions}
            </span>
          </div>
        </div>

        {actionMsg && (
          <div className="text-xs text-center py-2 rounded-xl" style={{ background: COLORS.background.card, color: COLORS.info.main }}>
            {actionMsg}
          </div>
        )}

        <div className="space-y-2.5">
          {questions.map((q, i) => {
            const isResolved = !!resolvedMap[q.id];
            const correctOpt = resolvedMap[q.id];
            const hasAutoRes = !!q.auto_resolution?.metric;
            return (
              <div key={q.id} className="rounded-xl p-3.5 transition-all" style={{
                background: COLORS.background.card,
                border: `1px solid ${isResolved ? COLORS.success.main + '44' : COLORS.border.light}`,
                opacity: isResolved ? 0.7 : 1
              }}>
                <div className="flex items-start justify-between gap-2 mb-2.5">
                  <div className="flex-1">
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded mr-2" style={{ background: COLORS.background.tertiary, color: COLORS.text.tertiary }}>Q{i + 1}</span>
                    {hasAutoRes && (
                      <span className="text-[10px] font-bold px-1.5 py-0.5 rounded mr-2" style={{ background: '#f59e0b22', color: '#f59e0b' }}>AUTO</span>
                    )}
                    <span className="text-xs font-medium text-white">{q.question_text_hi || q.question_text_en}</span>
                    {q.question_text_hi && q.question_text_en && (
                      <div className="text-[10px] mt-1" style={{ color: COLORS.text.tertiary }}>{q.question_text_en}</div>
                    )}
                  </div>
                  {isResolved && (
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full shrink-0" style={{ background: COLORS.success.bg, color: COLORS.success.main }}>
                      {correctOpt}
                    </span>
                  )}
                </div>

                <div className="flex gap-2 flex-wrap">
                  {(q.options || []).map(opt => {
                    const isCorrect = isResolved && opt.key === correctOpt;
                    return (
                      <button key={opt.key}
                        data-testid={`resolve-${q.id}-${opt.key}`}
                        onClick={() => resolveQuestion(selectedContest, q.id, opt.key)}
                        disabled={resolvingQ === q.id || isResolved}
                        className="flex-1 min-w-[80px] py-2.5 rounded-xl text-xs font-bold disabled:opacity-40 transition-all"
                        style={{
                          background: isCorrect ? COLORS.success.main : COLORS.background.tertiary,
                          color: '#fff',
                          border: `1.5px solid ${isCorrect ? COLORS.success.main : COLORS.border.light}`
                        }}>
                        <span className="opacity-60 mr-1">{opt.key}.</span>
                        {opt.text_hi || opt.text_en || opt.key}
                        {opt.min_value != null && (
                          <span className="block text-[9px] opacity-50 mt-0.5">
                            {opt.min_value}-{opt.max_value === 999 ? '+' : opt.max_value}
                          </span>
                        )}
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>

        <button data-testid="finalize-contest-btn"
          onClick={() => finalizeContest(selectedContest)}
          disabled={!allResolved || finalizing}
          className="w-full py-3.5 rounded-xl text-sm font-bold disabled:opacity-30 transition-all"
          style={{
            background: allResolved ? COLORS.accent.gold : COLORS.background.tertiary,
            color: allResolved ? '#000' : COLORS.text.tertiary
          }}>
          {finalizing ? 'Finalizing...'
            : !allResolved ? `Resolve All Questions First (${resolvedCount}/${totalQuestions})`
            : <><Award size={16} className="inline mr-1" /> Finalize & Distribute Prizes</>}
        </button>
      </div>
    );
  }

  // ==================== SETTLEMENT TAB ====================
  if (activeTab === 'settlement') {
    const matchesWithData = settlementStatus.filter(m => m.has_external_id || m.contests_count > 0);
    return (
      <div data-testid="settlement-page" className="space-y-3">
        <TabHeader />

        {actionMsg && (
          <div className="text-xs text-center py-2.5 rounded-xl" style={{ background: COLORS.background.card, color: COLORS.info.main }}>
            {actionMsg}
          </div>
        )}

        {/* Settlement Result */}
        {settlementResult && !settlementResult.error && (
          <div data-testid="settlement-result" className="rounded-xl p-4 space-y-3" style={{ background: '#10b98120', border: '1px solid #10b98140' }}>
            <div className="flex items-center gap-2 text-sm font-bold" style={{ color: '#10b981' }}>
              <Zap size={16} /> Auto-Settlement Report
            </div>

            {/* Key Metrics */}
            {settlementResult.key_metrics && (
              <div className="grid grid-cols-2 gap-2">
                {[
                  { label: '1st Inn', value: `${settlementResult.key_metrics.innings_1_runs} runs` },
                  { label: '2nd Inn', value: `${settlementResult.key_metrics.innings_2_runs} runs` },
                  { label: 'Sixes', value: settlementResult.key_metrics.total_sixes },
                  { label: 'Fours', value: settlementResult.key_metrics.total_fours },
                  { label: 'Top Scorer', value: settlementResult.key_metrics.highest_scorer },
                  { label: 'Best Bowler', value: settlementResult.key_metrics.best_bowler },
                ].map((m, i) => (
                  <div key={i} className="rounded-lg p-2" style={{ background: COLORS.background.card }}>
                    <div className="text-[10px] uppercase" style={{ color: COLORS.text.tertiary }}>{m.label}</div>
                    <div className="text-xs font-bold text-white">{m.value}</div>
                  </div>
                ))}
              </div>
            )}

            {/* Contest Reports */}
            {settlementResult.contests?.map((c, i) => (
              <div key={i} className="rounded-lg p-2.5 flex items-center justify-between" style={{ background: COLORS.background.card }}>
                <div>
                  <div className="text-xs font-semibold text-white">{c.contest_name}</div>
                  <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>
                    {c.auto_resolved} resolved | {c.skipped} skipped | {c.total_questions} total
                  </div>
                </div>
                {c.auto_finalized ? (
                  <span className="text-[10px] px-2 py-1 rounded-full font-bold" style={{ background: '#10b98120', color: '#10b981' }}>
                    Finalized
                  </span>
                ) : c.all_resolved ? (
                  <span className="text-[10px] px-2 py-1 rounded-full font-bold" style={{ background: '#f59e0b20', color: '#f59e0b' }}>
                    Ready
                  </span>
                ) : (
                  <span className="text-[10px] px-2 py-1 rounded-full font-bold" style={{ background: COLORS.background.tertiary, color: COLORS.text.tertiary }}>
                    {c.already_resolved + c.auto_resolved}/{c.total_questions}
                  </span>
                )}
              </div>
            ))}

            <div className="text-[10px] text-center" style={{ color: COLORS.text.tertiary }}>
              Match completed: {settlementResult.match_completed ? 'Yes' : 'No'} | Winner: {settlementResult.match_winner || 'TBD'}
            </div>
          </div>
        )}

        {settlementResult?.error && (
          <div className="rounded-xl p-3 text-xs font-medium" style={{ background: '#ef444420', color: '#ef4444', border: '1px solid #ef444440' }}>
            {settlementResult.error}
          </div>
        )}

        {/* Seed Button */}
        <button
          data-testid="seed-auto-questions"
          onClick={seedAutoQuestions}
          className="w-full py-2.5 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2"
          style={{ background: COLORS.background.card, color: COLORS.accent.gold, border: `1px solid ${COLORS.accent.gold}33` }}
        >
          <TrendingUp size={14} /> Seed 11 Auto-Resolution Questions + Template
        </button>

        {/* Matches List */}
        <div className="text-xs font-semibold uppercase tracking-wider" style={{ color: COLORS.text.tertiary }}>
          Matches ({matchesWithData.length})
        </div>

        {matchesWithData.length === 0 ? (
          <div className="text-center py-8">
            <Activity size={32} color={COLORS.text.tertiary} className="mx-auto mb-2" />
            <div className="text-xs" style={{ color: COLORS.text.tertiary }}>
              No active matches. Sync matches from the Matches tab first.
            </div>
          </div>
        ) : (
          <div className="space-y-2">
            {matchesWithData.map(m => {
              const ta = m.team_a?.short_name || m.team_a?.name || '?';
              const tb = m.team_b?.short_name || m.team_b?.name || '?';
              const progress = m.total_questions > 0
                ? Math.round((m.resolved_questions / m.total_questions) * 100) : 0;
              const isSettling = settlingMatch === m.match_id;
              const isCompleted = m.resolved_questions > 0 && m.resolved_questions >= m.total_questions;

              return (
                <div key={m.match_id} className="rounded-xl p-3.5 space-y-2.5" style={{
                  background: COLORS.background.card,
                  border: `1px solid ${isCompleted ? '#10b98130' : m.has_external_id ? COLORS.accent.gold + '22' : COLORS.border.light}`
                }}>
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-sm font-bold text-white">{ta} vs {tb}</div>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-[10px] px-1.5 py-0.5 rounded font-bold" style={{
                          background: m.match_status === 'live' ? '#ef444420' : m.match_status === 'completed' ? '#10b98120' : COLORS.background.tertiary,
                          color: m.match_status === 'live' ? '#ef4444' : m.match_status === 'completed' ? '#10b981' : COLORS.text.tertiary
                        }}>
                          {m.match_status?.toUpperCase()}
                        </span>
                        <span className="text-[10px]" style={{ color: COLORS.text.tertiary }}>
                          {m.contests_count} contests | {m.settlement_progress} questions
                        </span>
                      </div>
                    </div>
                    {!m.has_external_id && (
                      <span className="text-[9px] px-1.5 py-0.5 rounded" style={{ background: '#f59e0b15', color: '#f59e0b' }}>
                        No API Link
                      </span>
                    )}
                  </div>

                  {/* Progress Bar */}
                  {m.total_questions > 0 && (
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ background: COLORS.background.tertiary }}>
                        <div className="h-full rounded-full transition-all duration-700" style={{
                          width: `${progress}%`,
                          background: isCompleted ? '#10b981' : COLORS.accent.gold
                        }} />
                      </div>
                      <span className="text-[10px] font-bold" style={{ color: isCompleted ? '#10b981' : COLORS.text.tertiary }}>
                        {progress}%
                      </span>
                    </div>
                  )}

                  {/* Auto-Settle Button */}
                  <button
                    data-testid={`settle-${m.match_id}`}
                    onClick={() => runAutoSettlement(m.match_id)}
                    disabled={isSettling || isCompleted}
                    className="w-full py-2.5 rounded-xl text-xs font-bold disabled:opacity-30 transition-all flex items-center justify-center gap-2"
                    style={{
                      background: isCompleted ? '#10b98120' : COLORS.accent.gold,
                      color: isCompleted ? '#10b981' : '#000'
                    }}
                  >
                    {isSettling ? (
                      <><RefreshCw size={14} className="animate-spin" /> Settling...</>
                    ) : isCompleted ? (
                      <><CheckCircle size={14} /> All Settled</>
                    ) : (
                      <><Zap size={14} /> Auto-Settle Now</>
                    )}
                  </button>
                </div>
              );
            })}
          </div>
        )}

        {/* Refresh Button */}
        <button
          data-testid="refresh-settlement"
          onClick={() => { fetchSettlementStatus(); setActionMsg(''); }}
          className="w-full py-2.5 rounded-xl text-xs font-medium flex items-center justify-center gap-2"
          style={{ background: COLORS.background.tertiary, color: COLORS.text.secondary }}
        >
          <RefreshCw size={13} /> Refresh Status
        </button>
      </div>
    );
  }

  // ==================== CONTESTS LIST (Manual Resolve) ====================
  const openContests = contests.filter(c => c.status !== 'completed');
  const completedContests = contests.filter(c => c.status === 'completed');

  return (
    <div data-testid="resolve-page" className="space-y-3">
      <TabHeader />

      {actionMsg && (
        <div className="text-xs text-center py-2 rounded-xl" style={{ background: COLORS.background.card, color: COLORS.info.main }}>
          {actionMsg}
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-10">
          <div className="w-8 h-8 border-2 rounded-full animate-spin" style={{ borderColor: `${COLORS.accent.gold}30`, borderTopColor: COLORS.accent.gold }} />
        </div>
      ) : (
        <>
          {openContests.length === 0 && completedContests.length === 0 && (
            <div className="text-center py-10">
              <AlertCircle size={32} color={COLORS.text.tertiary} className="mx-auto mb-2" />
              <div className="text-sm" style={{ color: COLORS.text.tertiary }}>No contests to resolve</div>
            </div>
          )}

          {openContests.length > 0 && (
            <div className="space-y-2">
              <div className="text-xs font-semibold uppercase tracking-wider" style={{ color: COLORS.warning.main }}>
                Needs Resolution ({openContests.length})
              </div>
              {openContests.map(c => (
                <button key={c.id} data-testid={`resolve-contest-${c.id}`}
                  onClick={() => loadQuestions(c.id)}
                  className="w-full rounded-xl p-3.5 flex items-center justify-between text-left transition-all"
                  style={{ background: COLORS.background.card, border: `1px solid ${COLORS.warning.main}22` }}>
                  <div>
                    <div className="text-sm font-semibold text-white">{c.name}</div>
                    <div className="text-[10px] mt-0.5" style={{ color: COLORS.text.tertiary }}>
                      {c.current_participants || 0} players | {c.prize_pool} coins | {c.status}
                    </div>
                  </div>
                  <span className="text-xs font-bold px-3 py-1.5 rounded-lg" style={{ background: COLORS.warning.bg, color: COLORS.warning.main }}>
                    Resolve
                  </span>
                </button>
              ))}
            </div>
          )}

          {completedContests.length > 0 && (
            <div className="space-y-2 pt-2">
              <div className="text-xs font-semibold uppercase tracking-wider" style={{ color: COLORS.text.tertiary }}>
                Completed ({completedContests.length})
              </div>
              {completedContests.slice(0, 5).map(c => (
                <div key={c.id} className="rounded-xl p-3 flex items-center justify-between opacity-50" style={{ background: COLORS.background.card }}>
                  <div className="text-xs text-white">{c.name}</div>
                  <CheckCircle size={14} color={COLORS.success.main} />
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
