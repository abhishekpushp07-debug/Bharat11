/**
 * IPL SearchPage - World's Most Comprehensive IPL Search Experience
 * Features: Comprehensive search bar, IPL records, team logos, star players, team profiles
 */
import { useState, useEffect, useCallback, useRef } from 'react';
import apiClient from '../api/client';
import { COLORS } from '../constants/design';
import { TEAM_COLORS, TEAM_API_LOGOS, getTeamLogo, normalizeTeam } from '../constants/teams';
import { Search, X, Trophy, TrendingUp, Star, Flame, Target, Crown, Award, ChevronRight, ArrowLeft, Zap, Users } from 'lucide-react';
import TeamProfilePage from './TeamProfilePage';

const TEAM_LIST = [
  { short: 'MI', name: 'Mumbai Indians' },
  { short: 'CSK', name: 'Chennai Super Kings' },
  { short: 'RCB', name: 'Royal Challengers Bengaluru' },
  { short: 'KKR', name: 'Kolkata Knight Riders' },
  { short: 'DC', name: 'Delhi Capitals' },
  { short: 'PBKS', name: 'Punjab Kings' },
  { short: 'SRH', name: 'Sunrisers Hyderabad' },
  { short: 'RR', name: 'Rajasthan Royals' },
  { short: 'GT', name: 'Gujarat Titans' },
  { short: 'LSG', name: 'Lucknow Super Giants' },
];

const RECORD_ICONS = { bat: TrendingUp, flame: Flame, crown: Crown, zap: Zap, target: Target, rocket: Zap, award: Award, crosshair: Target, shield: Trophy, circle: Star, trophy: Trophy, 'alert-circle': Flame, hand: Users, calendar: Star, 'chevrons-right': ChevronRight, 'indian-rupee': Star };

export default function SearchPage({ onMatchClick, onBack }) {
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [searching, setSearching] = useState(false);
  const [records, setRecords] = useState([]);
  const [players, setPlayers] = useState([]);
  const [matches, setMatches] = useState([]);
  const [caps, setCaps] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [loading, setLoading] = useState(true);
  const inputRef = useRef(null);
  const searchTimer = useRef(null);

  // Load data on mount
  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [recRes, plRes, mRes, capRes] = await Promise.all([
          apiClient.get('/ipl/records'),
          apiClient.get('/ipl/players?limit=50'),
          apiClient.get('/matches?limit=50'),
          apiClient.get('/ipl/caps'),
        ]);
        setRecords(recRes.data.records || []);
        setPlayers(plRes.data.players || []);
        setMatches(mRes.data.matches || []);
        setCaps(capRes.data.cap_winners || []);
      } catch (_) {}
      finally { setLoading(false); }
    };
    fetchAll();
  }, []);

  // Debounced search
  const doSearch = useCallback(async (q) => {
    if (!q.trim()) { setSearchResults(null); return; }
    setSearching(true);
    try {
      const res = await apiClient.get(`/ipl/search?q=${encodeURIComponent(q)}`);
      setSearchResults(res.data);
    } catch (_) {}
    finally { setSearching(false); }
  }, []);

  useEffect(() => {
    clearTimeout(searchTimer.current);
    if (query.trim()) {
      searchTimer.current = setTimeout(() => doSearch(query), 300);
    } else {
      setSearchResults(null);
    }
    return () => clearTimeout(searchTimer.current);
  }, [query, doSearch]);

  // Team Profile View
  if (selectedTeam) {
    return <TeamProfilePage teamShort={selectedTeam} matches={matches} onMatchClick={onMatchClick} onBack={() => setSelectedTeam(null)} />;
  }

  // Player Profile View
  if (selectedPlayer) {
    return <PlayerProfileView player={selectedPlayer} onBack={() => setSelectedPlayer(null)} />;
  }

  const battingRecords = records.filter(r => r.category === 'batting');
  const bowlingRecords = records.filter(r => r.category === 'bowling');
  const specialRecords = records.filter(r => r.category === 'team' || r.category === 'special');
  const starPlayers = players.slice(0, 15);

  return (
    <div data-testid="search-page" className="space-y-5 pb-6">
      {/* Search Bar - Premium Design */}
      <div className="relative">
        {/* Ambient glow */}
        <div className="absolute -inset-2 rounded-3xl opacity-30" style={{
          background: 'linear-gradient(135deg, #1e3a8a, #FF3B3B22, #1e3a8a)',
          filter: 'blur(24px)'
        }} />
        <div className="relative rounded-2xl overflow-hidden" style={{
          background: 'linear-gradient(135deg, #0f172a, #1e293b)',
          border: '1px solid #334155',
          boxShadow: '0 8px 32px rgba(0,0,0,0.4)'
        }}>
          <div className="flex items-center gap-3 px-4 py-3.5">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
              style={{ background: 'linear-gradient(135deg, #1e3a8a, #3b82f6)' }}>
              <Search size={16} color="#fff" />
            </div>
            <input
              ref={inputRef}
              data-testid="ipl-search-input"
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="Search teams, players, records, matches..."
              className="flex-1 text-sm text-white bg-transparent outline-none placeholder:text-slate-500"
              style={{ fontFamily: "'Poppins', sans-serif" }}
            />
            {query && (
              <button data-testid="clear-search" onClick={() => setQuery('')} className="p-1">
                <X size={16} color="#64748b" />
              </button>
            )}
          </div>
          {/* Hint chips */}
          {!query && (
            <div className="flex gap-1.5 px-4 pb-3 overflow-x-auto no-scrollbar">
              {['CSK', 'Virat Kohli', 'Most Runs', 'Bumrah', 'Orange Cap'].map(hint => (
                <button key={hint} onClick={() => setQuery(hint)}
                  className="shrink-0 px-2.5 py-1 rounded-full text-[10px] font-medium whitespace-nowrap transition-all"
                  style={{ background: '#1e293b', color: '#94a3b8', border: '1px solid #334155' }}>
                  {hint}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Search Results */}
      {searchResults && query.trim() && (
        <SearchResultsView results={searchResults} onPlayerClick={setSelectedPlayer} onTeamClick={setSelectedTeam}
          onMatchClick={onMatchClick} players={players} />
      )}

      {/* Only show below sections when NOT searching */}
      {!query.trim() && (
        <>
          {/* IPL Records - Hero Section */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-1 h-5 rounded-full" style={{ background: '#FFD700' }} />
              <h3 className="text-sm font-bold text-white" style={{ fontFamily: "'Orbitron', sans-serif", letterSpacing: '1px' }}>
                IPL RECORDS
              </h3>
            </div>

            {/* Featured Record - Biggest one */}
            {battingRecords[0] && (
              <div className="rounded-2xl overflow-hidden relative" style={{ height: '100px' }}>
                <div className="absolute inset-0" style={{
                  background: 'linear-gradient(135deg, #991b1b, #7f1d1d, #451a03)',
                }} />
                <div className="absolute inset-0" style={{
                  background: 'radial-gradient(circle at 90% 50%, #FFD70033, transparent 60%)'
                }} />
                <div className="relative p-4 h-full flex items-center justify-between">
                  <div>
                    <div className="text-[10px] font-bold uppercase tracking-wider" style={{ color: '#fbbf24' }}>ALL-TIME RECORD</div>
                    <div className="text-lg font-black text-white mt-0.5">{battingRecords[0].title}</div>
                    <div className="text-xs mt-0.5" style={{ color: '#fca5a5' }}>{battingRecords[0].holder} | {battingRecords[0].team}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-3xl font-black" style={{ color: '#FFD700', fontFamily: "'Rajdhani', sans-serif" }}>
                      {battingRecords[0].value}
                    </div>
                    <div className="text-[9px]" style={{ color: '#fca5a5' }}>{battingRecords[0].year}</div>
                  </div>
                </div>
              </div>
            )}

            {/* Batting Records Grid */}
            <div className="text-[10px] font-bold uppercase tracking-wider" style={{ color: '#ef4444' }}>Batting</div>
            <div className="grid grid-cols-2 gap-2">
              {battingRecords.slice(1).map((r, i) => {
                const IconComp = RECORD_ICONS[r.icon] || Star;
                return (
                  <div key={r.title} className="p-3 rounded-xl relative overflow-hidden" style={{
                    background: COLORS.background.card,
                    border: `1px solid ${r.color}15`
                  }}>
                    <div className="absolute top-2 right-2 opacity-10"><IconComp size={28} color={r.color} /></div>
                    <div className="text-[9px] font-bold uppercase tracking-wider mb-1" style={{ color: r.color }}>{r.title}</div>
                    <div className="text-lg font-black text-white" style={{ fontFamily: "'Rajdhani', sans-serif" }}>{r.value}</div>
                    <div className="text-[10px] mt-0.5" style={{ color: COLORS.text.tertiary }}>{r.holder}</div>
                  </div>
                );
              })}
            </div>

            {/* Bowling Records */}
            <div className="text-[10px] font-bold uppercase tracking-wider mt-2" style={{ color: '#a855f7' }}>Bowling</div>
            <div className="grid grid-cols-2 gap-2">
              {bowlingRecords.map((r, i) => {
                const IconComp = RECORD_ICONS[r.icon] || Star;
                return (
                  <div key={r.title} className="p-3 rounded-xl relative overflow-hidden" style={{
                    background: COLORS.background.card,
                    border: `1px solid ${r.color}15`
                  }}>
                    <div className="absolute top-2 right-2 opacity-10"><IconComp size={28} color={r.color} /></div>
                    <div className="text-[9px] font-bold uppercase tracking-wider mb-1" style={{ color: r.color }}>{r.title}</div>
                    <div className="text-lg font-black text-white" style={{ fontFamily: "'Rajdhani', sans-serif" }}>{r.value}</div>
                    <div className="text-[10px] mt-0.5" style={{ color: COLORS.text.tertiary }}>{r.holder}</div>
                  </div>
                );
              })}
            </div>

            {/* Special Records */}
            <div className="text-[10px] font-bold uppercase tracking-wider mt-2" style={{ color: '#FFD700' }}>Team & Special</div>
            <div className="grid grid-cols-2 gap-2">
              {specialRecords.map((r) => (
                <div key={r.title} className="p-3 rounded-xl" style={{
                  background: COLORS.background.card,
                  border: `1px solid ${r.color}15`
                }}>
                  <div className="text-[9px] font-bold uppercase tracking-wider mb-1" style={{ color: r.color }}>{r.title}</div>
                  <div className="text-lg font-black text-white" style={{ fontFamily: "'Rajdhani', sans-serif" }}>{r.value}</div>
                  <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>{r.holder}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Orange & Purple Cap Winners */}
          {caps.length > 0 && (
            <div className="space-y-2.5">
              <div className="flex items-center gap-2">
                <div className="w-1 h-5 rounded-full" style={{ background: '#f97316' }} />
                <h3 className="text-sm font-bold text-white" style={{ fontFamily: "'Orbitron', sans-serif", letterSpacing: '1px' }}>
                  CAP WINNERS
                </h3>
              </div>
              <div className="overflow-x-auto pb-2 no-scrollbar">
                <div className="flex gap-2.5" style={{ width: 'max-content' }}>
                  {caps.slice(0, 6).map(c => (
                    <div key={c.year} className="w-[160px] shrink-0 rounded-xl p-3 space-y-2" style={{
                      background: COLORS.background.card,
                      border: `1px solid ${COLORS.border.light}`
                    }}>
                      <div className="text-center text-xs font-black" style={{ color: '#FFD700', fontFamily: "'Rajdhani', sans-serif" }}>
                        IPL {c.year}
                      </div>
                      {/* Orange Cap */}
                      <div className="p-2 rounded-lg" style={{ background: '#f9731611', border: '1px solid #f9731622' }}>
                        <div className="text-[8px] font-bold" style={{ color: '#f97316' }}>ORANGE CAP</div>
                        <div className="text-xs font-bold text-white">{c.orange_cap?.player}</div>
                        <div className="text-[10px]" style={{ color: '#f97316' }}>{c.orange_cap?.runs} runs | {c.orange_cap?.team}</div>
                      </div>
                      {/* Purple Cap */}
                      <div className="p-2 rounded-lg" style={{ background: '#a855f711', border: '1px solid #a855f722' }}>
                        <div className="text-[8px] font-bold" style={{ color: '#a855f7' }}>PURPLE CAP</div>
                        <div className="text-xs font-bold text-white">{c.purple_cap?.player}</div>
                        <div className="text-[10px]" style={{ color: '#a855f7' }}>{c.purple_cap?.wickets} wkts | {c.purple_cap?.team}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Team Logos Grid */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-1 h-5 rounded-full" style={{ background: COLORS.primary.main }} />
              <h3 className="text-sm font-bold text-white" style={{ fontFamily: "'Orbitron', sans-serif", letterSpacing: '1px' }}>
                IPL TEAMS
              </h3>
            </div>
            <div className="grid grid-cols-5 gap-2.5">
              {TEAM_LIST.map(team => {
                const color = TEAM_COLORS[team.short]?.primary || '#888';
                const logo = TEAM_API_LOGOS[team.short] || '';
                return (
                  <button key={team.short} data-testid={`team-${team.short}`}
                    onClick={() => setSelectedTeam(team.short)}
                    className="flex flex-col items-center gap-1.5 p-2.5 rounded-xl transition-all active:scale-95"
                    style={{
                      background: COLORS.background.card,
                      border: `1px solid ${color}22`,
                    }}>
                    <div className="w-11 h-11 rounded-full overflow-hidden flex items-center justify-center"
                      style={{ background: `${color}15`, border: `2px solid ${color}55` }}>
                      {logo ? <img src={logo} alt={team.short} className="w-8 h-8 object-contain" /> :
                        <span className="text-xs font-black" style={{ color }}>{team.short}</span>}
                    </div>
                    <span className="text-[9px] font-bold text-white">{team.short}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Star Players */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-1 h-5 rounded-full" style={{ background: '#f59e0b' }} />
              <h3 className="text-sm font-bold text-white" style={{ fontFamily: "'Orbitron', sans-serif", letterSpacing: '1px' }}>
                STAR PLAYERS
              </h3>
            </div>
            <div className="grid grid-cols-4 gap-3">
              {starPlayers.map(p => {
                const teamColor = TEAM_COLORS[normalizeTeam(p.current_team)]?.primary || '#888';
                const initials = p.name.split(' ').map(n => n[0]).join('');
                return (
                  <button key={p.name} data-testid={`player-${p.name.replace(/\s/g, '-').toLowerCase()}`}
                    onClick={() => setSelectedPlayer(p)}
                    className="flex flex-col items-center gap-1.5 transition-all active:scale-95">
                    {/* Player Avatar */}
                    <div className="w-14 h-14 rounded-full flex items-center justify-center relative"
                      style={{
                        background: `linear-gradient(135deg, ${teamColor}33, ${teamColor}11)`,
                        border: `2.5px solid ${teamColor}88`,
                        boxShadow: `0 2px 12px ${teamColor}22`
                      }}>
                      <span className="text-sm font-black" style={{ color: teamColor }}>{initials}</span>
                      {/* Team badge */}
                      <div className="absolute -bottom-0.5 -right-0.5 w-5 h-5 rounded-full flex items-center justify-center"
                        style={{ background: COLORS.background.primary, border: `1.5px solid ${teamColor}` }}>
                        <span className="text-[6px] font-black" style={{ color: teamColor }}>{p.current_team || '?'}</span>
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-[10px] font-bold text-white leading-tight">{p.name.split(' ').pop()}</div>
                      <div className="text-[8px]" style={{ color: COLORS.text.tertiary }}>{p.role}</div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

// ==================== SEARCH RESULTS VIEW ====================
function SearchResultsView({ results, onPlayerClick, onTeamClick, onMatchClick, players }) {
  const { players: pResults, teams: tResults, matches: mResults, records: rResults } = results.results;

  return (
    <div data-testid="search-results" className="space-y-4">
      <div className="text-xs" style={{ color: COLORS.text.tertiary }}>
        {results.total} results for "{results.query}"
      </div>

      {/* Player Results */}
      {pResults.length > 0 && (
        <div className="space-y-2">
          <div className="text-[10px] font-bold uppercase tracking-wider" style={{ color: '#f59e0b' }}>Players</div>
          {pResults.map(p => {
            const teamColor = TEAM_COLORS[normalizeTeam(p.current_team)]?.primary || '#888';
            return (
              <button key={p.name} onClick={() => onPlayerClick(p)}
                className="w-full text-left flex items-center gap-3 p-3 rounded-xl transition-all active:scale-[0.98]"
                style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
                <div className="w-10 h-10 rounded-full flex items-center justify-center shrink-0"
                  style={{ background: `${teamColor}22`, border: `2px solid ${teamColor}55` }}>
                  <span className="text-xs font-black" style={{ color: teamColor }}>
                    {p.name.split(' ').map(n => n[0]).join('')}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-xs font-bold text-white">{p.name}</div>
                  <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>{p.role} | {p.current_team} | {p.nationality}</div>
                </div>
                <ChevronRight size={14} color={COLORS.text.tertiary} />
              </button>
            );
          })}
        </div>
      )}

      {/* Team Results */}
      {tResults.length > 0 && (
        <div className="space-y-2">
          <div className="text-[10px] font-bold uppercase tracking-wider" style={{ color: COLORS.primary.main }}>Teams</div>
          {tResults.map(t => {
            const color = TEAM_COLORS[t.short]?.primary || '#888';
            const logo = TEAM_API_LOGOS[t.short] || '';
            return (
              <button key={t.short} onClick={() => onTeamClick(t.short)}
                className="w-full text-left flex items-center gap-3 p-3 rounded-xl transition-all active:scale-[0.98]"
                style={{ background: COLORS.background.card, border: `1px solid ${color}22` }}>
                <div className="w-10 h-10 rounded-full flex items-center justify-center shrink-0"
                  style={{ background: `${color}15`, border: `2px solid ${color}55` }}>
                  {logo ? <img src={logo} alt="" className="w-7 h-7" /> :
                    <span className="text-xs font-black" style={{ color }}>{t.short}</span>}
                </div>
                <div className="flex-1">
                  <div className="text-xs font-bold text-white">{t.name}</div>
                  <div className="text-[10px]" style={{ color }}>{t.short}</div>
                </div>
                <ChevronRight size={14} color={COLORS.text.tertiary} />
              </button>
            );
          })}
        </div>
      )}

      {/* Record Results */}
      {rResults.length > 0 && (
        <div className="space-y-2">
          <div className="text-[10px] font-bold uppercase tracking-wider" style={{ color: '#FFD700' }}>Records</div>
          {rResults.map(r => (
            <div key={r.title} className="p-3 rounded-xl flex items-center justify-between"
              style={{ background: COLORS.background.card, border: `1px solid ${r.color}15` }}>
              <div>
                <div className="text-[10px] font-bold" style={{ color: r.color }}>{r.title}</div>
                <div className="text-xs text-white">{r.holder} ({r.team})</div>
              </div>
              <div className="text-lg font-black" style={{ color: r.color, fontFamily: "'Rajdhani', sans-serif" }}>{r.value}</div>
            </div>
          ))}
        </div>
      )}

      {/* Match Results */}
      {mResults.length > 0 && (
        <div className="space-y-2">
          <div className="text-[10px] font-bold uppercase tracking-wider" style={{ color: COLORS.info.main }}>Matches</div>
          {mResults.map(m => {
            const ta = m.team_a?.short_name || '?';
            const tb = m.team_b?.short_name || '?';
            return (
              <button key={m.id} onClick={() => onMatchClick?.(m)}
                className="w-full text-left p-3 rounded-xl flex items-center justify-between transition-all active:scale-[0.98]"
                style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
                <div>
                  <div className="text-xs font-bold text-white">{ta} vs {tb}</div>
                  <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>
                    {m.venue?.slice(0, 25)} | {m.status}
                  </div>
                </div>
                <ChevronRight size={14} color={COLORS.text.tertiary} />
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ==================== PLAYER PROFILE VIEW ====================
function PlayerProfileView({ player, onBack }) {
  if (!player) return null;
  const p = player;
  const teamColor = TEAM_COLORS[normalizeTeam(p.current_team)]?.primary || '#888';
  const initials = p.name.split(' ').map(n => n[0]).join('');
  const stats = p.ipl_stats || {};

  return (
    <div data-testid="player-profile" className="space-y-4 pb-6">
      <button data-testid="player-back-btn" onClick={onBack}
        className="text-xs flex items-center gap-1" style={{ color: COLORS.text.secondary }}>
        <ArrowLeft size={14} /> Back
      </button>

      {/* Hero Header */}
      <div className="rounded-2xl overflow-hidden relative" style={{ height: '180px' }}>
        <div className="absolute inset-0" style={{
          background: `linear-gradient(135deg, ${teamColor}cc, ${teamColor}44, #0D0D0D)`,
        }} />
        <div className="absolute inset-0" style={{
          background: 'radial-gradient(circle at 30% 80%, rgba(255,255,255,0.05), transparent 50%)'
        }} />
        <div className="relative p-5 h-full flex items-end gap-4">
          {/* Large Avatar */}
          <div className="w-20 h-20 rounded-2xl flex items-center justify-center shadow-2xl"
            style={{
              background: `linear-gradient(135deg, ${teamColor}44, ${teamColor}22)`,
              border: `3px solid ${teamColor}`,
              boxShadow: `0 8px 32px ${teamColor}44`
            }}>
            <span className="text-2xl font-black" style={{ color: teamColor }}>{initials}</span>
          </div>
          <div className="flex-1 pb-1">
            <div className="text-xl font-black text-white leading-tight drop-shadow-lg">{p.name}</div>
            <div className="text-xs mt-0.5" style={{ color: '#ffffffcc' }}>{p.name_hi}</div>
            <div className="flex items-center gap-2 mt-1.5 flex-wrap">
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full" style={{ background: `${teamColor}33`, color: teamColor }}>
                {p.current_team || 'Retired'}
              </span>
              <span className="text-[10px]" style={{ color: '#ffffffaa' }}>{p.role}</span>
              <span className="text-[10px]" style={{ color: '#ffffffaa' }}>{p.nationality}</span>
              {p.jersey_no && <span className="text-[10px] font-bold" style={{ color: '#FFD700' }}>#{p.jersey_no}</span>}
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-4 gap-2">
        {[
          { label: 'Matches', value: stats.matches, color: COLORS.info.main },
          { label: 'Runs', value: stats.runs?.toLocaleString(), color: '#FF3B3B' },
          { label: 'Avg', value: stats.avg?.toFixed(1), color: '#FFD700' },
          { label: 'SR', value: stats.sr?.toFixed(1), color: '#10b981' },
        ].map(({ label, value, color }) => (
          <div key={label} className="text-center p-2.5 rounded-xl" style={{ background: COLORS.background.card }}>
            <div className="text-base font-black" style={{ color, fontFamily: "'Rajdhani', sans-serif" }}>{value || '-'}</div>
            <div className="text-[8px] font-bold uppercase" style={{ color: COLORS.text.tertiary }}>{label}</div>
          </div>
        ))}
      </div>

      {/* Detailed Stats */}
      <div className="p-4 rounded-2xl space-y-2" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
        <div className="text-xs font-bold uppercase tracking-wider" style={{ color: COLORS.text.tertiary }}>IPL Career Stats</div>
        <div className="grid grid-cols-2 gap-x-6 gap-y-1.5">
          {[
            { label: 'Highest Score', value: stats.highest_score },
            { label: '50s / 100s', value: `${stats.fifties || 0} / ${stats.hundreds || 0}` },
            { label: 'Fours', value: stats.fours },
            { label: 'Sixes', value: stats.sixes },
            { label: 'Wickets', value: stats.wickets },
            { label: 'Economy', value: stats.economy },
            { label: 'Best Bowling', value: stats.best_bowling },
            { label: 'Catches', value: stats.catches },
          ].filter(s => s.value !== undefined && s.value !== null).map(({ label, value }) => (
            <div key={label} className="flex justify-between py-1" style={{ borderBottom: `1px solid ${COLORS.border.light}` }}>
              <span className="text-[10px]" style={{ color: COLORS.text.tertiary }}>{label}</span>
              <span className="text-xs font-bold text-white">{value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Teams History */}
      {p.teams_history?.length > 0 && (
        <div className="p-4 rounded-2xl space-y-2" style={{ background: COLORS.background.card }}>
          <div className="text-xs font-bold uppercase tracking-wider" style={{ color: COLORS.text.tertiary }}>IPL Teams</div>
          <div className="flex gap-2 flex-wrap">
            {p.teams_history.map(t => {
              const tc = TEAM_COLORS[normalizeTeam(t)]?.primary || '#888';
              const isCurrent = normalizeTeam(t) === normalizeTeam(p.current_team);
              return (
                <div key={t} className="px-3 py-1.5 rounded-lg flex items-center gap-2" style={{
                  background: `${tc}15`,
                  border: `1px solid ${isCurrent ? tc : tc + '33'}`,
                }}>
                  <img src={getTeamLogo(t)} alt="" className="w-5 h-5 rounded-full" />
                  <span className="text-xs font-bold" style={{ color: tc }}>{t}</span>
                  {isCurrent && <span className="text-[8px] font-bold px-1 rounded" style={{ background: tc, color: '#fff' }}>NOW</span>}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Achievements */}
      {p.achievements?.length > 0 && (
        <div className="p-4 rounded-2xl space-y-2" style={{
          background: `linear-gradient(180deg, ${teamColor}08, ${COLORS.background.card})`,
          border: `1px solid ${teamColor}15`
        }}>
          <div className="flex items-center gap-2">
            <Award size={14} color={teamColor} />
            <span className="text-xs font-bold uppercase tracking-wider" style={{ color: teamColor }}>Achievements</span>
          </div>
          {p.achievements.map((a, i) => (
            <div key={i} className="flex items-start gap-2.5 p-2 rounded-lg" style={{ background: `${teamColor}08` }}>
              <div className="w-5 h-5 rounded-full flex items-center justify-center shrink-0 mt-0.5 text-[9px] font-black"
                style={{ background: `${teamColor}22`, color: teamColor }}>{i + 1}</div>
              <span className="text-[11px] leading-snug" style={{ color: COLORS.text.secondary }}>{a}</span>
            </div>
          ))}
        </div>
      )}

      {/* Bio */}
      <div className="p-4 rounded-2xl space-y-2" style={{ background: COLORS.background.card }}>
        <div className="text-xs font-bold uppercase tracking-wider" style={{ color: COLORS.text.tertiary }}>About</div>
        <div className="text-xs leading-relaxed" style={{ color: COLORS.text.secondary }}>{p.bio}</div>
        {p.bio_hi && (
          <div className="p-3 rounded-xl mt-2" style={{ background: `${teamColor}08` }}>
            <div className="text-[10px] font-bold mb-1" style={{ color: COLORS.text.tertiary }}>हिंदी</div>
            <div className="text-[11px] leading-relaxed" style={{ color: COLORS.text.secondary }}>{p.bio_hi}</div>
          </div>
        )}
      </div>
    </div>
  );
}
