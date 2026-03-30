/**
 * SearchPage - Vibrant team/match/player search experience
 * Clickable IPL team logos, search by team/player/match
 */
import { useState, useEffect, useCallback, useRef } from 'react';
import apiClient from '../api/client';
import { COLORS } from '../constants/design';
import { TEAM_COLORS, TEAM_API_LOGOS, TEAM_CARD_IMAGES, getTeamLogo, normalizeTeam } from '../constants/teams';
import { Search, X, Trophy, Calendar, Users, ChevronRight, ArrowLeft, Star, Zap } from 'lucide-react';

const TEAM_INFO = [
  { short: 'MI', name: 'Mumbai Indians', city: 'Mumbai' },
  { short: 'CSK', name: 'Chennai Super Kings', city: 'Chennai' },
  { short: 'RCB', name: 'Royal Challengers Bengaluru', city: 'Bengaluru' },
  { short: 'KKR', name: 'Kolkata Knight Riders', city: 'Kolkata' },
  { short: 'DC', name: 'Delhi Capitals', city: 'Delhi' },
  { short: 'PBKS', name: 'Punjab Kings', city: 'Mohali' },
  { short: 'SRH', name: 'Sunrisers Hyderabad', city: 'Hyderabad' },
  { short: 'RR', name: 'Rajasthan Royals', city: 'Jaipur' },
  { short: 'GT', name: 'Gujarat Titans', city: 'Ahmedabad' },
  { short: 'LSG', name: 'Lucknow Super Giants', city: 'Lucknow' },
];

export default function SearchPage({ onMatchClick, onBack }) {
  const [query, setQuery] = useState('');
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const inputRef = useRef(null);

  useEffect(() => {
    // Auto-focus search input
    setTimeout(() => inputRef.current?.focus(), 300);
  }, []);

  const fetchMatches = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/matches?limit=50');
      setMatches(res.data.matches || []);
    } catch (_) {}
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchMatches(); }, [fetchMatches]);

  // Filter results based on query or selected team
  const filteredMatches = matches.filter(m => {
    const teamA = m.team_a?.short_name || '';
    const teamB = m.team_b?.short_name || '';
    const teamAName = m.team_a?.name || '';
    const teamBName = m.team_b?.name || '';
    const venue = m.venue || '';

    if (selectedTeam) {
      const norm = normalizeTeam(selectedTeam);
      return normalizeTeam(teamA) === norm || normalizeTeam(teamB) === norm;
    }
    if (!query.trim()) return false;

    const q = query.toLowerCase();
    return teamA.toLowerCase().includes(q) || teamB.toLowerCase().includes(q) ||
           teamAName.toLowerCase().includes(q) || teamBName.toLowerCase().includes(q) ||
           venue.toLowerCase().includes(q);
  });

  const filteredTeams = query.trim()
    ? TEAM_INFO.filter(t =>
        t.short.toLowerCase().includes(query.toLowerCase()) ||
        t.name.toLowerCase().includes(query.toLowerCase()) ||
        t.city.toLowerCase().includes(query.toLowerCase())
      )
    : TEAM_INFO;

  return (
    <div data-testid="search-page" className="pb-4 space-y-4">
      {/* Back button */}
      {onBack && (
        <button onClick={onBack} className="text-xs flex items-center gap-1 mb-2" style={{ color: COLORS.text.secondary }}>
          <ArrowLeft size={14} /> Back
        </button>
      )}

      {/* Search Bar - Vibrant */}
      <div className="relative">
        <div className="absolute inset-0 rounded-2xl opacity-40" style={{
          background: 'linear-gradient(135deg, #FF3B3B22, #1e40af22, #f59e0b22)',
          filter: 'blur(20px)'
        }} />
        <div className="relative flex items-center gap-3 px-4 py-3.5 rounded-2xl" style={{
          background: COLORS.background.card,
          border: `1px solid ${COLORS.primary.main}33`,
          boxShadow: `0 4px 24px ${COLORS.primary.main}15`
        }}>
          <Search size={18} color={COLORS.primary.main} />
          <input
            ref={inputRef}
            data-testid="search-input"
            value={query}
            onChange={e => { setQuery(e.target.value); setSelectedTeam(null); }}
            placeholder="Search teams, players, matches..."
            className="flex-1 text-sm text-white bg-transparent outline-none placeholder:text-gray-500"
          />
          {(query || selectedTeam) && (
            <button data-testid="clear-search" onClick={() => { setQuery(''); setSelectedTeam(null); }}>
              <X size={16} color={COLORS.text.tertiary} />
            </button>
          )}
        </div>
      </div>

      {/* Selected Team Header */}
      {selectedTeam && (
        <div className="rounded-2xl overflow-hidden relative" style={{ height: '120px' }}>
          <img src={TEAM_CARD_IMAGES[selectedTeam] || ''} alt="" className="w-full h-full object-cover" />
          <div className="absolute inset-0" style={{ background: 'linear-gradient(to top, rgba(0,0,0,0.9) 0%, transparent 100%)' }} />
          <div className="absolute bottom-3 left-4 flex items-center gap-3">
            <img src={getTeamLogo(selectedTeam)} alt="" className="w-10 h-10 rounded-full" style={{ border: `2px solid ${TEAM_COLORS[selectedTeam]?.primary || '#fff'}` }} />
            <div>
              <div className="text-base font-bold text-white">{TEAM_INFO.find(t => t.short === selectedTeam)?.name}</div>
              <div className="text-xs" style={{ color: '#ffffffaa' }}>{filteredMatches.length} match(es) found</div>
            </div>
          </div>
        </div>
      )}

      {/* IPL Teams Grid - Always Visible */}
      {!selectedTeam && (
        <div>
          <h3 className="text-xs font-bold uppercase tracking-wider mb-3" style={{ color: COLORS.text.tertiary }}>IPL 2025 Teams</h3>
          <div className="grid grid-cols-5 gap-2.5">
            {filteredTeams.map(team => {
              const color = TEAM_COLORS[team.short]?.primary || '#888';
              const logo = TEAM_API_LOGOS[team.short] || '';
              return (
                <button key={team.short} data-testid={`team-${team.short}`}
                  onClick={() => { setSelectedTeam(team.short); setQuery(''); }}
                  className="flex flex-col items-center gap-1.5 p-2.5 rounded-xl transition-all active:scale-95"
                  style={{
                    background: COLORS.background.card,
                    border: `1px solid ${color}33`,
                    boxShadow: `0 2px 12px ${color}11`
                  }}>
                  <div className="w-10 h-10 rounded-full overflow-hidden flex items-center justify-center"
                    style={{ background: `${color}22`, border: `2px solid ${color}66` }}>
                    {logo ? <img src={logo} alt={team.short} className="w-7 h-7 object-contain" /> :
                      <span className="text-[10px] font-black" style={{ color }}>{team.short}</span>}
                  </div>
                  <span className="text-[10px] font-bold text-white">{team.short}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Search Results - Matches */}
      {(selectedTeam || query.trim()) && (
        <div className="space-y-2">
          <h3 className="text-xs font-bold uppercase tracking-wider" style={{ color: COLORS.text.tertiary }}>
            {selectedTeam ? `${selectedTeam} Matches` : 'Search Results'}
          </h3>
          {loading ? (
            <div className="flex justify-center py-6">
              <div className="w-6 h-6 border-2 rounded-full animate-spin" style={{ borderColor: `${COLORS.primary.main}30`, borderTopColor: COLORS.primary.main }} />
            </div>
          ) : filteredMatches.length === 0 ? (
            <div className="text-center py-8">
              <Search size={32} color={COLORS.text.tertiary} className="mx-auto mb-2" />
              <div className="text-sm" style={{ color: COLORS.text.tertiary }}>No matches found</div>
            </div>
          ) : (
            filteredMatches.map(m => {
              const ta = m.team_a?.short_name || '?';
              const tb = m.team_b?.short_name || '?';
              const colA = TEAM_COLORS[normalizeTeam(ta)]?.primary || '#888';
              const colB = TEAM_COLORS[normalizeTeam(tb)]?.primary || '#888';
              const isLive = m.status === 'live';
              const isUpcoming = m.status === 'upcoming';

              return (
                <button key={m.id} data-testid={`match-result-${m.id}`}
                  onClick={() => onMatchClick?.(m)}
                  className="w-full text-left rounded-xl p-3.5 transition-all active:scale-[0.98]"
                  style={{
                    background: `linear-gradient(135deg, ${colA}08, ${COLORS.background.card}, ${colB}08)`,
                    border: `1px solid ${isLive ? '#FF3B3B33' : COLORS.border.light}`,
                    boxShadow: isLive ? '0 0 12px rgba(255,59,59,0.1)' : 'none'
                  }}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <img src={getTeamLogo(ta)} alt="" className="w-8 h-8 rounded-full" style={{ border: `2px solid ${colA}` }} />
                      <div>
                        <div className="text-sm font-bold text-white">{ta} vs {tb}</div>
                        <div className="text-[10px] mt-0.5" style={{ color: COLORS.text.tertiary }}>
                          {m.venue?.slice(0, 30)} | {m.start_time ? new Date(m.start_time).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) : ''}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full" style={{
                        background: isLive ? '#FF3B3B22' : isUpcoming ? COLORS.info.bg : COLORS.background.tertiary,
                        color: isLive ? '#FF3B3B' : isUpcoming ? COLORS.info.main : COLORS.text.tertiary
                      }}>{m.status?.toUpperCase()}</span>
                      <ChevronRight size={14} color={COLORS.text.tertiary} />
                    </div>
                  </div>
                  {m.live_score?.status_text && (
                    <div className="text-[10px] mt-2 px-2 py-1 rounded-lg" style={{ background: '#FF3B3B11', color: '#FF3B3B' }}>
                      {m.live_score.status_text}
                    </div>
                  )}
                </button>
              );
            })
          )}
        </div>
      )}

      {/* Quick Stats */}
      {!selectedTeam && !query.trim() && (
        <div className="space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider" style={{ color: COLORS.text.tertiary }}>Quick Stats</h3>
          <div className="grid grid-cols-3 gap-2">
            {[
              { label: 'Live', value: matches.filter(m => m.status === 'live').length, Icon: Zap, color: '#FF3B3B' },
              { label: 'Upcoming', value: matches.filter(m => m.status === 'upcoming').length, Icon: Calendar, color: COLORS.info.main },
              { label: 'Completed', value: matches.filter(m => m.status === 'completed').length, Icon: Trophy, color: COLORS.success.main },
            ].map(({ label, value, Icon, color }) => (
              <div key={label} className="text-center p-3 rounded-xl" style={{ background: COLORS.background.card, border: `1px solid ${color}22` }}>
                <Icon size={16} color={color} className="mx-auto mb-1" />
                <div className="text-lg font-black text-white" style={{ fontFamily: "'Rajdhani', sans-serif" }}>{value}</div>
                <div className="text-[9px] font-bold" style={{ color: COLORS.text.tertiary }}>{label}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
