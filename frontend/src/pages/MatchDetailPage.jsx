import { useState, useEffect, useCallback } from 'react';
import apiClient from '../api/client';
import { COLORS } from '../constants/design';
import { getTeamLogo, getTeamGradient, getTeamCardImage } from '../constants/teams';
import { ArrowLeft, Clock, MapPin, Trophy, Users, ChevronRight, Loader2, Check, Coins, Swords, BarChart3, User2, Lock, Unlock, Radio, X } from 'lucide-react';
import ScorecardView from '../components/ScorecardView';

const getGrad = (s) => getTeamGradient(s);

const ROLE_COLORS = {
  'Batsman': '#E53E3E', 'Bowler': '#3182CE', 'WK-Batsman': '#38A169',
  'Batting Allrounder': '#D69300', 'Bowling Allrounder': '#805AD5',
};

const TABS = [
  { key: 'contests', label: 'Contests', icon: Trophy },
  { key: 'live', label: 'Live', icon: Radio },
  { key: 'scorecard', label: 'Scorecard', icon: BarChart3 },
  { key: 'squad', label: 'Squad', icon: Users },
  { key: 'fantasy', label: 'Fantasy Pts', icon: Swords },
];

export default function MatchDetailPage({ match, onBack, onJoinContest, onOpenPrediction, onOpenLeaderboard }) {
  const [activeTab, setActiveTab] = useState('contests');
  const [contests, setContests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [joiningId, setJoiningId] = useState(null);
  const [joinedIds, setJoinedIds] = useState(new Set());
  const [joinError, setJoinError] = useState('');
  const [matchInfo, setMatchInfo] = useState(null);

  // Squad state
  const [squad, setSquad] = useState([]);
  const [squadLoading, setSquadLoading] = useState(false);

  // Fantasy points state
  const [fantasyData, setFantasyData] = useState(null);
  const [fantasyLoading, setFantasyLoading] = useState(false);

  // Scorecard state
  const [scorecardData, setScorecardData] = useState(null);
  const [scorecardLoading, setScorecardLoading] = useState(false);

  // Ball-by-ball + Deadline state
  const [bbbData, setBbbData] = useState(null);
  const [bbbLoading, setBbbLoading] = useState(false);
  const [deadlines, setDeadlines] = useState([]);

  // Player profile modal
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [playerProfile, setPlayerProfile] = useState(null);
  const [profileLoading, setProfileLoading] = useState(false);

  const fetchContests = useCallback(async () => {
    try {
      const res = await apiClient.get(`/matches/${match.id}/contests`);
      setContests(res.data.contests || []);
      try {
        const myRes = await apiClient.get('/contests/user/my-contests?limit=50');
        const myContestIds = new Set(
          (myRes.data.my_contests || []).map(mc => mc.entry?.contest_id).filter(Boolean)
        );
        setJoinedIds(myContestIds);
      } catch (_) {}
    } catch (_) {}
    finally { setLoading(false); }
  }, [match?.id]);

  const fetchMatchInfo = useCallback(async () => {
    try {
      const res = await apiClient.get(`/matches/${match.id}/match-info`);
      if (!res.data.error) setMatchInfo(res.data);
    } catch (_) {}
  }, [match?.id]);

  useEffect(() => {
    if (match?.id) {
      fetchContests();
      fetchMatchInfo();
      // Fetch template deadlines
      apiClient.get(`/matches/${match.id}/template-deadlines`)
        .then(res => setDeadlines(res.data.templates || []))
        .catch(() => {});
    }
  }, [match?.id, fetchContests, fetchMatchInfo]);

  // Lazy load tabs
  useEffect(() => {
    if (activeTab === 'squad' && squad.length === 0 && !squadLoading) {
      setSquadLoading(true);
      apiClient.get(`/matches/${match.id}/squad`)
        .then(res => setSquad(res.data.squads || []))
        .catch(() => {})
        .finally(() => setSquadLoading(false));
    }
    if (activeTab === 'fantasy' && !fantasyData && !fantasyLoading) {
      setFantasyLoading(true);
      apiClient.get(`/matches/${match.id}/fantasy-points`)
        .then(res => setFantasyData(res.data))
        .catch(() => {})
        .finally(() => setFantasyLoading(false));
    }
    if (activeTab === 'scorecard' && !scorecardData && !scorecardLoading) {
      setScorecardLoading(true);
      apiClient.get(`/matches/${match.id}/scorecard`)
        .then(res => setScorecardData(res.data))
        .catch(() => {})
        .finally(() => setScorecardLoading(false));
    }
    if (activeTab === 'live' && !bbbData && !bbbLoading) {
      setBbbLoading(true);
      // Load both: AI commentary + scorecard for fallback
      Promise.allSettled([
        apiClient.get(`/matches/${match.id}/ai-commentary`),
        apiClient.get(`/matches/${match.id}/scorecard`),
      ]).then(([aiRes, scRes]) => {
        const aiData = aiRes.status === 'fulfilled' ? aiRes.value.data : null;
        const scData = scRes.status === 'fulfilled' ? scRes.value.data : null;
        setBbbData({ ai: aiData, scorecard: scData });
        if (scData && !scorecardData) setScorecardData(scData);
      }).finally(() => setBbbLoading(false));
    }
  }, [activeTab, match?.id, squad, fantasyData, scorecardData, bbbData, squadLoading, fantasyLoading, scorecardLoading, bbbLoading]);

  const openPlayerProfile = async (playerId) => {
    if (!playerId) return;
    setSelectedPlayer(playerId);
    setProfileLoading(true);
    try {
      const res = await apiClient.get(`/cricket/player/${playerId}`);
      setPlayerProfile(res.data);
    } catch (_) {}
    finally { setProfileLoading(false); }
  };

  const handleJoin = async (contestId) => {
    setJoiningId(contestId);
    setJoinError('');
    try {
      await apiClient.post(`/contests/${contestId}/join`, { team_name: `Team_${Date.now().toString(36)}` });
      setJoinedIds(prev => new Set([...prev, contestId]));
      onJoinContest?.(contestId);
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.message || 'Join failed';
      if (msg.includes('Already joined')) {
        setJoinedIds(prev => new Set([...prev, contestId]));
        onOpenPrediction?.(contestId);
      } else { setJoinError(msg); }
    } finally { setJoiningId(null); }
  };

  const teamA = match?.team_a || {};
  const teamB = match?.team_b || {};
  const isLive = match?.status === 'live';
  const isCompleted = match?.status === 'completed';
  const score = match?.live_score;
  const getGradLocal = (s) => getTeamGradient(s);

  return (
    <div data-testid="match-detail-page" className="pb-6 space-y-4">
      <button data-testid="match-back-btn" onClick={onBack} className="flex items-center gap-2 text-sm" style={{ color: COLORS.text.secondary }}>
        <ArrowLeft size={16} /> Back
      </button>

      {/* Match Hero Card */}
      <div className="rounded-2xl overflow-hidden" style={{ background: COLORS.background.card, border: `1px solid ${isLive ? COLORS.primary.main + '44' : COLORS.border.light}` }}>
        <div className="px-4 py-3 flex items-center justify-between" style={{ background: isLive ? `${COLORS.primary.main}15` : COLORS.background.tertiary }}>
          <span className="text-xs font-medium" style={{ color: COLORS.text.secondary }}>{match?.tournament || 'IPL 2026'}</span>
          {isLive && <span className="px-2 py-0.5 rounded text-xs font-bold text-white animate-pulse" style={{ background: COLORS.primary.main }}>LIVE</span>}
          {isCompleted && <span className="px-2 py-0.5 rounded text-xs font-bold" style={{ color: COLORS.text.tertiary, background: COLORS.background.tertiary }}>COMPLETED</span>}
        </div>
        <div className="px-6 py-5 flex items-center justify-between">
          <div className="flex flex-col items-center gap-2 flex-1">
            <div className="w-16 h-16 rounded-2xl flex items-center justify-center text-lg font-black text-white shadow-lg overflow-hidden" style={{ background: getGrad(teamA.short_name) }}>
              {getTeamLogo(teamA.short_name) ? <img src={getTeamLogo(teamA.short_name)} alt={teamA.short_name} className="w-12 h-12 object-contain" /> : teamA.short_name || '?'}
            </div>
            <div className="text-center">
              <div className="text-sm font-bold text-white">{teamA.short_name}</div>
              <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>{teamA.name}</div>
              {(isLive || isCompleted) && score?.scores?.[0] && (
                <div className="text-base font-bold mt-0.5" style={{ color: COLORS.primary.main, fontFamily: "'Rajdhani', sans-serif" }}>
                  {score.scores[0].runs}/{score.scores[0].wickets} ({score.scores[0].overs})
                </div>
              )}
            </div>
          </div>
          <div className="flex flex-col items-center">
            <div className="text-xs font-bold px-3 py-1 rounded-lg" style={{ background: `${COLORS.primary.main}22`, color: COLORS.primary.main }}>VS</div>
          </div>
          <div className="flex flex-col items-center gap-2 flex-1">
            <div className="w-16 h-16 rounded-2xl flex items-center justify-center text-lg font-black text-white shadow-lg overflow-hidden" style={{ background: getGrad(teamB.short_name) }}>
              {getTeamLogo(teamB.short_name) ? <img src={getTeamLogo(teamB.short_name)} alt={teamB.short_name} className="w-12 h-12 object-contain" /> : teamB.short_name || '?'}
            </div>
            <div className="text-center">
              <div className="text-sm font-bold text-white">{teamB.short_name}</div>
              <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>{teamB.name}</div>
              {(isLive || isCompleted) && score?.scores?.[1] && (
                <div className="text-base font-bold mt-0.5" style={{ color: COLORS.primary.main, fontFamily: "'Rajdhani', sans-serif" }}>
                  {score.scores[1].runs}/{score.scores[1].wickets} ({score.scores[1].overs})
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Toss + Status Info */}
        <div className="px-4 py-2.5 flex items-center justify-around text-center" style={{ borderTop: `1px solid ${COLORS.border.light}`, background: COLORS.background.tertiary }}>
          {matchInfo?.toss_winner ? (
            <div className="flex items-center gap-1.5">
              <Coins size={12} color={COLORS.accent.gold} />
              <span className="text-[10px]" style={{ color: COLORS.text.secondary }}>
                Toss: <b style={{ color: COLORS.accent.gold }}>{matchInfo.toss_winner}</b> chose to <b>{matchInfo.toss_choice}</b>
              </span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5">
              <MapPin size={12} color={COLORS.text.tertiary} />
              <span className="text-[10px]" style={{ color: COLORS.text.secondary }}>{match?.venue || 'TBD'}</span>
            </div>
          )}
          <div className="flex items-center gap-1.5">
            <Clock size={12} color={COLORS.warning.main} />
            <span className="text-[10px]" style={{ color: COLORS.warning.main }}>
              {isLive ? 'In Progress' : isCompleted ? matchInfo?.status || 'Completed' : new Date(match?.start_time).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
        </div>
      </div>

      {/* Tab Bar */}
      <div className="flex rounded-xl overflow-hidden" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
        {TABS.map(tab => {
          const Icon = tab.icon;
          const active = activeTab === tab.key;
          return (
            <button key={tab.key} data-testid={`tab-${tab.key}`} onClick={() => setActiveTab(tab.key)}
              className="flex-1 flex items-center justify-center gap-1.5 py-2.5 text-[11px] font-semibold transition-all"
              style={{
                color: active ? COLORS.primary.main : COLORS.text.tertiary,
                background: active ? `${COLORS.primary.main}15` : 'transparent',
                borderBottom: active ? `2px solid ${COLORS.primary.main}` : '2px solid transparent'
              }}>
              <Icon size={14} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {joinError && (
        <div data-testid="join-error" className="text-center text-sm py-2.5 px-3 rounded-xl" style={{ background: COLORS.error.bg, color: COLORS.error.main }}>
          {joinError}
        </div>
      )}

      {/* Tab Content */}
      {activeTab === 'contests' && <ContestsTab contests={contests} loading={loading} joinedIds={joinedIds} joiningId={joiningId} onJoin={handleJoin} onOpenPrediction={onOpenPrediction} onOpenLeaderboard={onOpenLeaderboard} deadlines={deadlines} />}
      {activeTab === 'live' && <LiveTab data={bbbData} loading={bbbLoading} />}
      {activeTab === 'scorecard' && <ScorecardTab data={scorecardData} loading={scorecardLoading} />}
      {activeTab === 'squad' && <SquadTab squads={squad} loading={squadLoading} onPlayerClick={openPlayerProfile} />}
      {activeTab === 'fantasy' && <FantasyPointsTab data={fantasyData} loading={fantasyLoading} onPlayerClick={openPlayerProfile} />}

      {/* Player Profile Modal */}
      {selectedPlayer && (
        <PlayerProfileModal
          player={playerProfile}
          loading={profileLoading}
          onClose={() => { setSelectedPlayer(null); setPlayerProfile(null); }}
        />
      )}
    </div>
  );
}


// ========== CONTESTS TAB ==========
function ContestsTab({ contests, loading, joinedIds, joiningId, onJoin, onOpenPrediction, onOpenLeaderboard, deadlines }) {
  if (loading) return <LoadingSpinner />;
  
  return (
    <div className="space-y-3">
      {/* Template Deadline Status */}
      {deadlines.length > 0 && (
        <div data-testid="deadline-status" className="space-y-1.5">
          <div className="text-[10px] font-bold uppercase tracking-wider" style={{ color: COLORS.text.tertiary }}>Template Status</div>
          {deadlines.map(d => (
            <div key={d.template_id} className="flex items-center justify-between px-3 py-2 rounded-lg"
              style={{ background: COLORS.background.card, border: `1px solid ${d.is_locked ? COLORS.error.main + '33' : COLORS.success.main + '33'}` }}>
              <div className="flex items-center gap-2">
                {d.is_locked ? <Lock size={12} color={COLORS.error.main} /> : <Unlock size={12} color={COLORS.success.main} />}
                <span className="text-xs font-semibold text-white">{d.phase_label || d.template_type}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[10px]" style={{ color: COLORS.text.tertiary }}>
                  Deadline: Inn {d.deadline_innings} Ov {d.deadline_over}
                </span>
                <span className="text-[9px] px-1.5 py-0.5 rounded font-bold"
                  style={{ background: d.is_locked ? COLORS.error.bg : COLORS.success.bg, color: d.is_locked ? COLORS.error.main : COLORS.success.main }}>
                  {d.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {!contests.length && (
        <div className="text-center py-8 rounded-2xl" style={{ background: COLORS.background.card }}>
          <Trophy size={32} color={COLORS.text.tertiary} className="mx-auto mb-2" />
          <p className="text-sm" style={{ color: COLORS.text.secondary }}>No contests yet</p>
        </div>
      )}
      {contests.map(c => {
        const isJoined = joinedIds.has(c.id);
        const isJoining = joiningId === c.id;
        const done = c.status === 'completed';
        return (
          <div key={c.id} data-testid={`contest-${c.id}`} className="p-4 rounded-xl" style={{ background: COLORS.background.card, border: `1px solid ${isJoined ? COLORS.success.main + '33' : COLORS.border.light}` }}>
            <div className="flex items-center justify-between">
              <div className="flex-1 min-w-0">
                <div className="text-sm font-semibold text-white">{c.name}</div>
                <div className="flex items-center gap-3 mt-1">
                  <span className="flex items-center gap-1 text-xs" style={{ color: COLORS.text.secondary }}>
                    <Coins size={11} color="#FFD700" /> {c.entry_fee}
                  </span>
                  <span className="text-xs" style={{ color: COLORS.accent.gold }}>Pool: {(c.prize_pool || c.entry_fee * (c.current_participants || 0)).toLocaleString()}</span>
                </div>
                <div className="flex items-center gap-1 mt-1">
                  <Users size={12} color={COLORS.info.main} />
                  <span className="text-xs" style={{ color: COLORS.text.tertiary }}>{c.current_participants || 0}/{c.max_participants || 0}</span>
                  <span className="text-xs font-medium ml-2 px-1.5 py-0.5 rounded" style={{ color: c.status === 'open' ? COLORS.success.main : COLORS.text.tertiary, background: c.status === 'open' ? COLORS.success.bg : COLORS.background.tertiary }}>{c.status?.toUpperCase()}</span>
                </div>
              </div>
              <div className="ml-3 shrink-0">
                {done ? (
                  <button data-testid={`leaderboard-btn-${c.id}`} onClick={() => onOpenLeaderboard?.(c.id)}
                    className="px-4 py-2.5 rounded-xl text-xs font-bold flex items-center gap-1" style={{ background: COLORS.background.tertiary, color: COLORS.accent.gold, border: `1px solid ${COLORS.accent.gold}33` }}>
                    <Trophy size={13} /> Results
                  </button>
                ) : isJoined ? (
                  <button data-testid={`predict-btn-${c.id}`} onClick={() => onOpenPrediction?.(c.id)}
                    className="px-4 py-2.5 rounded-xl text-xs font-bold flex items-center gap-1" style={{ background: COLORS.success.bg, color: COLORS.success.main, border: `1px solid ${COLORS.success.main}33` }}>
                    <Check size={13} /> Predict
                  </button>
                ) : (
                  <button data-testid={`join-btn-${c.id}`} onClick={() => onJoin(c.id)}
                    disabled={isJoining || c.status !== 'open'}
                    className="px-4 py-2.5 rounded-xl text-xs font-bold flex items-center gap-1 disabled:opacity-50" style={{ background: COLORS.primary.gradient, color: '#fff' }}>
                    {isJoining ? <Loader2 size={13} className="animate-spin" /> : null}
                    {isJoining ? 'Joining...' : 'Join'} {!isJoining && <ChevronRight size={13} />}
                  </button>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}


// ========== SCORECARD TAB ==========
function ScorecardTab({ data, loading }) {
  if (loading) return <LoadingSpinner />;
  if (!data || data.error || !data.scorecard?.length) return (
    <div className="text-center py-10 rounded-2xl" style={{ background: COLORS.background.card }}>
      <BarChart3 size={32} color={COLORS.text.tertiary} className="mx-auto mb-2" />
      <p className="text-sm" style={{ color: COLORS.text.secondary }}>Scorecard not available yet</p>
      <p className="text-xs mt-1" style={{ color: COLORS.text.tertiary }}>Available after match starts</p>
    </div>
  );
  return <ScorecardView data={data} />;
}


// ========== SQUAD TAB ==========
function SquadTab({ squads, loading, onPlayerClick }) {
  const [activeTeam, setActiveTeam] = useState(0);
  if (loading) return <LoadingSpinner />;
  if (!squads.length) return (
    <div className="text-center py-10 rounded-2xl" style={{ background: COLORS.background.card }}>
      <Users size={32} color={COLORS.text.tertiary} className="mx-auto mb-2" />
      <p className="text-sm" style={{ color: COLORS.text.secondary }}>Squad not available</p>
    </div>
  );

  const team = squads[activeTeam] || {};
  const players = team.players || [];

  // Group by role
  const batters = players.filter(p => p.role === 'Batsman');
  const allrounders = players.filter(p => p.role?.includes('Allrounder'));
  const bowlers = players.filter(p => p.role === 'Bowler');
  const wkBatters = players.filter(p => p.role === 'WK-Batsman');
  const others = players.filter(p => !['Batsman', 'Bowler', 'WK-Batsman'].includes(p.role) && !p.role?.includes('Allrounder'));

  return (
    <div className="space-y-3">
      {/* Team Selector */}
      <div className="flex rounded-xl overflow-hidden" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
        {squads.map((t, i) => (
          <button key={i} data-testid={`squad-team-${i}`} onClick={() => setActiveTeam(i)}
            className="flex-1 py-2.5 text-xs font-bold text-center transition-all"
            style={{ color: activeTeam === i ? '#fff' : COLORS.text.tertiary, background: activeTeam === i ? COLORS.primary.main : 'transparent' }}>
            {t.shortname || t.teamName?.split(' ')[0]}
            <span className="text-[9px] ml-1 opacity-70">({(t.players || []).length})</span>
          </button>
        ))}
      </div>

      {/* Players by Role */}
      {[{ label: 'Wicket-Keepers', players: wkBatters }, { label: 'Batters', players: batters }, { label: 'All-Rounders', players: allrounders }, { label: 'Bowlers', players: bowlers }, { label: 'Others', players: others }]
        .filter(g => g.players.length > 0)
        .map(group => (
          <div key={group.label}>
            <div className="text-[10px] font-bold mb-1.5 uppercase tracking-wider" style={{ color: COLORS.text.tertiary }}>{group.label}</div>
            <div className="rounded-xl overflow-hidden" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
              {group.players.map((p, i) => (
                <div key={p.id || i} data-testid={`player-${p.id}`}
                  className="flex items-center gap-3 px-3 py-2.5 cursor-pointer hover:opacity-80 transition-opacity"
                  onClick={() => onPlayerClick?.(p.id)}
                  style={{ borderBottom: i < group.players.length - 1 ? `1px solid ${COLORS.border.light}` : 'none' }}>
                  <div className="w-9 h-9 rounded-full overflow-hidden shrink-0 flex items-center justify-center" style={{ background: COLORS.background.tertiary }}>
                    {p.playerImg && !p.playerImg.includes('icon512') ? (
                      <img src={p.playerImg} alt={p.name} className="w-full h-full object-cover" onError={e => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'flex'; }} />
                    ) : null}
                    <User2 size={16} color={COLORS.text.tertiary} style={{ display: p.playerImg && !p.playerImg.includes('icon512') ? 'none' : 'block' }} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-xs font-semibold text-white truncate">{p.name}</div>
                    <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>
                      {p.battingStyle || ''}{p.bowlingStyle ? ` | ${p.bowlingStyle}` : ''}
                    </div>
                  </div>
                  <div className="px-2 py-0.5 rounded text-[9px] font-bold shrink-0"
                    style={{ background: (ROLE_COLORS[p.role] || '#666') + '18', color: ROLE_COLORS[p.role] || '#888' }}>
                    {p.role === 'WK-Batsman' ? 'WK' : p.role === 'Batting Allrounder' ? 'BAT AR' : p.role === 'Bowling Allrounder' ? 'BWL AR' : p.role || '?'}
                  </div>
                  <span className="text-[9px]" style={{ color: COLORS.text.tertiary }}>{p.country}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
    </div>
  );
}


// ========== FANTASY POINTS TAB ==========
function FantasyPointsTab({ data, loading, onPlayerClick }) {
  const [view, setView] = useState('totals');
  if (loading) return <LoadingSpinner />;
  if (!data || data.error || (!data.totals?.length && !data.innings?.length)) return (
    <div className="text-center py-10 rounded-2xl" style={{ background: COLORS.background.card }}>
      <Swords size={32} color={COLORS.text.tertiary} className="mx-auto mb-2" />
      <p className="text-sm" style={{ color: COLORS.text.secondary }}>Fantasy points not available</p>
      <p className="text-xs mt-1" style={{ color: COLORS.text.tertiary }}>Available after match starts</p>
    </div>
  );

  const innings = data.innings || [];
  const totals = data.totals || [];

  return (
    <div className="space-y-3">
      {/* View Toggle */}
      <div className="flex rounded-xl overflow-hidden" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
        <button onClick={() => setView('totals')} className="flex-1 py-2 text-xs font-bold"
          style={{ color: view === 'totals' ? '#fff' : COLORS.text.tertiary, background: view === 'totals' ? COLORS.primary.main : 'transparent' }}>
          Top Performers
        </button>
        {innings.map((inn, i) => (
          <button key={i} onClick={() => setView(`inn_${i}`)} className="flex-1 py-2 text-[10px] font-bold"
            style={{ color: view === `inn_${i}` ? '#fff' : COLORS.text.tertiary, background: view === `inn_${i}` ? COLORS.primary.main : 'transparent' }}>
            {(inn.inning || `Inning ${i + 1}`).replace(/ Inning /, ' Inn ')}
          </button>
        ))}
      </div>

      {/* Totals View */}
      {view === 'totals' && (
        <div className="rounded-xl overflow-hidden" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
          {totals.slice(0, 15).map((p, i) => (
            <div key={p.id || i} className="flex items-center gap-3 px-3 py-2.5"
              style={{ borderBottom: i < Math.min(totals.length, 15) - 1 ? `1px solid ${COLORS.border.light}` : 'none',
                background: i < 3 ? `${COLORS.accent.gold}08` : 'transparent' }}>
              <div className="w-6 text-center text-xs font-bold" style={{ color: i < 3 ? COLORS.accent.gold : COLORS.text.tertiary }}>
                {i + 1}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-xs font-semibold text-white truncate">{p.name}</div>
              </div>
              <div className="text-sm font-bold" style={{ color: (p.points || 0) >= 0 ? COLORS.success.main : COLORS.error.main, fontFamily: "'Rajdhani', sans-serif" }}>
                {p.points}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Innings Views */}
      {innings.map((inn, idx) => view === `inn_${idx}` && (
        <div key={idx} className="space-y-2">
          {[{ label: 'Batting', data: inn.batting || [] }, { label: 'Bowling', data: inn.bowling || [] }, { label: 'Catching', data: inn.catching || [] }]
            .filter(sec => sec.data.length > 0)
            .map(sec => (
              <div key={sec.label}>
                <div className="text-[10px] font-bold mb-1 uppercase tracking-wider" style={{ color: COLORS.text.tertiary }}>{sec.label}</div>
                <div className="rounded-xl overflow-hidden" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
                  {sec.data.map((p, i) => (
                    <div key={p.id || i} className="flex items-center justify-between px-3 py-2"
                      style={{ borderBottom: i < sec.data.length - 1 ? `1px solid ${COLORS.border.light}` : 'none' }}>
                      <span className="text-xs text-white truncate">{p.name}</span>
                      <span className="text-xs font-bold" style={{ color: (p.points || 0) >= 0 ? COLORS.success.main : COLORS.error.main }}>
                        {p.points} pts
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
        </div>
      ))}
    </div>
  );
}


// ========== LIVE TAB (AI-Powered Commentary) ==========
function LiveTab({ data, loading }) {
  if (loading) return <LoadingSpinner />;

  const aiCommentary = data?.ai?.commentary || [];
  const scorecard = data?.scorecard?.scorecard || [];

  // If AI commentary available, show it beautifully
  if (aiCommentary.length > 0) {
    return (
      <div className="space-y-2">
        <div className="flex items-center gap-2 mb-1">
          <Radio size={14} className="animate-pulse" color={COLORS.primary.main} />
          <span className="text-xs font-bold" style={{ color: COLORS.primary.main }}>AI COMMENTARY</span>
        </div>
        {aiCommentary.map((item, i) => {
          const colors = {
            six: { bg: '#F59E0B15', border: '#F59E0B44', accent: '#F59E0B' },
            four: { bg: '#3B82F615', border: '#3B82F644', accent: '#3B82F6' },
            wicket: { bg: '#EF444415', border: '#EF444444', accent: '#EF4444' },
            milestone: { bg: '#10B98115', border: '#10B98144', accent: '#10B981' },
            bowling: { bg: '#8B5CF615', border: '#8B5CF644', accent: '#8B5CF6' },
            result: { bg: '#F59E0B20', border: '#F59E0B66', accent: '#FFD700' },
            header: { bg: COLORS.background.tertiary, border: COLORS.border.light, accent: COLORS.text.secondary },
            general: { bg: COLORS.background.card, border: COLORS.border.light, accent: COLORS.text.secondary },
          };
          const c = colors[item.type] || colors.general;
          const isHighlight = ['six', 'wicket', 'milestone', 'result'].includes(item.type);

          return (
            <div key={i} className={`px-3 py-2.5 rounded-xl transition-all ${isHighlight ? 'animate-[slideUp_0.3s_ease]' : ''}`}
              style={{
                background: c.bg,
                border: `1px solid ${c.border}`,
                animationDelay: `${i * 0.05}s`,
                animationFillMode: 'backwards',
              }}>
              <p className="text-xs leading-relaxed" style={{ color: isHighlight ? '#fff' : COLORS.text.secondary }}>
                {item.text}
              </p>
            </div>
          );
        })}
      </div>
    );
  }

  // Fallback: Build from scorecard
  if (scorecard.length > 0) {
    const items = [];
    for (let idx = 0; idx < scorecard.length; idx++) {
      const inn = scorecard[idx];
      const batting = inn?.batting || [];
      const bowling = inn?.bowling || [];
      items.push({ type: 'header', text: `🏏 ${inn?.inning || `Innings ${idx + 1}`}` });

      for (const b of batting) {
        const runs = parseInt(b.r) || 0;
        const sixes = parseInt(b['6s']) || 0;
        const fours = parseInt(b['4s']) || 0;
        const balls = parseInt(b.b) || 0;

        if (runs >= 100) items.push({ type: 'milestone', text: `💯 CENTURY! ${b.batsman} smashes ${runs} off ${balls}! (${fours}x4 ${sixes}x6)` });
        else if (runs >= 50) items.push({ type: 'milestone', text: `⭐ FIFTY! ${b.batsman} scores ${runs}(${balls}) with ${fours} fours!` });
        if (sixes >= 3) items.push({ type: 'six', text: `🔥 ${b.batsman} hammers ${sixes} MASSIVE SIXES!` });
        if (b.dismissal && b.dismissal !== 'not out') items.push({ type: 'wicket', text: `❌ OUT! ${b.batsman} ${runs}(${balls}) — ${b.dismissal}` });
      }

      for (const bw of bowling) {
        if ((parseInt(bw.w) || 0) >= 3) items.push({ type: 'bowling', text: `🎯 ${bw.bowler} destroys with ${bw.w}/${bw.r} in ${bw.o} overs!` });
      }
    }

    return (
      <div className="space-y-2">
        <div className="flex items-center gap-2 mb-1">
          <Radio size={14} color={COLORS.text.tertiary} />
          <span className="text-xs font-bold" style={{ color: COLORS.text.tertiary }}>MATCH HIGHLIGHTS</span>
        </div>
        {items.map((item, i) => {
          const isHeader = item.type === 'header';
          const c = item.type === 'wicket' ? '#EF4444' : item.type === 'six' ? '#F59E0B' : item.type === 'milestone' ? '#10B981' : item.type === 'bowling' ? '#8B5CF6' : COLORS.text.secondary;
          return (
            <div key={i} className={isHeader ? 'mt-3' : ''}>
              {isHeader ? (
                <div className="text-[10px] font-bold uppercase tracking-wider" style={{ color: COLORS.primary.main }}>{item.text}</div>
              ) : (
                <div className="px-3 py-2 rounded-xl" style={{ background: `${c}12`, border: `1px solid ${c}33` }}>
                  <p className="text-xs" style={{ color: '#fff' }}>{item.text}</p>
                </div>
              )}
            </div>
          );
        })}
      </div>
    );
  }

  return (
    <div className="text-center py-10 rounded-2xl" style={{ background: COLORS.background.card }}>
      <Radio size={32} color={COLORS.text.tertiary} className="mx-auto mb-2" />
      <p className="text-sm" style={{ color: COLORS.text.secondary }}>Commentary available after match starts</p>
    </div>
  );
}


// ========== PLAYER PROFILE MODAL ==========
function PlayerProfileModal({ player, loading, onClose }) {
  if (!player && !loading) return null;

  const p = player?.player || {};
  const stats = player?.stats || [];

  // Group stats by format
  const formats = {};
  for (const s of stats) {
    const fmt = s.matchtype || 'Other';
    if (!formats[fmt]) formats[fmt] = [];
    formats[fmt].push(s);
  }

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center" style={{ background: 'rgba(0,0,0,0.6)' }}
      onClick={onClose}>
      <div className="w-full max-w-lg max-h-[80vh] overflow-y-auto rounded-t-3xl p-5 space-y-4"
        style={{ background: COLORS.background.primary, animation: 'slideUp 0.3s ease' }}
        onClick={e => e.stopPropagation()}>

        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-white">Player Profile</h3>
          <button onClick={onClose} className="p-1 rounded-full" style={{ background: COLORS.background.tertiary }}>
            <X size={16} color={COLORS.text.secondary} />
          </button>
        </div>

        {loading ? <LoadingSpinner /> : !p.name ? (
          <p className="text-sm text-center py-4" style={{ color: COLORS.text.secondary }}>Profile not available</p>
        ) : (
          <>
            {/* Player Header */}
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-2xl overflow-hidden shrink-0" style={{ background: COLORS.background.tertiary }}>
                {p.playerImg && !p.playerImg.includes('icon512') && (
                  <img src={p.playerImg} alt={p.name} className="w-full h-full object-cover" />
                )}
              </div>
              <div>
                <div className="text-lg font-bold text-white">{p.name}</div>
                <div className="text-xs" style={{ color: COLORS.text.secondary }}>{p.role} | {p.country}</div>
                <div className="text-[10px] mt-0.5" style={{ color: COLORS.text.tertiary }}>
                  {p.battingStyle}{p.bowlingStyle ? ` | ${p.bowlingStyle}` : ''}
                </div>
                {p.placeOfBirth && <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>Born: {p.placeOfBirth}</div>}
              </div>
            </div>

            {/* Stats by Format */}
            {Object.entries(formats).map(([fmt, fmtStats]) => (
              <div key={fmt}>
                <div className="text-[10px] font-bold uppercase tracking-wider mb-1" style={{ color: COLORS.primary.main }}>{fmt}</div>
                <div className="rounded-xl overflow-hidden" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
                  {fmtStats.map((s, i) => (
                    <div key={i} className="flex items-center justify-between px-3 py-1.5"
                      style={{ borderBottom: i < fmtStats.length - 1 ? `1px solid ${COLORS.border.light}` : 'none' }}>
                      <span className="text-xs" style={{ color: COLORS.text.secondary }}>{s.fn}</span>
                      <span className="text-xs font-semibold text-white">{s.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
}


function LoadingSpinner() {
  return (
    <div className="flex justify-center py-10">
      <div className="w-7 h-7 border-2 rounded-full animate-spin" style={{ borderColor: `${COLORS.primary.main}30`, borderTopColor: COLORS.primary.main }} />
    </div>
  );
}
