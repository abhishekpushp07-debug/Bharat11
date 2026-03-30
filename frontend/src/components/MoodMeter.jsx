import { useState, useEffect, useCallback } from 'react';
import apiClient from '../api/client';
import { COLORS } from '../constants/design';
import { getTeamLogo, getTeamGradient } from '../constants/teams';

export default function MoodMeter({ matchId, teamA, teamB, compact = false }) {
  const [data, setData] = useState(null);
  const [voting, setVoting] = useState(false);
  const [justVoted, setJustVoted] = useState(null);

  const fetchMood = useCallback(async () => {
    try {
      const res = await apiClient.get(`/matches/${matchId}/mood-meter`);
      setData(res.data);
    } catch (_) {}
  }, [matchId]);

  useEffect(() => { fetchMood(); }, [fetchMood]);

  const vote = async (team) => {
    if (voting) return;
    setVoting(true);
    setJustVoted(team);
    try {
      const res = await apiClient.post(`/matches/${matchId}/mood-vote`, { team });
      setData(res.data);
    } catch (_) {}
    finally {
      setVoting(false);
      setTimeout(() => setJustVoted(null), 600);
    }
  };

  if (!data && !teamA?.short_name) return null;

  const aShort = data?.team_a || teamA?.short_name || '?';
  const bShort = data?.team_b || teamB?.short_name || '?';
  const aPct = data?.team_a_pct || 50;
  const bPct = data?.team_b_pct || 50;
  const total = data?.total_votes || 0;
  const userVote = data?.user_vote || data?.your_vote;
  const hasVoted = !!userVote;

  const aColor = getTeamGradient(aShort) || 'linear-gradient(135deg, #3B82F6, #1D4ED8)';
  const bColor = getTeamGradient(bShort) || 'linear-gradient(135deg, #EF4444, #B91C1C)';

  if (compact) {
    return (
      <div data-testid="mood-meter-compact" className="flex items-center gap-2">
        <span className="text-[10px] font-bold" style={{ color: '#fff' }}>{aShort}</span>
        <div className="flex-1 h-2 rounded-full overflow-hidden flex" style={{ background: 'rgba(255,255,255,0.08)' }}>
          <div className="h-full transition-all duration-700 rounded-l-full" style={{ width: `${aPct}%`, background: aColor }} />
          <div className="h-full transition-all duration-700 rounded-r-full" style={{ width: `${bPct}%`, background: bColor }} />
        </div>
        <span className="text-[10px] font-bold" style={{ color: '#fff' }}>{bShort}</span>
      </div>
    );
  }

  return (
    <div data-testid="mood-meter" className="rounded-2xl overflow-hidden relative"
      style={{ background: '#0d1117', border: `1px solid rgba(255,255,255,0.06)` }}>

      {/* Header */}
      <div className="px-4 pt-3 pb-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full animate-live-pulse" style={{ background: '#10B981' }} />
          <span className="text-[9px] font-black tracking-[0.15em] uppercase" style={{ color: '#10B981' }}>MATCH MOOD</span>
        </div>
        <span className="text-[9px] font-semibold" style={{ color: 'rgba(255,255,255,0.3)' }}>
          {total} {total === 1 ? 'vote' : 'votes'}
        </span>
      </div>

      {/* Progress Bar */}
      <div className="px-4 pb-2">
        <div className="h-3 rounded-full overflow-hidden flex" style={{ background: 'rgba(255,255,255,0.06)' }}>
          <div className="h-full transition-all duration-700 ease-out flex items-center justify-end pr-1"
            style={{ width: `${Math.max(aPct, 5)}%`, background: aColor, borderRadius: aPct >= 95 ? '6px' : '6px 0 0 6px' }}>
            {aPct > 15 && <span className="text-[8px] font-black text-white drop-shadow">{aPct}%</span>}
          </div>
          <div className="h-full transition-all duration-700 ease-out flex items-center pl-1"
            style={{ width: `${Math.max(bPct, 5)}%`, background: bColor, borderRadius: bPct >= 95 ? '6px' : '0 6px 6px 0' }}>
            {bPct > 15 && <span className="text-[8px] font-black text-white drop-shadow">{bPct}%</span>}
          </div>
        </div>
      </div>

      {/* Vote Buttons */}
      <div className="px-4 pb-3 flex gap-2">
        <button data-testid="mood-vote-a" onClick={() => vote(aShort)} disabled={voting}
          className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-xs font-bold transition-all active:scale-95 ${justVoted === aShort ? 'animate-bounceIn' : ''}`}
          style={{
            background: userVote === aShort ? aColor : 'rgba(255,255,255,0.04)',
            color: userVote === aShort ? '#fff' : 'rgba(255,255,255,0.7)',
            border: userVote === aShort ? 'none' : '1px solid rgba(255,255,255,0.08)',
            boxShadow: userVote === aShort ? '0 4px 15px rgba(0,0,0,0.3)' : 'none',
          }}>
          <div className="w-6 h-6 rounded-lg overflow-hidden flex items-center justify-center shrink-0" style={{ background: 'rgba(255,255,255,0.1)' }}>
            {getTeamLogo(aShort) ? <img src={getTeamLogo(aShort)} alt="" className="w-5 h-5 object-contain" /> : <span className="text-[8px] font-bold">{aShort}</span>}
          </div>
          {aShort}
          {userVote === aShort && <span className="text-[8px] px-1 py-0.5 rounded bg-white/20">VOTED</span>}
        </button>

        <button data-testid="mood-vote-b" onClick={() => vote(bShort)} disabled={voting}
          className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-xs font-bold transition-all active:scale-95 ${justVoted === bShort ? 'animate-bounceIn' : ''}`}
          style={{
            background: userVote === bShort ? bColor : 'rgba(255,255,255,0.04)',
            color: userVote === bShort ? '#fff' : 'rgba(255,255,255,0.7)',
            border: userVote === bShort ? 'none' : '1px solid rgba(255,255,255,0.08)',
            boxShadow: userVote === bShort ? '0 4px 15px rgba(0,0,0,0.3)' : 'none',
          }}>
          <div className="w-6 h-6 rounded-lg overflow-hidden flex items-center justify-center shrink-0" style={{ background: 'rgba(255,255,255,0.1)' }}>
            {getTeamLogo(bShort) ? <img src={getTeamLogo(bShort)} alt="" className="w-5 h-5 object-contain" /> : <span className="text-[8px] font-bold">{bShort}</span>}
          </div>
          {bShort}
          {userVote === bShort && <span className="text-[8px] px-1 py-0.5 rounded bg-white/20">VOTED</span>}
        </button>
      </div>

      {/* Info text */}
      {!hasVoted && (
        <div className="px-4 pb-3 text-center">
          <span className="text-[9px]" style={{ color: 'rgba(255,255,255,0.25)' }}>Tap to vote — who's winning today?</span>
        </div>
      )}
    </div>
  );
}
