/**
 * Admin Resolve Page - Auto-Settlement + Auto-Pilot + Rich Scorecard
 * Manual resolve + Auto-settle + Auto-Pilot Mode (45s polling)
 */
import { useState, useEffect, useCallback } from 'react';
import apiClient from '../../api/client';
import { COLORS } from '../../constants/design';
import ScorecardView from '../../components/ScorecardView';
import { ArrowLeft, CheckCircle, Award, AlertCircle, Zap, RefreshCw, Activity, Target, Eye, Power } from 'lucide-react';

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
  const [activeTab, setActiveTab] = useState('settlement');
  const [autopilot, setAutopilot] = useState({ running: false, run_count: 0, recent_log: [] });
  const [showScorecard, setShowScorecard] = useState(null);
  const [scorecardData, setScorecardData] = useState(null);
  const [scorecardLoading, setScorecardLoading] = useState(false);

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

  const fetchAutopilotStatus = useCallback(async () => {
    try {
      const res = await apiClient.get('/admin/autopilot/status');
      setAutopilot(res.data);
    } catch (_) {}
  }, []);

  useEffect(() => {
    fetchContests();
    fetchSettlementStatus();
    fetchAutopilotStatus();
    // Poll autopilot status every 10s
    const interval = setInterval(() => {
      if (activeTab === 'settlement') {
        fetchAutopilotStatus();
        fetchSettlementStatus();
      }
    }, 10000);
    return () => clearInterval(interval);
  }, [fetchSettlementStatus, fetchAutopilotStatus, activeTab]);

  const loadQuestions = async (contestId) => {
    setActionMsg('Loading...');
    try {
      const res = await apiClient.get(`/contests/${contestId}/questions`);
      const qs = res.data.questions || [];
      setQuestions(qs);
      setSelectedContest(contestId);
      const resolved = {};
      qs.forEach(q => { if (q.correct_option) resolved[q.id] = q.correct_option; });
      setResolvedMap(resolved);
      setActionMsg('');
    } catch (e) { setActionMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
  };

  const resolveQuestion = async (contestId, questionId, correctOption) => {
    setResolvingQ(questionId);
    try {
      const res = await apiClient.post(`/contests/${contestId}/resolve`, { question_id: questionId, correct_option: correctOption });
      setActionMsg(res.data.message === 'Question already resolved'
        ? `Already: ${res.data.correct_option}`
        : `${correctOption} | ${res.data.correct}/${res.data.entries_evaluated} correct`);
      setResolvedMap(prev => ({ ...prev, [questionId]: correctOption }));
    } catch (e) { setActionMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
    finally { setResolvingQ(null); }
  };

  const finalizeContest = async (contestId) => {
    setFinalizing(true);
    try {
      const res = await apiClient.post(`/contests/${contestId}/finalize`);
      setActionMsg(`Finalized! ${res.data.prizes_distributed} coins distributed`);
      setSelectedContest(null);
      fetchContests();
    } catch (e) { setActionMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
    finally { setFinalizing(false); }
  };

  const runAutoSettlement = async (matchId) => {
    setSettlingMatch(matchId);
    setSettlementResult(null);
    try {
      const res = await apiClient.post(`/admin/settlement/${matchId}/run`);
      setSettlementResult(res.data);
      setActionMsg(res.data.error
        ? `Settlement: ${res.data.error}`
        : `Auto-settled: ${res.data.total_resolved} resolved`);
      fetchSettlementStatus();
      fetchContests();
    } catch (e) { setActionMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
    finally { setSettlingMatch(null); }
  };

  const toggleAutopilot = async () => {
    try {
      if (autopilot.running) {
        const res = await apiClient.post('/admin/autopilot/stop');
        setAutopilot(prev => ({ ...prev, running: false }));
        setActionMsg('Auto-Pilot stopped');
      } else {
        const res = await apiClient.post('/admin/autopilot/start');
        setAutopilot(prev => ({ ...prev, running: true }));
        setActionMsg('Auto-Pilot started! Polling every 45s');
      }
      fetchAutopilotStatus();
    } catch (e) { setActionMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
  };

  const loadScorecard = async (matchId) => {
    setScorecardLoading(true);
    try {
      const res = await apiClient.get(`/admin/scorecard/${matchId}`);
      setScorecardData(res.data);
      setShowScorecard(matchId);
    } catch (e) { setActionMsg(`Scorecard: ${e?.response?.data?.detail || e.message}`); }
    finally { setScorecardLoading(false); }
  };

  const seedAutoQuestions = async () => {
    try {
      const res = await apiClient.post('/admin/questions/bulk-import-with-auto');
      setActionMsg(res.data.message);
    } catch (e) { setActionMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
  };

  // ==================== AI OVERRIDE STATE ====================
  const [aiPreview, setAiPreview] = useState(null);
  const [aiPreviewLoading, setAiPreviewLoading] = useState(false);
  const [aiOverrides, setAiOverrides] = useState({});
  const [aiResolving, setAiResolving] = useState(false);
  const [aiSelectedContest, setAiSelectedContest] = useState(null);
  const [aiContests, setAiContests] = useState([]);

  const fetchAiContests = useCallback(async () => {
    try {
      const res = await apiClient.get('/admin/contests?limit=100');
      setAiContests(res.data.contests || []);
    } catch (_) {}
  }, []);

  useEffect(() => {
    if (activeTab === 'aioverride') fetchAiContests();
  }, [activeTab, fetchAiContests]);

  const loadAiPreview = async (contestId) => {
    setAiPreviewLoading(true);
    setAiPreview(null);
    setAiOverrides({});
    try {
      const res = await apiClient.get(`/admin/contests/${contestId}/ai-preview`);
      setAiPreview(res.data);
      setAiSelectedContest(contestId);
      // Pre-fill with AI answers and resolved answers
      const ov = {};
      (res.data.questions || []).forEach(q => {
        if (q.already_resolved && q.resolved_answer) ov[q.question_id] = q.resolved_answer;
        else if (q.ai_predicted_answer) ov[q.question_id] = q.ai_predicted_answer;
      });
      setAiOverrides(ov);
    } catch (e) { setActionMsg(`AI Preview Error: ${e?.response?.data?.detail || e.message}`); }
    finally { setAiPreviewLoading(false); }
  };

  const submitAiResolve = async (autoFinalize = false) => {
    const answers = Object.entries(aiOverrides)
      .filter(([qid]) => {
        const q = aiPreview?.questions?.find(q => q.question_id === qid);
        return !q?.already_resolved;
      })
      .map(([qid, opt]) => ({ question_id: qid, correct_option: opt }));

    if (answers.length === 0) { setActionMsg('No new answers to submit.'); return; }
    setAiResolving(true);
    try {
      const res = await apiClient.post(`/admin/contests/${aiSelectedContest}/resolve-override`, { answers, auto_finalize: autoFinalize });
      let msg = `Resolved: ${res.data.resolved} | Skipped: ${res.data.skipped}`;
      if (res.data.finalized) msg += ' | FINALIZED!';
      setActionMsg(msg);
      await loadAiPreview(aiSelectedContest);
    } catch (e) { setActionMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
    finally { setAiResolving(false); }
  };

  const resolvedCount = Object.keys(resolvedMap).length;
  const totalQuestions = questions.length;
  const allResolved = totalQuestions > 0 && resolvedCount >= totalQuestions;
  const progressPct = totalQuestions > 0 ? Math.round((resolvedCount / totalQuestions) * 100) : 0;

  // ==================== TAB HEADER (moved up to avoid hoisting issue) ====================
  const TabHeader = () => (
    <div className="flex gap-1 p-1 rounded-xl mb-3" style={{ background: COLORS.background.tertiary }}>
      {[
        { key: 'settlement', label: 'Auto-Settle', icon: Zap },
        { key: 'aioverride', label: 'AI Override', icon: Target },
        { key: 'contests', label: 'Manual', icon: Eye },
      ].map(tab => (
        <button key={tab.key} data-testid={`tab-${tab.key}`}
          onClick={() => { setActiveTab(tab.key); setSettlementResult(null); setActionMsg(''); }}
          className="flex-1 py-2.5 rounded-lg text-xs font-bold flex items-center justify-center gap-1.5 transition-all"
          style={{
            background: activeTab === tab.key ? COLORS.accent.gold : 'transparent',
            color: activeTab === tab.key ? '#000' : COLORS.text.tertiary
          }}>
          <tab.icon size={14} />{tab.label}
        </button>
      ))}
    </div>
  );

  // ==================== AI OVERRIDE VIEW ====================
  if (activeTab === 'aioverride' && aiSelectedContest && aiPreview) {
    const aiResolvedCount = aiPreview.questions?.filter(q => q.already_resolved).length || 0;
    const aiTotalQ = aiPreview.total_questions || 0;
    const aiAnsweredCount = aiPreview.ai_answered_count || 0;
    const aiAllResolved = aiResolvedCount >= aiTotalQ;

    return (
      <div data-testid="ai-override-detail" className="space-y-3">
        <TabHeader />
        <button onClick={() => { setAiSelectedContest(null); setAiPreview(null); }}
          className="text-xs flex items-center gap-1" style={{ color: COLORS.text.secondary }}>
          <ArrowLeft size={14} /> Back
        </button>

        <div className="p-3 rounded-xl" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.primary.main}33` }}>
          <div className="flex items-center gap-2">
            <Target size={18} color={COLORS.primary.main} />
            <div>
              <div className="text-sm font-bold text-white">{aiPreview.contest_name}</div>
              <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>
                {aiPreview.match_label} | {aiPreview.match_status?.toUpperCase()} | {aiPreview.template_type === 'full_match' ? 'Full Match' : 'In-Match'}
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-2">
          <div className="text-center p-2 rounded-lg" style={{ background: COLORS.background.card }}>
            <div className="text-sm font-bold" style={{ color: COLORS.info.main }}>{aiTotalQ}</div>
            <div className="text-[9px]" style={{ color: COLORS.text.tertiary }}>Total Qs</div>
          </div>
          <div className="text-center p-2 rounded-lg" style={{ background: COLORS.background.card }}>
            <div className="text-sm font-bold" style={{ color: COLORS.success.main }}>{aiResolvedCount}</div>
            <div className="text-[9px]" style={{ color: COLORS.text.tertiary }}>Resolved</div>
          </div>
          <div className="text-center p-2 rounded-lg" style={{ background: COLORS.background.card }}>
            <div className="text-sm font-bold" style={{ color: '#f59e0b' }}>{aiAnsweredCount}</div>
            <div className="text-[9px]" style={{ color: COLORS.text.tertiary }}>AI Answers</div>
          </div>
        </div>

        {/* Scorecard Status */}
        <div className="p-2.5 rounded-lg text-xs" style={{
          background: aiPreview.scorecard_available ? '#10b98115' : '#f59e0b15',
          color: aiPreview.scorecard_available ? '#10b981' : '#f59e0b'
        }}>
          {aiPreview.scorecard_available ? (
            <span>Scorecard OK | Runs: {aiPreview.key_metrics?.innings_1_runs || 'N/A'} / {aiPreview.key_metrics?.innings_2_runs || 'N/A'} | 6s: {aiPreview.key_metrics?.total_sixes || 'N/A'} | 4s: {aiPreview.key_metrics?.total_fours || 'N/A'}</span>
          ) : (
            <span>{aiPreview.scorecard_error || 'Scorecard unavailable'}</span>
          )}
        </div>

        {actionMsg && <div className="text-xs text-center py-2 rounded-lg" style={{ background: COLORS.background.card, color: COLORS.info.main }}>{actionMsg}</div>}

        {/* Questions with AI Answers */}
        <div className="space-y-2">
          {(aiPreview.questions || []).map((q, i) => {
            const isResolved = q.already_resolved;
            const currentOverride = aiOverrides[q.question_id];
            const aiAnswer = q.ai_predicted_answer;
            const isEdited = currentOverride && currentOverride !== aiAnswer;

            return (
              <div key={q.question_id} data-testid={`ai-q-${i}`} className="rounded-xl p-3" style={{
                background: COLORS.background.card,
                border: `1px solid ${isResolved ? '#10b98144' : COLORS.border.light}`,
                opacity: isResolved ? 0.65 : 1
              }}>
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="text-xs font-medium text-white">Q{i + 1}: {q.question_text_hi || q.question_text_en}</div>
                    <div className="flex items-center gap-2 mt-1 flex-wrap">
                      <span className="text-[9px] px-1.5 py-0.5 rounded" style={{ background: COLORS.primary.bg, color: COLORS.primary.main }}>{q.category}</span>
                      <span className="text-[9px] font-bold" style={{ color: COLORS.accent.gold }}>{q.points}pts</span>
                      <span className="text-[9px] px-1.5 py-0.5 rounded font-bold" style={{
                        background: q.ai_confidence === 'high' ? '#10b98115' : q.ai_confidence === 'low' ? '#f59e0b15' : '#ef444415',
                        color: q.ai_confidence === 'high' ? '#10b981' : q.ai_confidence === 'low' ? '#f59e0b' : '#ef4444'
                      }}>AI: {q.ai_confidence?.toUpperCase()}</span>
                    </div>
                    {q.ai_reason && <div className="text-[9px] mt-1" style={{ color: COLORS.text.tertiary }}>{q.ai_reason}</div>}
                  </div>
                  {isResolved && <span className="text-[10px] font-bold px-2 py-0.5 rounded-full shrink-0" style={{ background: '#10b98120', color: '#10b981' }}>DONE: {q.resolved_answer}</span>}
                  {isEdited && !isResolved && <span className="text-[10px] font-bold px-2 py-0.5 rounded-full shrink-0" style={{ background: '#f59e0b20', color: '#f59e0b' }}>EDITED</span>}
                </div>

                <div className="flex gap-1.5 flex-wrap">
                  {(q.options || []).map(opt => {
                    const optKey = opt.key;
                    const isAiPick = aiAnswer === optKey;
                    const isSelected = currentOverride === optKey;
                    const isResolvedAns = isResolved && q.resolved_answer === optKey;

                    let bg = COLORS.background.tertiary;
                    let border = COLORS.border.light;
                    if (isResolvedAns) { bg = '#10b981'; border = '#10b981'; }
                    else if (isSelected && isAiPick) { bg = '#2196f333'; border = '#2196f3'; }
                    else if (isSelected && !isAiPick) { bg = '#f59e0b33'; border = '#f59e0b'; }
                    else if (isAiPick) { bg = '#2196f315'; border = '#2196f344'; }

                    return (
                      <button key={optKey} data-testid={`ai-resolve-${q.question_id}-${optKey}`}
                        onClick={() => !isResolved && setAiOverrides(p => ({ ...p, [q.question_id]: optKey }))}
                        disabled={isResolved}
                        className="px-3 py-1.5 rounded-lg text-xs font-semibold disabled:cursor-not-allowed transition-all relative"
                        style={{ background: bg, color: '#fff', border: `1px solid ${border}` }}>
                        {optKey}: {(opt.text_hi || opt.text_en || '').slice(0, 18)}
                        {isAiPick && !isResolved && (
                          <span className="absolute -top-1.5 -right-1.5 text-[7px] px-1 rounded-full font-bold" style={{ background: '#2196f3', color: '#fff' }}>AI</span>
                        )}
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>

        {/* Submit */}
        <div className="space-y-2 pt-2">
          <button onClick={() => submitAiResolve(false)} data-testid="ai-submit-btn"
            disabled={aiResolving || aiAllResolved}
            className="w-full py-3 rounded-xl text-sm font-bold flex items-center justify-center gap-2 disabled:opacity-40"
            style={{ background: COLORS.primary.main, color: '#fff' }}>
            {aiResolving ? <><RefreshCw size={14} className="animate-spin" /> Resolving...</> : `Submit ${Object.keys(aiOverrides).filter(k => !aiPreview?.questions?.find(q => q.question_id === k)?.already_resolved).length} Answers`}
          </button>
          <button onClick={() => submitAiResolve(true)} data-testid="ai-resolve-finalize-btn"
            disabled={aiResolving}
            className="w-full py-2.5 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 disabled:opacity-40"
            style={{ background: COLORS.background.card, color: COLORS.info.main, border: `1px solid ${COLORS.info.main}33` }}>
            <Zap size={12} /> Resolve + Auto-Finalize
          </button>
          {aiAllResolved && (
            <button onClick={async () => {
              try {
                const res = await apiClient.post(`/contests/${aiSelectedContest}/finalize`);
                setActionMsg(`FINALIZED! Prizes: ${res.data.prizes_distributed} coins`);
              } catch (e) { setActionMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
            }} data-testid="ai-finalize-btn"
            className="w-full py-3 rounded-xl text-sm font-bold" style={{ background: COLORS.accent.gold, color: '#000' }}>
              <Award size={14} className="inline mr-1" /> Finalize & Distribute Prizes
            </button>
          )}
        </div>
      </div>
    );
  }

  // ==================== SCORECARD VIEW ====================
  if (showScorecard && scorecardData) {
    return (
      <div className="space-y-3">
        <button onClick={() => { setShowScorecard(null); setScorecardData(null); }}
          className="text-xs flex items-center gap-1" style={{ color: COLORS.text.secondary }}>
          <ArrowLeft size={14} /> Back to Settlement
        </button>
        <div className="text-sm font-bold text-white">{scorecardData.match_name}</div>
        <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>{scorecardData.venue}</div>
        <ScorecardView data={scorecardData} />
      </div>
    );
  }

  // ==================== MANUAL RESOLUTION VIEW ====================
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
          <div className="text-xs text-center py-2 rounded-xl" style={{ background: COLORS.background.card, color: COLORS.info.main }}>{actionMsg}</div>
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
                    {hasAutoRes && <span className="text-[10px] font-bold px-1.5 py-0.5 rounded mr-2" style={{ background: '#f59e0b22', color: '#f59e0b' }}>AUTO</span>}
                    <span className="text-xs font-bold" style={{ color: COLORS.accent.gold }}>{q.points}pts</span>
                    <div className="text-xs font-medium text-white mt-1">{q.question_text_hi || q.question_text_en}</div>
                  </div>
                  {isResolved && (
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full shrink-0" style={{ background: COLORS.success.bg, color: COLORS.success.main }}>{correctOpt}</span>
                  )}
                </div>
                <div className="flex gap-2 flex-wrap">
                  {(q.options || []).map(opt => {
                    const isCorrect = isResolved && opt.key === correctOpt;
                    return (
                      <button key={opt.key} data-testid={`resolve-${q.id}-${opt.key}`}
                        onClick={() => resolveQuestion(selectedContest, q.id, opt.key)}
                        disabled={resolvingQ === q.id || isResolved}
                        className="flex-1 min-w-[70px] py-2.5 rounded-xl text-xs font-bold disabled:opacity-40 transition-all"
                        style={{
                          background: isCorrect ? COLORS.success.main : COLORS.background.tertiary,
                          color: '#fff', border: `1.5px solid ${isCorrect ? COLORS.success.main : COLORS.border.light}`
                        }}>
                        <span className="opacity-60 mr-1">{opt.key}.</span>
                        {opt.text_hi || opt.text_en || opt.key}
                        {opt.min_value != null && (
                          <span className="block text-[9px] opacity-50 mt-0.5">{opt.min_value}-{opt.max_value === 999 ? '+' : opt.max_value}</span>
                        )}
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>

        <button data-testid="finalize-contest-btn" onClick={() => finalizeContest(selectedContest)}
          disabled={!allResolved || finalizing}
          className="w-full py-3.5 rounded-xl text-sm font-bold disabled:opacity-30 transition-all"
          style={{ background: allResolved ? COLORS.accent.gold : COLORS.background.tertiary, color: allResolved ? '#000' : COLORS.text.tertiary }}>
          {finalizing ? 'Finalizing...' : !allResolved ? `Resolve All First (${resolvedCount}/${totalQuestions})` : <><Award size={16} className="inline mr-1" /> Finalize & Distribute Prizes</>}
        </button>
      </div>
    );
  }

  // ==================== SETTLEMENT TAB ====================
  if (activeTab === 'settlement') {
    return (
      <div data-testid="settlement-page" className="space-y-3">
        <TabHeader />

        {/* AUTO-PILOT CONTROL */}
        <div className="rounded-xl p-4" style={{
          background: autopilot.running ? '#10b98110' : COLORS.background.card,
          border: `1px solid ${autopilot.running ? '#10b98140' : COLORS.border.light}`
        }}>
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-bold text-white flex items-center gap-2">
                <Power size={16} color={autopilot.running ? '#10b981' : COLORS.text.tertiary} />
                Auto-Pilot Mode
              </div>
              <div className="text-[10px] mt-0.5" style={{ color: autopilot.running ? '#10b981' : COLORS.text.tertiary }}>
                {autopilot.running
                  ? `Running | Cycle #{autopilot.run_count} | 45s interval`
                  : 'Hands-free settlement. Har 45 sec auto-check.'}
              </div>
            </div>
            <button data-testid="autopilot-toggle" onClick={toggleAutopilot}
              className="px-4 py-2 rounded-xl text-xs font-bold transition-all"
              style={{
                background: autopilot.running ? '#ef444420' : '#10b98120',
                color: autopilot.running ? '#ef4444' : '#10b981',
                border: `1px solid ${autopilot.running ? '#ef444440' : '#10b98140'}`
              }}>
              {autopilot.running ? 'STOP' : 'START'}
            </button>
          </div>

          {/* Auto-Pilot Log */}
          {autopilot.recent_log?.length > 0 && (
            <div className="mt-3 max-h-24 overflow-y-auto rounded-lg p-2 space-y-0.5" style={{ background: COLORS.background.tertiary }}>
              {[...autopilot.recent_log].reverse().map((log, i) => (
                <div key={i} className="text-[10px] font-mono" style={{ color: log.includes('FINALIZED') ? '#10b981' : log.includes('Error') ? '#ef4444' : COLORS.text.tertiary }}>
                  {log}
                </div>
              ))}
            </div>
          )}
        </div>

        {actionMsg && (
          <div className="text-xs text-center py-2.5 rounded-xl" style={{ background: COLORS.background.card, color: COLORS.info.main }}>{actionMsg}</div>
        )}

        {/* Settlement Result */}
        {settlementResult && !settlementResult.error && (
          <div data-testid="settlement-result" className="rounded-xl p-4 space-y-3" style={{ background: '#10b98115', border: '1px solid #10b98130' }}>
            <div className="flex items-center gap-2 text-sm font-bold" style={{ color: '#10b981' }}>
              <Zap size={16} /> Settlement Report
            </div>
            {settlementResult.key_metrics && (
              <div className="grid grid-cols-3 gap-1.5">
                {[
                  { label: '1st Inn', value: `${settlementResult.key_metrics.innings_1_runs}r` },
                  { label: '2nd Inn', value: `${settlementResult.key_metrics.innings_2_runs}r` },
                  { label: 'Sixes', value: settlementResult.key_metrics.total_sixes },
                  { label: 'Fours', value: settlementResult.key_metrics.total_fours },
                  { label: 'Top', value: (settlementResult.key_metrics.highest_scorer || '').slice(0, 15) },
                  { label: 'Bowler', value: (settlementResult.key_metrics.best_bowler || '').slice(0, 15) },
                ].map((m, i) => (
                  <div key={i} className="rounded-lg p-2" style={{ background: COLORS.background.card }}>
                    <div className="text-[9px] uppercase" style={{ color: COLORS.text.tertiary }}>{m.label}</div>
                    <div className="text-xs font-bold text-white">{m.value}</div>
                  </div>
                ))}
              </div>
            )}
            {settlementResult.contests?.map((c, i) => (
              <div key={i} className="rounded-lg p-2.5 flex items-center justify-between" style={{ background: COLORS.background.card }}>
                <div>
                  <div className="text-xs font-semibold text-white">{c.contest_name}</div>
                  <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>
                    {c.auto_resolved} auto | {c.skipped} skip | {c.total_questions} total
                  </div>
                </div>
                <span className="text-[10px] px-2 py-1 rounded-full font-bold" style={{
                  background: c.auto_finalized ? '#10b98120' : c.all_resolved ? '#f59e0b20' : COLORS.background.tertiary,
                  color: c.auto_finalized ? '#10b981' : c.all_resolved ? '#f59e0b' : COLORS.text.tertiary
                }}>
                  {c.auto_finalized ? 'FINALIZED' : c.all_resolved ? 'READY' : `${c.already_resolved + c.auto_resolved}/${c.total_questions}`}
                </span>
              </div>
            ))}
          </div>
        )}

        {settlementResult?.error && (
          <div className="rounded-xl p-3 text-xs font-medium" style={{ background: '#ef444420', color: '#ef4444' }}>{settlementResult.error}</div>
        )}

        {/* Quick Actions */}
        <div className="flex gap-2">
          <button data-testid="seed-auto-questions" onClick={seedAutoQuestions}
            className="flex-1 py-2.5 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5"
            style={{ background: '#f59e0b15', color: '#f59e0b', border: '1px solid #f59e0b22' }}>
            <Zap size={13} /> Seed 11 Auto Questions
          </button>
          <button data-testid="refresh-settlement" onClick={() => { fetchSettlementStatus(); fetchAutopilotStatus(); setActionMsg(''); }}
            className="px-4 py-2.5 rounded-xl text-xs font-medium flex items-center gap-1.5"
            style={{ background: COLORS.background.tertiary, color: COLORS.text.secondary }}>
            <RefreshCw size={13} />
          </button>
        </div>

        {/* Matches List */}
        <div className="text-xs font-semibold uppercase tracking-wider" style={{ color: COLORS.text.tertiary }}>
          IPL Matches ({settlementStatus.length})
        </div>

        {settlementStatus.length === 0 ? (
          <div className="text-center py-8">
            <Activity size={32} color={COLORS.text.tertiary} className="mx-auto mb-2" />
            <div className="text-xs" style={{ color: COLORS.text.tertiary }}>No active matches. Sync from Matches tab.</div>
          </div>
        ) : (
          <div className="space-y-2">
            {settlementStatus.map(m => {
              const ta = m.team_a?.short_name || m.team_a?.name || '?';
              const tb = m.team_b?.short_name || m.team_b?.name || '?';
              const progress = m.total_questions > 0 ? Math.round((m.resolved_questions / m.total_questions) * 100) : 0;
              const isSettling = settlingMatch === m.match_id;
              const isDone = m.resolved_questions > 0 && m.resolved_questions >= m.total_questions;

              return (
                <div key={m.match_id} className="rounded-xl p-3.5 space-y-2.5" style={{
                  background: COLORS.background.card,
                  border: `1px solid ${isDone ? '#10b98130' : COLORS.border.light}`
                }}>
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-sm font-bold text-white">{ta} vs {tb}</div>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-[10px] px-1.5 py-0.5 rounded font-bold" style={{
                          background: m.match_status === 'live' ? '#ef444420' : m.match_status === 'completed' ? '#10b98120' : COLORS.background.tertiary,
                          color: m.match_status === 'live' ? '#ef4444' : m.match_status === 'completed' ? '#10b981' : COLORS.text.tertiary
                        }}>{m.match_status?.toUpperCase()}</span>
                        <span className="text-[10px]" style={{ color: COLORS.text.tertiary }}>
                          {m.contests_count} contests | {m.settlement_progress} Qs
                        </span>
                      </div>
                    </div>
                    {/* View Scorecard */}
                    <button data-testid={`view-scorecard-${m.match_id}`}
                      onClick={() => loadScorecard(m.match_id)}
                      disabled={scorecardLoading}
                      className="p-2 rounded-lg" style={{ background: COLORS.background.tertiary }}>
                      <Eye size={14} color={COLORS.text.secondary} />
                    </button>
                  </div>

                  {m.total_questions > 0 && (
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ background: COLORS.background.tertiary }}>
                        <div className="h-full rounded-full transition-all duration-700" style={{ width: `${progress}%`, background: isDone ? '#10b981' : COLORS.accent.gold }} />
                      </div>
                      <span className="text-[10px] font-bold" style={{ color: isDone ? '#10b981' : COLORS.text.tertiary }}>{progress}%</span>
                    </div>
                  )}

                  <button data-testid={`settle-${m.match_id}`} onClick={() => runAutoSettlement(m.match_id)}
                    disabled={isSettling || isDone}
                    className="w-full py-2.5 rounded-xl text-xs font-bold disabled:opacity-30 transition-all flex items-center justify-center gap-2"
                    style={{ background: isDone ? '#10b98120' : COLORS.accent.gold, color: isDone ? '#10b981' : '#000' }}>
                    {isSettling ? <><RefreshCw size={14} className="animate-spin" /> Settling...</>
                      : isDone ? <><CheckCircle size={14} /> All Settled</>
                      : <><Zap size={14} /> Auto-Settle Now</>}
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    );
  }

  // ==================== AI OVERRIDE TAB (Contest List) ====================
  if (activeTab === 'aioverride' && !aiSelectedContest) {
    return (
      <div data-testid="ai-override-page" className="space-y-3">
        <TabHeader />

        <div className="p-3 rounded-xl" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
          <div className="flex items-center gap-2 mb-2">
            <Target size={16} color={COLORS.primary.main} />
            <span className="text-sm font-bold text-white">AI Override</span>
          </div>
          <div className="text-[10px]" style={{ color: COLORS.text.secondary }}>
            Contest par click karo — AI ka answer dikhega scorecard se. Galat ho toh EDIT karo, phir submit karo.
          </div>
        </div>

        {actionMsg && <div className="text-xs text-center py-2 rounded-lg" style={{ background: COLORS.background.card, color: COLORS.info.main }}>{actionMsg}</div>}

        {aiPreviewLoading && (
          <div className="flex justify-center py-4">
            <div className="w-6 h-6 border-2 rounded-full animate-spin" style={{ borderColor: `${COLORS.primary.main}30`, borderTopColor: COLORS.primary.main }} />
          </div>
        )}

        {aiContests.filter(c => c.status !== 'completed').map(c => {
          const tType = c.template_type || 'full_match';
          return (
            <div key={c.id} className="rounded-xl p-3.5 flex items-center justify-between"
              style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
              <div>
                <div className="text-sm font-semibold text-white">{c.name}</div>
                <div className="flex items-center gap-2 mt-0.5 flex-wrap">
                  <span className="text-[10px]" style={{ color: COLORS.text.tertiary }}>{c.current_participants || 0} players | {c.status}</span>
                  <span className="text-[9px] font-bold px-1.5 py-0.5 rounded" style={{
                    background: tType === 'full_match' ? COLORS.primary.main + '22' : '#f59e0b22',
                    color: tType === 'full_match' ? COLORS.primary.main : '#f59e0b'
                  }}>{tType === 'full_match' ? 'FULL' : 'IN-MATCH'}</span>
                  {c.match_label && <span className="text-[10px]" style={{ color: COLORS.text.tertiary }}>{c.match_label}</span>}
                </div>
              </div>
              <button data-testid={`ai-resolve-${c.id}`} onClick={() => loadAiPreview(c.id)}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1"
                style={{ background: '#2196f320', color: '#2196f3' }}>
                <Target size={12} /> Review AI
              </button>
            </div>
          );
        })}

        {aiContests.filter(c => c.status === 'completed').length > 0 && (
          <>
            <div className="text-xs font-medium pt-2" style={{ color: COLORS.text.tertiary }}>Completed</div>
            {aiContests.filter(c => c.status === 'completed').map(c => (
              <div key={c.id} className="rounded-xl p-3.5 flex items-center justify-between opacity-50" style={{ background: COLORS.background.card }}>
                <div className="text-sm text-white">{c.name}</div>
                <CheckCircle size={14} color={COLORS.success.main} />
              </div>
            ))}
          </>
        )}
      </div>
    );
  }

  // ==================== MANUAL RESOLVE TAB ====================
  const openContests = contests.filter(c => c.status !== 'completed');
  const completedContests = contests.filter(c => c.status === 'completed');

  return (
    <div data-testid="resolve-page" className="space-y-3">
      <TabHeader />

      {actionMsg && (
        <div className="text-xs text-center py-2 rounded-xl" style={{ background: COLORS.background.card, color: COLORS.info.main }}>{actionMsg}</div>
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
              <div className="text-sm" style={{ color: COLORS.text.tertiary }}>No contests</div>
            </div>
          )}

          {openContests.length > 0 && (
            <div className="space-y-2">
              <div className="text-xs font-semibold uppercase tracking-wider" style={{ color: COLORS.warning.main }}>
                Needs Resolution ({openContests.length})
              </div>
              {openContests.map(c => (
                <button key={c.id} data-testid={`resolve-contest-${c.id}`} onClick={() => loadQuestions(c.id)}
                  className="w-full rounded-xl p-3.5 flex items-center justify-between text-left transition-all"
                  style={{ background: COLORS.background.card, border: `1px solid ${COLORS.warning.main}22` }}>
                  <div>
                    <div className="text-sm font-semibold text-white">{c.name}</div>
                    <div className="text-[10px] mt-0.5" style={{ color: COLORS.text.tertiary }}>
                      {c.current_participants || 0} players | {c.prize_pool} coins
                    </div>
                  </div>
                  <span className="text-xs font-bold px-3 py-1.5 rounded-lg" style={{ background: COLORS.warning.bg, color: COLORS.warning.main }}>Resolve</span>
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
