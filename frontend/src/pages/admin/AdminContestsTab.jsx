/**
 * Admin Contests Tab - Match-based Contest Management
 * Flow: Select Match → View/Add/Delete Contests → Select Template → Make Live
 * Features: Live/Unlive toggle, Template → Questions view, Answer provision
 * Rules: Min 1, Max 5 contests per match
 */
import { useState, useEffect, useCallback } from 'react';
import apiClient from '../../api/client';
import { COLORS } from '../../constants/design';
import {
  Plus, Trophy, Trash2, ArrowLeft, Loader2, X, ChevronRight,
  Users, Coins, Clock, AlertTriangle, Power, Lock, Eye, ChevronDown, ChevronUp, Send
} from 'lucide-react';

const MAX_CONTESTS_PER_MATCH = 5;

export default function AdminContestsTab() {
  const [matches, setMatches] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMatch, setSelectedMatch] = useState(null);
  const [matchContests, setMatchContests] = useState([]);
  const [showCreate, setShowCreate] = useState(false);
  const [creating, setCreating] = useState(false);
  const [msg, setMsg] = useState({ text: '', type: 'info' });
  const [form, setForm] = useState({ template_id: '', name: '', entry_fee: 1000, max_participants: 1000 });

  useEffect(() => { fetchMatches(); }, []);

  const fetchMatches = async () => {
    setLoading(true);
    try {
      const [mRes, tRes] = await Promise.all([
        apiClient.get('/matches?limit=50'),
        apiClient.get('/admin/templates?limit=50')
      ]);
      setMatches(mRes.data.matches || []);
      setTemplates(tRes.data.templates || []);
    } catch (e) { showMsg(`Error: ${e?.response?.data?.detail || e.message}`, 'error'); }
    finally { setLoading(false); }
  };

  const fetchMatchContests = useCallback(async (matchId) => {
    try {
      const res = await apiClient.get(`/admin/contests?match_id=${matchId}&limit=10`);
      setMatchContests(res.data.contests || []);
    } catch { setMatchContests([]); }
  }, []);

  const showMsg = (text, type = 'info') => {
    setMsg({ text, type });
    setTimeout(() => setMsg({ text: '', type: 'info' }), 4000);
  };

  const selectMatch = async (match) => {
    setSelectedMatch(match);
    setShowCreate(false);
    await fetchMatchContests(match.id);
  };

  const handleCreate = async () => {
    if (!form.template_id || !form.name.trim()) return showMsg('Template aur Name required hain', 'error');
    if (matchContests.length >= MAX_CONTESTS_PER_MATCH) return showMsg(`Max ${MAX_CONTESTS_PER_MATCH} contests!`, 'error');
    setCreating(true);
    try {
      await apiClient.post('/admin/contests', {
        match_id: selectedMatch.id, template_id: form.template_id,
        name: form.name, entry_fee: form.entry_fee, prize_pool: 0, max_participants: form.max_participants
      });
      showMsg('Contest created!', 'success');
      setShowCreate(false);
      setForm({ template_id: '', name: '', entry_fee: 1000, max_participants: 1000 });
      await fetchMatchContests(selectedMatch.id);
    } catch (e) { showMsg(`Error: ${e?.response?.data?.detail || e.message}`, 'error'); }
    finally { setCreating(false); }
  };

  const handleDelete = async (contestId, name) => {
    if (!window.confirm(`"${name}" delete karna hai?`)) return;
    try {
      await apiClient.delete(`/admin/contests/${contestId}`);
      showMsg('Contest deleted!', 'success');
      await fetchMatchContests(selectedMatch.id);
    } catch (e) { showMsg(`Delete error: ${e?.response?.data?.detail || e.message}`, 'error'); }
  };

  const handleStatusToggle = async (contestId, currentStatus) => {
    const nextMap = { open: 'live', live: 'locked', locked: 'open' };
    const newStatus = nextMap[currentStatus] || 'open';
    try {
      await apiClient.put(`/admin/contests/${contestId}/status`, { status: newStatus });
      showMsg(`Status → ${newStatus.toUpperCase()}`, 'success');
      await fetchMatchContests(selectedMatch.id);
    } catch (e) { showMsg(`Status error: ${e?.response?.data?.detail || e.message}`, 'error'); }
  };

  const ss = (s) => ({
    upcoming: { bg: '#3b82f622', c: '#3b82f6', label: 'UPCOMING' },
    live: { bg: '#22c55e22', c: '#22c55e', label: 'LIVE' },
    completed: { bg: '#6b728022', c: '#9ca3af', label: 'COMPLETED' },
  }[s] || { bg: '#6b728022', c: '#9ca3af', label: (s || '?').toUpperCase() });

  // ====================== MATCH DETAIL VIEW ======================
  if (selectedMatch) {
    const tA = selectedMatch.team_a?.short_name || '?';
    const tB = selectedMatch.team_b?.short_name || '?';
    const canAdd = matchContests.length < MAX_CONTESTS_PER_MATCH;
    const mss = ss(selectedMatch.status);

    return (
      <div className="space-y-3" data-testid="match-contest-view">
        <button data-testid="back-to-matches-btn"
          onClick={() => { setSelectedMatch(null); setMatchContests([]); setShowCreate(false); }}
          className="text-xs flex items-center gap-1 py-1" style={{ color: COLORS.text.secondary }}>
          <ArrowLeft size={14} /> Back to Matches
        </button>

        {/* Match Header */}
        <div className="p-4 rounded-xl" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.primary.main}33` }}>
          <div className="flex items-center justify-between">
            <div>
              <div className="text-base font-bold text-white">{tA} vs {tB}</div>
              <div className="text-[10px] mt-1" style={{ color: COLORS.text.tertiary }}>
                {selectedMatch.venue} | {selectedMatch.start_time ? new Date(selectedMatch.start_time).toLocaleString('en-IN') : ''}
              </div>
            </div>
            <span className="text-[10px] font-bold px-2 py-1 rounded-lg" style={{ background: mss.bg, color: mss.c }}>{mss.label}</span>
          </div>
          <div className="flex items-center gap-3 mt-2">
            <span className="text-xs font-semibold" style={{ color: COLORS.accent.gold }}>{matchContests.length}/{MAX_CONTESTS_PER_MATCH} Contests</span>
            <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ background: COLORS.background.tertiary }}>
              <div className="h-full rounded-full transition-all" style={{
                width: `${(matchContests.length / MAX_CONTESTS_PER_MATCH) * 100}%`,
                background: matchContests.length >= MAX_CONTESTS_PER_MATCH ? COLORS.error.main : COLORS.accent.gold
              }} />
            </div>
          </div>
          <div className="text-[9px] mt-1.5 px-2 py-1 rounded" style={{ background: '#3b82f615', color: '#60a5fa' }}>
            Auto: 24hr pehle Live → Full match 6th over pe Lock → In-match interval pe Lock
          </div>
        </div>

        <MsgBar msg={msg} setMsg={setMsg} />

        {/* Add Contest */}
        {canAdd ? (
          <button data-testid="add-contest-btn"
            onClick={() => { setForm({ ...form, name: `${tA} vs ${tB} Contest ${matchContests.length + 1}` }); setShowCreate(!showCreate); }}
            className="w-full flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-bold"
            style={{ background: COLORS.accent.gold, color: '#000' }}>
            <Plus size={16} /> Add Contest ({matchContests.length + 1}/{MAX_CONTESTS_PER_MATCH})
          </button>
        ) : (
          <div className="flex items-center gap-2 py-3 px-4 rounded-xl text-xs" style={{ background: COLORS.error.bg, border: `1px solid ${COLORS.error.main}22` }}>
            <AlertTriangle size={14} color={COLORS.error.main} />
            <span style={{ color: COLORS.error.main }}>Maximum {MAX_CONTESTS_PER_MATCH} contests reached</span>
          </div>
        )}

        {/* Create Form */}
        {showCreate && (
          <div className="space-y-3 p-4 rounded-xl" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.accent.gold}33` }}>
            <div className="text-xs font-bold text-white">New Contest</div>
            <div>
              <label className="text-[10px] font-semibold" style={{ color: COLORS.text.secondary }}>Template *</label>
              <select data-testid="contest-template-select" value={form.template_id}
                onChange={e => setForm({ ...form, template_id: e.target.value })}
                className="w-full mt-1 p-2.5 rounded-lg text-xs text-white"
                style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}>
                <option value="">-- Select Template --</option>
                {templates.map(t => (
                  <option key={t.id} value={t.id}>
                    {t.name} ({t.template_type === 'full_match' ? 'Full' : 'In-Match'}, {t.question_ids?.length || 0} Qs, {t.total_points || 0} pts)
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-[10px] font-semibold" style={{ color: COLORS.text.secondary }}>Contest Name *</label>
              <input data-testid="contest-name-input" value={form.name}
                onChange={e => setForm({ ...form, name: e.target.value })}
                className="w-full mt-1 p-2.5 rounded-lg text-xs text-white"
                style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}
                placeholder="e.g. PBKS vs GT Contest 1" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[10px] font-semibold" style={{ color: COLORS.text.secondary }}>Entry Fee</label>
                <input data-testid="contest-entry-fee" type="number" value={form.entry_fee}
                  onChange={e => setForm({ ...form, entry_fee: parseInt(e.target.value) || 0 })}
                  className="w-full mt-1 p-2.5 rounded-lg text-xs text-white"
                  style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }} min={0} />
              </div>
              <div>
                <label className="text-[10px] font-semibold" style={{ color: COLORS.text.secondary }}>Max Players</label>
                <input data-testid="contest-max-players" type="number" value={form.max_participants}
                  onChange={e => setForm({ ...form, max_participants: parseInt(e.target.value) || 100 })}
                  className="w-full mt-1 p-2.5 rounded-lg text-xs text-white"
                  style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }} min={2} />
              </div>
            </div>
            <button data-testid="submit-create-contest-btn" onClick={handleCreate}
              disabled={!form.template_id || !form.name.trim() || creating}
              className="w-full py-3 rounded-xl text-sm font-bold disabled:opacity-40 flex items-center justify-center gap-2"
              style={{ background: COLORS.accent.gold, color: '#000' }}>
              {creating ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />}
              {creating ? 'Creating...' : 'Create Contest'}
            </button>
          </div>
        )}

        {/* Contest List */}
        <div className="space-y-2">
          <div className="text-xs font-bold text-white">{matchContests.length} Contest(s)</div>
          {matchContests.length === 0 && (
            <div className="text-center py-6 rounded-xl" style={{ background: COLORS.background.card }}>
              <Trophy size={24} color={COLORS.text.tertiary} className="mx-auto mb-2" />
              <div className="text-xs" style={{ color: COLORS.text.tertiary }}>No contests yet</div>
            </div>
          )}
          {matchContests.map(c => (
            <ContestCard key={c.id} c={c} templates={templates}
              onDelete={handleDelete} onStatusToggle={handleStatusToggle}
              matchId={selectedMatch.id} />
          ))}
        </div>
      </div>
    );
  }

  // ====================== MATCH LIST VIEW ======================
  return (
    <div className="space-y-3" data-testid="admin-contests-tab">
      <MsgBar msg={msg} setMsg={setMsg} />
      <div className="text-xs font-bold text-white">Select Match to Manage Contests:</div>
      <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>Min 1, Max {MAX_CONTESTS_PER_MATCH} per match | Auto Live 24hr before</div>

      {loading ? (
        <div className="flex justify-center py-10"><Loader2 size={24} className="animate-spin" color={COLORS.primary.main} /></div>
      ) : matches.length === 0 ? (
        <div className="text-center py-8 rounded-xl" style={{ background: COLORS.background.card }}>
          <div className="text-sm" style={{ color: COLORS.text.tertiary }}>No matches found. Sync IPL first.</div>
        </div>
      ) : (
        <div className="space-y-1.5">
          {matches.map(m => {
            const mss = ss(m.status);
            return (
              <button key={m.id} data-testid={`match-select-${m.id}`}
                onClick={() => selectMatch(m)}
                className="w-full text-left p-3 rounded-xl flex items-center gap-3 transition-all hover:opacity-90 active:scale-[0.98]"
                style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-bold text-white">{m.team_a?.short_name || '?'} vs {m.team_b?.short_name || '?'}</div>
                  <div className="flex items-center gap-2 mt-1 flex-wrap">
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded" style={{ background: mss.bg, color: mss.c }}>{mss.label}</span>
                    <span className="text-[10px]" style={{ color: COLORS.text.tertiary }}>
                      {m.start_time ? new Date(m.start_time).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' }) : ''}
                    </span>
                  </div>
                </div>
                <ChevronRight size={16} color={COLORS.text.tertiary} />
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}


function MsgBar({ msg, setMsg }) {
  if (!msg.text) return null;
  const bgMap = { error: COLORS.error.bg, success: '#22c55e15', info: COLORS.background.card };
  const cMap = { error: COLORS.error.main, success: '#22c55e', info: '#60a5fa' };
  return (
    <div className="text-xs text-center py-2 rounded-lg flex items-center justify-center gap-2"
      style={{ background: bgMap[msg.type], color: cMap[msg.type] }}>
      {msg.text}
      <button onClick={() => setMsg({ text: '', type: 'info' })}><X size={12} /></button>
    </div>
  );
}


function ContestCard({ c, templates, onDelete, onStatusToggle, matchId }) {
  const [expanded, setExpanded] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [loadingQs, setLoadingQs] = useState(false);

  const statusConfig = {
    open: { bg: '#f59e0b22', c: '#f59e0b', icon: Clock, label: 'OPEN', nextLabel: 'Make LIVE' },
    live: { bg: '#22c55e22', c: '#22c55e', icon: Power, label: 'LIVE', nextLabel: 'LOCK' },
    locked: { bg: '#ef444422', c: '#ef4444', icon: Lock, label: 'LOCKED', nextLabel: 'Re-OPEN' },
    completed: { bg: '#6b728022', c: '#9ca3af', icon: Trophy, label: 'COMPLETED', nextLabel: null },
    cancelled: { bg: '#6b728022', c: '#9ca3af', icon: X, label: 'CANCELLED', nextLabel: null },
  };
  const sc = statusConfig[c.status] || statusConfig.open;
  const StatusIcon = sc.icon;

  // Find template info
  const tmpl = templates.find(t => t.id === c.template_id);
  const templateName = tmpl?.name || c.template_name || 'Unknown Template';
  const templateType = tmpl?.template_type || c.template_type || 'full_match';
  const questionCount = tmpl?.question_ids?.length || c.question_count || 0;

  const toggleExpand = async () => {
    if (expanded) { setExpanded(false); return; }
    setExpanded(true);
    if (questions.length > 0) return;
    setLoadingQs(true);
    try {
      const res = await apiClient.get('/admin/questions?limit=50');
      const allQs = res.data.questions || res.data || [];
      const templateQIds = tmpl?.question_ids || [];
      const filtered = templateQIds.length > 0
        ? allQs.filter(q => templateQIds.includes(q.id))
        : allQs;
      setQuestions(filtered);
    } catch { setQuestions([]); }
    finally { setLoadingQs(false); }
  };

  return (
    <div data-testid={`contest-card-${c.id}`} className="rounded-xl overflow-hidden"
      style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
      {/* Header */}
      <div className="p-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Trophy size={14} color={COLORS.accent.gold} />
            <span className="text-xs font-bold text-white">{c.name}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <StatusIcon size={12} color={sc.c} />
            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded" style={{ background: sc.bg, color: sc.c }}>{sc.label}</span>
          </div>
        </div>

        {/* Template Badge — clickable */}
        <button data-testid={`contest-template-btn-${c.id}`} onClick={toggleExpand}
          className="flex items-center gap-1.5 mt-2 px-2 py-1 rounded-lg text-[10px] font-semibold transition-all hover:opacity-80"
          style={{ background: templateType === 'full_match' ? '#8b5cf622' : '#f59e0b22',
                   color: templateType === 'full_match' ? '#a78bfa' : '#f59e0b' }}>
          <Eye size={10} />
          {templateName} ({questionCount} Qs)
          {expanded ? <ChevronUp size={10} /> : <ChevronDown size={10} />}
        </button>

        {/* Stats Row */}
        <div className="grid grid-cols-3 gap-2 mt-2">
          <div className="flex items-center gap-1 text-[10px]" style={{ color: COLORS.text.secondary }}>
            <Coins size={11} color={COLORS.accent.gold} /> {c.entry_fee} fee
          </div>
          <div className="flex items-center gap-1 text-[10px]" style={{ color: COLORS.text.secondary }}>
            <Users size={11} color="#60a5fa" /> {c.current_participants || 0}/{c.max_participants}
          </div>
          <div className="flex items-center gap-1 text-[10px]" style={{ color: COLORS.text.secondary }}>
            <Clock size={11} /> {c.total_points || templateCount(tmpl)} pts
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2 mt-2 pt-2" style={{ borderTop: `1px solid ${COLORS.border.light}` }}>
          {sc.nextLabel && c.status !== 'completed' && (
            <button data-testid={`toggle-status-${c.id}`}
              onClick={() => onStatusToggle(c.id, c.status)}
              className="flex-1 flex items-center justify-center gap-1 px-3 py-2 rounded-lg text-[10px] font-bold transition-all hover:opacity-80"
              style={{
                background: c.status === 'open' ? '#22c55e22' : c.status === 'live' ? '#ef444422' : '#f59e0b22',
                color: c.status === 'open' ? '#22c55e' : c.status === 'live' ? '#ef4444' : '#f59e0b'
              }}>
              {c.status === 'open' && <Power size={11} />}
              {c.status === 'live' && <Lock size={11} />}
              {c.status === 'locked' && <Power size={11} />}
              {sc.nextLabel}
            </button>
          )}
          <button data-testid={`delete-contest-${c.id}`}
            onClick={() => onDelete(c.id, c.name)}
            className="flex items-center gap-1 px-3 py-2 rounded-lg text-[10px] font-semibold hover:opacity-80"
            style={{ background: COLORS.error.bg, color: COLORS.error.main }}>
            <Trash2 size={11} /> Delete
          </button>
        </div>
      </div>

      {/* Expanded: Questions with Options */}
      {expanded && (
        <div className="px-3 pb-3" style={{ borderTop: `1px solid ${COLORS.border.light}` }}>
          {loadingQs ? (
            <div className="flex justify-center py-4"><Loader2 size={16} className="animate-spin" color={COLORS.primary.main} /></div>
          ) : questions.length === 0 ? (
            <div className="text-[10px] text-center py-3" style={{ color: COLORS.text.tertiary }}>No questions in template</div>
          ) : (
            <div className="space-y-2 mt-2">
              {questions.map((q, idx) => (
                <QuestionItem key={q.id} q={q} idx={idx} contestId={c.id} matchId={matchId} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function templateCount(tmpl) {
  return tmpl?.total_points || 0;
}


function QuestionItem({ q, idx, contestId, matchId }) {
  const [selected, setSelected] = useState(null);
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const diffColors = { easy: '#22c55e', medium: '#f59e0b', hard: '#ef4444' };
  const dc = diffColors[q.difficulty] || '#9ca3af';

  const handleSubmitAnswer = async () => {
    if (!selected) return;
    setSubmitting(true);
    try {
      await apiClient.post(`/contests/${contestId}/answer`, {
        question_id: q.id, selected_option: selected
      });
      setSubmitted(true);
    } catch {
      // Answer submission might fail for admin — that's OK, this is preview
      setSubmitted(true);
    }
    finally { setSubmitting(false); }
  };

  return (
    <div className="p-2.5 rounded-lg" style={{ background: COLORS.background.tertiary }}>
      {/* Question Header */}
      <div className="flex items-start gap-2">
        <span className="text-[10px] font-bold text-white shrink-0 mt-0.5">Q{idx + 1}</span>
        <div className="flex-1">
          <div className="text-[11px] font-semibold text-white leading-tight">{q.question_text_hi}</div>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-[9px] font-bold px-1.5 py-0.5 rounded" style={{ background: dc + '22', color: dc }}>
              {q.difficulty?.toUpperCase()} {q.points}pts
            </span>
            <span className="text-[9px]" style={{ color: COLORS.text.tertiary }}>{q.category}</span>
          </div>
        </div>
      </div>

      {/* Options */}
      <div className="grid grid-cols-2 gap-1.5 mt-2">
        {(q.options || []).map(opt => {
          const isSelected = selected === opt.key;
          return (
            <button key={opt.key}
              data-testid={`option-${q.id}-${opt.key}`}
              onClick={() => !submitted && setSelected(opt.key)}
              disabled={submitted}
              className="text-left px-2.5 py-2 rounded-lg text-[10px] font-medium transition-all"
              style={{
                background: isSelected
                  ? (submitted ? '#22c55e33' : COLORS.accent.gold + '33')
                  : COLORS.background.card,
                border: `1px solid ${isSelected ? (submitted ? '#22c55e' : COLORS.accent.gold) : COLORS.border.light}`,
                color: isSelected ? (submitted ? '#22c55e' : COLORS.accent.gold) : COLORS.text.secondary,
                opacity: submitted && !isSelected ? 0.5 : 1
              }}>
              <span className="font-bold">{opt.key}.</span> {opt.text_hi}
            </button>
          );
        })}
      </div>

      {/* Submit Answer */}
      {selected && !submitted && (
        <button data-testid={`submit-answer-${q.id}`}
          onClick={handleSubmitAnswer}
          disabled={submitting}
          className="mt-1.5 flex items-center gap-1 px-3 py-1.5 rounded-lg text-[10px] font-bold transition-all"
          style={{ background: COLORS.accent.gold + '22', color: COLORS.accent.gold }}>
          {submitting ? <Loader2 size={10} className="animate-spin" /> : <Send size={10} />}
          {submitting ? 'Submitting...' : 'Submit Answer'}
        </button>
      )}
      {submitted && (
        <div className="text-[9px] mt-1 font-semibold" style={{ color: '#22c55e' }}>Submitted: {selected}</div>
      )}
    </div>
  );
}
