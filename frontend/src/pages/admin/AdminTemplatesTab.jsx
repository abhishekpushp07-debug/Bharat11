/**
 * Admin Templates Tab - One-click create + Edit (add/remove questions)
 * Templates always editable, whether auto-created or manual
 */
import { useState, useEffect } from 'react';
import apiClient from '../../api/client';
import { COLORS } from '../../constants/design';
import { Plus, Star, Trash2, ChevronDown, ChevronUp, Check, Edit2, Save, X, Zap } from 'lucide-react';

export default function AdminTemplatesTab() {
  const [templates, setTemplates] = useState([]);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingT, setEditingT] = useState(null);
  const [expandedT, setExpandedT] = useState(null);
  const [msg, setMsg] = useState('');

  const [form, setForm] = useState({
    name: '', description: '', match_type: 'T20',
    template_type: 'full_match', question_ids: [], is_default: false
  });

  const fetchAll = async () => {
    try {
      const [tRes, qRes] = await Promise.all([
        apiClient.get('/admin/templates?limit=50'),
        apiClient.get('/admin/questions?limit=100')
      ]);
      setTemplates(tRes.data.templates || []);
      setQuestions(qRes.data.questions || []);
    } catch (e) { setMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchAll(); }, []);

  const toggleQuestion = (qid) => {
    setForm(prev => ({
      ...prev,
      question_ids: prev.question_ids.includes(qid)
        ? prev.question_ids.filter(id => id !== qid)
        : [...prev.question_ids, qid]
    }));
  };

  const handleCreate = async () => {
    if (!form.name.trim() || form.question_ids.length === 0) {
      setMsg('Name and at least 1 question required');
      return;
    }
    try {
      await apiClient.post('/admin/templates', form);
      setMsg('Template created!');
      setShowForm(false);
      resetForm();
      fetchAll();
    } catch (e) { setMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
  };

  const handleUpdate = async () => {
    if (!editingT) return;
    try {
      await apiClient.put(`/admin/templates/${editingT}`, {
        name: form.name,
        description: form.description,
        question_ids: form.question_ids,
        is_default: form.is_default,
        template_type: form.template_type,
      });
      setMsg('Template updated!');
      setEditingT(null);
      resetForm();
      fetchAll();
    } catch (e) { setMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
  };

  const handleSetDefault = async (id) => {
    try {
      await apiClient.post(`/admin/templates/${id}/set-default`);
      setMsg('Default set!');
      fetchAll();
    } catch (e) { setMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
  };

  const handleDelete = async (id) => {
    try {
      await apiClient.delete(`/admin/templates/${id}`);
      setMsg('Deleted');
      fetchAll();
    } catch (e) { setMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
  };

  const startEditing = (t) => {
    setForm({
      name: t.name || '', description: t.description || '', match_type: t.match_type || 'T20',
      template_type: t.template_type || 'full_match',
      question_ids: t.question_ids || [],
      is_default: t.is_default || false,
    });
    setEditingT(t.id);
    setShowForm(false);
    setExpandedT(null);
  };

  const resetForm = () => {
    setForm({ name: '', description: '', match_type: 'T20', template_type: 'full_match', question_ids: [], is_default: false });
  };

  // One-click: select ALL auto-resolution questions
  const oneClickAutoTemplate = () => {
    const autoQs = questions.filter(q => q.auto_resolution?.metric);
    if (autoQs.length === 0) {
      setMsg('No auto-resolution questions found. Seed them first!');
      return;
    }
    setForm({
      name: 'IPL T20 Auto-Settle Template',
      description: `${autoQs.length} auto-resolvable questions`,
      match_type: 'T20',
      template_type: 'full_match',
      question_ids: autoQs.map(q => q.id),
      is_default: true,
    });
    setShowForm(true);
    setEditingT(null);
  };

  const selectedPts = form.question_ids.reduce((sum, qid) => {
    const q = questions.find(q => q.id === qid);
    return sum + (q?.points || 0);
  }, 0);

  const isEditing = !!editingT;
  const formTitle = isEditing ? 'Edit Template' : 'Create Template';

  // Question picker with category filter
  const QuestionPicker = () => {
    const [pickFilter, setPickFilter] = useState('');
    const filtered = pickFilter ? questions.filter(q => q.category === pickFilter) : questions;

    return (
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="text-xs font-medium" style={{ color: COLORS.text.secondary }}>
            Questions ({form.question_ids.length} selected, {selectedPts} pts)
          </label>
          <select value={pickFilter} onChange={e => setPickFilter(e.target.value)}
            className="p-1 rounded text-[10px] text-white" style={{ background: COLORS.background.tertiary }}>
            <option value="">All</option>
            <option value="match">Match</option>
            <option value="batting">Batting</option>
            <option value="bowling">Bowling</option>
            <option value="player_performance">Player</option>
            <option value="special">Special</option>
          </select>
        </div>
        <div className="max-h-60 overflow-y-auto space-y-1 rounded-lg p-2" style={{ background: COLORS.background.tertiary }}>
          {filtered.map(q => {
            const sel = form.question_ids.includes(q.id);
            const hasAuto = !!q.auto_resolution?.metric;
            return (
              <div key={q.id} onClick={() => toggleQuestion(q.id)}
                className="flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-all"
                style={{ background: sel ? `${COLORS.primary.main}22` : 'transparent', border: `1px solid ${sel ? COLORS.primary.main : 'transparent'}` }}>
                <div className="w-5 h-5 rounded flex items-center justify-center shrink-0"
                  style={{ background: sel ? COLORS.primary.main : COLORS.background.card }}>
                  {sel && <Check size={12} color="#fff" />}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-xs text-white truncate">{q.question_text_en}</div>
                  <div className="flex items-center gap-1 mt-0.5">
                    <span className="text-[9px]" style={{ color: COLORS.text.tertiary }}>{q.category}</span>
                    <span className="text-[9px] font-bold" style={{ color: COLORS.accent.gold }}>{q.points}pts</span>
                    {hasAuto && <span className="text-[8px] px-1 rounded font-bold" style={{ background: '#f59e0b15', color: '#f59e0b' }}>AUTO</span>}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-3">
      {msg && <div className="text-xs text-center py-1.5 rounded-lg" style={{ background: COLORS.background.card, color: COLORS.info.main }}>{msg}</div>}

      <div className="flex gap-2">
        <button data-testid="one-click-template" onClick={oneClickAutoTemplate}
          className="flex items-center gap-1 px-3 py-2 rounded-lg text-xs font-semibold"
          style={{ background: '#f59e0b15', color: '#f59e0b', border: '1px solid #f59e0b22' }}>
          <Zap size={14} /> One-Click Auto Template
        </button>
        <button data-testid="add-template-btn" onClick={() => { setShowForm(!showForm); setEditingT(null); resetForm(); }}
          className="flex items-center gap-1 px-3 py-2 rounded-lg text-xs font-semibold" style={{ background: COLORS.primary.main, color: '#fff' }}>
          <Plus size={14} /> New Template
        </button>
      </div>

      {/* Create/Edit Form */}
      {(showForm || isEditing) && (
        <div className="space-y-3 p-4 rounded-xl" style={{ background: COLORS.background.card, border: `1px solid ${isEditing ? COLORS.info.main + '44' : COLORS.border.light}` }}>
          <div className="text-xs font-bold" style={{ color: isEditing ? COLORS.info.main : COLORS.text.secondary }}>
            {formTitle}
          </div>

          <input data-testid="template-name" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })}
            className="w-full p-2.5 rounded-lg text-sm text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}
            placeholder="Template Name" />

          <input value={form.description} onChange={e => setForm({ ...form, description: e.target.value })}
            className="w-full p-2.5 rounded-lg text-sm text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}
            placeholder="Description" />

          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-xs" style={{ color: COLORS.text.secondary }}>Type</label>
              <select data-testid="template-type-select" value={form.template_type} onChange={e => setForm({ ...form, template_type: e.target.value })}
                className="w-full mt-1 p-2 rounded-lg text-xs text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}>
                <option value="full_match">Full Match</option>
                <option value="in_match">In-Match</option>
              </select>
            </div>
            <div className="flex items-end pb-1">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" checked={form.is_default} onChange={e => setForm({ ...form, is_default: e.target.checked })} className="accent-green-500" />
                <span className="text-xs" style={{ color: COLORS.text.secondary }}>Default</span>
              </label>
            </div>
          </div>

          <QuestionPicker />

          <div className="flex gap-2">
            <button data-testid={isEditing ? "update-template-btn" : "create-template-btn"}
              onClick={isEditing ? handleUpdate : handleCreate}
              disabled={!form.name.trim() || form.question_ids.length === 0}
              className="flex-1 py-2.5 rounded-lg text-sm font-semibold disabled:opacity-40 flex items-center justify-center gap-1"
              style={{ background: isEditing ? COLORS.info.main : COLORS.primary.main, color: '#fff' }}>
              {isEditing ? <><Save size={14} /> Update Template</> : 'Create Template'}
            </button>
            <button onClick={() => { setShowForm(false); setEditingT(null); resetForm(); }}
              className="px-4 py-2.5 rounded-lg text-sm" style={{ background: COLORS.background.tertiary, color: COLORS.text.secondary }}>Cancel</button>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-8"><div className="w-6 h-6 border-2 rounded-full animate-spin" style={{ borderColor: `${COLORS.primary.main}30`, borderTopColor: COLORS.primary.main }} /></div>
      ) : (
        <div className="space-y-2">
          <div className="text-xs" style={{ color: COLORS.text.tertiary }}>{templates.length} templates</div>
          {templates.map(t => {
            const autoCount = (t.question_ids || []).filter(qid => {
              const q = questions.find(qq => qq.id === qid);
              return q?.auto_resolution?.metric;
            }).length;

            return (
              <div key={t.id} className="rounded-xl overflow-hidden" style={{ background: COLORS.background.card, border: `1px solid ${t.is_default ? COLORS.success.main + '44' : COLORS.border.light}` }}>
                <div className="flex items-center gap-2 p-3 cursor-pointer" onClick={() => setExpandedT(expandedT === t.id ? null : t.id)}>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-white">{t.name}</span>
                      {t.is_default && <Star size={12} color={COLORS.accent.gold} fill={COLORS.accent.gold} />}
                    </div>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-[10px] px-1.5 py-0.5 rounded font-semibold"
                        style={{ background: t.template_type === 'full_match' ? COLORS.primary.main + '22' : COLORS.warning.bg, color: t.template_type === 'full_match' ? COLORS.primary.main : COLORS.warning.main }}>
                        {t.template_type === 'full_match' ? 'FULL' : 'IN-MATCH'}
                      </span>
                      <span className="text-[10px]" style={{ color: COLORS.text.tertiary }}>{t.question_count || t.question_ids?.length || 0} Qs | {t.total_points || 0}pts</span>
                      {autoCount > 0 && (
                        <span className="text-[9px] px-1 rounded font-bold" style={{ background: '#f59e0b15', color: '#f59e0b' }}>{autoCount} AUTO</span>
                      )}
                    </div>
                  </div>
                  {expandedT === t.id ? <ChevronUp size={14} color={COLORS.text.tertiary} /> : <ChevronDown size={14} color={COLORS.text.tertiary} />}
                </div>

                {expandedT === t.id && (
                  <div className="px-3 pb-3 border-t space-y-2" style={{ borderColor: COLORS.border.light }}>
                    {t.description && <div className="text-xs mt-2" style={{ color: COLORS.text.secondary }}>{t.description}</div>}

                    {/* Show questions in template */}
                    <div className="space-y-1 mt-2">
                      {(t.question_ids || []).map((qid, qi) => {
                        const q = questions.find(qq => qq.id === qid);
                        if (!q) return null;
                        return (
                          <div key={qid} className="flex items-center gap-2 p-1.5 rounded-lg text-[10px]" style={{ background: COLORS.background.tertiary }}>
                            <span className="font-mono w-5 text-center" style={{ color: COLORS.text.tertiary }}>#{qi + 1}</span>
                            <span className="flex-1 text-white truncate">{q.question_text_en}</span>
                            <span style={{ color: COLORS.accent.gold }}>{q.points}pts</span>
                          </div>
                        );
                      })}
                    </div>

                    <div className="flex gap-2 mt-3 flex-wrap">
                      <button data-testid={`edit-template-${t.id}`} onClick={() => startEditing(t)}
                        className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs" style={{ background: COLORS.info.bg, color: COLORS.info.main }}>
                        <Edit2 size={12} /> Edit
                      </button>
                      {!t.is_default && (
                        <button onClick={() => handleSetDefault(t.id)}
                          className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs" style={{ background: COLORS.accent.gold + '22', color: COLORS.accent.gold }}>
                          <Star size={12} /> Set Default
                        </button>
                      )}
                      <button onClick={() => handleDelete(t.id)}
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
