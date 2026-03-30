import { useState, useEffect } from 'react';
import apiClient from '../api/client';
import { COLORS } from '../constants/design';
import { ArrowLeft, LayoutDashboard, HelpCircle, FileText, Calendar, Trophy, CheckCircle, Award, AlertCircle } from 'lucide-react';
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
  { id: 'resolve', label: 'Resolve', Icon: CheckCircle },
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
