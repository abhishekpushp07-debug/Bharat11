/**
 * HeadToHead - IPL Player Comparison with Animated Bars
 * Select two players and see side-by-side stats comparison
 */
import { useState, useEffect, useRef } from 'react';
import { COLORS } from '../constants/design';
import { TEAM_COLORS, normalizeTeam } from '../constants/teams';
import { ChevronDown, X, Swords, TrendingUp, Target, Zap, Award } from 'lucide-react';

const COMPARE_STATS = [
  { key: 'matches', label: 'Matches', icon: Target, format: v => v },
  { key: 'runs', label: 'Runs', icon: TrendingUp, format: v => v?.toLocaleString() },
  { key: 'avg', label: 'Average', icon: Award, format: v => v?.toFixed(2) },
  { key: 'sr', label: 'Strike Rate', icon: Zap, format: v => v?.toFixed(2) },
  { key: 'fifties', label: 'Fifties', icon: Award, format: v => v },
  { key: 'hundreds', label: 'Centuries', icon: Award, format: v => v },
  { key: 'sixes', label: 'Sixes', icon: Target, format: v => v },
  { key: 'fours', label: 'Fours', icon: Target, format: v => v },
  { key: 'wickets', label: 'Wickets', icon: Target, format: v => v },
  { key: 'catches', label: 'Catches', icon: Target, format: v => v },
];

function PlayerSelector({ players, selected, onSelect, label, side }) {
  const [open, setOpen] = useState(false);
  const [filter, setFilter] = useState('');
  const ref = useRef(null);

  useEffect(() => {
    const handleClick = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const filtered = players.filter(p =>
    p.name.toLowerCase().includes(filter.toLowerCase()) ||
    p.current_team?.toLowerCase().includes(filter.toLowerCase())
  );

  const teamColor = selected ? (TEAM_COLORS[normalizeTeam(selected.current_team)]?.primary || '#888') : '#444';
  const initials = selected ? selected.name.split(' ').map(n => n[0]).join('') : '?';

  return (
    <div ref={ref} className="relative flex-1 min-w-0">
      <button
        data-testid={`h2h-select-${side}`}
        onClick={() => setOpen(!open)}
        className="w-full p-3 rounded-xl flex items-center gap-2 transition-all active:scale-[0.98]"
        style={{
          background: selected ? `${teamColor}15` : COLORS.background.card,
          border: `1.5px solid ${selected ? teamColor + '55' : COLORS.border?.light || '#333'}`,
        }}
      >
        <div className="w-9 h-9 rounded-full flex items-center justify-center shrink-0"
          style={{ background: `${teamColor}25`, border: `2px solid ${teamColor}` }}>
          <span className="text-[10px] font-black" style={{ color: teamColor }}>{initials}</span>
        </div>
        <div className="flex-1 text-left min-w-0">
          <div className="text-[10px] font-bold uppercase tracking-wider" style={{ color: COLORS.text.tertiary }}>{label}</div>
          <div className="text-xs font-bold text-white truncate">{selected?.name || 'Select Player'}</div>
        </div>
        {selected ? (
          <span role="button" tabIndex={0} onClick={(e) => { e.stopPropagation(); onSelect(null); setOpen(false); }}
            onKeyDown={(e) => { if (e.key === 'Enter') { e.stopPropagation(); onSelect(null); setOpen(false); } }}
            className="p-0.5 cursor-pointer">
            <X size={12} color={COLORS.text.tertiary} />
          </span>
        ) : (
          <ChevronDown size={14} color={COLORS.text.tertiary} className={`transition-transform ${open ? 'rotate-180' : ''}`} />
        )}
      </button>

      {open && (
        <div className="absolute z-50 top-full mt-1 left-0 right-0 rounded-xl overflow-hidden shadow-2xl"
          style={{ background: COLORS.background.secondary, border: `1px solid ${COLORS.border?.light || '#333'}`, maxHeight: '240px' }}>
          <div className="p-2 sticky top-0" style={{ background: COLORS.background.secondary }}>
            <input
              data-testid={`h2h-filter-${side}`}
              value={filter} onChange={e => setFilter(e.target.value)}
              placeholder="Search player..."
              className="w-full px-3 py-2 rounded-lg text-xs text-white bg-transparent outline-none"
              style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border?.light || '#333'}` }}
              autoFocus
            />
          </div>
          <div className="overflow-y-auto" style={{ maxHeight: '190px' }}>
            {filtered.map(p => {
              const tc = TEAM_COLORS[normalizeTeam(p.current_team)]?.primary || '#888';
              return (
                <button key={p.name}
                  data-testid={`h2h-option-${p.name.replace(/\s/g, '-').toLowerCase()}`}
                  onClick={() => { onSelect(p); setOpen(false); setFilter(''); }}
                  className="w-full text-left flex items-center gap-2.5 px-3 py-2 transition-colors hover:opacity-80"
                  style={{ borderBottom: `1px solid ${COLORS.background.tertiary}` }}>
                  <div className="w-7 h-7 rounded-full flex items-center justify-center shrink-0"
                    style={{ background: `${tc}22`, border: `1.5px solid ${tc}55` }}>
                    <span className="text-[8px] font-black" style={{ color: tc }}>{p.name.split(' ').map(n => n[0]).join('')}</span>
                  </div>
                  <div className="min-w-0">
                    <div className="text-[11px] font-bold text-white truncate">{p.name}</div>
                    <div className="text-[9px]" style={{ color: COLORS.text.tertiary }}>{p.role} | {p.current_team || 'Retired'}</div>
                  </div>
                </button>
              );
            })}
            {filtered.length === 0 && (
              <div className="px-3 py-4 text-center text-[10px]" style={{ color: COLORS.text.tertiary }}>No players found</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function AnimatedBar({ val1, val2, color1, color2, animate }) {
  const total = (val1 || 0) + (val2 || 0);
  if (total === 0) return null;
  const pct1 = ((val1 || 0) / total) * 100;
  const pct2 = ((val2 || 0) / total) * 100;
  const winner = val1 > val2 ? 1 : val2 > val1 ? 2 : 0;

  return (
    <div className="flex h-2.5 rounded-full overflow-hidden gap-[2px]" style={{ background: COLORS.background.tertiary }}>
      <div
        className="rounded-l-full transition-all duration-1000 ease-out"
        style={{
          width: animate ? `${pct1}%` : '0%',
          background: winner === 1 ? color1 : `${color1}55`,
          boxShadow: winner === 1 ? `0 0 8px ${color1}44` : 'none',
        }}
      />
      <div
        className="rounded-r-full transition-all duration-1000 ease-out"
        style={{
          width: animate ? `${pct2}%` : '0%',
          background: winner === 2 ? color2 : `${color2}55`,
          boxShadow: winner === 2 ? `0 0 8px ${color2}44` : 'none',
        }}
      />
    </div>
  );
}

export default function HeadToHead({ players }) {
  const [p1, setP1] = useState(null);
  const [p2, setP2] = useState(null);
  const [animate, setAnimate] = useState(false);

  const color1 = p1 ? (TEAM_COLORS[normalizeTeam(p1.current_team)]?.primary || '#3b82f6') : '#3b82f6';
  const color2 = p2 ? (TEAM_COLORS[normalizeTeam(p2.current_team)]?.primary || '#ef4444') : '#ef4444';

  useEffect(() => {
    if (p1 && p2) {
      setAnimate(false);
      const t = setTimeout(() => setAnimate(true), 100);
      return () => clearTimeout(t);
    }
    setAnimate(false);
  }, [p1, p2]);

  // Calculate verdict
  let p1Wins = 0, p2Wins = 0;
  if (p1 && p2) {
    COMPARE_STATS.forEach(({ key }) => {
      const v1 = p1.ipl_stats?.[key] || 0;
      const v2 = p2.ipl_stats?.[key] || 0;
      if (key === 'wickets' && v1 === 0 && v2 === 0) return;
      if (v1 > v2) p1Wins++;
      else if (v2 > v1) p2Wins++;
    });
  }

  const relevantStats = COMPARE_STATS.filter(({ key }) => {
    if (!p1 || !p2) return true;
    const v1 = p1.ipl_stats?.[key] || 0;
    const v2 = p2.ipl_stats?.[key] || 0;
    if (key === 'wickets' && v1 === 0 && v2 === 0) return false;
    return true;
  });

  return (
    <div data-testid="head-to-head-section" className="space-y-3">
      <div className="flex items-center gap-2">
        <div className="w-1 h-5 rounded-full" style={{ background: '#ef4444' }} />
        <Swords size={16} color="#ef4444" />
        <h3 className="text-sm font-bold text-white" style={{ fontFamily: "'Orbitron', sans-serif", letterSpacing: '1px' }}>
          HEAD TO HEAD
        </h3>
      </div>

      {/* Player Selectors */}
      <div className="flex items-center gap-2">
        <PlayerSelector players={players} selected={p1} onSelect={setP1} label="Player 1" side="left" />
        <div className="shrink-0 w-9 h-9 rounded-full flex items-center justify-center"
          style={{
            background: 'linear-gradient(135deg, #ef4444, #f97316)',
            boxShadow: '0 4px 16px rgba(239,68,68,0.3)',
          }}>
          <span className="text-[10px] font-black text-white">VS</span>
        </div>
        <PlayerSelector players={players} selected={p2} onSelect={setP2} label="Player 2" side="right" />
      </div>

      {/* Comparison Results */}
      {p1 && p2 && (
        <div className="space-y-2 rounded-2xl p-4" style={{
          background: COLORS.background.card,
          border: `1px solid ${COLORS.border?.light || '#333'}`,
        }}>
          {/* Verdict Banner */}
          <div className="flex items-center justify-between p-3 rounded-xl mb-2" style={{
            background: `linear-gradient(135deg, ${color1}15, ${color2}15)`,
            border: `1px solid ${COLORS.border?.light || '#333'}`,
          }}>
            <div className="text-center flex-1">
              <div className="text-lg font-black" style={{ color: color1, fontFamily: "'Rajdhani', sans-serif" }}>{p1Wins}</div>
              <div className="text-[8px] font-bold uppercase" style={{ color: COLORS.text.tertiary }}>WINS</div>
            </div>
            <div className="px-3">
              <div className="text-[10px] font-bold uppercase tracking-wider" style={{ color: COLORS.text.tertiary }}>
                {p1Wins > p2Wins ? 'Advantage' : p2Wins > p1Wins ? 'Advantage' : 'Draw'}
              </div>
              <div className="text-xs font-black text-center" style={{ color: p1Wins > p2Wins ? color1 : p2Wins > p1Wins ? color2 : '#FFD700' }}>
                {p1Wins > p2Wins ? p1.name.split(' ').pop() : p2Wins > p1Wins ? p2.name.split(' ').pop() : 'Even'}
              </div>
            </div>
            <div className="text-center flex-1">
              <div className="text-lg font-black" style={{ color: color2, fontFamily: "'Rajdhani', sans-serif" }}>{p2Wins}</div>
              <div className="text-[8px] font-bold uppercase" style={{ color: COLORS.text.tertiary }}>WINS</div>
            </div>
          </div>

          {/* Stat Bars */}
          {relevantStats.map(({ key, label, format }) => {
            const v1 = p1.ipl_stats?.[key] || 0;
            const v2 = p2.ipl_stats?.[key] || 0;
            const w1 = v1 > v2;
            const w2 = v2 > v1;
            return (
              <div key={key} className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className={`text-xs font-bold ${w1 ? '' : 'opacity-60'}`}
                    style={{ color: w1 ? color1 : COLORS.text.secondary, fontFamily: "'Rajdhani', sans-serif" }}>
                    {format(v1)}
                  </span>
                  <span className="text-[9px] font-bold uppercase tracking-wider" style={{ color: COLORS.text.tertiary }}>{label}</span>
                  <span className={`text-xs font-bold ${w2 ? '' : 'opacity-60'}`}
                    style={{ color: w2 ? color2 : COLORS.text.secondary, fontFamily: "'Rajdhani', sans-serif" }}>
                    {format(v2)}
                  </span>
                </div>
                <AnimatedBar val1={v1} val2={v2} color1={color1} color2={color2} animate={animate} />
              </div>
            );
          })}
        </div>
      )}

      {/* Empty state */}
      {(!p1 || !p2) && (
        <div className="text-center py-4 rounded-xl" style={{ background: COLORS.background.card }}>
          <Swords size={20} color={COLORS.text.tertiary} className="mx-auto mb-2 opacity-40" />
          <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>
            Select two players to compare stats
          </div>
        </div>
      )}
    </div>
  );
}
