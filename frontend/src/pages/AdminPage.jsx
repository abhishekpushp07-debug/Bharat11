import { useState, useEffect, useCallback } from 'react';
import apiClient from '../api/client';
import { COLORS } from '../constants/design';
import { ArrowLeft, Users, Trophy, Coins, Play, CheckCircle, AlertCircle, Plus, RefreshCw, Settings, ChevronRight, ChevronDown, Award } from 'lucide-react';

// ====== Dashboard Tab ======
function DashboardTab() {
  const [stats, setStats] = useState(null);
  useEffect(() => {
    const fetch = async () => {
      try {
        const [mRes, cRes] = await Promise.allSettled([
          apiClient.get('/matches?limit=50'),
          apiClient.get('/contests?limit=50')
        ]);
        const matches = mRes.status === 'fulfilled' ? mRes.value.data.matches || [] : [];
        const contests = cRes.status === 'fulfilled' ? cRes.value.data.contests || [] : [];
        setStats({
          totalMatches: matches.length,
          liveMatches: matches.filter(m => m.status === 'live').length,
          upcomingMatches: matches.filter(m => m.status === 'upcoming').length,
          totalContests: contests.length,
          openContests: contests.filter(c => c.status === 'open').length,
          completedContests: contests.filter(c => c.status === 'completed').length,
        });
      } catch (_) { /* silent */ }
    };
    fetch();
  }, []);

  if (!stats) return <div className="py-10 text-center"><div className="w-6 h-6 border-2 rounded-full animate-spin mx-auto" style={{ borderColor: `${COLORS.primary.main}30`, borderTopColor: COLORS.primary.main }} /></div>;

  const cards = [
    { label: 'Total Matches', val: stats.totalMatches, icon: Play, color: COLORS.info.main },
    { label: 'Live', val: stats.liveMatches, icon: Play, color: COLORS.primary.main },
    { label: 'Upcoming', val: stats.upcomingMatches, icon: Play, color: COLORS.warning.main },
    { label: 'Total Contests', val: stats.totalContests, icon: Trophy, color: COLORS.accent.gold },
    { label: 'Open', val: stats.openContests, icon: Trophy, color: COLORS.success.main },
    { label: 'Completed', val: stats.completedContests, icon: CheckCircle, color: COLORS.text.tertiary },
  ];

  return (
    <div className="grid grid-cols-2 gap-2.5">
      {cards.map((c, i) => (
        <div key={i} className="rounded-xl p-3.5" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
          <c.icon size={16} color={c.color} />
          <div className="text-2xl font-bold mt-1" style={{ color: c.color, fontFamily: "'Rajdhani', sans-serif" }}>{c.val}</div>
          <div className="text-xs" style={{ color: COLORS.text.secondary }}>{c.label}</div>
        </div>
      ))}
    </div>
  );
}

// ====== Match Manager Tab ======
function MatchManagerTab() {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [expandedMatch, setExpandedMatch] = useState(null);
  const [actionMsg, setActionMsg] = useState('');

  const fetchMatches = useCallback(async () => {
    try {
      const res = await apiClient.get('/matches?limit=50');
      setMatches(res.data.matches || []);
    } catch (_) { /* silent */ }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchMatches(); }, [fetchMatches]);

  const syncCricbuzz = async () => {
    setSyncing(true);
    try {
      const res = await apiClient.post('/matches/live/sync');
      if (res.data.message) {
        setActionMsg(res.data.message);
      } else {
        setActionMsg(`Synced: ${res.data.created || 0} new, ${res.data.updated || 0} updated`);
      }
      fetchMatches();
    } catch (e) {
      setActionMsg(`Sync failed: ${e?.response?.data?.detail || e.message}`);
    } finally { setSyncing(false); }
  };

  const updateStatus = async (matchId, newStatus) => {
    try {
      await apiClient.put(`/matches/${matchId}/status`, { status: newStatus });
      setActionMsg(`Match status -> ${newStatus}`);
      fetchMatches();
    } catch (e) {
      setActionMsg(`Error: ${e?.response?.data?.detail || e.message}`);
    }
  };

  return (
    <div className="space-y-3">
      <button data-testid="sync-cricbuzz-btn" onClick={syncCricbuzz} disabled={syncing}
        className="w-full py-3 rounded-xl text-sm font-semibold flex items-center justify-center gap-2"
        style={{ background: COLORS.primary.gradient, color: '#fff' }}>
        <RefreshCw size={14} className={syncing ? 'animate-spin' : ''} />
        {syncing ? 'Syncing...' : 'Sync from Cricbuzz'}
      </button>

      {actionMsg && <div className="text-xs text-center py-1.5 rounded-lg" style={{ background: COLORS.background.card, color: COLORS.info.main }}>{actionMsg}</div>}

      {loading ? (
        <div className="py-10 text-center"><div className="w-6 h-6 border-2 rounded-full animate-spin mx-auto" style={{ borderColor: `${COLORS.primary.main}30`, borderTopColor: COLORS.primary.main }} /></div>
      ) : matches.map(m => (
        <div key={m.id} className="rounded-xl overflow-hidden" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
          <div className="p-3.5 flex items-center justify-between cursor-pointer" onClick={() => setExpandedMatch(expandedMatch === m.id ? null : m.id)}>
            <div className="flex-1">
              <div className="text-sm font-semibold text-white">{m.team_a?.short_name} vs {m.team_b?.short_name}</div>
              <div className="text-xs mt-0.5" style={{ color: COLORS.text.tertiary }}>{m.tournament} | {m.status}</div>
            </div>
            <span className="text-xs px-2 py-0.5 rounded font-semibold" style={{
              color: m.status === 'live' ? COLORS.primary.main : m.status === 'completed' ? COLORS.text.tertiary : COLORS.success.main,
              background: m.status === 'live' ? COLORS.primary.main + '22' : m.status === 'completed' ? COLORS.background.tertiary : COLORS.success.bg
            }}>{m.status.toUpperCase()}</span>
            <ChevronDown size={14} color={COLORS.text.secondary} className="ml-2" />
          </div>

          {expandedMatch === m.id && (
            <div className="px-3.5 pb-3.5 space-y-2" style={{ borderTop: `1px solid ${COLORS.border.light}` }}>
              <div className="text-xs pt-2" style={{ color: COLORS.text.tertiary }}>ID: {m.id}</div>
              <div className="flex gap-2 flex-wrap">
                {['upcoming', 'live', 'completed', 'abandoned'].map(s => (
                  <button key={s} onClick={() => updateStatus(m.id, s)}
                    disabled={m.status === s}
                    className="px-2.5 py-1.5 rounded-lg text-xs font-medium disabled:opacity-30"
                    style={{ background: COLORS.background.tertiary, color: COLORS.text.secondary, border: `1px solid ${COLORS.border.light}` }}>
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// ====== Contest Resolution Tab ======
function ContestResolveTab() {
  const [contests, setContests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionMsg, setActionMsg] = useState('');
  const [resolvingQ, setResolvingQ] = useState(null);
  const [selectedContest, setSelectedContest] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [resolvedMap, setResolvedMap] = useState({});
  const [finalizing, setFinalizing] = useState(false);

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await apiClient.get('/contests?limit=50');
        setContests(res.data.contests || []);
      } catch (_) { /* silent */ }
      finally { setLoading(false); }
    };
    fetch();
  }, []);

  const loadQuestions = async (contestId) => {
    setActionMsg('Loading questions...');
    try {
      const res = await apiClient.get(`/contests/${contestId}/questions`);
      const qs = res.data.questions || [];
      setQuestions(qs);
      setSelectedContest(contestId);

      // Check which questions are already resolved by looking at correct_option
      const resolved = {};
      qs.forEach(q => {
        if (q.correct_option) {
          resolved[q.id] = q.correct_option;
        }
      });
      setResolvedMap(resolved);
      setActionMsg(qs.length > 0 ? '' : 'No questions found');
    } catch (e) {
      setActionMsg(`Error loading questions: ${e?.response?.data?.detail || e.message}`);
      console.error('Load questions error:', e);
    }
  };

  const resolveQuestion = async (contestId, questionId, correctOption) => {
    setResolvingQ(questionId);
    try {
      const res = await apiClient.post(`/contests/${contestId}/resolve`, {
        question_id: questionId,
        correct_option: correctOption
      });
      if (res.data.message === 'Question already resolved') {
        setActionMsg(`Already resolved with ${res.data.correct_option}`);
      } else {
        setActionMsg(`Q resolved: ${correctOption} | ${res.data.correct}/${res.data.entries_evaluated} correct`);
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
      const topNames = res.data.top_3?.map(t => `#${t.rank} ${t.username || t.team_name}`).join(', ') || 'N/A';
      setActionMsg(`Finalized! ${res.data.prizes_distributed} coins distributed. Top: ${topNames}`);
      setSelectedContest(null);
      setResolvedMap({});
      // Refresh
      const cRes = await apiClient.get('/contests?limit=50');
      setContests(cRes.data.contests || []);
    } catch (e) {
      setActionMsg(`Error: ${e?.response?.data?.detail || e.message}`);
    } finally { setFinalizing(false); }
  };

  const resolvedCount = Object.keys(resolvedMap).length;
  const totalQuestions = questions.length;
  const allResolved = totalQuestions > 0 && resolvedCount >= totalQuestions;

  if (selectedContest) {
    const contest = contests.find(c => c.id === selectedContest);
    return (
      <div className="space-y-3">
        <button onClick={() => { setSelectedContest(null); setResolvedMap({}); }} className="text-xs flex items-center gap-1" style={{ color: COLORS.text.secondary }}>
          <ArrowLeft size={14} /> Back to Contests
        </button>

        <div className="text-sm font-semibold text-white">{contest?.name} - Resolve Questions</div>

        {/* Resolution Progress */}
        <div className="flex items-center gap-2 text-xs" style={{ color: allResolved ? COLORS.success.main : COLORS.warning.main }}>
          <CheckCircle size={13} />
          <span>{resolvedCount}/{totalQuestions} Questions Resolved</span>
        </div>

        {actionMsg && <div className="text-xs text-center py-1.5 rounded-lg" style={{ background: COLORS.background.card, color: COLORS.info.main }}>{actionMsg}</div>}

        <div className="space-y-2">
          {questions.map((q, i) => {
            const isResolved = !!resolvedMap[q.id];
            const correctOpt = resolvedMap[q.id];
            return (
              <div key={q.id} className="rounded-xl p-3" style={{
                background: COLORS.background.card,
                border: `1px solid ${isResolved ? COLORS.success.main + '44' : COLORS.border.light}`,
                opacity: isResolved ? 0.75 : 1
              }}>
                <div className="flex items-center justify-between mb-2">
                  <div className="text-xs font-medium text-white flex-1">Q{i + 1}: {q.question_text_hi || q.question_text_en}</div>
                  {isResolved && (
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full ml-2 shrink-0" style={{ background: COLORS.success.bg, color: COLORS.success.main }}>
                      ANS: {correctOpt}
                    </span>
                  )}
                </div>
                <div className="flex gap-1.5 flex-wrap">
                  {(q.options || []).map(opt => {
                    const isCorrectAnswer = isResolved && opt.key === correctOpt;
                    return (
                      <button key={opt.key}
                        data-testid={`resolve-${q.id}-${opt.key}`}
                        onClick={() => resolveQuestion(selectedContest, q.id, opt.key)}
                        disabled={resolvingQ === q.id || isResolved}
                        className="px-3 py-1.5 rounded-lg text-xs font-semibold disabled:opacity-50 transition-all"
                        style={{
                          background: isCorrectAnswer ? COLORS.success.main : COLORS.background.tertiary,
                          color: isCorrectAnswer ? '#fff' : '#fff',
                          border: `1px solid ${isCorrectAnswer ? COLORS.success.main : COLORS.border.light}`
                        }}>
                        {opt.key}: {(opt.text_hi || opt.text_en || '').slice(0, 15)}
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>

        <button onClick={() => finalizeContest(selectedContest)}
          data-testid="finalize-contest-btn"
          disabled={!allResolved || finalizing}
          className="w-full py-3 rounded-xl text-sm font-bold disabled:opacity-40 transition-all"
          style={{ background: allResolved ? COLORS.accent.gold : COLORS.background.tertiary, color: allResolved ? '#000' : COLORS.text.tertiary }}>
          {finalizing ? 'Finalizing...' : !allResolved ? `Resolve All Questions First (${resolvedCount}/${totalQuestions})` : <><Award size={14} className="inline mr-1" /> Finalize & Distribute Prizes</>}
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {actionMsg && <div className="text-xs text-center py-1.5 rounded-lg" style={{ background: COLORS.background.card, color: COLORS.info.main }}>{actionMsg}</div>}

      {loading ? (
        <div className="py-10 text-center"><div className="w-6 h-6 border-2 rounded-full animate-spin mx-auto" style={{ borderColor: `${COLORS.primary.main}30`, borderTopColor: COLORS.primary.main }} /></div>
      ) : contests.filter(c => c.status !== 'completed').map(c => (
        <div key={c.id} className="rounded-xl p-3.5 flex items-center justify-between" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
          <div>
            <div className="text-sm font-semibold text-white">{c.name}</div>
            <div className="text-xs mt-0.5" style={{ color: COLORS.text.tertiary }}>
              {c.current_participants || 0} players | {c.status}
            </div>
          </div>
          <button onClick={() => loadQuestions(c.id)}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold"
            style={{ background: COLORS.warning.bg, color: COLORS.warning.main }}>
            Resolve
          </button>
        </div>
      ))}

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
    </div>
  );
}

// ====== Main Admin Page ======
export default function AdminPage({ onBack }) {
  const [tab, setTab] = useState('dashboard');

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: Settings },
    { id: 'matches', label: 'Matches', icon: Play },
    { id: 'resolve', label: 'Resolve', icon: Award },
  ];

  return (
    <div data-testid="admin-page" className="pb-6 space-y-4">
      <div className="flex items-center gap-3">
        <button data-testid="admin-back-btn" onClick={onBack} className="p-1.5 rounded-lg" style={{ background: COLORS.background.card }}>
          <ArrowLeft size={16} color={COLORS.text.secondary} />
        </button>
        <h1 className="text-lg font-bold text-white">Admin Panel</h1>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        {tabs.map(t => (
          <button key={t.id} data-testid={`admin-tab-${t.id}`} onClick={() => setTab(t.id)}
            className="flex-1 py-2.5 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
            style={{
              background: tab === t.id ? COLORS.primary.main : COLORS.background.card,
              color: tab === t.id ? '#fff' : COLORS.text.secondary,
              border: `1px solid ${tab === t.id ? COLORS.primary.main : COLORS.border.light}`
            }}>
            <t.icon size={13} /> {t.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {tab === 'dashboard' && <DashboardTab />}
      {tab === 'matches' && <MatchManagerTab />}
      {tab === 'resolve' && <ContestResolveTab />}
    </div>
  );
}
