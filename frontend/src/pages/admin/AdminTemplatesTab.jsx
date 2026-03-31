/**
 * Admin Templates Tab - Full CRUD with Multi-Select Delete + Default Templates Section
 */
import { useState, useEffect } from 'react';
import apiClient from '../../api/client';
import { COLORS } from '../../constants/design';
import { Plus, Star, Trash2, ChevronDown, ChevronUp, Check, Edit2, Save, X, Zap, CheckSquare, Square, Shield, Loader2 } from 'lucide-react';

export default function AdminTemplatesTab() {
  const [templates, setTemplates] = useState([]);
  const [questions, setQuestions] = useState([]);
  const [defaultTemplates, setDefaultTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingT, setEditingT] = useState(null);
  const [expandedT, setExpandedT] = useState(null);
  const [msg, setMsg] = useState('');
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [bulkDeleting, setBulkDeleting] = useState(false);
  const [showDefaults, setShowDefaults] = useState(false);

  const [form, setForm] = useState({
    name: '', description: '', match_type: 'T20',
    template_type: 'full_match', question_ids: [], is_default: false,
    innings_range: [], over_start: null, over_end: null,
    answer_deadline_over: null, phase_label: ''
  });

  const fetchAll = async () => {
    try {
      const [tRes, qRes, dRes] = await Promise.all([
        apiClient.get('/admin/templates?limit=50'),
        apiClient.get('/admin/questions?limit=50'),
        apiClient.get('/admin/default-templates')
      ]);
      setTemplates(tRes.data.templates || []);
      setQuestions(qRes.data.questions || []);
      setDefaultTemplates(dRes.data.default_templates || []);
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
    if (!form.name.trim()) {
      setMsg('Template name is required');
      return;
    }
    try {
      await apiClient.post('/admin/templates', form);
      setMsg(`Template created! ${form.question_ids.length > 0 ? `(${form.question_ids.length} questions)` : '(No questions — add via Edit)'}`);
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
        innings_range: form.innings_range,
        over_start: form.over_start,
        over_end: form.over_end,
        answer_deadline_over: form.answer_deadline_over,
        phase_label: form.phase_label,
      });
      setMsg('Template updated!');
      setEditingT(null);
      resetForm();
      fetchAll();
    } catch (e) { setMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
  };

  const handleToggleDefault = async (id) => {
    try {
      const res = await apiClient.post(`/admin/templates/${id}/toggle-default`);
      setMsg(res.data.message);
      fetchAll();
    } catch (e) { setMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this template?')) return;
    try {
      await apiClient.delete(`/admin/templates/${id}`);
      setMsg('Deleted');
      fetchAll();
    } catch (e) { setMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
  };

  const handleBulkDelete = async () => {
    if (selectedIds.size === 0) return;
    if (!window.confirm(`Delete ${selectedIds.size} selected templates?`)) return;
    setBulkDeleting(true);
    try {
      await apiClient.post('/admin/templates/bulk-delete', { ids: Array.from(selectedIds) });
      setSelectedIds(new Set());
      fetchAll();
    } catch (e) {
      alert('Bulk delete failed: ' + (e.response?.data?.detail || e.message));
    } finally { setBulkDeleting(false); }
  };

  const toggleSelect = (id) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const startEditing = (t) => {
    setForm({
      name: t.name || '', description: t.description || '', match_type: t.match_type || 'T20',
      template_type: t.template_type || 'full_match',
      question_ids: t.question_ids || [],
      is_default: t.is_default || false,
      innings_range: t.innings_range || [],
      over_start: t.over_start || null,
      over_end: t.over_end || null,
      answer_deadline_over: t.answer_deadline_over || null,
      phase_label: t.phase_label || '',
    });
    setEditingT(t.id);
    setShowForm(false);
    setExpandedT(null);
  };

  const resetForm = () => {
    setForm({ name: '', description: '', match_type: 'T20', template_type: 'full_match', question_ids: [], is_default: false,
      innings_range: [], over_start: null, over_end: null, answer_deadline_over: null, phase_label: '' });
  };

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
      question_ids: autoQs.slice(0, 11).map(q => q.id),
      is_default: true,
      innings_range: [], over_start: null, over_end: null,
      answer_deadline_over: null, phase_label: '',
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
      {msg && (
        <div className="text-xs text-center py-1.5 rounded-lg" style={{ background: COLORS.background.card, color: COLORS.info.main }}>
          {msg}
          <button onClick={() => setMsg('')} className="ml-2 opacity-50"><X size={10} /></button>
        </div>
      )}

      {/* Default Templates Section */}
      <div className="rounded-xl overflow-hidden" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.accent.gold}33` }}>
        <button onClick={() => setShowDefaults(!showDefaults)}
          className="w-full flex items-center justify-between p-3">
          <div className="flex items-center gap-2">
            <Shield size={16} color={COLORS.accent.gold} />
            <span className="text-sm font-bold" style={{ color: COLORS.accent.gold }}>Default Templates ({defaultTemplates.length}/5)</span>
          </div>
          {showDefaults ? <ChevronUp size={14} color={COLORS.text.tertiary} /> : <ChevronDown size={14} color={COLORS.text.tertiary} />}
        </button>
        {showDefaults && (
          <div className="px-3 pb-3 border-t space-y-2" style={{ borderColor: COLORS.border.light }}>
            <div className="text-[10px] mt-2" style={{ color: COLORS.text.secondary }}>
              These 5 templates auto-attach to matches 24hrs before start if no manual contest exists.
            </div>
            {defaultTemplates.length === 0 ? (
              <div className="text-xs text-center py-3" style={{ color: COLORS.text.tertiary }}>
                No default templates yet. Create templates below and mark them as Default.
              </div>
            ) : (
              defaultTemplates.map((t, idx) => (
                <div key={t.id} className="flex items-center gap-2 p-2 rounded-lg" style={{ background: COLORS.background.tertiary }}>
                  <Star size={14} color={COLORS.accent.gold} fill={COLORS.accent.gold} />
                  <div className="flex-1 min-w-0">
                    <div className="text-xs font-semibold text-white">{t.name}</div>
                    <div className="flex items-center gap-1.5 mt-0.5">
                      <span className="text-[9px] px-1.5 py-0.5 rounded font-semibold"
                        style={{ background: t.template_type === 'full_match' ? COLORS.primary.main + '22' : COLORS.warning.bg, color: t.template_type === 'full_match' ? COLORS.primary.main : COLORS.warning.main }}>
                        {t.template_type === 'full_match' ? 'FULL MATCH' : 'IN-MATCH'}
                      </span>
                      <span className="text-[9px]" style={{ color: COLORS.text.tertiary }}>{t.question_ids?.length || 0} Qs</span>
                      {t.phase_label && <span className="text-[9px]" style={{ color: '#818cf8' }}>{t.phase_label}</span>}
                    </div>
                  </div>
                  <button onClick={() => handleToggleDefault(t.id)}
                    className="px-2 py-1 rounded text-[10px] font-bold" style={{ background: COLORS.error.bg, color: COLORS.error.main }}>
                    Remove
                  </button>
                </div>
              ))
            )}
            {defaultTemplates.length < 5 && (
              <div className="text-[10px] text-center" style={{ color: COLORS.text.tertiary }}>
                {5 - defaultTemplates.length} slot(s) remaining. Mark templates as Default below.
              </div>
            )}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2 flex-wrap">
        <button data-testid="one-click-template" onClick={oneClickAutoTemplate}
          className="flex items-center gap-1 px-3 py-2 rounded-lg text-xs font-semibold"
          style={{ background: '#f59e0b15', color: '#f59e0b', border: '1px solid #f59e0b22' }}>
          <Zap size={14} /> Auto Template
        </button>
        <button data-testid="add-template-btn" onClick={() => { setShowForm(!showForm); setEditingT(null); resetForm(); }}
          className="flex items-center gap-1 px-3 py-2 rounded-lg text-xs font-semibold" style={{ background: COLORS.primary.main, color: '#fff' }}>
          <Plus size={14} /> New Template
        </button>
      </div>

      {/* Multi-Select Actions */}
      {selectedIds.size > 0 && (
        <div data-testid="bulk-actions-bar" className="flex items-center gap-3 p-2.5 rounded-xl"
          style={{ background: COLORS.error.bg, border: `1px solid ${COLORS.error.main}33` }}>
          <span className="text-xs font-bold" style={{ color: COLORS.error.main }}>{selectedIds.size} selected</span>
          <button data-testid="bulk-delete-templates-btn" onClick={handleBulkDelete} disabled={bulkDeleting}
            className="px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1 disabled:opacity-50"
            style={{ background: COLORS.error.main, color: '#fff' }}>
            {bulkDeleting ? <Loader2 size={12} className="animate-spin" /> : <Trash2 size={12} />}
            Delete Selected
          </button>
          <button onClick={() => setSelectedIds(new Set())}
            className="px-2 py-1 rounded text-xs" style={{ color: COLORS.text.tertiary }}>Clear</button>
        </div>
      )}

      {/* Create/Edit Form */}
      {(showForm || isEditing) && (
        <div className="space-y-3 p-4 rounded-xl" style={{ background: COLORS.background.card, border: `1px solid ${isEditing ? COLORS.info.main + '44' : COLORS.border.light}` }}>
          <div className="text-xs font-bold" style={{ color: isEditing ? COLORS.info.main : COLORS.text.secondary }}>{formTitle}</div>

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
                <span className="text-xs" style={{ color: COLORS.text.secondary }}>Default Template</span>
              </label>
            </div>
          </div>

          {/* In-Match Routing Fields */}
          {form.template_type === 'in_match' && (
            <div className="p-3 rounded-lg space-y-2" style={{ background: '#818cf808', border: '1px solid #818cf818' }}>
              <div className="text-[10px] font-bold" style={{ color: '#818cf8' }}>In-Match Routing Config</div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[10px]" style={{ color: COLORS.text.tertiary }}>Phase Label</label>
                  <input value={form.phase_label || ''} onChange={e => setForm({ ...form, phase_label: e.target.value })}
                    className="w-full mt-0.5 p-1.5 rounded-lg text-[10px] text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}
                    placeholder="e.g. Innings 1 Powerplay" />
                </div>
                <div>
                  <label className="text-[10px]" style={{ color: COLORS.text.tertiary }}>Innings</label>
                  <select value={JSON.stringify(form.innings_range || [])} onChange={e => setForm({ ...form, innings_range: JSON.parse(e.target.value) })}
                    className="w-full mt-0.5 p-1.5 rounded-lg text-[10px] text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}>
                    <option value="[]">Both</option>
                    <option value="[1]">Innings 1</option>
                    <option value="[2]">Innings 2</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="text-[10px]" style={{ color: COLORS.text.tertiary }}>Over Start</label>
                  <input type="number" value={form.over_start || ''} onChange={e => setForm({ ...form, over_start: e.target.value ? parseInt(e.target.value) : null })}
                    className="w-full mt-0.5 p-1.5 rounded-lg text-[10px] text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}
                    placeholder="1" min={1} max={20} />
                </div>
                <div>
                  <label className="text-[10px]" style={{ color: COLORS.text.tertiary }}>Over End</label>
                  <input type="number" value={form.over_end || ''} onChange={e => setForm({ ...form, over_end: e.target.value ? parseInt(e.target.value) : null })}
                    className="w-full mt-0.5 p-1.5 rounded-lg text-[10px] text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}
                    placeholder="6" min={1} max={20} />
                </div>
                <div>
                  <label className="text-[10px]" style={{ color: COLORS.text.tertiary }}>Deadline Over</label>
                  <input type="number" value={form.answer_deadline_over || ''} onChange={e => setForm({ ...form, answer_deadline_over: e.target.value ? parseInt(e.target.value) : null })}
                    className="w-full mt-0.5 p-1.5 rounded-lg text-[10px] text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}
                    placeholder="1" min={1} max={20} />
                </div>
              </div>
            </div>
          )}

          <QuestionPicker />

          <div className="flex gap-2">
            <button data-testid={isEditing ? "update-template-btn" : "create-template-btn"}
              onClick={isEditing ? handleUpdate : handleCreate}
              disabled={!form.name.trim()}
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
              <div key={t.id} className="rounded-xl overflow-hidden" style={{
                background: selectedIds.has(t.id) ? `${COLORS.primary.main}11` : COLORS.background.card,
                border: `1px solid ${t.is_default ? COLORS.accent.gold + '44' : selectedIds.has(t.id) ? COLORS.primary.main + '44' : COLORS.border.light}`
              }}>
                <div className="flex items-center gap-2 p-3">
                  {/* Checkbox */}
                  <button onClick={() => toggleSelect(t.id)} className="shrink-0">
                    {selectedIds.has(t.id) ?
                      <CheckSquare size={16} color={COLORS.primary.main} /> :
                      <Square size={16} color={COLORS.text.tertiary} />
                    }
                  </button>
                  <div className="flex-1 min-w-0 cursor-pointer" onClick={() => setExpandedT(expandedT === t.id ? null : t.id)}>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-white">{t.name}</span>
                      {t.is_default && <Star size={12} color={COLORS.accent.gold} fill={COLORS.accent.gold} />}
                    </div>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-[10px] px-1.5 py-0.5 rounded font-semibold"
                        style={{ background: t.template_type === 'full_match' ? COLORS.primary.main + '22' : COLORS.warning.bg, color: t.template_type === 'full_match' ? COLORS.primary.main : COLORS.warning.main }}>
                        {t.template_type === 'full_match' ? 'FULL MATCH' : 'IN-MATCH'}
                      </span>
                      {t.phase_label && (
                        <span className="text-[9px] px-1.5 py-0.5 rounded font-semibold" style={{ background: '#6366f115', color: '#818cf8' }}>
                          {t.phase_label}
                        </span>
                      )}
                      {t.over_start && t.over_end && (
                        <span className="text-[9px]" style={{ color: COLORS.text.tertiary }}>Ov {t.over_start}-{t.over_end}</span>
                      )}
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
                      <button onClick={() => handleToggleDefault(t.id)}
                        className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs"
                        style={{ background: t.is_default ? COLORS.error.bg : COLORS.accent.gold + '22', color: t.is_default ? COLORS.error.main : COLORS.accent.gold }}>
                        <Star size={12} /> {t.is_default ? 'Remove Default' : 'Set Default'}
                      </button>
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
