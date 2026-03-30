/**
 * Admin Resolve Page - Resolution Center
 * Resolve questions per contest, finalize, distribute prizes
 */
import { useState, useEffect } from 'react';
import apiClient from '../../api/client';
import { COLORS } from '../../constants/design';
import { ArrowLeft, CheckCircle, Award, AlertCircle } from 'lucide-react';

export default function AdminResolvePage() {
  const [contests, setContests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionMsg, setActionMsg] = useState('');
  const [resolvingQ, setResolvingQ] = useState(null);
  const [selectedContest, setSelectedContest] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [resolvedMap, setResolvedMap] = useState({});
  const [finalizing, setFinalizing] = useState(false);

  const fetchContests = async () => {
    try {
      const res = await apiClient.get('/contests?limit=100');
      setContests(res.data.contests || []);
    } catch (_) {}
    finally { setLoading(false); }
  };

  useEffect(() => { fetchContests(); }, []);

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

  const resolvedCount = Object.keys(resolvedMap).length;
  const totalQuestions = questions.length;
  const allResolved = totalQuestions > 0 && resolvedCount >= totalQuestions;
  const progressPct = totalQuestions > 0 ? Math.round((resolvedCount / totalQuestions) * 100) : 0;

  // RESOLUTION VIEW
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

          {/* Progress Bar */}
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

        {/* Questions List */}
        <div className="space-y-2.5">
          {questions.map((q, i) => {
            const isResolved = !!resolvedMap[q.id];
            const correctOpt = resolvedMap[q.id];
            return (
              <div key={q.id} className="rounded-xl p-3.5 transition-all" style={{
                background: COLORS.background.card,
                border: `1px solid ${isResolved ? COLORS.success.main + '44' : COLORS.border.light}`,
                opacity: isResolved ? 0.7 : 1
              }}>
                <div className="flex items-start justify-between gap-2 mb-2.5">
                  <div className="flex-1">
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded mr-2" style={{ background: COLORS.background.tertiary, color: COLORS.text.tertiary }}>Q{i + 1}</span>
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
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>

        {/* Finalize Button */}
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

  // CONTESTS LIST
  const openContests = contests.filter(c => c.status !== 'completed');
  const completedContests = contests.filter(c => c.status === 'completed');

  return (
    <div data-testid="resolve-page" className="space-y-3">
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
