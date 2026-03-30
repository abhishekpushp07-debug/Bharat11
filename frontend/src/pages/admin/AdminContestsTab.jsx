import { useState, useEffect } from 'react';
import apiClient from '../../api/client';
import { COLORS } from '../../constants/design';
import { Plus, Trophy, ChevronDown, ChevronUp } from 'lucide-react';

export default function AdminContestsTab() {
  const [matches, setMatches] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [contests, setContests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [expandedC, setExpandedC] = useState(null);
  const [msg, setMsg] = useState('');

  const [form, setForm] = useState({
    match_id: '', template_id: '', name: '',
    entry_fee: 0, prize_pool: 1000, max_participants: 100
  });

  const fetchAll = async () => {
    try {
      const [mRes, tRes, cRes] = await Promise.all([
        apiClient.get('/matches?limit=50'),
        apiClient.get('/admin/templates?limit=50'),
        apiClient.get('/contests?limit=50')
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
      setForm({ match_id: '', template_id: '', name: '', entry_fee: 0, prize_pool: 1000, max_participants: 100 });
      fetchAll();
    } catch (e) { setMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
  };

  const activeMatches = matches.filter(m => ['upcoming', 'live'].includes(m.status));

  const getMatchLabel = (id) => {
    const m = matches.find(m => m.id === id);
    return m ? `${m.team_a?.short_name} vs ${m.team_b?.short_name}` : id?.slice(0, 8);
  };

  return (
    <div className="space-y-3">
      {msg && <div className="text-xs text-center py-1.5 rounded-lg" style={{ background: COLORS.background.card, color: COLORS.info.main }}>{msg}</div>}

      <button data-testid="create-contest-btn" onClick={() => setShowCreate(!showCreate)}
        className="flex items-center gap-1 px-3 py-2 rounded-lg text-xs font-semibold" style={{ background: COLORS.accent.gold, color: '#000' }}>
        <Plus size={14} /> Create Contest
      </button>

      {showCreate && (
        <div className="space-y-3 p-4 rounded-xl" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
          <div>
            <label className="text-xs" style={{ color: COLORS.text.secondary }}>Match *</label>
            <select data-testid="contest-match-select" value={form.match_id} onChange={e => setForm({ ...form, match_id: e.target.value })}
              className="w-full mt-1 p-2 rounded-lg text-xs text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}>
              <option value="">Select Match</option>
              {activeMatches.map(m => (
                <option key={m.id} value={m.id}>{m.team_a?.short_name} vs {m.team_b?.short_name} ({m.status})</option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs" style={{ color: COLORS.text.secondary }}>Template *</label>
            <select data-testid="contest-template-select" value={form.template_id} onChange={e => setForm({ ...form, template_id: e.target.value })}
              className="w-full mt-1 p-2 rounded-lg text-xs text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}>
              <option value="">Select Template</option>
              {templates.map(t => (
                <option key={t.id} value={t.id}>
                  {t.name} ({t.template_type === 'full_match' ? 'Full' : 'In-Match'}, {t.question_count || t.question_ids?.length || 0}Qs)
                </option>
              ))}
            </select>
          </div>

          <input data-testid="contest-name-input" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })}
            className="w-full p-2.5 rounded-lg text-sm text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}
            placeholder="Contest Name (e.g., Free Contest)" />

          <div className="grid grid-cols-3 gap-2">
            <div>
              <label className="text-xs" style={{ color: COLORS.text.secondary }}>Entry Fee</label>
              <input type="number" value={form.entry_fee} onChange={e => setForm({ ...form, entry_fee: parseInt(e.target.value) || 0 })}
                className="w-full mt-1 p-2 rounded-lg text-xs text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }} min={0} />
            </div>
            <div>
              <label className="text-xs" style={{ color: COLORS.text.secondary }}>Prize Pool</label>
              <input type="number" value={form.prize_pool} onChange={e => setForm({ ...form, prize_pool: parseInt(e.target.value) || 0 })}
                className="w-full mt-1 p-2 rounded-lg text-xs text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }} min={0} />
            </div>
            <div>
              <label className="text-xs" style={{ color: COLORS.text.secondary }}>Max Players</label>
              <input type="number" value={form.max_participants} onChange={e => setForm({ ...form, max_participants: parseInt(e.target.value) || 100 })}
                className="w-full mt-1 p-2 rounded-lg text-xs text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }} min={2} />
            </div>
          </div>

          <button data-testid="submit-contest-btn" onClick={handleCreate}
            disabled={!form.match_id || !form.template_id || !form.name.trim()}
            className="w-full py-2.5 rounded-lg text-sm font-semibold disabled:opacity-40" style={{ background: COLORS.accent.gold, color: '#000' }}>
            Create Contest
          </button>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-8"><div className="w-6 h-6 border-2 rounded-full animate-spin" style={{ borderColor: `${COLORS.primary.main}30`, borderTopColor: COLORS.primary.main }} /></div>
      ) : (
        <div className="space-y-2">
          <div className="text-xs" style={{ color: COLORS.text.tertiary }}>{contests.length} contests</div>
          {contests.map(c => {
            const statusColor = c.status === 'open' ? COLORS.success.main : c.status === 'completed' ? COLORS.text.tertiary : COLORS.info.main;
            return (
              <div key={c.id} className="rounded-xl overflow-hidden" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
                <div className="flex items-center gap-2 p-3 cursor-pointer" onClick={() => setExpandedC(expandedC === c.id ? null : c.id)}>
                  <Trophy size={16} color={COLORS.accent.gold} />
                  <div className="flex-1 min-w-0">
                    <div className="text-xs font-semibold text-white">{c.name}</div>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-[10px] font-semibold" style={{ color: statusColor }}>{c.status?.toUpperCase()}</span>
                      <span className="text-[10px]" style={{ color: COLORS.text.tertiary }}>{getMatchLabel(c.match_id)}</span>
                      <span className="text-[10px]" style={{ color: COLORS.accent.gold }}>{c.prize_pool} coins</span>
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
                        <div className="text-xs font-bold" style={{ color: COLORS.accent.gold }}>{c.prize_pool}</div>
                        <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>Prize</div>
                      </div>
                      <div className="text-center p-2 rounded" style={{ background: COLORS.background.tertiary }}>
                        <div className="text-xs font-bold text-white">{c.current_participants}/{c.max_participants}</div>
                        <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>Players</div>
                      </div>
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
