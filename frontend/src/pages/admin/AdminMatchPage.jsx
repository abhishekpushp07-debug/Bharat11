/**
 * Admin Match Page — 2 Sub-Tabs: Matches | Contests
 * Each tab has 3 sections: LIVE, UPCOMING, COMPLETED
 * Match card: Make Live | Add Contest | Make Unlive
 * Contest card: 5 actions
 * All times displayed in IST (GMT+5:30)
 */
import { useState, useEffect, useCallback } from 'react';
import apiClient from '../../api/client';
import { COLORS } from '../../constants/design';
import {
  Loader2, Plus, Play, Pause, Trash2, Trophy, Power, Lock,
  Eye, Zap, Settings, RefreshCw, X, Users, Coins, ChevronDown, ChevronUp
} from 'lucide-react';

const MAX_CONTESTS = 5;

const toIST = (dt) => {
  if (!dt) return '—';
  try {
    return new Date(dt).toLocaleString('en-IN', {
      timeZone: 'Asia/Kolkata', day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit', hour12: true
    });
  } catch { return dt; }
};

const toISTShort = (dt) => {
  if (!dt) return '—';
  try {
    return new Date(dt).toLocaleString('en-IN', {
      timeZone: 'Asia/Kolkata', day: '2-digit', month: 'short',
      hour: '2-digit', minute: '2-digit', hour12: true
    });
  } catch { return dt; }
};

export default function AdminMatchPage() {
  const [subTab, setSubTab] = useState('matches');
  const [matches, setMatches] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [allContests, setAllContests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [msg, setMsg] = useState({ text: '', type: '' });

  useEffect(() => { fetchAll(); }, []);

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [mR, tR, cR] = await Promise.all([
        apiClient.get('/matches?limit=50'),
        apiClient.get('/admin/templates?limit=50'),
        apiClient.get('/admin/contests?limit=50')
      ]);
      setMatches(mR.data.matches || []);
      setTemplates(tR.data.templates || []);
      setAllContests(cR.data.contests || []);
    } catch (e) { showMsg(e?.response?.data?.detail || e.message, 'error'); }
    finally { setLoading(false); }
  };

  const showMsg = (text, type = 'info') => {
    setMsg({ text, type });
    setTimeout(() => setMsg({ text: '', type: '' }), 4000);
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      const r = await apiClient.post('/matches/live/sync-ipl-schedule');
      showMsg(`Synced! ${r.data.created || 0} new, ${r.data.updated || 0} updated`, 'success');
      fetchAll();
    } catch (e) { showMsg(`Sync: ${e?.response?.data?.detail || e.message}`, 'error'); }
    finally { setSyncing(false); }
  };

  // Group by status
  const grouped = (items, statusKey = 'status') => {
    const live = items.filter(i => i[statusKey] === 'live');
    const upcoming = items.filter(i => i[statusKey] === 'upcoming' || i[statusKey] === 'open');
    const completed = items.filter(i => !['live', 'upcoming', 'open'].includes(i[statusKey]));
    return { live, upcoming, completed };
  };

  const matchGroups = grouped(matches);
  const contestGroups = grouped(allContests);

  const tabStyle = (t) => ({
    background: subTab === t ? COLORS.accent.gold : 'transparent',
    color: subTab === t ? '#000' : COLORS.text.secondary,
    fontWeight: 700, fontSize: '12px', padding: '8px 20px',
    borderRadius: '8px', border: 'none', cursor: 'pointer',
    transition: 'all 0.2s'
  });

  return (
    <div className="space-y-3" data-testid="admin-match-page">
      {/* Sync + Sub-Tabs */}
      <div className="flex items-center gap-2">
        <button data-testid="sync-ipl-btn" onClick={handleSync} disabled={syncing}
          className="flex items-center gap-1 px-3 py-2 rounded-lg text-[10px] font-bold disabled:opacity-50"
          style={{ background: '#22c55e22', color: '#22c55e', border: '1px solid #22c55e33' }}>
          {syncing ? <Loader2 size={12} className="animate-spin" /> : <RefreshCw size={12} />}
          {syncing ? 'Syncing...' : 'Sync IPL'}
        </button>
        <div className="flex-1 flex justify-center gap-1 p-1 rounded-xl" style={{ background: COLORS.background.tertiary }}>
          <button data-testid="sub-tab-matches" style={tabStyle('matches')} onClick={() => setSubTab('matches')}>
            Matches
          </button>
          <button data-testid="sub-tab-contests" style={tabStyle('contests')} onClick={() => setSubTab('contests')}>
            Contests
          </button>
        </div>
      </div>

      <MsgBar msg={msg} setMsg={setMsg} />

      {loading ? (
        <div className="flex justify-center py-10"><Loader2 size={24} className="animate-spin" color={COLORS.primary.main} /></div>
      ) : subTab === 'matches' ? (
        <MatchesView groups={matchGroups} templates={templates} allContests={allContests}
          showMsg={showMsg} onRefresh={fetchAll} />
      ) : (
        <ContestsView groups={contestGroups} templates={templates} matches={matches}
          showMsg={showMsg} onRefresh={fetchAll} />
      )}
    </div>
  );
}


// ============================================================
// MATCHES VIEW — 3 sections: Live | Upcoming | Completed
// ============================================================
function MatchesView({ groups, templates, allContests, showMsg, onRefresh }) {
  return (
    <div className="space-y-4">
      <StatusSection label="LIVE" icon={<Play size={12} />} color="#22c55e"
        items={groups.live} emptyText="No live matches">
        {groups.live.map(m => (
          <MatchCard key={m.id} m={m} templates={templates} allContests={allContests}
            showMsg={showMsg} onRefresh={onRefresh} />
        ))}
      </StatusSection>

      <StatusSection label="UPCOMING" icon={<Power size={12} />} color="#3b82f6"
        items={groups.upcoming} emptyText="No upcoming matches">
        {groups.upcoming.map(m => (
          <MatchCard key={m.id} m={m} templates={templates} allContests={allContests}
            showMsg={showMsg} onRefresh={onRefresh} />
        ))}
      </StatusSection>

      <StatusSection label="COMPLETED" icon={<Trophy size={12} />} color="#9ca3af"
        items={groups.completed} emptyText="No completed matches" collapsed>
        {groups.completed.map(m => (
          <MatchCard key={m.id} m={m} templates={templates} allContests={allContests}
            showMsg={showMsg} onRefresh={onRefresh} />
        ))}
      </StatusSection>
    </div>
  );
}


// ============================================================
// CONTESTS VIEW — 3 sections: Live | Upcoming(Open) | Completed
// ============================================================
function ContestsView({ groups, templates, matches, showMsg, onRefresh }) {
  return (
    <div className="space-y-4">
      <StatusSection label="LIVE" icon={<Play size={12} />} color="#22c55e"
        items={groups.live} emptyText="No live contests">
        {groups.live.map(c => (
          <ContestFullCard key={c.id} c={c} templates={templates} matches={matches}
            showMsg={showMsg} onRefresh={onRefresh} />
        ))}
      </StatusSection>

      <StatusSection label="OPEN" icon={<Power size={12} />} color="#f59e0b"
        items={groups.upcoming} emptyText="No open contests">
        {groups.upcoming.map(c => (
          <ContestFullCard key={c.id} c={c} templates={templates} matches={matches}
            showMsg={showMsg} onRefresh={onRefresh} />
        ))}
      </StatusSection>

      <StatusSection label="COMPLETED / LOCKED" icon={<Lock size={12} />} color="#9ca3af"
        items={groups.completed} emptyText="No completed contests" collapsed>
        {groups.completed.map(c => (
          <ContestFullCard key={c.id} c={c} templates={templates} matches={matches}
            showMsg={showMsg} onRefresh={onRefresh} />
        ))}
      </StatusSection>
    </div>
  );
}


// ============================================================
// STATUS SECTION — collapsible group header
// ============================================================
function StatusSection({ label, icon, color, items, emptyText, children, collapsed = false }) {
  const [open, setOpen] = useState(!collapsed);
  return (
    <div>
      <button onClick={() => setOpen(!open)}
        className="flex items-center gap-2 w-full py-1.5 mb-1"
        data-testid={`section-${label.toLowerCase()}`}>
        {icon}
        <span className="text-[11px] font-bold" style={{ color }}>{label}</span>
        <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full" style={{ background: color + '22', color }}>{items.length}</span>
        <div className="flex-1" />
        {open ? <ChevronUp size={12} color={COLORS.text.tertiary} /> : <ChevronDown size={12} color={COLORS.text.tertiary} />}
      </button>
      {open && (
        <div className="space-y-1.5">
          {items.length === 0 ? (
            <div className="text-[10px] text-center py-3 rounded-lg" style={{ background: COLORS.background.card, color: COLORS.text.tertiary }}>{emptyText}</div>
          ) : children}
        </div>
      )}
    </div>
  );
}


// ============================================================
// MATCH CARD — 3 actions: Make Live | Add Contest | Make Unlive
// ============================================================
function MatchCard({ m, templates, allContests, showMsg, onRefresh }) {
  const [expanded, setExpanded] = useState(false);
  const [showAdd, setShowAdd] = useState(false);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({ template_id: '', name: '' });

  const tA = m.team_a?.short_name || '?';
  const tB = m.team_b?.short_name || '?';
  const contests = allContests.filter(c => c.match_id === m.id);

  const scores = m.live_score?.scores || [];
  const scoreText = scores.map(s => `${s.r || s.runs || 0}/${s.w || s.wickets || 0} (${s.o || s.overs || 0})`).join(' | ');

  const handleMatchStatus = async (newStatus) => {
    try {
      await apiClient.put(`/matches/${m.id}/status`, { status: newStatus });
      showMsg(`Match → ${newStatus.toUpperCase()}`, 'success');
      onRefresh();
    } catch (e) { showMsg(e?.response?.data?.detail || e.message, 'error'); }
  };

  const handleCreate = async () => {
    if (!form.template_id || !form.name.trim()) return showMsg('Template aur Name required', 'error');
    setCreating(true);
    try {
      await apiClient.post('/admin/contests', {
        match_id: m.id, template_id: form.template_id,
        name: form.name, entry_fee: 500, prize_pool: 0, max_participants: 1000
      });
      showMsg('Contest created!', 'success');
      setShowAdd(false);
      setForm({ template_id: '', name: '' });
      onRefresh();
    } catch (e) { showMsg(e?.response?.data?.detail || e.message, 'error'); }
    finally { setCreating(false); }
  };

  return (
    <div data-testid={`match-card-${m.id}`} className="rounded-xl overflow-hidden"
      style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>

      {/* Header */}
      <button className="w-full text-left p-3 flex items-center gap-2" onClick={() => setExpanded(!expanded)}
        data-testid={`match-toggle-${m.id}`}>
        <div className="flex-1 min-w-0">
          <span className="text-sm font-bold text-white">{tA} vs {tB}</span>
          <div className="text-[10px] mt-0.5" style={{ color: COLORS.text.tertiary }}>
            {toISTShort(m.start_time)} IST {scoreText && `• ${scoreText}`}
          </div>
        </div>
        <span className="text-[9px] font-bold" style={{ color: COLORS.accent.gold }}>{contests.length}C</span>
        {expanded ? <ChevronUp size={12} color={COLORS.text.tertiary} /> : <ChevronDown size={12} color={COLORS.text.tertiary} />}
      </button>

      {expanded && (
        <div className="px-3 pb-3 space-y-2" style={{ borderTop: `1px solid ${COLORS.border.light}` }}>
          <div className="text-[9px] mt-1.5" style={{ color: COLORS.text.tertiary }}>
            {m.venue} | {toIST(m.start_time)} IST
          </div>
          {m.status_text && (
            <div className="text-[10px] font-semibold" style={{ color: '#f59e0b' }}>{m.status_text}</div>
          )}

          {/* 3 MATCH ACTIONS */}
          <div className="flex gap-1.5 flex-wrap">
            {m.status === 'upcoming' && (
              <ActionBtn testId={`match-live-${m.id}`} onClick={() => handleMatchStatus('live')}
                icon={<Play size={10} />} label="Make Live" bg="#22c55e22" color="#22c55e" />
            )}
            {m.status === 'live' && (
              <ActionBtn testId={`match-unlive-${m.id}`} onClick={() => handleMatchStatus('upcoming')}
                icon={<Pause size={10} />} label="Make Unlive" bg="#ef444422" color="#ef4444" />
            )}
            {contests.length < MAX_CONTESTS && m.status !== 'completed' && (
              <ActionBtn testId={`match-add-contest-${m.id}`}
                onClick={() => {
                  setForm({ template_id: '', name: `${tA} vs ${tB} Contest ${contests.length + 1}` });
                  setShowAdd(!showAdd);
                }}
                icon={<Plus size={10} />} label={`Add Contest (${contests.length}/${MAX_CONTESTS})`}
                bg={COLORS.accent.gold + '22'} color={COLORS.accent.gold} />
            )}
          </div>

          {/* Add Contest Form */}
          {showAdd && (
            <div className="space-y-2 p-2.5 rounded-lg" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.accent.gold}33` }}>
              <select data-testid="contest-template-select" value={form.template_id}
                onChange={e => setForm({ ...form, template_id: e.target.value })}
                className="w-full p-2 rounded-lg text-xs text-white"
                style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
                <option value="">-- Select Template --</option>
                {templates.map(t => (
                  <option key={t.id} value={t.id}>
                    {t.name} ({t.question_ids?.length || 0} Qs, {t.total_points || 0} pts)
                  </option>
                ))}
              </select>
              <input data-testid="contest-name-input" value={form.name}
                onChange={e => setForm({ ...form, name: e.target.value })}
                className="w-full p-2 rounded-lg text-xs text-white"
                style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}
                placeholder="Contest Name" />
              <button data-testid="submit-create-contest-btn" onClick={handleCreate}
                disabled={!form.template_id || !form.name.trim() || creating}
                className="w-full py-2 rounded-lg text-xs font-bold disabled:opacity-40 flex items-center justify-center gap-1"
                style={{ background: COLORS.accent.gold, color: '#000' }}>
                {creating ? <Loader2 size={12} className="animate-spin" /> : <Plus size={12} />}
                {creating ? 'Creating...' : 'Create'}
              </button>
            </div>
          )}

          {/* Contests List */}
          {contests.length > 0 && (
            <div className="space-y-1">
              {contests.map(c => (
                <MiniContestCard key={c.id} c={c} templates={templates} showMsg={showMsg} onRefresh={onRefresh} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}


// ============================================================
// MINI CONTEST CARD (inside match card) — 5 actions
// ============================================================
function MiniContestCard({ c, templates, showMsg, onRefresh }) {
  const tmpl = templates.find(t => t.id === c.template_id);
  const cSS = {
    open: { bg: '#f59e0b22', c: '#f59e0b', label: 'OPEN' },
    live: { bg: '#22c55e22', c: '#22c55e', label: 'LIVE' },
    locked: { bg: '#ef444422', c: '#ef4444', label: 'LOCKED' },
    completed: { bg: '#6b728022', c: '#9ca3af', label: 'DONE' },
  }[c.status] || { bg: '#6b728022', c: '#9ca3af', label: '?' };

  return (
    <div data-testid={`mini-contest-${c.id}`} className="p-2 rounded-lg" style={{ background: COLORS.background.tertiary }}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <Trophy size={10} color={COLORS.accent.gold} />
          <span className="text-[10px] font-bold text-white">{c.name}</span>
        </div>
        <span className="text-[8px] font-bold px-1 py-0.5 rounded" style={{ background: cSS.bg, color: cSS.c }}>{cSS.label}</span>
      </div>
      <div className="text-[9px] mt-0.5" style={{ color: COLORS.text.tertiary }}>
        {tmpl?.name || '—'} | {c.entry_fee} coins | {c.current_participants || 0} joined
      </div>
      <ContestActions c={c} showMsg={showMsg} onRefresh={onRefresh} />
    </div>
  );
}


// ============================================================
// CONTEST FULL CARD (in Contests tab) — 5 actions
// ============================================================
function ContestFullCard({ c, templates, matches, showMsg, onRefresh }) {
  const [showQs, setShowQs] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [loadingQs, setLoadingQs] = useState(false);

  const tmpl = templates.find(t => t.id === c.template_id);
  const match = matches.find(m => m.id === c.match_id);
  const tA = match?.team_a?.short_name || '?';
  const tB = match?.team_b?.short_name || '?';

  const cSS = {
    open: { bg: '#f59e0b22', c: '#f59e0b', label: 'OPEN' },
    live: { bg: '#22c55e22', c: '#22c55e', label: 'LIVE' },
    locked: { bg: '#ef444422', c: '#ef4444', label: 'LOCKED' },
    completed: { bg: '#6b728022', c: '#9ca3af', label: 'DONE' },
  }[c.status] || { bg: '#6b728022', c: '#9ca3af', label: '?' };

  const loadQs = async () => {
    if (showQs) { setShowQs(false); return; }
    setShowQs(true);
    if (questions.length > 0) return;
    setLoadingQs(true);
    try {
      const res = await apiClient.get('/admin/questions?limit=50');
      const all = res.data.questions || res.data || [];
      const ids = tmpl?.question_ids || [];
      setQuestions(ids.length > 0 ? all.filter(q => ids.includes(q.id)) : all);
    } catch { setQuestions([]); }
    finally { setLoadingQs(false); }
  };

  return (
    <div data-testid={`contest-card-${c.id}`} className="rounded-xl overflow-hidden"
      style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
      <div className="p-3">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-[11px] font-bold text-white">{c.name}</div>
            <div className="text-[9px] mt-0.5" style={{ color: COLORS.text.tertiary }}>
              {tA} vs {tB} | {toISTShort(match?.start_time)} IST
            </div>
          </div>
          <span className="text-[9px] font-bold px-1.5 py-0.5 rounded" style={{ background: cSS.bg, color: cSS.c }}>{cSS.label}</span>
        </div>

        {/* Template badge — clickable */}
        <button data-testid={`contest-template-${c.id}`} onClick={loadQs}
          className="flex items-center gap-1 mt-1.5 text-[9px] font-semibold px-2 py-0.5 rounded"
          style={{ background: '#8b5cf622', color: '#a78bfa' }}>
          <Eye size={9} /> {tmpl?.name || '—'} ({tmpl?.question_ids?.length || 0}Q) {showQs ? '▲' : '▼'}
        </button>

        {/* Stats */}
        <div className="flex gap-3 mt-1.5">
          <span className="text-[9px] flex items-center gap-1" style={{ color: COLORS.text.tertiary }}>
            <Coins size={9} color={COLORS.accent.gold} /> {c.entry_fee}
          </span>
          <span className="text-[9px] flex items-center gap-1" style={{ color: COLORS.text.tertiary }}>
            <Users size={9} color="#60a5fa" /> {c.current_participants || 0}/{c.max_participants}
          </span>
        </div>

        {/* 5 Actions */}
        <ContestActions c={c} showMsg={showMsg} onRefresh={onRefresh} />
      </div>

      {/* Questions */}
      {showQs && (
        <div className="px-3 pb-3" style={{ borderTop: `1px solid ${COLORS.border.light}` }}>
          {loadingQs ? (
            <div className="flex justify-center py-3"><Loader2 size={12} className="animate-spin" color={COLORS.primary.main} /></div>
          ) : questions.length === 0 ? (
            <div className="text-[9px] text-center py-2" style={{ color: COLORS.text.tertiary }}>No questions</div>
          ) : (
            <div className="space-y-1 mt-2">
              {questions.map((q, i) => {
                const dc = { easy: '#22c55e', medium: '#f59e0b', hard: '#ef4444' }[q.difficulty] || '#9ca3af';
                return (
                  <div key={q.id} className="p-2 rounded" style={{ background: COLORS.background.tertiary }}>
                    <div className="text-[10px] font-semibold text-white">Q{i + 1}. {q.question_text_hi}</div>
                    <span className="text-[8px] font-bold px-1 py-0.5 rounded mt-0.5 inline-block" style={{ background: dc + '22', color: dc }}>
                      {q.difficulty?.toUpperCase()} {q.points}pts
                    </span>
                    <div className="grid grid-cols-2 gap-1 mt-1">
                      {(q.options || []).map(o => (
                        <div key={o.key} className="text-[9px] px-1.5 py-1 rounded"
                          style={{ background: COLORS.background.card, color: COLORS.text.secondary }}>
                          <b>{o.key}.</b> {o.text_hi}
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}


// ============================================================
// 5 CONTEST ACTIONS — shared between Mini and Full contest cards
// ============================================================
function ContestActions({ c, showMsg, onRefresh }) {
  const handleStatus = async (newStatus) => {
    try {
      await apiClient.put(`/admin/contests/${c.id}/status`, { status: newStatus });
      showMsg(`Contest → ${newStatus.toUpperCase()}`, 'success');
      onRefresh();
    } catch (e) { showMsg(e?.response?.data?.detail || e.message, 'error'); }
  };

  const handleDelete = async () => {
    if (!window.confirm(`"${c.name}" delete karna hai?`)) return;
    try {
      await apiClient.delete(`/admin/contests/${c.id}`);
      showMsg('Deleted!', 'success');
      onRefresh();
    } catch (e) { showMsg(e?.response?.data?.detail || e.message, 'error'); }
  };

  const goResolve = (mode) => {
    window.__adminNavigate?.('resolve', { matchId: c.match_id, contestId: c.id, mode });
  };

  return (
    <div className="grid grid-cols-3 gap-1 mt-2">
      {/* 1. Make Contest Live */}
      {(c.status === 'open' || c.status === 'locked') && (
        <ActionBtn testId={`contest-live-${c.id}`} onClick={() => handleStatus('live')}
          icon={<Power size={9} />} label="Make Live" bg="#22c55e22" color="#22c55e" />
      )}

      {/* 2. Make Contest Unlive */}
      {c.status === 'live' && (
        <ActionBtn testId={`contest-unlive-${c.id}`} onClick={() => handleStatus('open')}
          icon={<Pause size={9} />} label="Unlive" bg="#f59e0b22" color="#f59e0b" />
      )}

      {/* 3. Resolve by AI */}
      <ActionBtn testId={`contest-ai-resolve-${c.id}`} onClick={() => goResolve('ai_resolve')}
        icon={<Zap size={9} />} label="AI Resolve" bg="#8b5cf622" color="#a78bfa" />

      {/* 4. See AI Answers & Override */}
      <ActionBtn testId={`contest-ai-answers-${c.id}`} onClick={() => goResolve('ai_answers')}
        icon={<Eye size={9} />} label="AI Answers" bg="#3b82f622" color="#60a5fa" />

      {/* 5. Manual Resolve */}
      <ActionBtn testId={`contest-manual-${c.id}`} onClick={() => goResolve('manual')}
        icon={<Settings size={9} />} label="Manual" bg="#06b6d422" color="#22d3ee" />

      {/* Delete */}
      <ActionBtn testId={`delete-contest-${c.id}`} onClick={handleDelete}
        icon={<Trash2 size={9} />} label="Delete" bg="#ef444422" color="#ef4444" />
    </div>
  );
}


// ============================================================
// SHARED ACTION BUTTON
// ============================================================
function ActionBtn({ testId, onClick, icon, label, bg, color }) {
  return (
    <button data-testid={testId} onClick={onClick}
      className="flex items-center justify-center gap-1 px-1.5 py-1.5 rounded text-[8px] font-bold transition-all hover:opacity-80"
      style={{ background: bg, color }}>
      {icon} {label}
    </button>
  );
}


function MsgBar({ msg, setMsg }) {
  if (!msg.text) return null;
  const bg = msg.type === 'error' ? '#ef444422' : msg.type === 'success' ? '#22c55e22' : COLORS.background.card;
  const c = msg.type === 'error' ? '#ef4444' : msg.type === 'success' ? '#22c55e' : '#60a5fa';
  return (
    <div className="text-xs text-center py-2 rounded-lg flex items-center justify-center gap-2" style={{ background: bg, color: c }}>
      {msg.text}
      <button onClick={() => setMsg({ text: '', type: '' })}><X size={12} /></button>
    </div>
  );
}
