import { useState, useEffect, useCallback } from 'react';
import apiClient from '../api/client';
import { COLORS } from '../constants/design';
import { ArrowLeft, Check, Lock, AlertCircle, BarChart3 } from 'lucide-react';

const OPTION_COLORS = {
  A: { bg: '#E53E3E15', border: '#E53E3E44', active: '#E53E3E' },
  B: { bg: '#3182CE15', border: '#3182CE44', active: '#3182CE' },
  C: { bg: '#38A16915', border: '#38A16944', active: '#38A169' },
  D: { bg: '#D6930015', border: '#D6930044', active: '#D69300' },
};

export default function PredictionPage({ contestId, onBack, onViewLeaderboard }) {
  const [data, setData] = useState(null);
  const [answers, setAnswers] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');
  const [currentQ, setCurrentQ] = useState(0);

  const fetchQuestions = useCallback(async () => {
    try {
      const res = await apiClient.get(`/contests/${contestId}/questions`);
      setData(res.data);
      const existing = {};
      (res.data.my_predictions || []).forEach(p => {
        existing[p.question_id] = p.selected_option;
      });
      if (Object.keys(existing).length > 0) {
        setAnswers(existing);
        setSubmitted(true);
      }
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to load questions');
    }
  }, [contestId]);

  useEffect(() => { fetchQuestions(); }, [fetchQuestions]);

  const selectAnswer = (qid, option) => {
    if (!canEdit) return;
    setAnswers(prev => ({ ...prev, [qid]: option }));
    setSubmitted(false);
  };

  const submitPredictions = async () => {
    if (!data) return;
    const preds = data.questions.map(q => ({
      question_id: q.id,
      selected_option: answers[q.id] || 'A'
    }));

    setSubmitting(true);
    setError('');
    try {
      await apiClient.post(`/contests/${contestId}/predict`, { predictions: preds });
      setSubmitted(true);
    } catch (e) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to submit');
    } finally {
      setSubmitting(false);
    }
  };

  const answeredCount = Object.keys(answers).length;
  const totalQ = data?.questions?.length || 0;
  const isLocked = data?.is_locked;
  const contestStatus = data?.contest_status || '';
  const isStatusLocked = contestStatus && !['open', 'live'].includes(contestStatus);
  const canEdit = !isLocked && !isStatusLocked;

  if (!data) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        {error ? (
          <div className="text-center">
            <AlertCircle size={36} color={COLORS.error.main} className="mx-auto mb-3" />
            <p className="text-sm" style={{ color: COLORS.error.main }}>{error}</p>
            <button onClick={onBack} className="mt-4 px-4 py-2 rounded-lg text-sm" style={{ background: COLORS.background.card, color: COLORS.text.secondary }}>Go Back</button>
          </div>
        ) : (
          <div className="w-8 h-8 border-2 rounded-full animate-spin" style={{ borderColor: `${COLORS.primary.main}30`, borderTopColor: COLORS.primary.main }} />
        )}
      </div>
    );
  }

  const question = data.questions[currentQ];
  const myPred = data.my_predictions?.find(p => p.question_id === question?.id);
  const isResolved = myPred?.is_correct !== undefined && myPred?.is_correct !== null;

  return (
    <div data-testid="prediction-page" className="pb-6 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <button data-testid="pred-back-btn" onClick={onBack} className="flex items-center gap-2 text-sm" style={{ color: COLORS.text.secondary }}>
          <ArrowLeft size={16} /> Back
        </button>
        <div className="flex items-center gap-3">
          {!canEdit && <Lock size={14} color={COLORS.warning.main} />}
          <span className="text-xs font-semibold" style={{ color: !canEdit ? COLORS.warning.main : COLORS.text.secondary }}>
            {isStatusLocked ? `Contest ${contestStatus}` : isLocked ? 'Locked' : `${answeredCount}/${totalQ} Answered`}
          </span>
          <button
            data-testid="view-leaderboard-btn"
            onClick={() => onViewLeaderboard?.(contestId)}
            className="flex items-center gap-1 px-2 py-1 rounded-lg text-xs"
            style={{ background: COLORS.background.card, color: COLORS.accent.gold, border: `1px solid ${COLORS.accent.gold}33` }}>
            <BarChart3 size={12} /> Rank
          </button>
        </div>
      </div>

      {/* Template name */}
      <div className="text-xs font-medium" style={{ color: COLORS.text.tertiary }}>
        {data.template_name} - {totalQ} Questions - {data.total_points} pts
      </div>

      {/* Progress Bar */}
      <div className="h-1.5 rounded-full overflow-hidden" style={{ background: COLORS.background.tertiary }}>
        <div className="h-full rounded-full transition-all duration-500" style={{ width: `${(answeredCount / totalQ) * 100}%`, background: COLORS.primary.main }} />
      </div>

      {/* Question Navigation Dots */}
      <div className="flex gap-1.5 overflow-x-auto pb-2 scrollbar-hide justify-center" style={{ scrollbarWidth: 'none' }}>
        {data.questions.map((q, i) => {
          const pred = data.my_predictions?.find(p => p.question_id === q.id);
          const resolved = pred?.is_correct !== undefined && pred?.is_correct !== null;
          let dotColor = COLORS.background.tertiary;
          if (resolved) {
            dotColor = pred.is_correct ? COLORS.success.main : COLORS.error.main;
          } else if (answers[q.id]) {
            dotColor = COLORS.primary.main;
          }
          return (
            <button key={i} data-testid={`q-dot-${i}`} onClick={() => setCurrentQ(i)}
              className="w-7 h-7 rounded-full flex items-center justify-center text-[10px] font-bold transition-all"
              style={{
                background: i === currentQ ? `${COLORS.primary.main}33` : dotColor + '22',
                border: `2px solid ${i === currentQ ? COLORS.primary.main : dotColor}`,
                color: i === currentQ ? COLORS.primary.main : '#fff'
              }}>
              {i + 1}
            </button>
          );
        })}
      </div>

      {/* Question Card */}
      {question && (
        <div data-testid={`question-${currentQ}`} className="rounded-2xl p-5" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
          {/* Category + Points */}
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-medium px-2 py-0.5 rounded" style={{ background: COLORS.primary.main + '22', color: COLORS.primary.main }}>
              {(question.category || '').replace(/_/g, ' ').toUpperCase()}
            </span>
            <span className="text-xs font-bold" style={{ color: COLORS.accent.gold }}>
              {question.points} pts
            </span>
          </div>

          {/* Question Text (Hindi primary, English secondary) */}
          <h3 className="text-base font-semibold text-white mb-1">{question.question_text_hi || question.question_text_en}</h3>
          {question.question_text_hi && question.question_text_en && (
            <p className="text-xs mb-4" style={{ color: COLORS.text.tertiary }}>{question.question_text_en}</p>
          )}

          {/* Options */}
          <div className="space-y-2.5">
            {(question.options || []).map(opt => {
              const selected = answers[question.id] === opt.key;
              const optColor = OPTION_COLORS[opt.key] || OPTION_COLORS.A;
              const isCorrectOption = isResolved && myPred?.selected_option === opt.key && myPred.is_correct;
              const isWrongOption = isResolved && myPred?.selected_option === opt.key && !myPred.is_correct;

              let borderColor = selected ? optColor.active : optColor.border;
              let bgColor = selected ? optColor.bg : 'transparent';
              if (isCorrectOption) { borderColor = COLORS.success.main; bgColor = COLORS.success.bg; }
              if (isWrongOption) { borderColor = COLORS.error.main; bgColor = COLORS.error.bg; }

              return (
                <button
                  key={opt.key}
                  data-testid={`option-${opt.key}`}
                  onClick={() => selectAnswer(question.id, opt.key)}
                  disabled={!canEdit || isResolved}
                  className="w-full flex items-center gap-3 p-3.5 rounded-xl transition-all text-left disabled:opacity-70"
                  style={{ background: bgColor, border: `2px solid ${borderColor}` }}>
                  <div className="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold shrink-0"
                    style={{ background: selected ? optColor.active : optColor.bg, color: selected ? '#fff' : optColor.active }}>
                    {opt.key}
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-medium text-white">{opt.text_hi || opt.text_en}</div>
                    {opt.text_hi && opt.text_en && <div className="text-xs" style={{ color: COLORS.text.tertiary }}>{opt.text_en}</div>}
                  </div>
                  {isCorrectOption && <Check size={18} color={COLORS.success.main} />}
                  {isWrongOption && <AlertCircle size={18} color={COLORS.error.main} />}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Navigation - Sticky bottom */}
      <div className="flex gap-3 sticky bottom-0 pt-3 pb-2" style={{ background: COLORS.background.primary }}>
        <button
          data-testid="prev-q-btn"
          disabled={currentQ === 0}
          onClick={() => setCurrentQ(c => c - 1)}
          className="flex-1 py-3 rounded-xl text-sm font-semibold disabled:opacity-30"
          style={{ background: COLORS.background.card, color: COLORS.text.secondary, border: `1px solid ${COLORS.border.light}` }}>
          Previous
        </button>
        {currentQ < totalQ - 1 ? (
          <button
            data-testid="next-q-btn"
            onClick={() => setCurrentQ(c => c + 1)}
            className="flex-1 py-3 rounded-xl text-sm font-semibold"
            style={{ background: COLORS.primary.gradient, color: '#fff' }}>
            Next
          </button>
        ) : (
          <button
            data-testid="submit-predictions-btn"
            onClick={submitPredictions}
            disabled={submitting || !canEdit || answeredCount === 0}
            className="flex-1 py-3 rounded-xl text-sm font-bold disabled:opacity-50"
            style={{ background: submitted ? COLORS.success.bg : !canEdit ? COLORS.background.tertiary : COLORS.primary.gradient, color: submitted ? COLORS.success.main : '#fff' }}>
            {submitting ? 'Submitting...' : !canEdit ? 'Locked' : submitted ? 'Submitted!' : `Submit (${answeredCount}/${totalQ})`}
          </button>
        )}
      </div>

      {error && (
        <div data-testid="prediction-error" className="text-center text-sm py-2 rounded-lg" style={{ background: COLORS.error.bg, color: COLORS.error.main }}>
          {error}
        </div>
      )}
    </div>
  );
}
