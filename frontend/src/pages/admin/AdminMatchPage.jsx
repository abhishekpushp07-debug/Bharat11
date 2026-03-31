/**
 * Admin Match Page — Unified Match + Contest Management
 * NO sub-tabs. Single page with:
 * - Match list (proper IST dates)
 * - Match card: Make Live | Add Contest | Make Unlive
 * - Contest card: 5 actions (Live/Unlive/AI Resolve/AI Answers/Manual Resolve)
 * - Max 5 contests per match
 */
import { useState, useEffect, useCallback } from 'react';
import apiClient from '../../api/client';
import { COLORS } from '../../constants/design';
import {
  Loader2, ChevronDown, ChevronUp, Plus, Play, Pause, Trash2,
  Trophy, Power, Lock, Eye, Zap, Settings, RefreshCw, X, Users, Coins
} from 'lucide-react';

const MAX_CONTESTS = 5;

const toIST = (dt) => {
  if (!dt) return '—';
  return new Date(dt).toLocaleString('en-IN', {
    timeZone: 'Asia/Kolkata',
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit', hour12: true
  });
};

const toISTShort = (dt) => {
  if (!dt) return '—';
  return new Date(dt).toLocaleString('en-IN', {
    timeZone: 'Asia/Kolkata',
    day: '2-digit', month: 'short',
    hour: '2-digit', minute: '2-digit', hour12: true
  });
};

const statusStyle = (s) => ({
  upcoming: { bg: '#3b82f622', c: '#3b82f6', label: 'UPCOMING' },
  live: { bg: '#22c55e22', c: '#22c55e', label: 'LIVE' },
  completed: { bg: '#6b728022', c: '#9ca3af', label: 'COMPLETED' },
  cancelled: { bg: '#ef444422', c: '#ef4444', label: 'CANCELLED' },
  abandoned: { bg: '#ef444422', c: '#ef4444', label: 'ABANDONED' },
}[s] || { bg: '#6b728022', c: '#9ca3af', label: (s || '?').toUpperCase() });


export default function AdminMatchPage() {
  const [matches, setMatches] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [expanded, setExpanded] = useState(null);
  const [matchContests, setMatchContests] = useState({});
  const [msg, setMsg] = useState({ text: '', type: 'info' });

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

  const fetchContestsFor = useCallback(async (matchId) => {
    try {
      const res = await apiClient.get(`/admin/contests?match_id=${matchId}&limit=10`);
      setMatchContests(prev => ({ ...prev, [matchId]: res.data.contests || [] }));
    } catch { setMatchContests(prev => ({ ...prev, [matchId]: [] })); }
  }, []);

  const showMsg = (text, type = 'info') => {
    setMsg({ text, type });
    setTimeout(() => setMsg({ text: '', type: 'info' }), 4000);
  };

  const toggleExpand = async (matchId) => {
    if (expanded === matchId) { setExpanded(null); return; }
    setExpanded(matchId);
    await fetchContestsFor(matchId);
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      const res = await apiClient.post('/matches/live/sync-ipl-schedule');
      const d = res.data;
      showMsg(`Synced! ${d.created || 0} new, ${d.updated || 0} updated, ${d.linked_orphans || 0} linked`, 'success');
      fetchMatches();
    } catch (e) { showMsg(`Sync error: ${e?.response?.data?.detail || e.message}`, 'error'); }
    finally { setSyncing(false); }
  };

  const handleMatchStatus = async (matchId, newStatus) => {
    try {
      await apiClient.put(`/matches/${matchId}/status`, { status: newStatus });
      showMsg(`Match → ${newStatus.toUpperCase()}`, 'success');
      fetchMatches();
    } catch (e) { showMsg(`${e?.response?.data?.detail || e.message}`, 'error'); }
  };

  return (
    <div className="space-y-3" data-testid="admin-match-page">
      {/* Header Actions */}
      <div className="flex items-center gap-2">
        <button data-testid="sync-ipl-btn" onClick={handleSync} disabled={syncing}
          className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-xs font-bold flex-1 justify-center disabled:opacity-50 transition-all"
          style={{ background: '#22c55e22', color: '#22c55e', border: '1px solid #22c55e33' }}>
          {syncing ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
          {syncing ? 'Syncing...' : 'Sync IPL Schedule'}
        </button>
      </div>

      <MsgBar msg={msg} setMsg={setMsg} />

      {/* Match List */}
      {loading ? (
        <div className="flex justify-center py-10"><Loader2 size={24} className="animate-spin" color={COLORS.primary.main} /></div>
      ) : matches.length === 0 ? (
        <div className="text-center py-8 rounded-xl" style={{ background: COLORS.background.card }}>
          <div className="text-sm" style={{ color: COLORS.text.tertiary }}>No matches. Click "Sync IPL Schedule" to fetch.</div>
        </div>
      ) : (
        <div className="space-y-1.5">
          <div className="text-[10px] font-semibold" style={{ color: COLORS.text.tertiary }}>{matches.length} matches (IST)</div>
          {matches.map(m => (
            <MatchCard key={m.id} m={m} templates={templates}
              isExpanded={expanded === m.id}
              onToggle={() => toggleExpand(m.id)}
              contests={matchContests[m.id] || []}
              onMatchStatus={handleMatchStatus}
              onRefreshContests={() => fetchContestsFor(m.id)}
              showMsg={showMsg} />
          ))}
        </div>
      )}
    </div>
  );
}


function MsgBar({ msg, setMsg }) {
  if (!msg.text) return null;
  const bg = msg.type === 'error' ? '#ef444422' : msg.type === 'success' ? '#22c55e22' : COLORS.background.card;
  const c = msg.type === 'error' ? '#ef4444' : msg.type === 'success' ? '#22c55e' : '#60a5fa';
  return (
    <div className="text-xs text-center py-2 rounded-lg flex items-center justify-center gap-2" style={{ background: bg, color: c }}>
      {msg.text}
      <button onClick={() => setMsg({ text: '', type: 'info' })}><X size={12} /></button>
    </div>
  );
}


function MatchCard({ m, templates, isExpanded, onToggle, contests, onMatchStatus, onRefreshContests, showMsg }) {
  const [showAddContest, setShowAddContest] = useState(false);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({ template_id: '', name: '' });

  const tA = m.team_a?.short_name || '?';
  const tB = m.team_b?.short_name || '?';
  const ss = statusStyle(m.status);
  const canAdd = contests.length < MAX_CONTESTS;

  // Score display
  const scores = m.live_score?.scores || [];
  const scoreText = scores.map(s => {
    const r = s.r || s.runs || 0;
    const w = s.w || s.wickets || 0;
    const o = s.o || s.overs || 0;
    return `${r}/${w} (${o})`;
  }).join(' | ');

  const handleCreateContest = async () => {
    if (!form.template_id || !form.name.trim()) return showMsg('Template aur Name required', 'error');
    setCreating(true);
    try {
      await apiClient.post('/admin/contests', {
        match_id: m.id, template_id: form.template_id,
        name: form.name, entry_fee: 500, prize_pool: 0, max_participants: 1000
      });
      showMsg('Contest created!', 'success');
      setShowAddContest(false);
      setForm({ template_id: '', name: '' });
      onRefreshContests();
    } catch (e) { showMsg(`${e?.response?.data?.detail || e.message}`, 'error'); }
    finally { setCreating(false); }
  };

  const handleDeleteContest = async (cid, cname) => {
    if (!window.confirm(`"${cname}" delete karna hai?`)) return;
    try {
      await apiClient.delete(`/admin/contests/${cid}`);
      showMsg('Deleted!', 'success');
      onRefreshContests();
    } catch (e) { showMsg(`${e?.response?.data?.detail || e.message}`, 'error'); }
  };

  const handleContestStatus = async (cid, newStatus) => {
    try {
      await apiClient.put(`/admin/contests/${cid}/status`, { status: newStatus });
      showMsg(`Contest → ${newStatus.toUpperCase()}`, 'success');
      onRefreshContests();
    } catch (e) { showMsg(`${e?.response?.data?.detail || e.message}`, 'error'); }
  };

  return (
    <div data-testid={`match-card-${m.id}`} className="rounded-xl overflow-hidden"
      style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>

      {/* Match Header — clickable */}
      <button className="w-full text-left p-3 flex items-center gap-2" onClick={onToggle}
        data-testid={`match-toggle-${m.id}`}>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-sm font-bold text-white">{tA} vs {tB}</span>
            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded" style={{ background: ss.bg, color: ss.c }}>{ss.label}</span>
          </div>
          <div className="text-[10px] mt-0.5" style={{ color: COLORS.text.tertiary }}>
            {toISTShort(m.start_time)} {scoreText && `• ${scoreText}`}
          </div>
        </div>
        {isExpanded ? <ChevronUp size={14} color={COLORS.text.tertiary} /> : <ChevronDown size={14} color={COLORS.text.tertiary} />}
      </button>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="px-3 pb-3 space-y-2" style={{ borderTop: `1px solid ${COLORS.border.light}` }}>
          {/* Full Details */}
          <div className="text-[10px] mt-2" style={{ color: COLORS.text.tertiary }}>
            {m.venue} | {toIST(m.start_time)}
          </div>
          {m.status_text && (
            <div className="text-[10px] font-semibold" style={{ color: '#f59e0b' }}>{m.status_text}</div>
          )}

          {/* === 3 MATCH ACTIONS === */}
          <div className="flex gap-1.5 flex-wrap">
            {/* Make Match Live */}
            {m.status === 'upcoming' && (
              <button data-testid={`match-go-live-${m.id}`}
                onClick={() => onMatchStatus(m.id, 'live')}
                className="flex items-center gap-1 px-3 py-2 rounded-lg text-[10px] font-bold transition-all"
                style={{ background: '#22c55e22', color: '#22c55e', border: '1px solid #22c55e33' }}>
                <Play size={11} /> Make Live
              </button>
            )}

            {/* Make Match Unlive */}
            {m.status === 'live' && (
              <button data-testid={`match-unlive-${m.id}`}
                onClick={() => onMatchStatus(m.id, 'upcoming')}
                className="flex items-center gap-1 px-3 py-2 rounded-lg text-[10px] font-bold transition-all"
                style={{ background: '#ef444422', color: '#ef4444', border: '1px solid #ef444433' }}>
                <Pause size={11} /> Make Unlive
              </button>
            )}

            {/* Add Contest */}
            {canAdd && m.status !== 'completed' && (
              <button data-testid={`match-add-contest-${m.id}`}
                onClick={() => {
                  setForm({ template_id: '', name: `${tA} vs ${tB} Contest ${contests.length + 1}` });
                  setShowAddContest(!showAddContest);
                }}
                className="flex items-center gap-1 px-3 py-2 rounded-lg text-[10px] font-bold transition-all"
                style={{ background: COLORS.accent.gold + '22', color: COLORS.accent.gold, border: `1px solid ${COLORS.accent.gold}33` }}>
                <Plus size={11} /> Add Contest ({contests.length}/{MAX_CONTESTS})
              </button>
            )}
          </div>

          {/* === ADD CONTEST FORM === */}
          {showAddContest && (
            <div className="space-y-2 p-3 rounded-xl" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.accent.gold}33` }}>
              <div className="text-[10px] font-bold text-white">New Contest</div>
              <select data-testid="contest-template-select" value={form.template_id}
                onChange={e => setForm({ ...form, template_id: e.target.value })}
                className="w-full p-2.5 rounded-lg text-xs text-white"
                style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
                <option value="">-- Select Template --</option>
                {templates.map(t => (
                  <option key={t.id} value={t.id}>
                    {t.name} ({t.template_type === 'full_match' ? 'Full' : 'In-Match'}, {t.question_ids?.length || 0} Qs, {t.total_points || 0} pts)
                  </option>
                ))}
              </select>
              <input data-testid="contest-name-input" value={form.name}
                onChange={e => setForm({ ...form, name: e.target.value })}
                className="w-full p-2.5 rounded-lg text-xs text-white"
                style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}
                placeholder="Contest Name" />
              <button data-testid="submit-create-contest-btn" onClick={handleCreateContest}
                disabled={!form.template_id || !form.name.trim() || creating}
                className="w-full py-2.5 rounded-lg text-xs font-bold disabled:opacity-40 flex items-center justify-center gap-1"
                style={{ background: COLORS.accent.gold, color: '#000' }}>
                {creating ? <Loader2 size={12} className="animate-spin" /> : <Plus size={12} />}
                {creating ? 'Creating...' : 'Create Contest'}
              </button>
            </div>
          )}

          {/* === CONTESTS LIST === */}
          {contests.length > 0 && (
            <div className="space-y-1.5">
              <div className="text-[10px] font-bold text-white">{contests.length} Contest(s)</div>
              {contests.map(c => (
                <ContestCard key={c.id} c={c} templates={templates} matchId={m.id}
                  onDelete={handleDeleteContest}
                  onStatusChange={handleContestStatus} />
              ))}
            </div>
          )}

          {contests.length === 0 && (
            <div className="text-[10px] text-center py-3 rounded-lg" style={{ background: COLORS.background.tertiary, color: COLORS.text.tertiary }}>
              No contests yet
            </div>
          )}
        </div>
      )}
    </div>
  );
}


function ContestCard({ c, templates, matchId, onDelete, onStatusChange }) {
  const [showQuestions, setShowQuestions] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [loadingQs, setLoadingQs] = useState(false);

  const tmpl = templates.find(t => t.id === c.template_id);
  const templateName = tmpl?.name || c.template_name || '—';
  const qCount = tmpl?.question_ids?.length || c.question_count || 0;

  const contestSS = {
    open: { bg: '#f59e0b22', c: '#f59e0b', label: 'OPEN' },
    live: { bg: '#22c55e22', c: '#22c55e', label: 'LIVE' },
    locked: { bg: '#ef444422', c: '#ef4444', label: 'LOCKED' },
    completed: { bg: '#6b728022', c: '#9ca3af', label: 'DONE' },
    cancelled: { bg: '#6b728022', c: '#9ca3af', label: 'CANCELLED' },
  }[c.status] || { bg: '#6b728022', c: '#9ca3af', label: '?' };

  const loadQuestions = async () => {
    if (showQuestions) { setShowQuestions(false); return; }
    setShowQuestions(true);
    if (questions.length > 0) return;
    setLoadingQs(true);
    try {
      const res = await apiClient.get('/admin/questions?limit=50');
      const allQs = res.data.questions || res.data || [];
      const ids = tmpl?.question_ids || [];
      setQuestions(ids.length > 0 ? allQs.filter(q => ids.includes(q.id)) : allQs);
    } catch { setQuestions([]); }
    finally { setLoadingQs(false); }
  };

  // Navigate to Resolve page for AI resolve
  const goToResolve = () => {
    // Store match context and switch to Resolve tab
    window.__adminNavigate?.('resolve', { matchId, contestId: c.id });
  };

  return (
    <div data-testid={`contest-card-${c.id}`} className="rounded-lg overflow-hidden"
      style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}>

      {/* Contest Header */}
      <div className="p-2.5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <Trophy size={12} color={COLORS.accent.gold} />
            <span className="text-[11px] font-bold text-white">{c.name}</span>
          </div>
          <span className="text-[9px] font-bold px-1.5 py-0.5 rounded" style={{ background: contestSS.bg, color: contestSS.c }}>{contestSS.label}</span>
        </div>

        {/* Template info */}
        <button onClick={loadQuestions} data-testid={`contest-template-${c.id}`}
          className="flex items-center gap-1 mt-1.5 text-[9px] font-semibold px-2 py-0.5 rounded transition-all"
          style={{ background: '#8b5cf622', color: '#a78bfa' }}>
          <Eye size={9} /> {templateName} ({qCount}Q) {showQuestions ? '▲' : '▼'}
        </button>

        {/* Stats */}
        <div className="flex items-center gap-3 mt-1.5">
          <span className="text-[9px] flex items-center gap-1" style={{ color: COLORS.text.tertiary }}>
            <Coins size={9} color={COLORS.accent.gold} /> {c.entry_fee}
          </span>
          <span className="text-[9px] flex items-center gap-1" style={{ color: COLORS.text.tertiary }}>
            <Users size={9} color="#60a5fa" /> {c.current_participants || 0}/{c.max_participants}
          </span>
        </div>

        {/* === 5 CONTEST ACTIONS === */}
        <div className="grid grid-cols-2 gap-1 mt-2">
          {/* 1. Make Contest Live */}
          {(c.status === 'open' || c.status === 'locked') && (
            <ActionBtn testId={`contest-live-${c.id}`}
              onClick={() => onStatusChange(c.id, 'live')}
              icon={<Power size={10} />} label="Make Live"
              bg="#22c55e22" color="#22c55e" />
          )}

          {/* 2. Make Contest Unlive */}
          {c.status === 'live' && (
            <ActionBtn testId={`contest-unlive-${c.id}`}
              onClick={() => onStatusChange(c.id, 'open')}
              icon={<Pause size={10} />} label="Make Unlive"
              bg="#f59e0b22" color="#f59e0b" />
          )}

          {/* 3. Resolve by AI */}
          {c.status !== 'cancelled' && (
            <ActionBtn testId={`contest-ai-resolve-${c.id}`}
              onClick={goToResolve}
              icon={<Zap size={10} />} label="AI Resolve"
              bg="#8b5cf622" color="#a78bfa" />
          )}

          {/* 4. See AI Answers & Override */}
          {c.status !== 'cancelled' && (
            <ActionBtn testId={`contest-ai-answers-${c.id}`}
              onClick={goToResolve}
              icon={<Eye size={10} />} label="AI Answers"
              bg="#3b82f622" color="#60a5fa" />
          )}

          {/* 5. Answer & Resolve Manually */}
          {c.status !== 'cancelled' && (
            <ActionBtn testId={`contest-manual-resolve-${c.id}`}
              onClick={goToResolve}
              icon={<Settings size={10} />} label="Manual Resolve"
              bg="#06b6d422" color="#22d3ee" />
          )}

          {/* Delete */}
          <ActionBtn testId={`delete-contest-${c.id}`}
            onClick={() => onDelete(c.id, c.name)}
            icon={<Trash2 size={10} />} label="Delete"
            bg="#ef444422" color="#ef4444" />
        </div>
      </div>

      {/* Questions Panel */}
      {showQuestions && (
        <div className="px-2.5 pb-2.5" style={{ borderTop: `1px solid ${COLORS.border.light}` }}>
          {loadingQs ? (
            <div className="flex justify-center py-3"><Loader2 size={14} className="animate-spin" color={COLORS.primary.main} /></div>
          ) : questions.length === 0 ? (
            <div className="text-[9px] text-center py-2" style={{ color: COLORS.text.tertiary }}>No questions</div>
          ) : (
            <div className="space-y-1.5 mt-2">
              {questions.map((q, idx) => (
                <QuestionRow key={q.id} q={q} idx={idx} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}


function ActionBtn({ testId, onClick, icon, label, bg, color }) {
  return (
    <button data-testid={testId} onClick={onClick}
      className="flex items-center justify-center gap-1 px-2 py-1.5 rounded text-[9px] font-bold transition-all hover:opacity-80"
      style={{ background: bg, color }}>
      {icon} {label}
    </button>
  );
}


function QuestionRow({ q, idx }) {
  const dc = { easy: '#22c55e', medium: '#f59e0b', hard: '#ef4444' }[q.difficulty] || '#9ca3af';
  return (
    <div className="p-2 rounded" style={{ background: COLORS.background.card }}>
      <div className="flex items-start gap-1.5">
        <span className="text-[9px] font-bold text-white shrink-0">Q{idx + 1}</span>
        <div className="flex-1">
          <div className="text-[10px] font-semibold text-white leading-tight">{q.question_text_hi}</div>
          <span className="text-[8px] font-bold px-1 py-0.5 rounded mt-0.5 inline-block" style={{ background: dc + '22', color: dc }}>
            {q.difficulty?.toUpperCase()} {q.points}pts
          </span>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-1 mt-1.5">
        {(q.options || []).map(opt => (
          <div key={opt.key} className="text-[9px] px-2 py-1 rounded"
            style={{ background: COLORS.background.tertiary, color: COLORS.text.secondary }}>
            <span className="font-bold">{opt.key}.</span> {opt.text_hi}
          </div>
        ))}
      </div>
    </div>
  );
}
