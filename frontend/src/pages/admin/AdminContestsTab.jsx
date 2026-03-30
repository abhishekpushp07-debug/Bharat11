/**
 * Admin Contests Tab - Full CRUD with Multi-Select Delete + Template Type Badges
 * Contest creation happens INSIDE a match view with default template options
 */
import { useState, useEffect } from 'react';
import apiClient from '../../api/client';
import { COLORS } from '../../constants/design';
import { Plus, Trophy, ChevronDown, ChevronUp, Trash2, Edit2, CheckSquare, Square, Loader2, X, ArrowLeft, Zap } from 'lucide-react';

export default function AdminContestsTab() {
  const [matches, setMatches] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [contests, setContests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMatch, setSelectedMatch] = useState(null);
  const [showCreate, setShowCreate] = useState(false);
  const [expandedC, setExpandedC] = useState(null);
  const [msg, setMsg] = useState('');
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [bulkDeleting, setBulkDeleting] = useState(false);

  const [form, setForm] = useState({
    match_id: '', template_id: '', name: '',
    entry_fee: 1000, prize_pool: 0, max_participants: 1000
  });

  const fetchAll = async () => {
    try {
      const [mRes, tRes, cRes] = await Promise.all([
        apiClient.get('/matches?limit=50'),
        apiClient.get('/admin/templates?limit=50'),
        apiClient.get('/admin/contests?limit=50')
      ]);
      setMatches(mRes.data.matches || []);
      setTemplates(tRes.data.templates || []);
      setContests(cRes.data.contests || []);
    } catch (e) { setMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchAll(); }, []);

  const handleCreate = async () => {
    if (!form.match_id || !form.template_id || !form.name.trim()) {
      setMsg('Match, Template and Name required');
      return;
    }
    try {
      await apiClient.post('/admin/contests', form);
      setMsg('Contest created!');
      setShowCreate(false);
      setForm({ match_id: '', template_id: '', name: '', entry_fee: 1000, prize_pool: 0, max_participants: 1000 });
      fetchAll();
    } catch (e) { setMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this contest?')) return;
    try {
      await apiClient.post('/admin/contests/bulk-delete', { ids: [id] });
      setMsg('Contest deleted');
      fetchAll();
    } catch (e) { setMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
  };

  const handleBulkDelete = async () => {
    if (selectedIds.size === 0) return;
    if (!window.confirm(`Delete ${selectedIds.size} selected contests?`)) return;
    setBulkDeleting(true);
    try {
      await apiClient.post('/admin/contests/bulk-delete', { ids: Array.from(selectedIds) });
      setSelectedIds(new Set());
      setMsg(`${selectedIds.size} contests deleted`);
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

  const activeMatches = matches.filter(m => ['upcoming', 'live'].includes(m.status));

  const getMatchLabel = (id) => {
    const m = matches.find(m => m.id === id);
    return m ? `${m.team_a?.short_name} vs ${m.team_b?.short_name}` : id?.slice(0, 8);
  };

  // Group contests by match
  const matchContestGroups = {};
  contests.forEach(c => {
    const mid = c.match_id || 'unlinked';
    if (!matchContestGroups[mid]) matchContestGroups[mid] = [];
    matchContestGroups[mid].push(c);
  });

  // If a match is selected for creating contests inside it
  if (selectedMatch) {
    const match = matches.find(m => m.id === selectedMatch);
    const matchContests = contests.filter(c => c.match_id === selectedMatch);
    const teamA = match?.team_a?.short_name || '?';
    const teamB = match?.team_b?.short_name || '?';

    return (
      <div className="space-y-3">
        <button onClick={() => { setSelectedMatch(null); setShowCreate(false); }}
          className="text-xs flex items-center gap-1" style={{ color: COLORS.text.secondary }}>
          <ArrowLeft size={14} /> Back to All Contests
        </button>

        <div className="p-3 rounded-xl" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.primary.main}33` }}>
          <div className="text-sm font-bold text-white">{teamA} vs {teamB}</div>
          <div className="text-[10px] mt-0.5" style={{ color: COLORS.text.tertiary }}>
            {match?.venue} | {match?.start_time ? new Date(match.start_time).toLocaleString() : ''} | {match?.status?.toUpperCase()}
          </div>
          <div className="text-xs mt-1" style={{ color: COLORS.info.main }}>{matchContests.length} contest(s)</div>
        </div>

        {/* Create Contest in this Match */}
        <button data-testid="create-contest-in-match-btn"
          onClick={() => {
            setForm({ ...form, match_id: selectedMatch, name: `${teamA} vs ${teamB} Contest` });
            setShowCreate(!showCreate);
          }}
          className="flex items-center gap-1 px-3 py-2 rounded-lg text-xs font-semibold" style={{ background: COLORS.accent.gold, color: '#000' }}>
          <Plus size={14} /> Create Contest Here
        </button>

        {showCreate && (
          <div className="space-y-3 p-4 rounded-xl" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
            <div>
              <label className="text-xs" style={{ color: COLORS.text.secondary }}>Template *</label>
              <select data-testid="contest-template-select" value={form.template_id}
                onChange={e => setForm({ ...form, template_id: e.target.value })}
                className="w-full mt-1 p-2 rounded-lg text-xs text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}>
                <option value="">Select Template</option>
                {/* Default templates first with prefix */}
                {templates.filter(t => t.is_default).map(t => (
                  <option key={t.id} value={t.id}>
                    [DEFAULT] {t.name} ({t.template_type === 'full_match' ? 'Full' : 'In-Match'}, {t.question_count || t.question_ids?.length || 0}Qs)
                  </option>
                ))}
                {/* Then regular templates */}
                {templates.filter(t => !t.is_default).map(t => (
                  <option key={t.id} value={t.id}>
                    {t.name} ({t.template_type === 'full_match' ? 'Full' : 'In-Match'}, {t.question_count || t.question_ids?.length || 0}Qs)
                  </option>
                ))}
              </select>
            </div>

            <input data-testid="contest-name-input" value={form.name}
              onChange={e => setForm({ ...form, name: e.target.value })}
              className="w-full p-2.5 rounded-lg text-sm text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}
              placeholder="Contest Name" />

            <div className="grid grid-cols-3 gap-2">
              <div>
                <label className="text-xs" style={{ color: COLORS.text.secondary }}>Entry Fee</label>
                <input type="number" value={form.entry_fee}
                  onChange={e => setForm({ ...form, entry_fee: parseInt(e.target.value) || 0 })}
                  className="w-full mt-1 p-2 rounded-lg text-xs text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }} min={0} />
              </div>
              <div>
                <label className="text-xs" style={{ color: COLORS.text.secondary }}>Max Players</label>
                <input type="number" value={form.max_participants}
                  onChange={e => setForm({ ...form, max_participants: parseInt(e.target.value) || 1000 })}
                  className="w-full mt-1 p-2 rounded-lg text-xs text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }} min={2} />
              </div>
              <div className="flex flex-col justify-end">
                <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>Prize Pool</div>
                <div className="text-xs font-bold" style={{ color: COLORS.accent.gold }}>Dynamic</div>
                <div className="text-[9px]" style={{ color: COLORS.text.tertiary }}>50/30/20 split</div>
              </div>
            </div>

            <button data-testid="submit-contest-btn" onClick={handleCreate}
              disabled={!form.template_id || !form.name.trim()}
              className="w-full py-2.5 rounded-lg text-sm font-semibold disabled:opacity-40" style={{ background: COLORS.accent.gold, color: '#000' }}>
              Create Contest
            </button>
          </div>
        )}

        {/* Existing contests for this match */}
        <div className="space-y-2">
          {matchContests.map(c => (
            <ContestCard key={c.id} c={c} expandedC={expandedC} setExpandedC={setExpandedC}
              selectedIds={selectedIds} toggleSelect={toggleSelect} handleDelete={handleDelete}
              getMatchLabel={getMatchLabel} />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {msg && (
        <div className="text-xs text-center py-1.5 rounded-lg" style={{ background: COLORS.background.card, color: COLORS.info.main }}>
          {msg}
          <button onClick={() => setMsg('')} className="ml-2 opacity-50"><X size={10} /></button>
        </div>
      )}

      {/* Multi-Select Actions */}
      {selectedIds.size > 0 && (
        <div data-testid="bulk-actions-bar" className="flex items-center gap-3 p-2.5 rounded-xl"
          style={{ background: COLORS.error.bg, border: `1px solid ${COLORS.error.main}33` }}>
          <span className="text-xs font-bold" style={{ color: COLORS.error.main }}>{selectedIds.size} selected</span>
          <button data-testid="bulk-delete-contests-btn" onClick={handleBulkDelete} disabled={bulkDeleting}
            className="px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1 disabled:opacity-50"
            style={{ background: COLORS.error.main, color: '#fff' }}>
            {bulkDeleting ? <Loader2 size={12} className="animate-spin" /> : <Trash2 size={12} />}
            Delete Selected
          </button>
          <button onClick={() => setSelectedIds(new Set())}
            className="px-2 py-1 rounded text-xs" style={{ color: COLORS.text.tertiary }}>Clear</button>
        </div>
      )}

      {/* Match List for Contest Creation */}
      <div className="text-xs font-bold text-white mb-1">Select a Match to Create Contests:</div>
      <div className="space-y-1.5">
        {activeMatches.map(m => {
          const mContests = contests.filter(c => c.match_id === m.id);
          return (
            <button key={m.id} onClick={() => setSelectedMatch(m.id)}
              className="w-full text-left p-3 rounded-xl flex items-center justify-between"
              style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
              <div>
                <div className="text-sm font-bold text-white">{m.team_a?.short_name} vs {m.team_b?.short_name}</div>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded"
                    style={{ background: (m.status === 'live' ? COLORS.success.main : COLORS.info.main) + '22', color: m.status === 'live' ? COLORS.success.main : COLORS.info.main }}>
                    {m.status?.toUpperCase()}
                  </span>
                  <span className="text-[10px]" style={{ color: COLORS.text.tertiary }}>{mContests.length} contest(s)</span>
                </div>
              </div>
              <Plus size={16} color={COLORS.accent.gold} />
            </button>
          );
        })}
      </div>

      {/* All Contests List */}
      {loading ? (
        <div className="flex justify-center py-8"><div className="w-6 h-6 border-2 rounded-full animate-spin" style={{ borderColor: `${COLORS.primary.main}30`, borderTopColor: COLORS.primary.main }} /></div>
      ) : (
        <div className="space-y-2">
          <div className="text-xs font-bold text-white mt-4">All Contests ({contests.length})</div>
          {contests.map(c => (
            <ContestCard key={c.id} c={c} expandedC={expandedC} setExpandedC={setExpandedC}
              selectedIds={selectedIds} toggleSelect={toggleSelect} handleDelete={handleDelete}
              getMatchLabel={getMatchLabel} />
          ))}
        </div>
      )}
    </div>
  );
}

function ContestCard({ c, expandedC, setExpandedC, selectedIds, toggleSelect, handleDelete, getMatchLabel }) {
  const statusColor = c.status === 'open' ? COLORS.success.main : c.status === 'completed' ? COLORS.text.tertiary : COLORS.info.main;
  const templateType = c.template_type || 'full_match';

  return (
    <div className="rounded-xl overflow-hidden" style={{
      background: selectedIds.has(c.id) ? `${COLORS.primary.main}11` : COLORS.background.card,
      border: `1px solid ${selectedIds.has(c.id) ? COLORS.primary.main + '44' : COLORS.border.light}`
    }}>
      <div className="flex items-center gap-2 p-3">
        {/* Checkbox */}
        <button onClick={() => toggleSelect(c.id)} className="shrink-0">
          {selectedIds.has(c.id) ?
            <CheckSquare size={16} color={COLORS.primary.main} /> :
            <Square size={16} color={COLORS.text.tertiary} />
          }
        </button>
        <div className="flex-1 min-w-0 cursor-pointer" onClick={() => setExpandedC(expandedC === c.id ? null : c.id)}>
          <div className="flex items-center gap-2">
            <Trophy size={14} color={COLORS.accent.gold} />
            <span className="text-xs font-semibold text-white">{c.name}</span>
          </div>
          <div className="flex items-center gap-2 mt-0.5 flex-wrap">
            <span className="text-[10px] font-semibold" style={{ color: statusColor }}>{c.status?.toUpperCase()}</span>
            {/* Template Type Badge */}
            <span data-testid={`badge-${c.id}`} className="text-[9px] font-bold px-1.5 py-0.5 rounded"
              style={{
                background: templateType === 'full_match' ? COLORS.primary.main + '22' : COLORS.warning.bg,
                color: templateType === 'full_match' ? COLORS.primary.main : COLORS.warning.main
              }}>
              {templateType === 'full_match' ? 'FULL MATCH' : 'IN-MATCH'}
            </span>
            {c.phase_label && (
              <span className="text-[9px] px-1.5 py-0.5 rounded font-semibold" style={{ background: '#6366f115', color: '#818cf8' }}>
                {c.phase_label}
              </span>
            )}
            <span className="text-[10px]" style={{ color: COLORS.text.tertiary }}>{c.match_label || getMatchLabel(c.match_id)}</span>
            <span className="text-[10px]" style={{ color: COLORS.accent.gold }}>{c.prize_pool || 0} coins</span>
            {c.auto_created && <span className="text-[8px] font-bold px-1 rounded" style={{ background: '#10b98115', color: '#10b981' }}>AUTO</span>}
          </div>
        </div>
        {expandedC === c.id ? <ChevronUp size={14} color={COLORS.text.tertiary} /> : <ChevronDown size={14} color={COLORS.text.tertiary} />}
      </div>

      {expandedC === c.id && (
        <div className="px-3 pb-3 border-t" style={{ borderColor: COLORS.border.light }}>
          <div className="grid grid-cols-3 gap-2 mt-2">
            <div className="text-center p-2 rounded" style={{ background: COLORS.background.tertiary }}>
              <div className="text-xs font-bold text-white">{c.entry_fee}</div>
              <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>Entry</div>
            </div>
            <div className="text-center p-2 rounded" style={{ background: COLORS.background.tertiary }}>
              <div className="text-xs font-bold" style={{ color: COLORS.accent.gold }}>{(c.prize_pool || c.entry_fee * (c.current_participants || 0)).toLocaleString()}</div>
              <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>Pool</div>
            </div>
            <div className="text-center p-2 rounded" style={{ background: COLORS.background.tertiary }}>
              <div className="text-xs font-bold text-white">{c.current_participants || 0}/{c.max_participants}</div>
              <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>Players</div>
            </div>
          </div>
          {c.template_name && (
            <div className="text-[10px] mt-2" style={{ color: COLORS.text.tertiary }}>
              Template: {c.template_name} | {c.question_count || 0} questions
            </div>
          )}
          <div className="flex gap-2 mt-2">
            <button onClick={() => handleDelete(c.id)}
              className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs" style={{ background: COLORS.error.bg, color: COLORS.error.main }}>
              <Trash2 size={12} /> Delete
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
