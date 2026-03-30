import { useState, useEffect } from 'react';
import apiClient from '../../api/client';
import { COLORS } from '../../constants/design';
import { Plus, Edit2, Trash2, ChevronDown, ChevronUp, X } from 'lucide-react';

const CATEGORIES = [
  { value: 'batting', label: 'Batting' },
  { value: 'bowling', label: 'Bowling' },
  { value: 'powerplay', label: 'Powerplay' },
  { value: 'death_overs', label: 'Death Overs' },
  { value: 'match', label: 'Match' },
  { value: 'player_performance', label: 'Player Performance' },
  { value: 'special', label: 'Special' },
];

const DIFFICULTIES = ['easy', 'medium', 'hard'];

function QuestionForm({ initial, onSave, onCancel }) {
  const [form, setForm] = useState(initial || {
    question_text_en: '', question_text_hi: '',
    category: 'match', difficulty: 'easy', points: 10,
    options: [
      { key: 'A', text_en: '', text_hi: '' },
      { key: 'B', text_en: '', text_hi: '' },
    ],
    is_active: true
  });
  const [saving, setSaving] = useState(false);

  const updateOption = (idx, field, value) => {
    const opts = [...form.options];
    opts[idx] = { ...opts[idx], [field]: value };
    setForm({ ...form, options: opts });
  };

  const addOption = () => {
    if (form.options.length >= 4) return;
    const keys = ['A', 'B', 'C', 'D'];
    setForm({ ...form, options: [...form.options, { key: keys[form.options.length], text_en: '', text_hi: '' }] });
  };

  const removeOption = (idx) => {
    if (form.options.length <= 2) return;
    const opts = form.options.filter((_, i) => i !== idx);
    const keys = ['A', 'B', 'C', 'D'];
    setForm({ ...form, options: opts.map((o, i) => ({ ...o, key: keys[i] })) });
  };

  const handleSave = async () => {
    if (!form.question_text_en.trim()) return;
    setSaving(true);
    try {
      await onSave(form);
    } finally { setSaving(false); }
  };

  return (
    <div className="space-y-3 p-4 rounded-xl" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
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
          placeholder="e.g., पहली पारी में कितने रन?" />
      </div>

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

      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="text-xs font-medium" style={{ color: COLORS.text.secondary }}>Options ({form.options.length}/4)</label>
          {form.options.length < 4 && (
            <button onClick={addOption} className="text-xs px-2 py-1 rounded" style={{ color: COLORS.primary.main }}>+ Add</button>
          )}
        </div>
        {form.options.map((opt, i) => (
          <div key={opt.key} className="flex items-center gap-2 mb-1.5">
            <span className="text-xs font-bold w-5 text-center" style={{ color: COLORS.primary.main }}>{opt.key}</span>
            <input value={opt.text_en} onChange={e => updateOption(i, 'text_en', e.target.value)}
              className="flex-1 p-2 rounded-lg text-xs text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}
              placeholder="English" />
            <input value={opt.text_hi} onChange={e => updateOption(i, 'text_hi', e.target.value)}
              className="flex-1 p-2 rounded-lg text-xs text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}
              placeholder="Hindi" />
            {form.options.length > 2 && (
              <button onClick={() => removeOption(i)}><X size={14} color={COLORS.error.main} /></button>
            )}
          </div>
        ))}
      </div>

      <div className="flex gap-2 pt-2">
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

  const handleCreate = async (form) => {
    try {
      await apiClient.post('/admin/questions', form);
      setMsg('Question created!');
      setShowForm(false);
      fetchQuestions();
    } catch (e) { setMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
  };

  const handleUpdate = async (form) => {
    try {
      await apiClient.put(`/admin/questions/${editingQ.id}`, form);
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

  const diffColor = (d) => d === 'hard' ? COLORS.error.main : d === 'medium' ? COLORS.warning.main : COLORS.success.main;

  return (
    <div className="space-y-3">
      {msg && <div className="text-xs text-center py-1.5 rounded-lg" style={{ background: COLORS.background.card, color: COLORS.info.main }}>{msg}</div>}

      <div className="flex items-center justify-between gap-2">
        <select data-testid="filter-category" value={filterCat} onChange={e => setFilterCat(e.target.value)}
          className="p-2 rounded-lg text-xs text-white flex-1" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}>
          <option value="">All Categories</option>
          {CATEGORIES.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
        </select>
        <button data-testid="add-question-btn" onClick={() => { setShowForm(true); setEditingQ(null); }}
          className="flex items-center gap-1 px-3 py-2 rounded-lg text-xs font-semibold" style={{ background: COLORS.primary.main, color: '#fff' }}>
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
          {questions.map((q, i) => (
            <div key={q.id} className="rounded-xl overflow-hidden" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
              <div className="flex items-center gap-2 p-3 cursor-pointer" onClick={() => setExpandedQ(expandedQ === q.id ? null : q.id)}>
                <span className="text-xs font-mono w-6 text-center" style={{ color: COLORS.text.tertiary }}>#{i + 1}</span>
                <div className="flex-1 min-w-0">
                  <div className="text-xs font-medium text-white truncate">{q.question_text_en}</div>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-[10px] px-1.5 py-0.5 rounded" style={{ background: COLORS.background.tertiary, color: COLORS.text.tertiary }}>{q.category}</span>
                    <span className="text-[10px] font-bold" style={{ color: diffColor(q.difficulty) }}>{q.difficulty}</span>
                    <span className="text-[10px]" style={{ color: COLORS.accent.gold }}>{q.points}pts</span>
                  </div>
                </div>
                {expandedQ === q.id ? <ChevronUp size={14} color={COLORS.text.tertiary} /> : <ChevronDown size={14} color={COLORS.text.tertiary} />}
              </div>

              {expandedQ === q.id && (
                <div className="px-3 pb-3 border-t" style={{ borderColor: COLORS.border.light }}>
                  {q.question_text_hi && <div className="text-xs mt-2 italic" style={{ color: COLORS.text.secondary }}>{q.question_text_hi}</div>}
                  <div className="grid grid-cols-2 gap-1 mt-2">
                    {(q.options || []).map(opt => (
                      <div key={opt.key} className="text-xs p-1.5 rounded" style={{ background: COLORS.background.tertiary }}>
                        <span className="font-bold" style={{ color: COLORS.primary.main }}>{opt.key}:</span>{' '}
                        <span className="text-white">{opt.text_en}</span>
                        {opt.text_hi && <span style={{ color: COLORS.text.tertiary }}> ({opt.text_hi})</span>}
                      </div>
                    ))}
                  </div>
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
          ))}
        </div>
      )}
    </div>
  );
}
