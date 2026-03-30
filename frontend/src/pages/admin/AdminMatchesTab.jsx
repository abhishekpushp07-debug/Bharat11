import { useState, useEffect } from 'react';
import apiClient from '../../api/client';
import { COLORS } from '../../constants/design';
import { Plus, Play, Square, ChevronDown, ChevronUp, Link as LinkIcon } from 'lucide-react';

const IPL_TEAMS = [
  'Mumbai Indians', 'Chennai Super Kings', 'Royal Challengers Bangalore',
  'Kolkata Knight Riders', 'Delhi Capitals', 'Punjab Kings',
  'Rajasthan Royals', 'Sunrisers Hyderabad', 'Gujarat Titans', 'Lucknow Super Giants'
];

const SHORT = { 'Mumbai Indians': 'MI', 'Chennai Super Kings': 'CSK', 'Royal Challengers Bangalore': 'RCB', 'Kolkata Knight Riders': 'KKR', 'Delhi Capitals': 'DC', 'Punjab Kings': 'PBKS', 'Rajasthan Royals': 'RR', 'Sunrisers Hyderabad': 'SRH', 'Gujarat Titans': 'GT', 'Lucknow Super Giants': 'LSG' };

const VENUES = [
  'Wankhede Stadium, Mumbai', 'M.A. Chidambaram Stadium, Chennai',
  'M. Chinnaswamy Stadium, Bangalore', 'Eden Gardens, Kolkata',
  'Arun Jaitley Stadium, Delhi', 'Narendra Modi Stadium, Ahmedabad',
];

const STATUS_COLORS = {
  upcoming: COLORS.info.main, live: COLORS.success.main,
  completed: COLORS.text.tertiary, abandoned: COLORS.error.main, cancelled: COLORS.error.main
};

export default function AdminMatchesTab() {
  const [matches, setMatches] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [expandedM, setExpandedM] = useState(null);
  const [assigningM, setAssigningM] = useState(null);
  const [selectedTemplateIds, setSelectedTemplateIds] = useState([]);
  const [msg, setMsg] = useState('');

  const [form, setForm] = useState({
    team_a_name: IPL_TEAMS[0], team_b_name: IPL_TEAMS[1],
    venue: VENUES[0], start_time: '', match_type: 'T20'
  });

  const fetchAll = async () => {
    try {
      const [mRes, tRes] = await Promise.all([
        apiClient.get('/matches?limit=50'),
        apiClient.get('/admin/templates?limit=50')
      ]);
      setMatches(mRes.data.matches || []);
      setTemplates(tRes.data.templates || []);
    } catch (e) { setMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchAll(); }, []);

  const handleCreateMatch = async () => {
    if (!form.start_time) { setMsg('Start time required'); return; }
    try {
      await apiClient.post('/matches', {
        team_a: { name: form.team_a_name, short_name: SHORT[form.team_a_name] || form.team_a_name.slice(0, 3).toUpperCase() },
        team_b: { name: form.team_b_name, short_name: SHORT[form.team_b_name] || form.team_b_name.slice(0, 3).toUpperCase() },
        venue: form.venue,
        match_type: form.match_type,
        start_time: new Date(form.start_time).toISOString()
      });
      setMsg('Match created!');
      setShowCreate(false);
      fetchAll();
    } catch (e) { setMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
  };

  const updateStatus = async (matchId, newStatus) => {
    try {
      await apiClient.put(`/matches/${matchId}/status`, { status: newStatus });
      setMsg(`Status updated to ${newStatus}`);
      fetchAll();
    } catch (e) { setMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
  };

  const handleAssignTemplates = async (matchId) => {
    if (selectedTemplateIds.length === 0) { setMsg('Select at least 1 template'); return; }
    try {
      await apiClient.post(`/admin/matches/${matchId}/assign-templates`, selectedTemplateIds);
      setMsg('Templates assigned!');
      setAssigningM(null);
      setSelectedTemplateIds([]);
      fetchAll();
    } catch (e) { setMsg(`Error: ${e?.response?.data?.detail || e.message}`); }
  };

  const toggleTemplate = (tid) => {
    setSelectedTemplateIds(prev =>
      prev.includes(tid) ? prev.filter(id => id !== tid) : [...prev, tid]
    );
  };

  return (
    <div className="space-y-3">
      {msg && <div className="text-xs text-center py-1.5 rounded-lg" style={{ background: COLORS.background.card, color: COLORS.info.main }}>{msg}</div>}

      <button data-testid="create-match-btn" onClick={() => setShowCreate(!showCreate)}
        className="flex items-center gap-1 px-3 py-2 rounded-lg text-xs font-semibold" style={{ background: COLORS.primary.main, color: '#fff' }}>
        <Plus size={14} /> Create Match
      </button>

      {showCreate && (
        <div className="space-y-3 p-4 rounded-xl" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-xs" style={{ color: COLORS.text.secondary }}>Team A</label>
              <select value={form.team_a_name} onChange={e => setForm({ ...form, team_a_name: e.target.value })}
                className="w-full mt-1 p-2 rounded-lg text-xs text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}>
                {IPL_TEAMS.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs" style={{ color: COLORS.text.secondary }}>Team B</label>
              <select value={form.team_b_name} onChange={e => setForm({ ...form, team_b_name: e.target.value })}
                className="w-full mt-1 p-2 rounded-lg text-xs text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}>
                {IPL_TEAMS.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
          </div>

          <div>
            <label className="text-xs" style={{ color: COLORS.text.secondary }}>Venue</label>
            <select value={form.venue} onChange={e => setForm({ ...form, venue: e.target.value })}
              className="w-full mt-1 p-2 rounded-lg text-xs text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }}>
              {VENUES.map(v => <option key={v} value={v}>{v}</option>)}
            </select>
          </div>

          <div>
            <label className="text-xs" style={{ color: COLORS.text.secondary }}>Start Time *</label>
            <input data-testid="match-start-time" type="datetime-local" value={form.start_time}
              onChange={e => setForm({ ...form, start_time: e.target.value })}
              className="w-full mt-1 p-2 rounded-lg text-xs text-white" style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }} />
          </div>

          <button data-testid="submit-match-btn" onClick={handleCreateMatch} disabled={!form.start_time}
            className="w-full py-2.5 rounded-lg text-sm font-semibold disabled:opacity-40" style={{ background: COLORS.primary.main, color: '#fff' }}>
            Create Match
          </button>
        </div>
      )}

      {/* Template Assignment Modal */}
      {assigningM && (
        <div className="p-4 rounded-xl space-y-3" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.primary.main}44` }}>
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-white">Assign Templates (Min 1 Full Match, Max 5)</span>
            <button onClick={() => setAssigningM(null)} className="text-xs" style={{ color: COLORS.text.tertiary }}>Cancel</button>
          </div>
          <div className="space-y-1.5 max-h-48 overflow-y-auto">
            {templates.map(t => {
              const sel = selectedTemplateIds.includes(t.id);
              return (
                <div key={t.id} onClick={() => toggleTemplate(t.id)}
                  className="flex items-center gap-2 p-2 rounded-lg cursor-pointer" style={{ background: sel ? `${COLORS.primary.main}22` : COLORS.background.tertiary, border: `1px solid ${sel ? COLORS.primary.main : 'transparent'}` }}>
                  <div className="w-4 h-4 rounded border flex items-center justify-center" style={{ borderColor: sel ? COLORS.primary.main : COLORS.border.light, background: sel ? COLORS.primary.main : 'transparent' }}>
                    {sel && <span className="text-white text-[10px]">+</span>}
                  </div>
                  <div className="flex-1">
                    <span className="text-xs text-white">{t.name}</span>
                    <span className="text-[10px] ml-2 px-1 rounded" style={{ background: t.template_type === 'full_match' ? COLORS.primary.main + '22' : COLORS.warning.bg, color: t.template_type === 'full_match' ? COLORS.primary.main : COLORS.warning.main }}>
                      {t.template_type === 'full_match' ? 'FULL' : 'IN-MATCH'}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
          <button onClick={() => handleAssignTemplates(assigningM)} disabled={selectedTemplateIds.length === 0}
            className="w-full py-2 rounded-lg text-xs font-semibold disabled:opacity-40" style={{ background: COLORS.primary.main, color: '#fff' }}>
            Assign {selectedTemplateIds.length} Template(s)
          </button>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-8"><div className="w-6 h-6 border-2 rounded-full animate-spin" style={{ borderColor: `${COLORS.primary.main}30`, borderTopColor: COLORS.primary.main }} /></div>
      ) : (
        <div className="space-y-2">
          <div className="text-xs" style={{ color: COLORS.text.tertiary }}>{matches.length} matches</div>
          {matches.map(m => {
            const teamA = m.team_a?.short_name || '?';
            const teamB = m.team_b?.short_name || '?';
            const tCount = m.templates_assigned?.length || 0;
            return (
              <div key={m.id} className="rounded-xl overflow-hidden" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
                <div className="flex items-center gap-2 p-3 cursor-pointer" onClick={() => setExpandedM(expandedM === m.id ? null : m.id)}>
                  <div className="flex-1">
                    <div className="text-sm font-bold text-white">{teamA} vs {teamB}</div>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded" style={{ background: (STATUS_COLORS[m.status] || COLORS.text.tertiary) + '22', color: STATUS_COLORS[m.status] }}>
                        {m.status?.toUpperCase()}
                      </span>
                      <span className="text-[10px]" style={{ color: COLORS.text.tertiary }}>{tCount} templates</span>
                    </div>
                  </div>
                  {expandedM === m.id ? <ChevronUp size={14} color={COLORS.text.tertiary} /> : <ChevronDown size={14} color={COLORS.text.tertiary} />}
                </div>

                {expandedM === m.id && (
                  <div className="px-3 pb-3 border-t space-y-2" style={{ borderColor: COLORS.border.light }}>
                    <div className="text-[10px] mt-2" style={{ color: COLORS.text.tertiary }}>
                      {m.venue} | {new Date(m.start_time).toLocaleString()}
                    </div>

                    {/* Status Controls */}
                    <div className="flex flex-wrap gap-1.5">
                      {['upcoming', 'live', 'completed'].map(s => (
                        <button key={s} onClick={() => updateStatus(m.id, s)} disabled={m.status === s}
                          className="px-3 py-1.5 rounded-lg text-[10px] font-semibold disabled:opacity-30 flex items-center gap-1"
                          style={{ background: (STATUS_COLORS[s] || COLORS.text.tertiary) + '22', color: STATUS_COLORS[s] }}>
                          {s === 'live' && <Play size={10} />}
                          {s === 'completed' && <Square size={10} />}
                          {s.toUpperCase()}
                        </button>
                      ))}
                    </div>

                    {/* Assign Templates */}
                    <button onClick={() => { setAssigningM(m.id); setSelectedTemplateIds(m.templates_assigned || []); }}
                      className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs" style={{ background: COLORS.info.bg, color: COLORS.info.main }}>
                      <LinkIcon size={12} /> Assign Templates ({tCount})
                    </button>
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
