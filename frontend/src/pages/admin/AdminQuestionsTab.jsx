import { useState, useEffect, useCallback } from 'react';
import apiClient from '../../api/client';
import { COLORS } from '../../constants/design';
import { Plus, Trash2, Edit, ChevronLeft, ChevronRight, Search, X, Save, Loader2 } from 'lucide-react';

export default function AdminQuestionsTab() {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [showAdd, setShowAdd] = useState(false);
  const [editingQ, setEditingQ] = useState(null);
  const [seeding, setSeeding] = useState(false);
  const [seedResult, setSeedResult] = useState(null);
  const LIMIT = 100;

  const fetchQuestions = useCallback(async (p = 1) => {
    setLoading(true);
    try {
      let url = `/admin/questions?page=${p}&limit=${LIMIT}`;
      if (search) url += `&search=${encodeURIComponent(search)}`;
      if (categoryFilter) url += `&category=${categoryFilter}`;
      const res = await apiClient.get(url);
      setQuestions(res.data.questions || []);
      setTotal(res.data.total || 0);
      setHasMore(res.data.has_more || false);
      setPage(p);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [search, categoryFilter]);

  useEffect(() => { fetchQuestions(1); }, [fetchQuestions]);

  const handleDelete = async (qId) => {
    if (!window.confirm('Delete this question?')) return;
    try {
      await apiClient.delete(`/admin/questions/${qId}`);
      fetchQuestions(page);
    } catch (e) {
      alert('Delete failed: ' + (e.response?.data?.detail || e.message));
    }
  };

  const handleSeed = async () => {
    if (!window.confirm('This will seed 500+ bilingual questions into the pool. Continue?')) return;
    setSeeding(true);
    setSeedResult(null);
    try {
      const res = await apiClient.post('/admin/seed-question-pool?force=false&count=2000');
      setSeedResult(res.data);
      fetchQuestions(1);
    } catch (e) {
      setSeedResult({ error: e.response?.data?.detail || e.message });
    } finally { setSeeding(false); }
  };

  const totalPages = Math.ceil(total / LIMIT);
  const categories = ['batting', 'bowling', 'powerplay', 'death_overs', 'match', 'player_performance', 'special'];

  return (
    <div data-testid="admin-questions-tab" className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-white">Question Pool</h2>
          <span className="text-xs" style={{ color: COLORS.text.tertiary }}>{total} questions (max 2000)</span>
        </div>
        <div className="flex gap-2">
          <button data-testid="seed-btn" onClick={handleSeed} disabled={seeding}
            className="px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1 disabled:opacity-50"
            style={{ background: COLORS.warning.bg, color: COLORS.warning.main }}>
            {seeding ? <Loader2 size={12} className="animate-spin" /> : <Plus size={12} />}
            {seeding ? 'Seeding...' : 'Seed Pool'}
          </button>
          <button data-testid="add-question-btn" onClick={() => { setEditingQ(null); setShowAdd(true); }}
            className="px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1"
            style={{ background: COLORS.primary.gradient, color: '#fff' }}>
            <Plus size={12} /> Add
          </button>
        </div>
      </div>

      {seedResult && (
        <div className="p-3 rounded-lg text-xs" style={{
          background: seedResult.error ? COLORS.error.bg : COLORS.success.bg,
          color: seedResult.error ? COLORS.error.main : COLORS.success.main,
        }}>
          {seedResult.error || `Seeded ${seedResult.seeded} questions. Total: ${seedResult.total_in_db}`}
        </div>
      )}

      {/* Search + Filter */}
      <div className="flex gap-2">
        <div className="flex-1 relative">
          <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2" color={COLORS.text.tertiary} />
          <input data-testid="search-input" value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Search questions..."
            className="w-full pl-8 pr-8 py-2 rounded-lg text-xs text-white placeholder:text-gray-500 outline-none"
            style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }} />
          {search && <button onClick={() => setSearch('')} className="absolute right-2 top-1/2 -translate-y-1/2"><X size={12} color={COLORS.text.tertiary} /></button>}
        </div>
        <select data-testid="category-filter" value={categoryFilter} onChange={e => setCategoryFilter(e.target.value)}
          className="px-2 py-2 rounded-lg text-xs text-white outline-none"
          style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
          <option value="">All Categories</option>
          {categories.map(c => <option key={c} value={c}>{c.replace('_', ' ')}</option>)}
        </select>
      </div>

      {/* Question List */}
      {loading ? (
        <div className="flex items-center justify-center py-10"><Loader2 size={24} className="animate-spin" color={COLORS.primary.main} /></div>
      ) : (
        <div className="space-y-1.5">
          {questions.map((q, i) => (
            <div key={q.id} data-testid={`question-row-${i}`}
              className="flex items-start gap-2 p-2.5 rounded-lg group"
              style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
              <div className="flex-1 min-w-0">
                <div className="text-xs font-bold text-white mb-0.5 leading-snug">{q.question_text_en}</div>
                <div className="text-[10px] mb-1" style={{ color: COLORS.text.tertiary }}>{q.question_text_hi}</div>
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-[8px] font-bold px-1.5 py-0.5 rounded" style={{ background: COLORS.primary.bg, color: COLORS.primary.main }}>{q.category}</span>
                  <span className="text-[8px] font-bold px-1.5 py-0.5 rounded" style={{ background: COLORS.warning.bg, color: COLORS.warning.main }}>{q.points} pts</span>
                  <span className="text-[8px]" style={{ color: COLORS.text.tertiary }}>{q.difficulty}</span>
                  {q.auto_resolution?.trigger && (
                    <span className="text-[8px] font-bold px-1.5 py-0.5 rounded" style={{ background: 'rgba(96,165,250,0.1)', color: '#60a5fa' }}>{q.auto_resolution.trigger}</span>
                  )}
                </div>
              </div>
              <div className="flex gap-1 opacity-60 group-hover:opacity-100 transition-opacity shrink-0">
                <button data-testid={`edit-q-${i}`} onClick={() => { setEditingQ(q); setShowAdd(true); }}
                  className="p-1.5 rounded" style={{ background: 'rgba(255,255,255,0.05)' }}>
                  <Edit size={12} color={COLORS.primary.main} />
                </button>
                <button data-testid={`delete-q-${i}`} onClick={() => handleDelete(q.id)}
                  className="p-1.5 rounded" style={{ background: 'rgba(255,255,255,0.05)' }}>
                  <Trash2 size={12} color={COLORS.error.main} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div data-testid="pagination" className="flex items-center justify-center gap-3 pt-2">
          <button onClick={() => fetchQuestions(page - 1)} disabled={page <= 1}
            className="p-2 rounded-lg disabled:opacity-30" style={{ background: COLORS.background.card }}>
            <ChevronLeft size={14} color="#fff" />
          </button>
          <span className="text-xs font-bold text-white">
            Page {page} of {totalPages}
          </span>
          <button onClick={() => fetchQuestions(page + 1)} disabled={!hasMore}
            className="p-2 rounded-lg disabled:opacity-30" style={{ background: COLORS.background.card }}>
            <ChevronRight size={14} color="#fff" />
          </button>
        </div>
      )}

      {/* Add/Edit Modal */}
      {showAdd && (
        <QuestionFormModal
          question={editingQ}
          categories={categories}
          onClose={() => { setShowAdd(false); setEditingQ(null); }}
          onSaved={() => { setShowAdd(false); setEditingQ(null); fetchQuestions(page); }}
        />
      )}
    </div>
  );
}

function QuestionFormModal({ question, categories, onClose, onSaved }) {
  const isEdit = !!question;
  const [form, setForm] = useState({
    question_text_en: question?.question_text_en || '',
    question_text_hi: question?.question_text_hi || '',
    category: question?.category || 'batting',
    difficulty: question?.difficulty || 'medium',
    points: question?.points || 50,
    options: question?.options || [
      { label_en: '', label_hi: '', value_min: 0, value_max: 0 },
      { label_en: '', label_hi: '', value_min: 0, value_max: 0 },
      { label_en: '', label_hi: '', value_min: 0, value_max: 0 },
      { label_en: '', label_hi: '', value_min: 0, value_max: 0 },
    ],
    auto_resolution: question?.auto_resolution || { metric: '', trigger: 'match_end', comparison: 'range' },
  });
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    if (!form.question_text_en.trim()) return alert('English question text required');
    setSaving(true);
    try {
      if (isEdit) {
        await apiClient.put(`/admin/questions/${question.id}`, form);
      } else {
        await apiClient.post('/admin/questions', form);
      }
      onSaved();
    } catch (e) {
      alert('Error: ' + (e.response?.data?.detail || e.message));
    } finally { setSaving(false); }
  };

  const updateOption = (idx, field, value) => {
    const opts = [...form.options];
    opts[idx] = { ...opts[idx], [field]: field.includes('value') ? Number(value) : value };
    setForm(f => ({ ...f, options: opts }));
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: 'rgba(0,0,0,0.8)' }}>
      <div className="w-full max-w-lg rounded-2xl p-4 max-h-[85vh] overflow-y-auto" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold text-white">{isEdit ? 'Edit Question' : 'Add Question'}</h3>
          <button onClick={onClose} className="p-1"><X size={16} color={COLORS.text.tertiary} /></button>
        </div>

        <div className="space-y-3">
          <div>
            <label className="text-[10px] font-bold mb-1 block" style={{ color: COLORS.text.tertiary }}>Question (English)</label>
            <textarea data-testid="q-text-en" value={form.question_text_en} onChange={e => setForm(f => ({ ...f, question_text_en: e.target.value }))}
              rows={2} className="w-full p-2 rounded-lg text-xs text-white outline-none resize-none"
              style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }} />
          </div>
          <div>
            <label className="text-[10px] font-bold mb-1 block" style={{ color: COLORS.text.tertiary }}>Question (Hindi)</label>
            <textarea data-testid="q-text-hi" value={form.question_text_hi} onChange={e => setForm(f => ({ ...f, question_text_hi: e.target.value }))}
              rows={2} className="w-full p-2 rounded-lg text-xs text-white outline-none resize-none"
              style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }} />
          </div>
          <div className="grid grid-cols-3 gap-2">
            <div>
              <label className="text-[10px] font-bold mb-1 block" style={{ color: COLORS.text.tertiary }}>Category</label>
              <select data-testid="q-category" value={form.category} onChange={e => setForm(f => ({ ...f, category: e.target.value }))}
                className="w-full p-2 rounded-lg text-xs text-white outline-none"
                style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}>
                {categories.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="text-[10px] font-bold mb-1 block" style={{ color: COLORS.text.tertiary }}>Difficulty</label>
              <select data-testid="q-difficulty" value={form.difficulty} onChange={e => setForm(f => ({ ...f, difficulty: e.target.value }))}
                className="w-full p-2 rounded-lg text-xs text-white outline-none"
                style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}>
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>
            <div>
              <label className="text-[10px] font-bold mb-1 block" style={{ color: COLORS.text.tertiary }}>Points</label>
              <input data-testid="q-points" type="number" value={form.points} onChange={e => setForm(f => ({ ...f, points: Number(e.target.value) }))}
                className="w-full p-2 rounded-lg text-xs text-white outline-none"
                style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }} />
            </div>
          </div>

          {/* Options */}
          <div>
            <label className="text-[10px] font-bold mb-1 block" style={{ color: COLORS.text.tertiary }}>Options (4)</label>
            {form.options.map((opt, idx) => (
              <div key={idx} className="grid grid-cols-4 gap-1 mb-1">
                <input placeholder={`Option ${idx + 1} EN`} value={opt.label_en} onChange={e => updateOption(idx, 'label_en', e.target.value)}
                  className="p-1.5 rounded text-[10px] text-white outline-none col-span-2"
                  style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }} />
                <input placeholder="Min" type="number" value={opt.value_min} onChange={e => updateOption(idx, 'value_min', e.target.value)}
                  className="p-1.5 rounded text-[10px] text-white outline-none"
                  style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }} />
                <input placeholder="Max" type="number" value={opt.value_max} onChange={e => updateOption(idx, 'value_max', e.target.value)}
                  className="p-1.5 rounded text-[10px] text-white outline-none"
                  style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }} />
              </div>
            ))}
          </div>

          {/* Auto Resolution */}
          <div className="grid grid-cols-3 gap-2">
            <div>
              <label className="text-[10px] font-bold mb-1 block" style={{ color: COLORS.text.tertiary }}>Metric Key</label>
              <input data-testid="q-metric" value={form.auto_resolution.metric} onChange={e => setForm(f => ({ ...f, auto_resolution: { ...f.auto_resolution, metric: e.target.value } }))}
                className="w-full p-2 rounded-lg text-xs text-white outline-none"
                style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }} />
            </div>
            <div>
              <label className="text-[10px] font-bold mb-1 block" style={{ color: COLORS.text.tertiary }}>Trigger</label>
              <select value={form.auto_resolution.trigger} onChange={e => setForm(f => ({ ...f, auto_resolution: { ...f.auto_resolution, trigger: e.target.value } }))}
                className="w-full p-2 rounded-lg text-xs text-white outline-none"
                style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}>
                <option value="match_end">match_end</option>
                <option value="innings_1_end">innings_1_end</option>
                <option value="innings_2_end">innings_2_end</option>
                <option value="toss">toss</option>
                <option value="powerplay_end">powerplay_end</option>
              </select>
            </div>
            <div>
              <label className="text-[10px] font-bold mb-1 block" style={{ color: COLORS.text.tertiary }}>Comparison</label>
              <select value={form.auto_resolution.comparison} onChange={e => setForm(f => ({ ...f, auto_resolution: { ...f.auto_resolution, comparison: e.target.value } }))}
                className="w-full p-2 rounded-lg text-xs text-white outline-none"
                style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}>
                <option value="range">range</option>
                <option value="exact">exact</option>
                <option value="yes_no">yes_no</option>
                <option value="category">category</option>
              </select>
            </div>
          </div>

          <button data-testid="save-question-btn" onClick={handleSave} disabled={saving}
            className="w-full py-2.5 rounded-xl text-sm font-bold flex items-center justify-center gap-2 disabled:opacity-50"
            style={{ background: COLORS.primary.gradient, color: '#fff' }}>
            {saving ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />}
            {isEdit ? 'Update Question' : 'Create Question'}
          </button>
        </div>
      </div>
    </div>
  );
}
