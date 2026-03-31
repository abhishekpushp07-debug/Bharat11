/**
 * Admin Dashboard - Command Center
 * Real-time stats, alerts, quick actions, Auto-Pilot toggle
 */
import { useState, useEffect, useCallback } from 'react';
import apiClient from '../../api/client';
import { COLORS } from '../../constants/design';
import { Users, HelpCircle, FileText, Calendar, Trophy, Zap, AlertTriangle, Play, ChevronRight, CheckCircle, Brain, Loader2, X, Power, Pause, Database, Layers, RotateCw } from 'lucide-react';

export default function AdminDashboard({ onNavigate }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [unresolvedContests, setUnresolvedContests] = useState([]);
  const [quickResolving, setQuickResolving] = useState(false);
  const [quickResult, setQuickResult] = useState(null);

  // Auto-Pilot state
  const [autopilot, setAutopilot] = useState({ running: false, run_count: 0, last_run: null, recent_log: [] });
  const [apLoading, setApLoading] = useState(false);
  const [apMsg, setApMsg] = useState('');
  const [showApLogs, setShowApLogs] = useState(false);

  // Auto-Engine actions state
  const [seedingQuestions, setSeedingQuestions] = useState(false);
  const [generatingTemplates, setGeneratingTemplates] = useState(false);
  const [creatingContests, setCreatingContests] = useState(false);
  const [engineResult, setEngineResult] = useState(null);

  const fetchAutopilotStatus = useCallback(async () => {
    try {
      const res = await apiClient.get('/admin/autopilot/status');
      setAutopilot(res.data);
    } catch (_) {}
  }, []);

  useEffect(() => {
    const fetch = async () => {
      try {
        const [sRes, cRes] = await Promise.allSettled([
          apiClient.get('/admin/stats'),
          apiClient.get('/contests?status=open&limit=20')
        ]);
        if (sRes.status === 'fulfilled') setStats(sRes.value.data);
        if (cRes.status === 'fulfilled') {
          const contests = cRes.value.data.contests || [];
          setUnresolvedContests(contests.filter(c => c.status !== 'completed'));
        }
      } catch (_) {}
      finally { setLoading(false); }
    };
    fetch();
    fetchAutopilotStatus();
  }, [fetchAutopilotStatus]);

  // Poll autopilot status when running
  useEffect(() => {
    if (!autopilot.running) return;
    const iv = setInterval(fetchAutopilotStatus, 15000);
    return () => clearInterval(iv);
  }, [autopilot.running, fetchAutopilotStatus]);

  const toggleAutopilot = async () => {
    setApLoading(true);
    setApMsg('');
    try {
      if (autopilot.running) {
        await apiClient.post('/admin/autopilot/stop');
        setApMsg('Auto-Pilot STOPPED');
      } else {
        await apiClient.post('/admin/autopilot/start');
        setApMsg('Auto-Pilot STARTED');
      }
      await fetchAutopilotStatus();
    } catch (e) {
      setApMsg(`Error: ${e?.response?.data?.detail || e.message}`);
    } finally { setApLoading(false); }
  };

  const handleSeedQuestions = async () => {
    if (!window.confirm('200 question pool seed karna hai? (Existing pool safe rahega)')) return;
    setSeedingQuestions(true);
    setEngineResult(null);
    try {
      const res = await apiClient.post('/admin/seed-question-pool');
      setEngineResult({ type: 'seed', ...res.data });
    } catch (e) { setEngineResult({ type: 'seed', message: `Error: ${e?.response?.data?.detail || e.message}` }); }
    finally { setSeedingQuestions(false); }
  };

  const handleAutoTemplatesAll = async () => {
    if (!window.confirm('Sabhi upcoming matches ke liye 5-5 templates auto-generate?')) return;
    setGeneratingTemplates(true);
    setEngineResult(null);
    try {
      const res = await apiClient.post('/admin/auto-templates-all');
      setEngineResult({ type: 'templates', ...res.data });
    } catch (e) { setEngineResult({ type: 'templates', message: `Error: ${e?.response?.data?.detail || e.message}` }); }
    finally { setGeneratingTemplates(false); }
  };

  const handleAutoContests24h = async () => {
    if (!window.confirm('24 ghante ke andar ke matches ke liye contests auto-create?')) return;
    setCreatingContests(true);
    setEngineResult(null);
    try {
      const res = await apiClient.post('/admin/auto-contests-24h');
      setEngineResult({ type: 'contests', ...res.data });
    } catch (e) { setEngineResult({ type: 'contests', message: `Error: ${e?.response?.data?.detail || e.message}` }); }
    finally { setCreatingContests(false); }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-3">
        <div className="w-10 h-10 border-2 rounded-full animate-spin" style={{ borderColor: `${COLORS.accent.gold}30`, borderTopColor: COLORS.accent.gold }} />
        <span className="text-xs" style={{ color: COLORS.text.tertiary }}>Loading Command Center...</span>
      </div>
    );
  }

  const statCards = [
    { label: 'Users', value: stats?.users || 0, Icon: Users, color: COLORS.primary.main, tab: 'users' },
    { label: 'Questions', value: stats?.questions || 0, Icon: HelpCircle, color: COLORS.info.main, tab: 'content' },
    { label: 'Templates', value: stats?.templates || 0, Icon: FileText, color: COLORS.warning.main, tab: 'content' },
    { label: 'Matches', value: stats?.matches || 0, Icon: Calendar, color: COLORS.success.main, tab: 'matches' },
    { label: 'Contests', value: stats?.contests || 0, Icon: Trophy, color: COLORS.accent.gold, tab: 'matches' },
    { label: 'Entries', value: stats?.active_entries || 0, Icon: Zap, color: COLORS.accent.purple, tab: 'resolve' },
  ];

  const liveCount = stats?.live_matches || 0;
  const upcomingCount = stats?.upcoming_matches || 0;
  const openContests = stats?.open_contests || 0;

  return (
    <div data-testid="admin-dashboard" className="space-y-5">
      {/* Live Status Bar */}
      {liveCount > 0 && (
        <div className="flex items-center gap-3 p-3 rounded-xl animate-pulse" style={{ background: `${COLORS.success.main}15`, border: `1px solid ${COLORS.success.main}33` }}>
          <div className="w-3 h-3 rounded-full animate-ping" style={{ background: COLORS.success.main }} />
          <span className="text-sm font-bold" style={{ color: COLORS.success.main }}>{liveCount} LIVE MATCH{liveCount > 1 ? 'ES' : ''}</span>
          <button onClick={() => onNavigate('matches')} className="ml-auto text-xs font-semibold" style={{ color: COLORS.success.main }}>
            View <ChevronRight size={12} className="inline" />
          </button>
        </div>
      )}

      {/* Quick Resolve - ONE TAP */}
      <div className="rounded-2xl overflow-hidden relative" style={{
        background: 'linear-gradient(135deg, #1e1b4b, #312e81, #1e1b4b)',
        border: '1px solid #6366f133'
      }}>
        <div className="absolute inset-0 opacity-20" style={{
          background: 'radial-gradient(circle at 80% 20%, #818cf855, transparent 60%)'
        }} />
        <div className="relative p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2.5">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: '#818cf822' }}>
                <Brain size={20} color="#818cf8" />
              </div>
              <div>
                <div className="text-sm font-bold text-white">Quick Resolve</div>
                <div className="text-[10px]" style={{ color: '#a5b4fc' }}>
                  AI resolves all active contests in one tap
                </div>
              </div>
            </div>
            <button
              data-testid="quick-resolve-btn"
              onClick={async () => {
                if (!window.confirm('AI will resolve ALL active contests. Continue?')) return;
                setQuickResolving(true);
                setQuickResult(null);
                try {
                  const res = await apiClient.post('/admin/quick-resolve-all');
                  setQuickResult(res.data);
                } catch (e) {
                  setQuickResult({ message: `Error: ${e?.response?.data?.detail || e.message}`, total_resolved: 0 });
                } finally { setQuickResolving(false); }
              }}
              disabled={quickResolving}
              className="px-4 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2 disabled:opacity-50 transition-all active:scale-95"
              style={{
                background: 'linear-gradient(135deg, #818cf8, #6366f1)',
                color: '#fff',
                boxShadow: '0 4px 16px #6366f144'
              }}>
              {quickResolving ? <Loader2 size={14} className="animate-spin" /> : <Zap size={14} />}
              {quickResolving ? 'Resolving...' : 'Resolve All'}
            </button>
          </div>

          {/* Quick Resolve Result */}
          {quickResult && (
            <div className="mt-3 p-3 rounded-xl space-y-2" style={{ background: 'rgba(0,0,0,0.3)' }}>
              <div className="flex items-center justify-between">
                <div className="text-xs font-bold text-white">{quickResult.message}</div>
                <button onClick={() => setQuickResult(null)}><X size={12} color="#a5b4fc" /></button>
              </div>
              <div className="grid grid-cols-3 gap-2">
                <div className="text-center p-2 rounded-lg" style={{ background: '#10b98122' }}>
                  <div className="text-sm font-bold" style={{ color: '#10b981' }}>{quickResult.total_resolved}</div>
                  <div className="text-[8px]" style={{ color: '#10b98199' }}>Resolved</div>
                </div>
                <div className="text-center p-2 rounded-lg" style={{ background: '#f59e0b22' }}>
                  <div className="text-sm font-bold" style={{ color: '#f59e0b' }}>{quickResult.total_skipped}</div>
                  <div className="text-[8px]" style={{ color: '#f59e0b99' }}>Skipped</div>
                </div>
                <div className="text-center p-2 rounded-lg" style={{ background: '#ef444422' }}>
                  <div className="text-sm font-bold" style={{ color: '#ef4444' }}>{quickResult.total_errors}</div>
                  <div className="text-[8px]" style={{ color: '#ef444499' }}>Errors</div>
                </div>
              </div>
              {(quickResult.results || []).map((r, i) => (
                <div key={i} className="text-[10px] flex items-center gap-2" style={{ color: '#a5b4fc' }}>
                  <span className="font-bold text-white">{r.contest_name?.slice(0, 25)}</span>
                  <span style={{ color: '#10b981' }}>+{r.resolved}</span>
                  {r.finalized && <span className="px-1 rounded text-[8px] font-bold" style={{ background: '#10b98133', color: '#10b981' }}>DONE</span>}
                  {r.errors?.length > 0 && <span style={{ color: '#ef4444' }}>{r.errors[0]?.slice(0, 30)}</span>}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* =================== AUTO-PILOT CONTROL PANEL =================== */}
      <div className="rounded-2xl overflow-hidden" style={{
        background: autopilot.running
          ? 'linear-gradient(135deg, #052e16, #14532d, #052e16)'
          : COLORS.background.card,
        border: `1px solid ${autopilot.running ? '#22c55e33' : COLORS.border.light}`
      }}>
        <div className="p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2.5">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: autopilot.running ? '#22c55e22' : '#ef444422' }}>
                {autopilot.running ?
                  <Play size={20} color="#22c55e" /> :
                  <Pause size={20} color="#ef4444" />
                }
              </div>
              <div>
                <div className="text-sm font-bold text-white">Auto-Pilot</div>
                <div className="text-[10px]" style={{ color: autopilot.running ? '#4ade80' : COLORS.text.tertiary }}>
                  {autopilot.running ? `Running (Cycle #${autopilot.run_count})` : 'Stopped — Manual Mode'}
                </div>
              </div>
            </div>

            {/* Toggle Button */}
            <button
              data-testid="autopilot-toggle-btn"
              onClick={toggleAutopilot}
              disabled={apLoading}
              className="px-5 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2 disabled:opacity-50 transition-all active:scale-95"
              style={{
                background: autopilot.running ? '#ef4444' : '#22c55e',
                color: '#fff',
                boxShadow: autopilot.running ? '0 4px 16px #ef444433' : '0 4px 16px #22c55e33'
              }}>
              {apLoading ? <Loader2 size={14} className="animate-spin" /> :
                autopilot.running ? <Pause size={14} /> : <Power size={14} />}
              {apLoading ? '...' : autopilot.running ? 'STOP' : 'START'}
            </button>
          </div>

          {apMsg && (
            <div className="text-[10px] text-center py-1.5 rounded-lg mb-2" style={{
              background: apMsg.includes('Error') ? '#ef444422' : '#22c55e22',
              color: apMsg.includes('Error') ? '#ef4444' : '#22c55e'
            }}>{apMsg}</div>
          )}

          {/* Status Details */}
          {autopilot.running && (
            <div className="grid grid-cols-3 gap-2 mb-3">
              <div className="text-center p-2 rounded-lg" style={{ background: '#22c55e11' }}>
                <div className="text-sm font-bold" style={{ color: '#22c55e' }}>{autopilot.run_count}</div>
                <div className="text-[8px]" style={{ color: '#22c55e88' }}>Cycles</div>
              </div>
              <div className="text-center p-2 rounded-lg" style={{ background: '#22c55e11' }}>
                <div className="text-sm font-bold" style={{ color: '#4ade80' }}>{autopilot.interval_seconds || 45}s</div>
                <div className="text-[8px]" style={{ color: '#22c55e88' }}>Interval</div>
              </div>
              <div className="text-center p-2 rounded-lg" style={{ background: '#22c55e11' }}>
                <div className="text-[10px] font-bold" style={{ color: '#86efac' }}>
                  {autopilot.last_run ? new Date(autopilot.last_run).toLocaleTimeString('en-IN', { timeZone: 'Asia/Kolkata', hour: '2-digit', minute: '2-digit' }) : '—'}
                </div>
                <div className="text-[8px]" style={{ color: '#22c55e88' }}>Last Run</div>
              </div>
            </div>
          )}

          {/* Logs Toggle */}
          {autopilot.recent_log?.length > 0 && (
            <div>
              <button onClick={() => setShowApLogs(!showApLogs)}
                className="text-[10px] font-semibold flex items-center gap-1 mb-1"
                style={{ color: autopilot.running ? '#86efac' : COLORS.text.tertiary }}>
                {showApLogs ? 'Hide Logs' : `Show Logs (${autopilot.recent_log.length})`}
              </button>
              {showApLogs && (
                <div className="max-h-32 overflow-y-auto rounded-lg p-2 space-y-0.5" style={{ background: 'rgba(0,0,0,0.3)' }}>
                  {autopilot.recent_log.map((log, i) => (
                    <div key={i} className="text-[9px] font-mono" style={{ color: '#86efac' }}>{log}</div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Auto Mode Info */}
          <div className="text-[9px] mt-2 p-2 rounded-lg" style={{ background: 'rgba(0,0,0,0.2)', color: autopilot.running ? '#86efac99' : COLORS.text.tertiary }}>
            {autopilot.running
              ? 'Auto: 45s polling, auto-resolve, auto-finalize, auto-create contests'
              : 'Manual: Admin manually manages matches, contests & resolution'}
          </div>
        </div>
      </div>

      {/* =================== MATCH AUTO-ENGINE =================== */}
      <div className="rounded-2xl p-4 space-y-3" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
        <div className="flex items-center gap-2">
          <Layers size={16} color={COLORS.accent.gold} />
          <span className="text-sm font-bold text-white">Match Auto-Engine</span>
        </div>
        <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>
          One-tap actions to seed questions, generate templates & create contests
        </div>

        <div className="grid grid-cols-3 gap-2">
          <button data-testid="seed-questions-btn" onClick={handleSeedQuestions} disabled={seedingQuestions}
            className="flex flex-col items-center gap-1.5 p-3 rounded-xl transition-all active:scale-95 disabled:opacity-50"
            style={{ background: '#3b82f615', border: '1px solid #3b82f622' }}>
            {seedingQuestions ? <Loader2 size={16} className="animate-spin" color="#60a5fa" /> : <Database size={16} color="#60a5fa" />}
            <span className="text-[9px] font-bold" style={{ color: '#60a5fa' }}>Seed 200 Qs</span>
          </button>

          <button data-testid="auto-templates-all-btn" onClick={handleAutoTemplatesAll} disabled={generatingTemplates}
            className="flex flex-col items-center gap-1.5 p-3 rounded-xl transition-all active:scale-95 disabled:opacity-50"
            style={{ background: '#f59e0b15', border: '1px solid #f59e0b22' }}>
            {generatingTemplates ? <Loader2 size={16} className="animate-spin" color="#f59e0b" /> : <FileText size={16} color="#f59e0b" />}
            <span className="text-[9px] font-bold" style={{ color: '#f59e0b' }}>Auto Templates</span>
          </button>

          <button data-testid="auto-contests-24h-btn" onClick={handleAutoContests24h} disabled={creatingContests}
            className="flex flex-col items-center gap-1.5 p-3 rounded-xl transition-all active:scale-95 disabled:opacity-50"
            style={{ background: '#22c55e15', border: '1px solid #22c55e22' }}>
            {creatingContests ? <Loader2 size={16} className="animate-spin" color="#22c55e" /> : <Trophy size={16} color="#22c55e" />}
            <span className="text-[9px] font-bold" style={{ color: '#22c55e' }}>24h Contests</span>
          </button>
        </div>

        {/* Engine Result */}
        {engineResult && (
          <div className="p-3 rounded-xl space-y-1" style={{ background: COLORS.background.tertiary }}>
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white">
                {engineResult.type === 'seed' ? 'Question Seed' : engineResult.type === 'templates' ? 'Auto Templates' : 'Auto Contests'}
              </span>
              <button onClick={() => setEngineResult(null)}><X size={12} color={COLORS.text.tertiary} /></button>
            </div>
            <div className="text-[10px]" style={{ color: COLORS.text.secondary }}>{engineResult.message}</div>
            {engineResult.seeded > 0 && (
              <div className="text-[10px]" style={{ color: '#22c55e' }}>Seeded: {engineResult.seeded} questions</div>
            )}
            {engineResult.processed > 0 && (
              <div className="text-[10px]" style={{ color: '#22c55e' }}>Processed: {engineResult.processed} matches</div>
            )}
            {engineResult.results?.length > 0 && (
              <div className="max-h-24 overflow-y-auto space-y-0.5 mt-1">
                {engineResult.results.map((r, i) => (
                  <div key={i} className="text-[9px]" style={{ color: r.status === 'created' ? '#22c55e' : r.status === 'skipped' ? '#f59e0b' : '#ef4444' }}>
                    {r.name || r.match_id?.slice(0, 8)} — {r.status} {r.reason || ''}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Stats Grid - All Clickable */}
      <div className="grid grid-cols-3 gap-2.5">
        {statCards.map(({ label, value, Icon, color, tab }) => (
          <button key={label} data-testid={`stat-${label.toLowerCase()}`}
            onClick={() => tab && onNavigate(tab)}
            className="text-center p-3.5 rounded-xl transition-all active:scale-95 cursor-pointer card-hover relative overflow-hidden"
            style={{ background: COLORS.background.card, border: `1px solid ${color}18` }}>
            {tab && <div className="absolute top-1.5 right-1.5"><ChevronRight size={10} color={`${color}66`} /></div>}
            <Icon size={18} color={color} className="mx-auto mb-1.5" strokeWidth={1.5} />
            <div className="text-xl font-black" style={{ color, fontFamily: "'Rajdhani', sans-serif" }}>{value.toLocaleString()}</div>
            <div className="text-[10px] font-semibold mt-0.5" style={{ color: COLORS.text.tertiary }}>{label}</div>
          </button>
        ))}
      </div>

      {/* Alerts */}
      {(unresolvedContests.length > 0 || upcomingCount > 0) && (
        <div className="space-y-2">
          <h3 className="text-xs font-semibold uppercase tracking-wider" style={{ color: COLORS.text.tertiary }}>Alerts</h3>

          {unresolvedContests.length > 0 && (
            <button data-testid="alert-resolve" onClick={() => onNavigate('resolve')}
              className="w-full flex items-center gap-3 p-3 rounded-xl text-left transition-all"
              style={{ background: COLORS.background.card, border: `1px solid ${COLORS.warning.main}22` }}>
              <div className="w-9 h-9 rounded-lg flex items-center justify-center shrink-0" style={{ background: COLORS.warning.bg }}>
                <AlertTriangle size={18} color={COLORS.warning.main} />
              </div>
              <div className="flex-1">
                <div className="text-sm font-semibold text-white">{openContests} contest(s) need resolution</div>
                <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>Resolve questions to distribute prizes</div>
              </div>
              <ChevronRight size={16} color={COLORS.text.tertiary} />
            </button>
          )}

          {upcomingCount > 0 && (
            <button data-testid="alert-upcoming" onClick={() => onNavigate('matches')}
              className="w-full flex items-center gap-3 p-3 rounded-xl text-left transition-all"
              style={{ background: COLORS.background.card, border: `1px solid ${COLORS.info.main}22` }}>
              <div className="w-9 h-9 rounded-lg flex items-center justify-center shrink-0" style={{ background: COLORS.info.bg }}>
                <Calendar size={18} color={COLORS.info.main} />
              </div>
              <div className="flex-1">
                <div className="text-sm font-semibold text-white">{upcomingCount} upcoming match(es)</div>
                <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>Ensure templates & contests are ready</div>
              </div>
              <ChevronRight size={16} color={COLORS.text.tertiary} />
            </button>
          )}
        </div>
      )}

      {/* Quick Actions */}
      <div className="space-y-2">
        <h3 className="text-xs font-semibold uppercase tracking-wider" style={{ color: COLORS.text.tertiary }}>Quick Actions</h3>
        <div className="grid grid-cols-2 gap-2">
          {[
            { label: 'Create Question', tab: 'content', Icon: HelpCircle, color: COLORS.info.main },
            { label: 'Create Match', tab: 'matches', Icon: Calendar, color: COLORS.success.main },
            { label: 'Create Contest', tab: 'matches', Icon: Trophy, color: COLORS.accent.gold },
            { label: 'Resolve Now', tab: 'resolve', Icon: CheckCircle, color: COLORS.warning.main },
          ].map(({ label, tab, Icon, color }) => (
            <button key={label} data-testid={`quick-${label.toLowerCase().replace(/\s/g, '-')}`}
              onClick={() => onNavigate(tab)}
              className="flex items-center gap-2.5 p-3.5 rounded-xl text-left transition-all active:scale-95 card-hover"
              style={{ background: COLORS.background.card, border: `1px solid ${color}18` }}>
              <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0" style={{ background: `${color}15` }}>
                <Icon size={16} color={color} />
              </div>
              <span className="text-xs font-bold text-white flex-1">{label}</span>
              <ChevronRight size={14} color={`${color}66`} />
            </button>
          ))}
        </div>
      </div>

      {/* Admin Workflow Guide */}
      <div className="p-4 rounded-2xl" style={{ background: COLORS.background.card, border: `1px solid rgba(255,255,255,0.06)` }}>
        <h3 className="text-[10px] font-black uppercase tracking-[0.12em] mb-3" style={{ color: COLORS.text.tertiary }}>Admin Workflow</h3>
        <div className="space-y-1.5">
          {[
            { step: 1, text: 'Create questions with bilingual text & points', tab: 'content', color: COLORS.info.main },
            { step: 2, text: 'Build templates (1 Full Match required)', tab: 'content', color: COLORS.warning.main },
            { step: 3, text: 'Create match & assign templates', tab: 'matches', color: COLORS.success.main },
            { step: 4, text: 'Create contests (fee + prize pool)', tab: 'matches', color: COLORS.accent.gold },
            { step: 5, text: 'Set match LIVE when it starts', tab: 'matches', color: '#FF4444' },
            { step: 6, text: 'Resolve questions & finalize prizes', tab: 'resolve', color: COLORS.accent.purple },
          ].map(({ step, text, tab, color }) => (
            <button key={step} onClick={() => onNavigate(tab)}
              className="flex items-center gap-3 w-full text-left p-2.5 rounded-xl transition-all active:scale-[0.98] card-hover"
              style={{ background: 'rgba(255,255,255,0.02)' }}>
              <div className="w-7 h-7 rounded-lg flex items-center justify-center text-[10px] font-black shrink-0" style={{ background: color + '18', color }}>
                {step}
              </div>
              <span className="text-xs font-medium flex-1" style={{ color: COLORS.text.secondary }}>{text}</span>
              <ChevronRight size={12} color={`${color}55`} />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
