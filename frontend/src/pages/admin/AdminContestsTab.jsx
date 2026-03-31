/**
 * Admin Contests Tab - Match-based Contest Management
 * Flow: Select Match → View/Add/Delete Contests → Select Template → Make Live
 * Rules: Min 1, Max 5 contests per match
 */
import { useState, useEffect } from 'react';
import apiClient from '../../api/client';
import { COLORS } from '../../constants/design';
import { Plus, Trophy, Trash2, ArrowLeft, Loader2, X, ChevronRight, Users, Coins, Clock, AlertTriangle } from 'lucide-react';

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

  const [form, setForm] = useState({
    template_id: '', name: '', entry_fee: 1000, max_participants: 1000
  });

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

  const fetchMatchContests = async (matchId) => {
    try {
      const res = await apiClient.get(`/admin/contests?match_id=${matchId}&limit=10`);
      setMatchContests(res.data.contests || []);
    } catch (e) { setMatchContests([]); }
  };

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
    if (!form.template_id || !form.name.trim()) {
      showMsg('Template aur Name dono required hain', 'error');
      return;
    }
    if (matchContests.length >= MAX_CONTESTS_PER_MATCH) {
      showMsg(`Maximum ${MAX_CONTESTS_PER_MATCH} contests allowed per match!`, 'error');
      return;
    }
    setCreating(true);
    try {
      await apiClient.post('/admin/contests', {
        match_id: selectedMatch.id,
        template_id: form.template_id,
        name: form.name,
        entry_fee: form.entry_fee,
        prize_pool: 0,
        max_participants: form.max_participants
      });
      showMsg('Contest created!', 'success');
      setShowCreate(false);
      setForm({ template_id: '', name: '', entry_fee: 1000, max_participants: 1000 });
      await fetchMatchContests(selectedMatch.id);
    } catch (e) {
      showMsg(`Error: ${e?.response?.data?.detail || e.message}`, 'error');
    } finally { setCreating(false); }
  };

  const handleDelete = async (contestId, contestName) => {
    if (!window.confirm(`"${contestName}" contest delete karna hai?`)) return;
    try {
      await apiClient.delete(`/admin/contests/${contestId}`);
      showMsg('Contest deleted!', 'success');
      await fetchMatchContests(selectedMatch.id);
    } catch (e) {
      showMsg(`Delete error: ${e?.response?.data?.detail || e.message}`, 'error');
    }
  };

  const getStatusStyle = (s) => {
    const map = {
      upcoming: { bg: COLORS.info.main + '22', color: COLORS.info.main },
      live: { bg: COLORS.success.main + '22', color: COLORS.success.main },
      completed: { bg: COLORS.text.tertiary + '22', color: COLORS.text.tertiary },
    };
    return map[s] || map.completed;
  };

  // ======== MATCH DETAIL VIEW (with contests) ========
  if (selectedMatch) {
    const teamA = selectedMatch.team_a?.short_name || '?';
    const teamB = selectedMatch.team_b?.short_name || '?';
    const canAdd = matchContests.length < MAX_CONTESTS_PER_MATCH;
    const ss = getStatusStyle(selectedMatch.status);

    return (
      <div className="space-y-3" data-testid="match-contest-view">
        {/* Back Button */}
        <button data-testid="back-to-matches-btn"
          onClick={() => { setSelectedMatch(null); setMatchContests([]); setShowCreate(false); }}
          className="text-xs flex items-center gap-1 py-1" style={{ color: COLORS.text.secondary }}>
          <ArrowLeft size={14} /> Back to Matches
        </button>

        {/* Match Header */}
        <div className="p-4 rounded-xl" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.primary.main}33` }}>
          <div className="flex items-center justify-between">
            <div>
              <div className="text-base font-bold text-white">{teamA} vs {teamB}</div>
              <div className="text-[10px] mt-1" style={{ color: COLORS.text.tertiary }}>
                {selectedMatch.venue} | {selectedMatch.start_time ? new Date(selectedMatch.start_time).toLocaleString('en-IN') : ''}
              </div>
            </div>
            <span className="text-[10px] font-bold px-2 py-1 rounded-lg" style={{ background: ss.bg, color: ss.color }}>
              {selectedMatch.status?.toUpperCase()}
            </span>
          </div>
          <div className="flex items-center gap-3 mt-2">
            <span className="text-xs font-semibold" style={{ color: COLORS.accent.gold }}>
              {matchContests.length}/{MAX_CONTESTS_PER_MATCH} Contests
            </span>
            <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ background: COLORS.background.tertiary }}>
              <div className="h-full rounded-full transition-all" style={{
                width: `${(matchContests.length / MAX_CONTESTS_PER_MATCH) * 100}%`,
                background: matchContests.length >= MAX_CONTESTS_PER_MATCH ? COLORS.error.main : COLORS.accent.gold
              }} />
            </div>
          </div>
        </div>

        {/* Message */}
        {msg.text && (
          <div className="text-xs text-center py-2 rounded-lg flex items-center justify-center gap-2" style={{
            background: msg.type === 'error' ? COLORS.error.bg : msg.type === 'success' ? COLORS.success.main + '15' : COLORS.background.card,
            color: msg.type === 'error' ? COLORS.error.main : msg.type === 'success' ? COLORS.success.main : COLORS.info.main
          }}>
            {msg.text}
            <button onClick={() => setMsg({ text: '', type: 'info' })}><X size={12} /></button>
          </div>
        )}

        {/* Add Contest Button */}
        {canAdd ? (
          <button data-testid="add-contest-btn"
            onClick={() => {
              setForm({ ...form, name: `${teamA} vs ${teamB} Contest ${matchContests.length + 1}` });
              setShowCreate(!showCreate);
            }}
            className="w-full flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-bold transition-all"
            style={{ background: COLORS.accent.gold, color: '#000' }}>
            <Plus size={16} /> Add Contest ({matchContests.length + 1}/{MAX_CONTESTS_PER_MATCH})
          </button>
        ) : (
          <div className="flex items-center gap-2 py-3 px-4 rounded-xl text-xs" style={{ background: COLORS.error.bg, border: `1px solid ${COLORS.error.main}22` }}>
            <AlertTriangle size={14} color={COLORS.error.main} />
            <span style={{ color: COLORS.error.main }}>Maximum {MAX_CONTESTS_PER_MATCH} contests reached</span>
          </div>
        )}

        {/* Create Contest Form */}
        {showCreate && (
          <div className="space-y-3 p-4 rounded-xl" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.accent.gold}33` }}>
            <div className="text-xs font-bold text-white">New Contest</div>

            {/* Template Select */}
            <div>
              <label className="text-[10px] font-semibold" style={{ color: COLORS.text.secondary }}>Template *</label>
              <select data-testid="contest-template-select"
                value={form.template_id}
                onChange={e => setForm({ ...form, template_id: e.target.value })}
                className="w-full mt-1 p-2.5 rounded-lg text-xs text-white"
                style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}>
                <option value="">-- Select Template --</option>
                {templates.filter(t => t.is_default).map(t => (
                  <option key={t.id} value={t.id}>
                    [DEFAULT] {t.name} ({t.template_type === 'full_match' ? 'Full' : 'In-Match'}, {t.question_ids?.length || 0} Qs, {t.total_points || 0} pts)
                  </option>
                ))}
                {templates.filter(t => !t.is_default).map(t => (
                  <option key={t.id} value={t.id}>
                    {t.name} ({t.template_type === 'full_match' ? 'Full' : 'In-Match'}, {t.question_ids?.length || 0} Qs)
                  </option>
                ))}
              </select>
            </div>

            {/* Contest Name */}
            <div>
              <label className="text-[10px] font-semibold" style={{ color: COLORS.text.secondary }}>Contest Name *</label>
              <input data-testid="contest-name-input"
                value={form.name}
                onChange={e => setForm({ ...form, name: e.target.value })}
                className="w-full mt-1 p-2.5 rounded-lg text-xs text-white"
                style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}
                placeholder="e.g. PBKS vs GT Contest 1" />
            </div>

            {/* Entry Fee + Max Players */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[10px] font-semibold" style={{ color: COLORS.text.secondary }}>Entry Fee (coins)</label>
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

            <div className="text-[10px] px-2 py-1.5 rounded-lg" style={{ background: COLORS.accent.gold + '15', color: COLORS.accent.gold }}>
              Prize Pool = Dynamic (50/30/20 split based on entries)
            </div>

            {/* Submit */}
            <button data-testid="submit-create-contest-btn" onClick={handleCreate}
              disabled={!form.template_id || !form.name.trim() || creating}
              className="w-full py-3 rounded-xl text-sm font-bold disabled:opacity-40 flex items-center justify-center gap-2 transition-all"
              style={{ background: COLORS.accent.gold, color: '#000' }}>
              {creating ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />}
              {creating ? 'Creating...' : 'Create Contest'}
            </button>
          </div>
        )}

        {/* Existing Contests List */}
        <div className="space-y-2">
          <div className="text-xs font-bold text-white">{matchContests.length} Contest(s)</div>
          {matchContests.length === 0 && (
            <div className="text-center py-6 rounded-xl" style={{ background: COLORS.background.card }}>
              <Trophy size={24} color={COLORS.text.tertiary} className="mx-auto mb-2" />
              <div className="text-xs" style={{ color: COLORS.text.tertiary }}>No contests yet. Add one above!</div>
            </div>
          )}
          {matchContests.map(c => (
            <ContestCard key={c.id} c={c} onDelete={handleDelete} />
          ))}
        </div>
      </div>
    );
  }

  // ======== MATCH LIST VIEW ========
  return (
    <div className="space-y-3" data-testid="admin-contests-tab">
      {msg.text && (
        <div className="text-xs text-center py-2 rounded-lg" style={{
          background: msg.type === 'error' ? COLORS.error.bg : COLORS.background.card,
          color: msg.type === 'error' ? COLORS.error.main : COLORS.info.main
        }}>
          {msg.text}
          <button onClick={() => setMsg({ text: '', type: 'info' })} className="ml-2"><X size={10} /></button>
        </div>
      )}

      <div className="text-xs font-bold text-white">Select Match to Manage Contests:</div>
      <div className="text-[10px] mb-1" style={{ color: COLORS.text.tertiary }}>
        Min 1, Max {MAX_CONTESTS_PER_MATCH} contests per match
      </div>

      {loading ? (
        <div className="flex justify-center py-10">
          <Loader2 size={24} className="animate-spin" color={COLORS.primary.main} />
        </div>
      ) : matches.length === 0 ? (
        <div className="text-center py-8 rounded-xl" style={{ background: COLORS.background.card }}>
          <div className="text-sm" style={{ color: COLORS.text.tertiary }}>No matches found. Sync from CricketData API first.</div>
        </div>
      ) : (
        <div className="space-y-1.5">
          {matches.map(m => {
            const teamA = m.team_a?.short_name || '?';
            const teamB = m.team_b?.short_name || '?';
            const ss = getStatusStyle(m.status);
            return (
              <button key={m.id} data-testid={`match-select-${m.id}`}
                onClick={() => selectMatch(m)}
                className="w-full text-left p-3 rounded-xl flex items-center gap-3 transition-all hover:opacity-90 active:scale-[0.98]"
                style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-bold text-white">{teamA} vs {teamB}</div>
                  <div className="flex items-center gap-2 mt-1 flex-wrap">
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded" style={{ background: ss.bg, color: ss.color }}>
                      {m.status?.toUpperCase()}
                    </span>
                    <span className="text-[10px]" style={{ color: COLORS.text.tertiary }}>
                      {m.start_time ? new Date(m.start_time).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' }) : ''}
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


function ContestCard({ c, onDelete }) {
  const statusColor = c.status === 'open' ? COLORS.success.main : c.status === 'completed' ? COLORS.text.tertiary : c.status === 'live' ? '#22d3ee' : COLORS.info.main;
  const templateType = c.template_type || 'full_match';

  return (
    <div data-testid={`contest-card-${c.id}`} className="rounded-xl p-3"
      style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Trophy size={14} color={COLORS.accent.gold} />
          <span className="text-xs font-bold text-white">{c.name}</span>
        </div>
        <span className="text-[10px] font-bold px-1.5 py-0.5 rounded" style={{ background: statusColor + '22', color: statusColor }}>
          {c.status?.toUpperCase()}
        </span>
      </div>

      {/* Badges */}
      <div className="flex items-center gap-2 mt-1.5 flex-wrap">
        <span className="text-[9px] font-bold px-1.5 py-0.5 rounded" style={{
          background: templateType === 'full_match' ? COLORS.primary.main + '22' : '#f59e0b22',
          color: templateType === 'full_match' ? COLORS.primary.main : '#f59e0b'
        }}>
          {templateType === 'full_match' ? 'FULL MATCH' : 'IN-MATCH'}
        </span>
        {c.template_name && (
          <span className="text-[9px]" style={{ color: COLORS.text.tertiary }}>{c.template_name}</span>
        )}
        {c.question_count > 0 && (
          <span className="text-[9px]" style={{ color: COLORS.text.tertiary }}>{c.question_count} Qs</span>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-2 mt-2">
        <div className="flex items-center gap-1.5 text-[10px]" style={{ color: COLORS.text.secondary }}>
          <Coins size={11} color={COLORS.accent.gold} />
          <span>{c.entry_fee} fee</span>
        </div>
        <div className="flex items-center gap-1.5 text-[10px]" style={{ color: COLORS.text.secondary }}>
          <Users size={11} color={COLORS.info.main} />
          <span>{c.current_participants || 0}/{c.max_participants}</span>
        </div>
        <div className="flex items-center gap-1.5 text-[10px]" style={{ color: COLORS.text.secondary }}>
          <Clock size={11} />
          <span>{c.lock_time ? new Date(c.lock_time).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) : '--'}</span>
        </div>
      </div>

      {/* Delete */}
      <div className="flex justify-end mt-2 pt-2" style={{ borderTop: `1px solid ${COLORS.border.light}` }}>
        <button data-testid={`delete-contest-${c.id}`}
          onClick={() => onDelete(c.id, c.name)}
          className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-[10px] font-semibold transition-all hover:opacity-80"
          style={{ background: COLORS.error.bg, color: COLORS.error.main }}>
          <Trash2 size={11} /> Delete
        </button>
      </div>
    </div>
  );
}
