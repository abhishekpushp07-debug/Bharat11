import { useState, useEffect } from 'react';
import apiClient from '../api/client';
import { COLORS } from '../constants/design';
import { ArrowLeft, LayoutDashboard, HelpCircle, FileText, Calendar, Trophy, CheckCircle, Award, AlertCircle, Loader2, Edit2, Zap, Brain, ShieldCheck, X } from 'lucide-react';
import AdminQuestionsTab from './admin/AdminQuestionsTab';
import AdminTemplatesTab from './admin/AdminTemplatesTab';
import AdminMatchesTab from './admin/AdminMatchesTab';
import AdminContestsTab from './admin/AdminContestsTab';

const TABS = [
  { id: 'dashboard', label: 'Dashboard', Icon: LayoutDashboard },
  { id: 'questions', label: 'Questions', Icon: HelpCircle },
  { id: 'templates', label: 'Templates', Icon: FileText },
  { id: 'matches', label: 'Matches', Icon: Calendar },
  { id: 'contests', label: 'Contests', Icon: Trophy },
  { id: 'resolve', label: 'Auto Resolve', Icon: Brain },
];

// ====== Dashboard Tab ======
function DashboardTab() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await apiClient.get('/admin/stats');
        setStats(res.data);
      } catch (_) { /* silent */ }
      finally { setLoading(false); }
    };
    fetch();
  }, []);

  if (loading) return <div className="flex justify-center py-10"><div className="w-6 h-6 border-2 rounded-full animate-spin" style={{ borderColor: `${COLORS.primary.main}30`, borderTopColor: COLORS.primary.main }} /></div>;

  const cards = [
    { label: 'Users', value: stats?.users || 0, color: COLORS.primary.main },
    { label: 'Questions', value: stats?.questions || 0, color: COLORS.info.main },
    { label: 'Templates', value: stats?.templates || 0, color: COLORS.warning.main },
    { label: 'Matches', value: stats?.matches || 0, color: COLORS.success.main },
    { label: 'Live', value: stats?.live_matches || 0, color: '#FF4444' },
    { label: 'Upcoming', value: stats?.upcoming_matches || 0, color: COLORS.info.main },
    { label: 'Contests', value: stats?.contests || 0, color: COLORS.accent.gold },
    { label: 'Open', value: stats?.open_contests || 0, color: COLORS.success.main },
    { label: 'Entries', value: stats?.active_entries || 0, color: COLORS.primary.main },
  ];

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-3 gap-2">
        {cards.map(c => (
          <div key={c.label} className="text-center p-3 rounded-xl" style={{ background: COLORS.background.card, border: `1px solid ${c.color}22` }}>
            <div className="text-lg font-bold" style={{ color: c.color, fontFamily: "'Rajdhani', sans-serif" }}>{c.value}</div>
            <div className="text-[10px]" style={{ color: COLORS.text.secondary }}>{c.label}</div>
          </div>
        ))}
      </div>

      <div className="p-3 rounded-xl text-xs" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
        <div className="font-semibold text-white mb-2">Admin Flow</div>
        <div className="space-y-1.5" style={{ color: COLORS.text.secondary }}>
          <div>1. <span style={{ color: COLORS.primary.main }}>Questions</span> - Create bilingual questions with points</div>
          <div>2. <span style={{ color: COLORS.warning.main }}>Templates</span> - Group questions (1 Full Match required)</div>
          <div>3. <span style={{ color: COLORS.success.main }}>Matches</span> - Create match, assign templates</div>
          <div>4. <span style={{ color: COLORS.accent.gold }}>Contests</span> - Create contests with entry fee</div>
          <div>5. <span style={{ color: '#FF4444' }}>Resolve</span> - Resolve questions as match progresses</div>
        </div>
      </div>
    </div>
  );
}

// ====== AI Auto-Resolve Tab with Override ======
function ContestResolveTab() {
  const [contests, setContests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedContest, setSelectedContest] = useState(null);
  const [aiPreview, setAiPreview] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [overrides, setOverrides] = useState({});
  const [resolving, setResolving] = useState(false);
  const [actionMsg, setActionMsg] = useState('');

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await apiClient.get('/admin/contests?limit=100');
        setContests(res.data.contests || []);
      } catch (_) { /* silent */ }
      finally { setLoading(false); }
    };
    fetch();
  }, []);

  const loadAiPreview = async (contestId) => {
    setPreviewLoading(true);
    setActionMsg('');
    setAiPreview(null);
    setOverrides({});
    try {
      const res = await apiClient.get(`/admin/contests/${contestId}/ai-preview`);
      setAiPreview(res.data);
      setSelectedContest(contestId);

      // Pre-fill overrides with AI answers and already-resolved answers
      const ov = {};
      (res.data.questions || []).forEach(q => {
        if (q.already_resolved && q.resolved_answer) {
          ov[q.question_id] = q.resolved_answer;
        } else if (q.ai_predicted_answer) {
          ov[q.question_id] = q.ai_predicted_answer;
        }
      });
      setOverrides(ov);
    } catch (e) {
      setActionMsg(`Error loading AI preview: ${e?.response?.data?.detail || e.message}`);
    } finally { setPreviewLoading(false); }
  };

  const submitResolve = async (autoFinalize = false) => {
    const answers = Object.entries(overrides)
      .filter(([qid, opt]) => {
        const q = aiPreview?.questions?.find(q => q.question_id === qid);
        return opt && !q?.already_resolved;
      })
      .map(([qid, opt]) => ({ question_id: qid, correct_option: opt }));

    if (answers.length === 0) {
      setActionMsg('No new questions to resolve. All already resolved or no answers selected.');
      return;
    }

    setResolving(true);
    setActionMsg('');
    try {
      const res = await apiClient.post(`/admin/contests/${selectedContest}/resolve-override`, {
        answers,
        auto_finalize: autoFinalize
      });
      const d = res.data;
      let msg = `Resolved: ${d.resolved} | Skipped: ${d.skipped}`;
      if (d.finalized) msg += ' | Contest FINALIZED!';
      setActionMsg(msg);

      // Refresh preview
      await loadAiPreview(selectedContest);
    } catch (e) {
      setActionMsg(`Error: ${e?.response?.data?.detail || e.message}`);
    } finally { setResolving(false); }
  };

  // Contest detail view with AI preview
  if (selectedContest && aiPreview) {
    const resolvedCount = aiPreview.questions?.filter(q => q.already_resolved).length || 0;
    const totalQ = aiPreview.total_questions || 0;
    const aiAnswered = aiPreview.ai_answered_count || 0;
    const allResolved = resolvedCount >= totalQ;
    const allHaveOverrides = Object.keys(overrides).length >= totalQ;

    return (
      <div className="space-y-3">
        <button onClick={() => { setSelectedContest(null); setAiPreview(null); }}
          className="text-xs flex items-center gap-1" style={{ color: COLORS.text.secondary }}>
          <ArrowLeft size={14} /> Back to Contests
        </button>

        {/* Contest Header */}
        <div className="p-3 rounded-xl" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.primary.main}33` }}>
          <div className="flex items-center gap-2">
            <Brain size={18} color={COLORS.primary.main} />
            <div>
              <div className="text-sm font-bold text-white">{aiPreview.contest_name}</div>
              <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>
                {aiPreview.match_label} | {aiPreview.match_status?.toUpperCase()} | {aiPreview.template_type === 'full_match' ? 'Full Match' : 'In-Match'}
              </div>
            </div>
          </div>
        </div>

        {/* Status Bar */}
        <div className="grid grid-cols-3 gap-2">
          <div className="text-center p-2 rounded-lg" style={{ background: COLORS.background.card }}>
            <div className="text-sm font-bold" style={{ color: COLORS.info.main }}>{totalQ}</div>
            <div className="text-[9px]" style={{ color: COLORS.text.tertiary }}>Total Qs</div>
          </div>
          <div className="text-center p-2 rounded-lg" style={{ background: COLORS.background.card }}>
            <div className="text-sm font-bold" style={{ color: COLORS.success.main }}>{resolvedCount}</div>
            <div className="text-[9px]" style={{ color: COLORS.text.tertiary }}>Resolved</div>
          </div>
          <div className="text-center p-2 rounded-lg" style={{ background: COLORS.background.card }}>
            <div className="text-sm font-bold" style={{ color: '#f59e0b' }}>{aiAnswered}</div>
            <div className="text-[9px]" style={{ color: COLORS.text.tertiary }}>AI Answers</div>
          </div>
        </div>

        {/* Scorecard Status */}
        <div className="p-2.5 rounded-lg text-xs" style={{
          background: aiPreview.scorecard_available ? COLORS.success.bg : COLORS.warning.bg,
          color: aiPreview.scorecard_available ? COLORS.success.main : COLORS.warning.main
        }}>
          {aiPreview.scorecard_available ? (
            <div className="flex items-center gap-2">
              <ShieldCheck size={14} />
              <span>Scorecard loaded | Runs: {aiPreview.key_metrics?.innings_1_runs || 'N/A'} / {aiPreview.key_metrics?.innings_2_runs || 'N/A'} | 6s: {aiPreview.key_metrics?.total_sixes || 'N/A'} | 4s: {aiPreview.key_metrics?.total_fours || 'N/A'}</span>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <AlertCircle size={14} />
              <span>{aiPreview.scorecard_error || 'Scorecard not available'}</span>
            </div>
          )}
        </div>

        {actionMsg && (
          <div className="text-xs text-center py-2 rounded-lg" style={{ background: COLORS.background.card, color: COLORS.info.main }}>
            {actionMsg}
          </div>
        )}

        {/* Questions with AI Answers + Override */}
        <div className="space-y-2">
          {(aiPreview.questions || []).map((q, i) => {
            const isResolved = q.already_resolved;
            const currentOverride = overrides[q.question_id];
            const aiAnswer = q.ai_predicted_answer;
            const isEdited = currentOverride && currentOverride !== aiAnswer;

            return (
              <div key={q.question_id} data-testid={`resolve-q-${i}`}
                className="rounded-xl p-3" style={{
                  background: COLORS.background.card,
                  border: `1px solid ${isResolved ? COLORS.success.main + '44' : COLORS.border.light}`,
                  opacity: isResolved ? 0.7 : 1
                }}>
                {/* Question Header */}
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="text-xs font-medium text-white">Q{i + 1}: {q.question_text_hi || q.question_text_en}</div>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-[9px] px-1.5 py-0.5 rounded" style={{ background: COLORS.primary.bg, color: COLORS.primary.main }}>{q.category}</span>
                      <span className="text-[9px] font-bold" style={{ color: COLORS.accent.gold }}>{q.points} pts</span>
                      {/* AI Confidence Badge */}
                      <span className="text-[9px] px-1.5 py-0.5 rounded font-bold"
                        style={{
                          background: q.ai_confidence === 'high' ? COLORS.success.bg : q.ai_confidence === 'low' ? COLORS.warning.bg : COLORS.error.bg,
                          color: q.ai_confidence === 'high' ? COLORS.success.main : q.ai_confidence === 'low' ? COLORS.warning.main : COLORS.error.main,
                        }}>
                        AI: {q.ai_confidence?.toUpperCase() || 'NONE'}
                      </span>
                    </div>
                    {q.ai_reason && (
                      <div className="text-[9px] mt-1" style={{ color: COLORS.text.tertiary }}>{q.ai_reason}</div>
                    )}
                  </div>
                  {isResolved && (
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full shrink-0" style={{ background: COLORS.success.bg, color: COLORS.success.main }}>
                      RESOLVED: {q.resolved_answer}
                    </span>
                  )}
                  {isEdited && !isResolved && (
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full shrink-0" style={{ background: COLORS.warning.bg, color: COLORS.warning.main }}>
                      <Edit2 size={10} className="inline mr-0.5" /> EDITED
                    </span>
                  )}
                </div>

                {/* Options - Admin can click to override */}
                <div className="flex gap-1.5 flex-wrap">
                  {(q.options || []).map(opt => {
                    const optKey = opt.key;
                    const isAiPick = aiAnswer === optKey;
                    const isSelected = currentOverride === optKey;
                    const isResolvedAnswer = isResolved && q.resolved_answer === optKey;

                    let bgColor = COLORS.background.tertiary;
                    let borderColor = COLORS.border.light;
                    let textColor = '#fff';

                    if (isResolvedAnswer) {
                      bgColor = COLORS.success.main;
                      borderColor = COLORS.success.main;
                    } else if (isSelected && isAiPick) {
                      bgColor = `${COLORS.info.main}33`;
                      borderColor = COLORS.info.main;
                    } else if (isSelected && !isAiPick) {
                      bgColor = `${COLORS.warning.main}33`;
                      borderColor = COLORS.warning.main;
                    } else if (isAiPick && !isSelected) {
                      bgColor = `${COLORS.info.main}15`;
                      borderColor = `${COLORS.info.main}44`;
                    }

                    return (
                      <button key={optKey}
                        data-testid={`resolve-${q.question_id}-${optKey}`}
                        onClick={() => {
                          if (!isResolved) {
                            setOverrides(prev => ({ ...prev, [q.question_id]: optKey }));
                          }
                        }}
                        disabled={isResolved}
                        className="px-3 py-1.5 rounded-lg text-xs font-semibold disabled:cursor-not-allowed transition-all relative"
                        style={{ background: bgColor, color: textColor, border: `1px solid ${borderColor}` }}>
                        {optKey}: {(opt.text_hi || opt.text_en || '').slice(0, 20)}
                        {isAiPick && !isResolved && (
                          <span className="absolute -top-1.5 -right-1.5 text-[7px] px-1 rounded-full font-bold"
                            style={{ background: COLORS.info.main, color: '#fff' }}>AI</span>
                        )}
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>

        {/* Submit Buttons */}
        <div className="space-y-2 pt-2">
          <button onClick={() => submitResolve(false)}
            data-testid="submit-resolve-btn"
            disabled={resolving || allResolved || Object.keys(overrides).filter(k => {
              const q = aiPreview?.questions?.find(q => q.question_id === k);
              return !q?.already_resolved;
            }).length === 0}
            className="w-full py-3 rounded-xl text-sm font-bold flex items-center justify-center gap-2 disabled:opacity-40 transition-all"
            style={{ background: COLORS.primary.main, color: '#fff' }}>
            {resolving ? <Loader2 size={14} className="animate-spin" /> : <ShieldCheck size={14} />}
            {resolving ? 'Resolving...' : `Resolve ${Object.keys(overrides).filter(k => !aiPreview?.questions?.find(q => q.question_id === k)?.already_resolved).length} Answers`}
          </button>

          {allResolved && (
            <button onClick={async () => {
              try {
                const res = await apiClient.post(`/contests/${selectedContest}/finalize`);
                setActionMsg(`FINALIZED! Prizes: ${res.data.prizes_distributed} coins | Top: ${res.data.top_3?.map(t => `#${t.rank} ${t.username}`).join(', ')}`);
              } catch (e) {
                setActionMsg(`Error: ${e?.response?.data?.detail || e.message}`);
              }
            }}
            data-testid="finalize-contest-btn"
            className="w-full py-3 rounded-xl text-sm font-bold flex items-center justify-center gap-2"
            style={{ background: COLORS.accent.gold, color: '#000' }}>
            <Award size={14} /> Finalize & Distribute Prizes
          </button>
          )}

          <button onClick={() => submitResolve(true)}
            data-testid="resolve-and-finalize-btn"
            disabled={resolving || !allHaveOverrides}
            className="w-full py-2.5 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 disabled:opacity-40"
            style={{ background: COLORS.background.card, color: COLORS.info.main, border: `1px solid ${COLORS.info.main}33` }}>
            <Zap size={12} /> Resolve All + Auto-Finalize
          </button>
        </div>
      </div>
    );
  }

  // Contest list for resolution
  return (
    <div className="space-y-3">
      <div className="p-3 rounded-xl" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
        <div className="flex items-center gap-2 mb-2">
          <Brain size={16} color={COLORS.primary.main} />
          <span className="text-sm font-bold text-white">AI Auto-Resolve</span>
        </div>
        <div className="text-[10px]" style={{ color: COLORS.text.secondary }}>
          Click any contest to see AI's predicted answers from scorecard data. Review, edit if wrong, then submit.
        </div>
      </div>

      {actionMsg && (
        <div className="text-xs text-center py-1.5 rounded-lg" style={{ background: COLORS.background.card, color: COLORS.info.main }}>
          {actionMsg}
        </div>
      )}

      {previewLoading && (
        <div className="flex justify-center py-4">
          <Loader2 size={24} className="animate-spin" color={COLORS.primary.main} />
        </div>
      )}

      {loading ? (
        <div className="py-10 text-center"><div className="w-6 h-6 border-2 rounded-full animate-spin mx-auto" style={{ borderColor: `${COLORS.primary.main}30`, borderTopColor: COLORS.primary.main }} /></div>
      ) : (
        <>
          {/* Active Contests */}
          {contests.filter(c => c.status !== 'completed').map(c => {
            const templateType = c.template_type || 'full_match';
            return (
              <div key={c.id} className="rounded-xl p-3.5 flex items-center justify-between"
                style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
                <div>
                  <div className="text-sm font-semibold text-white">{c.name}</div>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-[10px]" style={{ color: COLORS.text.tertiary }}>
                      {c.current_participants || 0} players | {c.status}
                    </span>
                    <span className="text-[9px] font-bold px-1.5 py-0.5 rounded"
                      style={{
                        background: templateType === 'full_match' ? COLORS.primary.main + '22' : COLORS.warning.bg,
                        color: templateType === 'full_match' ? COLORS.primary.main : COLORS.warning.main
                      }}>
                      {templateType === 'full_match' ? 'FULL' : 'IN-MATCH'}
                    </span>
                    {c.match_label && <span className="text-[10px]" style={{ color: COLORS.text.tertiary }}>{c.match_label}</span>}
                  </div>
                </div>
                <button onClick={() => loadAiPreview(c.id)}
                  data-testid={`resolve-btn-${c.id}`}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1"
                  style={{ background: COLORS.warning.bg, color: COLORS.warning.main }}>
                  <Brain size={12} /> Resolve
                </button>
              </div>
            );
          })}

          {/* Completed */}
          {contests.filter(c => c.status === 'completed').length > 0 && (
            <>
              <div className="text-xs font-medium pt-2" style={{ color: COLORS.text.tertiary }}>Completed</div>
              {contests.filter(c => c.status === 'completed').map(c => (
                <div key={c.id} className="rounded-xl p-3.5 flex items-center justify-between opacity-60" style={{ background: COLORS.background.card }}>
                  <div className="text-sm text-white">{c.name}</div>
                  <CheckCircle size={14} color={COLORS.success.main} />
                </div>
              ))}
            </>
          )}
        </>
      )}
    </div>
  );
}

// ====== Main Admin Page ======
export default function AdminPage({ onBack }) {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div data-testid="admin-page" className="pb-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <button data-testid="admin-back-btn" onClick={onBack} className="p-1.5 rounded-lg" style={{ background: COLORS.background.card }}>
          <ArrowLeft size={18} color={COLORS.text.secondary} />
        </button>
        <h1 className="text-lg font-bold text-white">Admin Panel</h1>
      </div>

      {/* Tab Bar - Scrollable */}
      <div className="flex gap-1 overflow-x-auto pb-3 -mx-1 px-1 no-scrollbar" style={{ scrollbarWidth: 'none' }}>
        {TABS.map(({ id, label, Icon }) => (
          <button key={id} data-testid={`admin-tab-${id}`}
            onClick={() => setActiveTab(id)}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all shrink-0"
            style={{
              background: activeTab === id ? COLORS.primary.main : COLORS.background.card,
              color: activeTab === id ? '#fff' : COLORS.text.secondary,
              border: `1px solid ${activeTab === id ? COLORS.primary.main : COLORS.border.light}`
            }}>
            <Icon size={14} />
            {label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'dashboard' && <DashboardTab />}
      {activeTab === 'questions' && <AdminQuestionsTab />}
      {activeTab === 'templates' && <AdminTemplatesTab />}
      {activeTab === 'matches' && <AdminMatchesTab />}
      {activeTab === 'contests' && <AdminContestsTab />}
      {activeTab === 'resolve' && <ContestResolveTab />}
    </div>
  );
}
