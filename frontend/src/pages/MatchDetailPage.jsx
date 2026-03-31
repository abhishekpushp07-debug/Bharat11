import { useState, useEffect, useCallback, useRef } from 'react';
import apiClient from '../api/client';
import { COLORS } from '../constants/design';
import { getTeamLogo, getTeamGradient, getTeamCardImage, TEAM_COLORS, normalizeTeam } from '../constants/teams';
import { ArrowLeft, Clock, MapPin, Trophy, Users, ChevronRight, Loader2, Check, Coins, Swords, BarChart3, User2, Lock, Unlock, Radio, X, RefreshCw } from 'lucide-react';
import ScorecardView from '../components/ScorecardView';
import MoodMeter from '../components/MoodMeter';
import AICommentaryTab from '../components/AICommentaryTab';
import { useSocketStore } from '../stores/socketStore';

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

export default function MatchDetailPage({ match, onBack, onJoinContest, onOpenPrediction, onOpenLeaderboard, onCelebrate }) {
  const [activeTab, setActiveTab] = useState('contests');
  const [contests, setContests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [joiningId, setJoiningId] = useState(null);
  const [joinedIds, setJoinedIds] = useState(new Set());
  const [joinError, setJoinError] = useState('');
  const [matchInfo, setMatchInfo] = useState(null);
  const [liveMatchData, setLiveMatchData] = useState(null);

  // Socket.IO for real-time match updates
  const { joinMatch, leaveMatch, on, off } = useSocketStore();

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
  const [lastUpdated, setLastUpdated] = useState(null);
  const [pollCount, setPollCount] = useState(0);

  // Last score tracking for auto-celebration detection
  const lastScoreRef = useRef(null);

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

  // ===== LIVE DATA POLLING (15s) =====
  // Fetches: scorecard, AI commentary, and detects events for celebrations
  const fetchLiveData = useCallback(async (forceAi = false) => {
    if (!match?.id) return;

    try {
      const aiUrl = forceAi
        ? `/matches/${match.id}/ai-commentary?force=true`
        : `/matches/${match.id}/ai-commentary`;

      const scUrl = forceAi
        ? `/matches/${match.id}/scorecard?force=true`
        : `/matches/${match.id}/scorecard`;

      const [scRes, aiRes] = await Promise.allSettled([
        apiClient.get(scUrl),
        apiClient.get(aiUrl),
      ]);

      const newScorecard = scRes.status === 'fulfilled' ? scRes.value.data : null;
      const newAi = aiRes.status === 'fulfilled' ? aiRes.value.data : null;

      // Update scorecard
      if (newScorecard && !newScorecard.error) {
        setScorecardData(newScorecard);
        setLastUpdated(new Date());
        setPollCount(c => c + 1);

        // ===== AUTO-CELEBRATION DETECTION =====
        const allInnings = newScorecard?.scorecard || [];
        let totalFours = 0, totalSixes = 0, totalWickets = 0;
        for (const inn of allInnings) {
          const batting = inn?.batting || [];
          for (const b of batting) {
            totalSixes += parseInt(b['6s']) || 0;
            totalFours += parseInt(b['4s']) || 0;
            if (b.dismissal && b.dismissal !== 'not out' && b.dismissal !== '') totalWickets++;
          }
        }

        const prevScore = lastScoreRef.current;
        if (prevScore) {
          if (totalWickets > prevScore.wickets) {
            onCelebrate?.('wicket');
          } else if (totalSixes > prevScore.sixes) {
            onCelebrate?.('six');
          } else if (totalFours > prevScore.fours) {
            onCelebrate?.('four');
          }
        }

        lastScoreRef.current = { wickets: totalWickets, sixes: totalSixes, fours: totalFours };
      }

      // Update AI commentary
      if (newAi || newScorecard) {
        setBbbData(prev => ({
          ai: newAi || prev?.ai,
          scorecard: newScorecard || prev?.scorecard,
        }));
        setBbbLoading(false);
      }
    } catch (err) {
      console.error('Live data fetch error:', err);
    }
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

  // ===== 15-SECOND POLLING for LIVE/OPEN matches =====
  useEffect(() => {
    if (!match?.id) return;
    const isMatchRunning = match?.status === 'live' || match?.status === 'open';
    if (!isMatchRunning) return;

    // Initial fetch immediately
    fetchLiveData();

    // Poll every 15 seconds for real-time experience
    const pollInterval = setInterval(() => fetchLiveData(), 15000);

    return () => clearInterval(pollInterval);
  }, [match?.id, match?.status, fetchLiveData]);

  // Update the "Updated Xs ago" display every 5 seconds
  useEffect(() => {
    if (!lastUpdated) return;
    const tick = setInterval(() => setLastUpdated(prev => prev ? new Date(prev.getTime()) : null), 5000);
    return () => clearInterval(tick);
  }, [lastUpdated]);


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

  // Socket.IO: Join match room for real-time updates
  useEffect(() => {
    if (!match?.id) return;
    joinMatch(match.id);

    const handleLiveScore = (data) => {
      if (data.match_id === match.id) {
        setLiveMatchData(data);
      }
    };

    const handleQuestionResolved = (data) => {
      if (data.match_id === match.id) {
        // Refresh contests to show updated question results
        fetchContests();
      }
    };

    const handleTemplateLocked = (data) => {
      if (data.match_id === match.id) {
        // Update deadlines to reflect locked template
        setDeadlines(prev => prev.map(d =>
          d.template_id === data.template_id ? { ...d, is_locked: true } : d
        ));
      }
    };

    on('live_score', handleLiveScore);
    on('question_resolved', handleQuestionResolved);
    on('template_locked', handleTemplateLocked);

    const handleCelebration = (data) => {
      if (data.match_id === match.id && data.event_type) {
        onCelebrate?.(data.event_type);
      }
    };
    on('celebration', handleCelebration);

    return () => {
      leaveMatch(match.id);
      off('live_score', handleLiveScore);
      off('question_resolved', handleQuestionResolved);
      off('template_locked', handleTemplateLocked);
      off('celebration', handleCelebration);
    };
  }, [match?.id, joinMatch, leaveMatch, on, off, fetchContests]);

  const handleJoin = async (contestId) => {
    setJoiningId(contestId);
    setJoinError('');
    try {
      await apiClient.post(`/contests/${contestId}/join`, { team_name: `Team_${Date.now().toString(36)}` });
      setJoinedIds(prev => new Set([...prev, contestId]));
      onJoinContest?.(contestId);
      fetchContests();  // Refresh contest list after successful join
    } catch (e) {
      let msg = 'Join failed';
      if (e?.response?.data?.detail) {
        msg = typeof e.response.data.detail === 'string' ? e.response.data.detail : JSON.stringify(e.response.data.detail);
      } else if (e?.response?.data?.message) {
        msg = e.response.data.message;
      } else if (e?.message) {
        msg = e.message;
      }
      console.error('Join error:', e?.response?.status, msg);
      if (msg.includes('Already joined') || msg.includes('409')) {
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

      {/* Match Hero Card - Immersive */}
      <div className={`rounded-2xl overflow-hidden relative ${isLive ? 'animate-border-glow' : ''}`} style={{ border: `1px solid ${isLive ? COLORS.primary.main + '44' : COLORS.border.light}` }}>
        {/* Background image */}
        {(() => {
          const heroImg = getTeamCardImage(teamA.short_name) || getTeamCardImage(teamB.short_name);
          return heroImg ? (
            <div className="absolute inset-0">
              <img src={heroImg} alt="" className="w-full h-full object-cover" style={{ filter: 'brightness(0.2) saturate(1.3)' }} />
              <div className="absolute inset-0" style={{ background: 'linear-gradient(180deg, rgba(13,13,13,0.4) 0%, rgba(13,13,13,0.95) 100%)' }} />
            </div>
          ) : (
            <div className="absolute inset-0" style={{ background: COLORS.background.card }} />
          );
        })()}

        <div className="relative">
          <div className="px-4 py-3 flex items-center justify-between">
            <span className="text-[10px] font-semibold glass px-2 py-0.5 rounded-full" style={{ color: '#fff' }}>{match?.tournament || 'IPL 2026'}</span>
            {isLive && (
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black text-white flex items-center gap-1.5" style={{ background: COLORS.primary.main }}>
                <span className="w-1.5 h-1.5 rounded-full bg-white animate-live-pulse" /> LIVE
              </span>
            )}
            {isCompleted && <span className="px-2 py-0.5 rounded text-[10px] font-bold glass" style={{ color: COLORS.text.tertiary }}>COMPLETED</span>}
          </div>
          <div className="px-6 py-5 flex items-center justify-between">
            <div className="flex flex-col items-center gap-2 flex-1">
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center text-lg font-black text-white shadow-lg overflow-hidden" style={{ background: getGrad(teamA.short_name), boxShadow: `0 4px 20px ${(TEAM_COLORS[teamA.short_name] || {primary:'#555'}).primary}44` }}>
                {getTeamLogo(teamA.short_name) ? <img src={getTeamLogo(teamA.short_name)} alt={teamA.short_name} className="w-12 h-12 object-contain" /> : teamA.short_name || '?'}
              </div>
              <div className="text-center">
                <div className="text-sm font-bold text-white">{teamA.short_name}</div>
                <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>{teamA.name}</div>
                {(isLive || isCompleted) && score?.scores?.[0] && (
                  <div className="text-lg font-black mt-0.5 animate-count" style={{ color: '#fff', fontFamily: "'Rajdhani', sans-serif", textShadow: `0 0 20px ${COLORS.primary.main}66` }}>
                    {score.scores[0].r || score.scores[0].runs}/{score.scores[0].w || score.scores[0].wickets} <span className="text-xs opacity-70">({score.scores[0].o || score.scores[0].overs})</span>
                  </div>
                )}
              </div>
            </div>
            <div className="flex flex-col items-center">
              <div className={`text-xs font-black px-3 py-1.5 rounded-xl ${isLive ? 'animate-live-pulse' : ''}`} style={{ background: `${COLORS.primary.main}22`, color: COLORS.primary.main }}>VS</div>
            </div>
            <div className="flex flex-col items-center gap-2 flex-1">
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center text-lg font-black text-white shadow-lg overflow-hidden" style={{ background: getGrad(teamB.short_name), boxShadow: `0 4px 20px ${(TEAM_COLORS[teamB.short_name] || {primary:'#555'}).primary}44` }}>
                {getTeamLogo(teamB.short_name) ? <img src={getTeamLogo(teamB.short_name)} alt={teamB.short_name} className="w-12 h-12 object-contain" /> : teamB.short_name || '?'}
              </div>
              <div className="text-center">
                <div className="text-sm font-bold text-white">{teamB.short_name}</div>
                <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>{teamB.name}</div>
                {(isLive || isCompleted) && score?.scores?.[1] && (
                  <div className="text-lg font-black mt-0.5 animate-count" style={{ color: '#fff', fontFamily: "'Rajdhani', sans-serif", textShadow: `0 0 20px ${COLORS.primary.main}66` }}>
                    {score.scores[1].r || score.scores[1].runs}/{score.scores[1].w || score.scores[1].wickets} <span className="text-xs opacity-70">({score.scores[1].o || score.scores[1].overs})</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Toss + Status Info */}
          <div className="px-3 py-2.5 flex items-center justify-between gap-2 text-center" style={{ borderTop: `1px solid ${COLORS.border.light}`, background: 'rgba(0,0,0,0.3)' }}>
            {matchInfo?.toss_winner ? (
              <div className="flex items-center gap-1.5 min-w-0 flex-1">
                <Coins size={12} color={COLORS.accent.gold} className="shrink-0" />
                <span className="text-[10px] truncate" style={{ color: COLORS.text.secondary }}>
                  Toss: <b style={{ color: COLORS.accent.gold }}>{matchInfo.toss_winner}</b> chose to <b>{matchInfo.toss_choice}</b>
                </span>
              </div>
            ) : (
              <div className="flex items-center gap-1.5 min-w-0 flex-1">
                <MapPin size={12} color={COLORS.text.tertiary} className="shrink-0" />
                <span className="text-[10px] truncate" style={{ color: COLORS.text.secondary }}>{match?.venue || 'TBD'}</span>
              </div>
            )}
            <div className="flex items-center gap-1.5 shrink-0">
              <Clock size={12} color={COLORS.warning.main} />
              <span className="text-[10px] whitespace-nowrap" style={{ color: COLORS.warning.main }}>
                {isLive ? 'In Progress' : isCompleted ? matchInfo?.status || 'Completed' : (match?.start_time_ist || new Date(match?.start_time).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Kolkata' }))}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Mood Meter — Instagram-style live poll */}
      <MoodMeter matchId={match?.id} teamA={teamA} teamB={teamB} />

      {/* Celebration Demo Strip — Test all animations */}
      <div className="flex gap-2 overflow-x-auto pb-1 no-scrollbar">
        {[
          { type: 'six', label: 'SIX', color: '#FFD700', icon: '6', glow: true },
          { type: 'four', label: 'FOUR', color: '#007AFF', icon: '4', glow: false },
          { type: 'wicket', label: 'WICKET', color: '#DC2626', icon: 'W', glow: true },
          { type: 'prize', label: 'WINNER', color: '#FFD700', icon: '1st', glow: true },
        ].map(c => (
          <button
            key={c.type}
            data-testid={`demo-${c.type}`}
            onClick={() => onCelebrate?.(c.type)}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-[10px] font-black tracking-wider whitespace-nowrap transition-all active:scale-90 hover:scale-105"
            style={{
              background: `linear-gradient(135deg, ${c.color}08, ${c.color}18)`,
              border: `1.5px solid ${c.color}40`,
              color: c.color,
              fontFamily: "'Orbitron', sans-serif",
              boxShadow: c.glow ? `0 0 15px ${c.color}15, inset 0 0 10px ${c.color}08` : 'none',
            }}>
            <span className="w-6 h-6 rounded-lg flex items-center justify-center text-[11px] font-black"
              style={{
                background: `${c.color}20`,
                boxShadow: `0 0 8px ${c.color}22`,
              }}>
              {c.icon}
            </span>
            {c.label}
          </button>
        ))}
      </div>

      {/* Live Update Indicator */}
      {(isLive || match?.status === 'open') && (
        <div className="flex items-center justify-between px-1" data-testid="live-update-indicator">
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full animate-pulse" style={{ background: '#22C55E' }} />
            <span className="text-[10px]" style={{ color: COLORS.text.tertiary }}>
              {lastUpdated
                ? `Updated ${Math.round((Date.now() - lastUpdated.getTime()) / 1000)}s ago`
                : 'Connecting...'}
            </span>
            {pollCount > 0 && (
              <span className="text-[9px] px-1.5 py-0.5 rounded-full" style={{ background: COLORS.primary.main + '22', color: COLORS.primary.main }}>
                Poll #{pollCount}
              </span>
            )}
          </div>
          <button
            data-testid="force-refresh-btn"
            onClick={() => fetchLiveData(true)}
            className="flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] font-semibold active:scale-95 transition-all"
            style={{ background: COLORS.background.card, color: COLORS.accent.gold, border: `1px solid ${COLORS.accent.gold}33` }}>
            <RefreshCw size={10} /> Refresh
          </button>
        </div>
      )}

      {/* Tab Bar - Glass morphism, scroll on mobile */}
      <div className="flex rounded-xl overflow-x-auto scrollbar-hide glass" style={{ border: `1px solid ${COLORS.border.light}`, scrollbarWidth: 'none' }}>
        {TABS.map(tab => {
          const Icon = tab.icon;
          const active = activeTab === tab.key;
          return (
            <button key={tab.key} data-testid={`tab-${tab.key}`} onClick={() => setActiveTab(tab.key)}
              className="flex-1 flex items-center justify-center gap-1 py-2.5 px-2 text-[10px] font-bold transition-all relative whitespace-nowrap min-w-0"
              style={{
                color: active ? '#fff' : COLORS.text.tertiary,
                background: active ? `${COLORS.primary.main}20` : 'transparent',
                minHeight: '44px',
              }}>
              <Icon size={13} className="shrink-0" />
              <span className="truncate">{tab.label}</span>
              {active && <div className="absolute bottom-0 left-1/4 right-1/4 h-[2px] rounded-full" style={{ background: COLORS.primary.main }} />}
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
      {activeTab === 'live' && <AICommentaryTab data={bbbData} loading={bbbLoading} onCelebrate={(type) => onCelebrate?.(type)} />}
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
          <div className="text-[10px] font-black uppercase tracking-[0.12em]" style={{ color: COLORS.text.tertiary }}>Template Status</div>
          {deadlines.map(d => (
            <div key={d.template_id} className="flex items-center justify-between px-3 py-2.5 rounded-xl"
              style={{ background: d.is_locked ? 'rgba(239,68,68,0.06)' : 'rgba(0,200,83,0.06)', border: `1px solid ${d.is_locked ? 'rgba(239,68,68,0.15)' : 'rgba(0,200,83,0.15)'}` }}>
              <div className="flex items-center gap-2">
                {d.is_locked ? <Lock size={12} color={COLORS.error.main} /> : <Unlock size={12} color={COLORS.success.main} />}
                <span className="text-xs font-bold text-white">{d.phase_label || d.template_type}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-medium" style={{ color: COLORS.text.secondary }}>
                  Inn {d.deadline_innings} Ov {d.deadline_over}
                </span>
                <span className="text-[9px] px-2 py-0.5 rounded-full font-bold"
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
        const isLive = c.status === 'live';
        const isOpen = c.status === 'open';  // participation closed, match ongoing
        const participantPct = c.max_participants > 0 ? Math.min(100, Math.round((c.current_participants || 0) / c.max_participants * 100)) : 0;

        // Status label mapping
        const statusLabel = done ? 'DONE' : isLive ? 'LIVE' : isOpen ? 'OPEN' : (c.status || '').toUpperCase();
        const statusColor = isLive ? '#FF3B3B' : isOpen ? '#F59E0B' : done ? '#22c55e' : COLORS.text.tertiary;

        return (
          <div key={c.id} data-testid={`contest-${c.id}`} className="rounded-2xl overflow-hidden"
            style={{ background: COLORS.background.card, border: `1px solid ${isJoined ? COLORS.success.main + '30' : 'rgba(255,255,255,0.06)'}` }}>
            <div className="p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-bold text-white tracking-tight">{c.name}</div>
                  <div className="flex items-center gap-3 mt-1.5">
                    <span className="flex items-center gap-1 text-xs font-semibold" style={{ color: COLORS.accent.gold }}>
                      <Coins size={12} color="#FFD700" /> {c.entry_fee} coins
                    </span>
                    <span className="text-xs font-bold" style={{ color: '#10B981' }}>Pool {(c.prize_pool || c.entry_fee * (c.current_participants || 0)).toLocaleString()}</span>
                  </div>
                </div>
                <div className="ml-3 shrink-0">
                  {(done || isOpen) ? (
                    /* Open or Completed → show Leaderboard */
                    <button data-testid={`leaderboard-btn-${c.id}`} onClick={() => onOpenLeaderboard?.(c.id)}
                      className="px-4 py-2.5 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-transform active:scale-95"
                      style={{ background: `${COLORS.accent.gold}15`, color: COLORS.accent.gold, border: `1px solid ${COLORS.accent.gold}30` }}>
                      <Trophy size={13} /> {done ? 'Results' : 'Leaderboard'}
                    </button>
                  ) : isJoined && isLive ? (
                    /* Joined + Live → Predict */
                    <button data-testid={`predict-btn-${c.id}`} onClick={() => onOpenPrediction?.(c.id)}
                      className="px-4 py-2.5 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-transform active:scale-95"
                      style={{ background: `${COLORS.success.main}15`, color: COLORS.success.main, border: `1px solid ${COLORS.success.main}30` }}>
                      <Check size={13} /> Predict
                    </button>
                  ) : !isJoined && isLive ? (
                    /* Not Joined + Live → Join */
                    <button data-testid={`join-btn-${c.id}`} onClick={() => onJoin(c.id)}
                      disabled={isJoining}
                      className="px-5 py-2.5 rounded-xl text-xs font-bold flex items-center gap-1.5 disabled:opacity-50 transition-transform active:scale-95"
                      style={{ background: COLORS.primary.gradient, color: '#fff', boxShadow: '0 4px 12px rgba(255,59,59,0.25)' }}>
                      {isJoining ? <Loader2 size={13} className="animate-spin" /> : null}
                      {isJoining ? 'Joining...' : 'Join'} {!isJoining && <ChevronRight size={13} />}
                    </button>
                  ) : null}
                </div>
              </div>
              {/* Participant progress bar */}
              <div className="flex items-center gap-2">
                <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.06)' }}>
                  <div className="h-full rounded-full transition-all" style={{ width: `${participantPct}%`, background: participantPct > 80 ? COLORS.error.main : COLORS.info.main }} />
                </div>
                <div className="flex items-center gap-1 shrink-0">
                  <Users size={10} color={COLORS.text.tertiary} />
                  <span className="text-[10px] font-semibold" style={{ color: COLORS.text.secondary }}>{c.current_participants || 0}/{c.max_participants || 0}</span>
                </div>
                <span className="text-[9px] font-bold px-1.5 py-0.5 rounded shrink-0"
                  style={{
                    color: statusColor,
                    background: isLive ? 'rgba(255,59,59,0.1)' : isOpen ? 'rgba(245,158,11,0.1)' : done ? 'rgba(34,197,94,0.1)' : 'rgba(255,255,255,0.04)',
                  }}>
                  {isLive && <span className="inline-block w-1.5 h-1.5 rounded-full mr-1 animate-pulse" style={{ background: '#FF3B3B' }} />}
                  {statusLabel}
                </span>
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
      <div className="flex rounded-xl overflow-hidden" style={{ background: COLORS.background.card, border: `1px solid rgba(255,255,255,0.06)` }}>
        {squads.map((t, i) => (
          <button key={i} data-testid={`squad-team-${i}`} onClick={() => setActiveTeam(i)}
            className="flex-1 py-2.5 text-xs font-bold text-center transition-all"
            style={{ color: activeTeam === i ? '#fff' : COLORS.text.tertiary, background: activeTeam === i ? COLORS.primary.main : 'transparent', boxShadow: activeTeam === i ? '0 2px 8px rgba(255,59,59,0.3)' : 'none' }}>
            {normalizeTeam(t.shortname || t.teamName?.split(' ')[0] || '')}
            <span className="text-[9px] ml-1 opacity-60">({(t.players || []).length})</span>
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
      <div className="flex rounded-xl overflow-hidden" style={{ background: COLORS.background.card, border: `1px solid rgba(255,255,255,0.06)` }}>
        <button onClick={() => setView('totals')} className="flex-1 py-2.5 text-xs font-bold transition-all"
          style={{ color: view === 'totals' ? '#fff' : COLORS.text.tertiary, background: view === 'totals' ? COLORS.primary.main : 'transparent', boxShadow: view === 'totals' ? '0 2px 8px rgba(255,59,59,0.3)' : 'none' }}>
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
        <div className="rounded-xl overflow-hidden" style={{ background: COLORS.background.card, border: `1px solid rgba(255,255,255,0.06)` }}>
          {totals.slice(0, 15).map((p, i) => (
            <div key={p.id || i} className="flex items-center gap-3 px-3 py-3"
              style={{ borderBottom: i < Math.min(totals.length, 15) - 1 ? `1px solid rgba(255,255,255,0.04)` : 'none',
                background: i < 3 ? `${COLORS.accent.gold}06` : 'transparent' }}>
              <div className="w-7 text-center text-xs font-black" style={{ color: i === 0 ? '#FFD700' : i === 1 ? '#C0C0C0' : i === 2 ? '#CD7F32' : COLORS.text.tertiary }}>
                {i + 1}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-xs font-bold text-white truncate">{p.name}</div>
              </div>
              <div className="text-sm font-black" style={{ color: (p.points || 0) >= 0 ? COLORS.success.main : COLORS.error.main, fontFamily: "'Rajdhani', sans-serif" }}>
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


// LiveTab and _buildFromScorecard moved to AICommentaryTab.jsx


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
    <div className="fixed inset-0 z-50 flex items-end justify-center" style={{ background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(4px)' }}
      onClick={onClose}>
      <div className="w-full max-w-lg max-h-[80vh] overflow-y-auto rounded-t-3xl p-5 space-y-4"
        style={{ background: COLORS.background.primary, animation: 'slideUp 0.3s ease', boxShadow: '0 -4px 30px rgba(0,0,0,0.5)' }}
        onClick={e => e.stopPropagation()}>

        <div className="flex items-center justify-between">
          <h3 className="text-base font-black text-white tracking-tight">Player Profile</h3>
          <button onClick={onClose} className="p-1.5 rounded-full transition-colors" style={{ background: 'rgba(255,255,255,0.06)' }}>
            <X size={16} color={COLORS.text.secondary} />
          </button>
        </div>

        {loading ? <LoadingSpinner /> : !p.name ? (
          <p className="text-sm text-center py-4" style={{ color: COLORS.text.secondary }}>Profile not available</p>
        ) : (
          <>
            {/* Player Header */}
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-2xl overflow-hidden shrink-0 shadow-lg" style={{ background: COLORS.background.tertiary }}>
                {p.playerImg && !p.playerImg.includes('icon512') && (
                  <img src={p.playerImg} alt={p.name} className="w-full h-full object-cover" />
                )}
              </div>
              <div>
                <div className="text-lg font-black text-white">{p.name}</div>
                <div className="text-xs font-semibold" style={{ color: COLORS.text.secondary }}>{p.role} | {p.country}</div>
                <div className="text-[10px] mt-0.5 font-medium" style={{ color: COLORS.text.tertiary }}>
                  {p.battingStyle}{p.bowlingStyle ? ` | ${p.bowlingStyle}` : ''}
                </div>
                {p.placeOfBirth && <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>Born: {p.placeOfBirth}</div>}
              </div>
            </div>

            {/* Stats by Format */}
            {Object.entries(formats).map(([fmt, fmtStats]) => (
              <div key={fmt}>
                <div className="text-[10px] font-black uppercase tracking-[0.12em] mb-1.5" style={{ color: COLORS.primary.main }}>{fmt}</div>
                <div className="rounded-xl overflow-hidden" style={{ background: COLORS.background.card, border: `1px solid rgba(255,255,255,0.06)` }}>
                  {fmtStats.map((s, i) => (
                    <div key={i} className="flex items-center justify-between px-3 py-2"
                      style={{ borderBottom: i < fmtStats.length - 1 ? `1px solid rgba(255,255,255,0.04)` : 'none' }}>
                      <span className="text-xs font-medium" style={{ color: COLORS.text.secondary }}>{s.fn}</span>
                      <span className="text-xs font-bold text-white">{s.value}</span>
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
