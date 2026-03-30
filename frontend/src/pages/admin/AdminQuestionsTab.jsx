/**
 * Admin Questions Tab - Enhanced with Auto-Resolution support
 * Each question has: text (EN+HI), options (with ranges), points, auto_resolution config
 */
import { useState, useEffect } from 'react';
import apiClient from '../../api/client';
import { COLORS } from '../../constants/design';
import { Plus, Edit2, Trash2, ChevronDown, ChevronUp, X, Zap } from 'lucide-react';

const CATEGORIES = [
  { value: 'batting', label: 'Batting' },
  { value: 'bowling', label: 'Bowling' },
  { value: 'powerplay', label: 'Powerplay' },
  { value: 'death_overs', label: 'Death Overs' },
  { value: 'match', label: 'Match' },
  { value: 'player_performance', label: 'Player' },
  { value: 'special', label: 'Special' },
];

const DIFFICULTIES = ['easy', 'medium', 'hard'];

const METRICS = [
  { value: '', label: 'None (Manual)' },
  { value: 'innings_1_total_runs', label: '1st Inn Total Runs' },
  { value: 'innings_2_total_runs', label: '2nd Inn Total Runs' },
  { value: 'match_total_runs', label: 'Match Total Runs' },
  { value: 'innings_1_total_wickets', label: '1st Inn Wickets' },
  { value: 'innings_2_total_wickets', label: '2nd Inn Wickets' },
  { value: 'match_total_sixes', label: 'Match Total Sixes' },
  { value: 'innings_1_total_sixes', label: '1st Inn Sixes' },
  { value: 'innings_2_total_sixes', label: '2nd Inn Sixes' },
  { value: 'match_total_fours', label: 'Match Total Fours' },
  { value: 'innings_1_total_fours', label: '1st Inn Fours' },
  { value: 'match_total_extras', label: 'Match Total Extras' },
  { value: 'innings_1_run_rate', label: '1st Inn Run Rate' },
  { value: 'innings_2_run_rate', label: '2nd Inn Run Rate' },
  { value: 'highest_run_scorer_runs', label: 'Highest Score (Runs)' },
  { value: 'best_bowler_wickets', label: 'Best Bowler Wickets' },
  { value: 'innings_1_highest_score', label: '1st Inn Highest Score' },
  { value: 'innings_1_maiden_overs', label: '1st Inn Maiden Overs' },
  { value: 'match_winner', label: 'Match Winner (Text)' },
  { value: 'toss_winner', label: 'Toss Winner (Text)' },
];

const TRIGGERS = [
  { value: 'match_end', label: 'Match End' },
  { value: 'innings_1_end', label: '1st Innings End' },
  { value: 'innings_2_end', label: '2nd Innings End' },
  { value: 'toss', label: 'After Toss' },
];

function QuestionForm({ initial, onSave, onCancel }) {
  const [form, setForm] = useState(() => {
    if (initial) {
      return {
        ...initial,
        options: (initial.options || []).map(o => ({
          key: o.key, text_en: o.text_en || '', text_hi: o.text_hi || '',
          min_value: o.min_value ?? '', max_value: o.max_value ?? ''
        })),
        auto_metric: initial.auto_resolution?.metric || '',
        auto_trigger: initial.auto_resolution?.trigger || 'match_end',
        auto_type: initial.auto_resolution?.resolution_type || 'range',
      };
    }
    return {
      question_text_en: '', question_text_hi: '',
      category: 'match', difficulty: 'easy', points: 10,
      options: [
        { key: 'A', text_en: '', text_hi: '', min_value: '', max_value: '' },
        { key: 'B', text_en: '', text_hi: '', min_value: '', max_value: '' },
      ],
      auto_metric: '', auto_trigger: 'match_end', auto_type: 'range',
      is_active: true,
    };
  });
  const [saving, setSaving] = useState(false);
  const [showAutoConfig, setShowAutoConfig] = useState(!!form.auto_metric);

  const updateOption = (idx, field, value) => {
    const opts = [...form.options];
    opts[idx] = { ...opts[idx], [field]: value };
    setForm({ ...form, options: opts });
  };

  const addOption = () => {
    if (form.options.length >= 4) return;
    const keys = ['A', 'B', 'C', 'D'];
    setForm({
      ...form,
      options: [...form.options, { key: keys[form.options.length], text_en: '', text_hi: '', min_value: '', max_value: '' }]
    });
  };

  const removeOption = (idx) => {
    if (form.options.length <= 2) return;
    const keys = ['A', 'B', 'C', 'D'];
    setForm({ ...form, options: form.options.filter((_, i) => i !== idx).map((o, i) => ({ ...o, key: keys[i] })) });
  };

  const handleSave = async () => {
    if (!form.question_text_en.trim()) return;
    setSaving(true);
    try {
      const payload = {
        question_text_en: form.question_text_en,
        question_text_hi: form.question_text_hi,
        category: form.category,
        difficulty: form.difficulty,
        points: form.points,
        options: form.options.map(o => ({
          key: o.key, text_en: o.text_en, text_hi: o.text_hi,
          min_value: o.min_value !== '' ? parseFloat(o.min_value) : null,
          max_value: o.max_value !== '' ? parseFloat(o.max_value) : null,
        })),
        is_active: form.is_active !== false,
      };
      if (form.auto_metric) {
        payload.auto_resolution = {
          metric: form.auto_metric,
          trigger: form.auto_trigger,
          resolution_type: form.auto_type,
        };
      }
      await onSave(payload);
    } finally { setSaving(false); }
  };

  const isTextMatch = form.auto_type === 'text_match';

  return (
    <div className="space-y-3 p-4 rounded-xl" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
      {/* Question Text */}
      <div>
        <label className="text-xs font-medium" style={{ color: COLORS.text.secondary }}>Question (English) *</label>
        <input data-testid="q-text-en" value={form.question_text_en} onChange={e => setForm({ ...form, question_text_en: e.target.value })}
          className="w-full mt-1 p-2.5 rounded-lg text-sm text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}
          placeholder="e.g., How many runs in first innings?" />
      </div>
      <div>
        <label className="text-xs font-medium" style={{ color: COLORS.text.secondary }}>Question (Hindi)</label>
        <input data-testid="q-text-hi" value={form.question_text_hi} onChange={e => setForm({ ...form, question_text_hi: e.target.value })}
          className="w-full mt-1 p-2.5 rounded-lg text-sm text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}
          placeholder="Hindi translation" />
      </div>

      {/* Category / Difficulty / Points */}
      <div className="grid grid-cols-3 gap-2">
        <div>
          <label className="text-xs" style={{ color: COLORS.text.secondary }}>Category</label>
          <select value={form.category} onChange={e => setForm({ ...form, category: e.target.value })}
            className="w-full mt-1 p-2 rounded-lg text-xs text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}>
            {CATEGORIES.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs" style={{ color: COLORS.text.secondary }}>Difficulty</label>
          <select value={form.difficulty} onChange={e => setForm({ ...form, difficulty: e.target.value })}
            className="w-full mt-1 p-2 rounded-lg text-xs text-white capitalize" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}>
            {DIFFICULTIES.map(d => <option key={d} value={d}>{d}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs" style={{ color: COLORS.text.secondary }}>Points</label>
          <input type="number" value={form.points} onChange={e => setForm({ ...form, points: parseInt(e.target.value) || 10 })}
            className="w-full mt-1 p-2 rounded-lg text-xs text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }} min={1} max={200} />
        </div>
      </div>

      {/* Options */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="text-xs font-medium" style={{ color: COLORS.text.secondary }}>
            Options ({form.options.length}/4) {!isTextMatch && '+ Ranges'}
          </label>
          {form.options.length < 4 && (
            <button onClick={addOption} className="text-xs px-2 py-1 rounded" style={{ color: COLORS.primary.main }}>+ Add</button>
          )}
        </div>
        {form.options.map((opt, i) => (
          <div key={opt.key} className="flex items-start gap-1.5 mb-2">
            <span className="text-xs font-bold w-5 text-center pt-2.5" style={{ color: COLORS.primary.main }}>{opt.key}</span>
            <div className="flex-1 space-y-1">
              <div className="flex gap-1.5">
                <input value={opt.text_en} onChange={e => updateOption(i, 'text_en', e.target.value)}
                  className="flex-1 p-2 rounded-lg text-xs text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}
                  placeholder="English" />
                <input value={opt.text_hi} onChange={e => updateOption(i, 'text_hi', e.target.value)}
                  className="flex-1 p-2 rounded-lg text-xs text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}
                  placeholder="Hindi" />
              </div>
              {!isTextMatch && (
                <div className="flex gap-1.5">
                  <input type="number" value={opt.min_value} onChange={e => updateOption(i, 'min_value', e.target.value)}
                    className="flex-1 p-1.5 rounded-lg text-[10px] text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}
                    placeholder="Min value" />
                  <input type="number" value={opt.max_value} onChange={e => updateOption(i, 'max_value', e.target.value)}
                    className="flex-1 p-1.5 rounded-lg text-[10px] text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}
                    placeholder="Max value" />
                </div>
              )}
            </div>
            {form.options.length > 2 && (
              <button className="pt-2" onClick={() => removeOption(i)}><X size={14} color={COLORS.error.main} /></button>
            )}
          </div>
        ))}
      </div>

      {/* Auto-Resolution Config */}
      <div>
        <button data-testid="toggle-auto-config"
          onClick={() => setShowAutoConfig(!showAutoConfig)}
          className="flex items-center gap-1.5 text-xs font-semibold py-1.5 px-3 rounded-lg transition-all"
          style={{ background: showAutoConfig ? '#f59e0b15' : COLORS.background.tertiary, color: showAutoConfig ? '#f59e0b' : COLORS.text.tertiary }}>
          <Zap size={12} /> Auto-Resolution {showAutoConfig ? 'ON' : 'OFF'}
        </button>

        {showAutoConfig && (
          <div className="mt-2 p-3 rounded-lg space-y-2" style={{ background: '#f59e0b08', border: '1px solid #f59e0b18' }}>
            <div className="grid grid-cols-3 gap-2">
              <div>
                <label className="text-[10px]" style={{ color: '#f59e0b88' }}>Metric</label>
                <select value={form.auto_metric} onChange={e => setForm({ ...form, auto_metric: e.target.value })}
                  className="w-full mt-0.5 p-1.5 rounded-lg text-[10px] text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}>
                  {METRICS.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
                </select>
              </div>
              <div>
                <label className="text-[10px]" style={{ color: '#f59e0b88' }}>Trigger</label>
                <select value={form.auto_trigger} onChange={e => setForm({ ...form, auto_trigger: e.target.value })}
                  className="w-full mt-0.5 p-1.5 rounded-lg text-[10px] text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}>
                  {TRIGGERS.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                </select>
              </div>
              <div>
                <label className="text-[10px]" style={{ color: '#f59e0b88' }}>Type</label>
                <select value={form.auto_type} onChange={e => setForm({ ...form, auto_type: e.target.value })}
                  className="w-full mt-0.5 p-1.5 rounded-lg text-[10px] text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}>
                  <option value="range">Range (min-max)</option>
                  <option value="text_match">Text Match</option>
                  <option value="boolean">Boolean (Yes/No)</option>
                </select>
              </div>
            </div>
            <div className="text-[9px]" style={{ color: COLORS.text.tertiary }}>
              Range: Options ke min/max se match karega | Text: Option text se match karega
            </div>
          </div>
        )}
      </div>

      {/* Save */}
      <div className="flex gap-2 pt-1">
        <button data-testid="save-question-btn" onClick={handleSave} disabled={saving || !form.question_text_en.trim()}
          className="flex-1 py-2.5 rounded-lg text-sm font-semibold disabled:opacity-40" style={{ background: COLORS.primary.main, color: '#fff' }}>
          {saving ? 'Saving...' : (initial ? 'Update' : 'Create Question')}
        </button>
        <button onClick={onCancel} className="px-4 py-2.5 rounded-lg text-sm" style={{ background: COLORS.background.tertiary, color: COLORS.text.secondary }}>Cancel</button>
      </div>
    </div>
  );
}

export default function AdminQuestionsTab() {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingQ, setEditingQ] = useState(null);
  const [expandedQ, setExpandedQ] = useState(null);
  const [filterCat, setFilterCat] = useState('');
  const [msg, setMsg] = useState('');

  const fetchQuestions = async () => {
    try {
      const params = filterCat ? `?category=${filterCat}&limit=100` : '?limit=100';
      const res = await apiClient.get(`/admin/questions${params}`);
      setQuestions(res.data.questions || []);
    } catch (e) { setMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
    finally { setLoading(false); }
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { fetchQuestions(); }, [filterCat]);

  const handleCreate = async (payload) => {
    try {
      await apiClient.post('/admin/questions', payload);
      setMsg('Question created!');
      setShowForm(false);
      fetchQuestions();
    } catch (e) { setMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
  };

  const handleUpdate = async (payload) => {
    try {
      await apiClient.put(`/admin/questions/${editingQ.id}`, payload);
      setMsg('Question updated!');
      setEditingQ(null);
      fetchQuestions();
    } catch (e) { setMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
  };

  const handleDelete = async (id) => {
    try {
      await apiClient.delete(`/admin/questions/${id}`);
      setMsg('Deleted');
      fetchQuestions();
    } catch (e) { setMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
  };

  const seedAutoQuestions = async () => {
    try {
      const res = await apiClient.post('/admin/questions/bulk-import-with-auto');
      setMsg(res.data.message);
      fetchQuestions();
    } catch (e) { setMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
  };

  const seed200Questions = async () => {
    try {
      setMsg('Seeding 200 questions...');
      const res = await apiClient.post('/admin/seed-200-questions');
      setMsg(res.data.message);
      fetchQuestions();
    } catch (e) { setMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
  };

  const diffColor = (d) => d === 'hard' ? COLORS.error.main : d === 'medium' ? COLORS.warning.main : COLORS.success.main;

  return (
    <div className="space-y-3">
      {msg && <div className="text-xs text-center py-1.5 rounded-lg" style={{ background: COLORS.background.card, color: COLORS.info.main }}>{msg}</div>}

      <div className="flex items-center gap-2">
        <select data-testid="filter-category" value={filterCat} onChange={e => setFilterCat(e.target.value)}
          className="p-2 rounded-lg text-xs text-white flex-1" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}>
          <option value="">All Categories</option>
          {CATEGORIES.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
        </select>
        <button data-testid="seed-200-btn" onClick={seed200Questions}
          className="flex items-center gap-1 px-2.5 py-2 rounded-lg text-[10px] font-bold" style={{ background: '#10b98115', color: '#10b981', border: '1px solid #10b98122' }}>
          <Zap size={12} /> Seed 200
        </button>
        <button data-testid="seed-auto-btn" onClick={seedAutoQuestions}
          className="flex items-center gap-1 px-2.5 py-2 rounded-lg text-[10px] font-bold" style={{ background: '#f59e0b15', color: '#f59e0b', border: '1px solid #f59e0b22' }}>
          <Zap size={12} /> Seed Auto
        </button>
        <button data-testid="add-question-btn" onClick={() => { setShowForm(true); setEditingQ(null); }}
          className="flex items-center gap-1 px-2.5 py-2 rounded-lg text-xs font-semibold" style={{ background: COLORS.primary.main, color: '#fff' }}>
          <Plus size={14} /> New
        </button>
      </div>

      {showForm && !editingQ && <QuestionForm onSave={handleCreate} onCancel={() => setShowForm(false)} />}
      {editingQ && <QuestionForm initial={editingQ} onSave={handleUpdate} onCancel={() => setEditingQ(null)} />}

      {loading ? (
        <div className="flex justify-center py-8"><div className="w-6 h-6 border-2 rounded-full animate-spin" style={{ borderColor: `${COLORS.primary.main}30`, borderTopColor: COLORS.primary.main }} /></div>
      ) : (
        <div className="space-y-1.5">
          <div className="text-xs" style={{ color: COLORS.text.tertiary }}>{questions.length} questions</div>
          {questions.map((q, i) => {
            const hasAuto = !!q.auto_resolution?.metric;
            return (
              <div key={q.id} className="rounded-xl overflow-hidden" style={{ background: COLORS.background.card, border: `1px solid ${hasAuto ? '#f59e0b18' : COLORS.border.light}` }}>
                <div className="flex items-center gap-2 p-3 cursor-pointer" onClick={() => setExpandedQ(expandedQ === q.id ? null : q.id)}>
                  <span className="text-xs font-mono w-6 text-center" style={{ color: COLORS.text.tertiary }}>#{i + 1}</span>
                  <div className="flex-1 min-w-0">
                    <div className="text-xs font-medium text-white truncate">{q.question_text_en}</div>
                    <div className="flex items-center gap-1.5 mt-0.5 flex-wrap">
                      <span className="text-[10px] px-1.5 py-0.5 rounded" style={{ background: COLORS.background.tertiary, color: COLORS.text.tertiary }}>{q.category}</span>
                      <span className="text-[10px] font-bold" style={{ color: diffColor(q.difficulty) }}>{q.difficulty}</span>
                      <span className="text-[10px] font-bold" style={{ color: COLORS.accent.gold }}>{q.points}pts</span>
                      {hasAuto && <span className="text-[9px] px-1 py-0.5 rounded font-bold" style={{ background: '#f59e0b15', color: '#f59e0b' }}>AUTO</span>}
                    </div>
                  </div>
                  {expandedQ === q.id ? <ChevronUp size={14} color={COLORS.text.tertiary} /> : <ChevronDown size={14} color={COLORS.text.tertiary} />}
                </div>

                {expandedQ === q.id && (
                  <div className="px-3 pb-3 border-t" style={{ borderColor: COLORS.border.light }}>
                    {q.question_text_hi && <div className="text-xs mt-2 italic" style={{ color: COLORS.text.secondary }}>{q.question_text_hi}</div>}
                    <div className="grid grid-cols-2 gap-1 mt-2">
                      {(q.options || []).map(opt => (
                        <div key={opt.key} className="text-xs p-2 rounded-lg" style={{ background: COLORS.background.tertiary }}>
                          <span className="font-bold" style={{ color: COLORS.primary.main }}>{opt.key}:</span>{' '}
                          <span className="text-white">{opt.text_en}</span>
                          {opt.min_value != null && (
                            <div className="text-[9px] mt-0.5" style={{ color: COLORS.text.tertiary }}>
                              Range: {opt.min_value} - {opt.max_value === 999 ? '+' : opt.max_value}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                    {hasAuto && (
                      <div className="mt-2 text-[10px] p-2 rounded-lg" style={{ background: '#f59e0b08', border: '1px solid #f59e0b15' }}>
                        <Zap size={10} className="inline mr-1" color="#f59e0b" />
                        <span style={{ color: '#f59e0b' }}>Auto: {q.auto_resolution.metric}</span>
                        <span style={{ color: COLORS.text.tertiary }}> | {q.auto_resolution.trigger} | {q.auto_resolution.resolution_type}</span>
                      </div>
                    )}
                    <div className="flex gap-2 mt-3">
                      <button data-testid={`edit-q-${q.id}`} onClick={() => { setEditingQ(q); setShowForm(false); }}
                        className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs" style={{ background: COLORS.info.bg, color: COLORS.info.main }}>
                        <Edit2 size={12} /> Edit
                      </button>
                      <button data-testid={`delete-q-${q.id}`} onClick={() => handleDelete(q.id)}
                        className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs" style={{ background: COLORS.error.bg, color: COLORS.error.main }}>
                        <Trash2 size={12} /> Delete
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
