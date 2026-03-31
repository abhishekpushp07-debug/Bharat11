/**
 * Admin Dashboard - Command Center
 * Real-time stats, alerts, quick actions
 */
import { useState, useEffect } from 'react';
import apiClient from '../../api/client';
import { COLORS } from '../../constants/design';
import { Users, HelpCircle, FileText, Calendar, Trophy, Zap, AlertTriangle, Play, ChevronRight, CheckCircle, Brain, Loader2, X } from 'lucide-react';

export default function AdminDashboard({ onNavigate }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [unresolvedContests, setUnresolvedContests] = useState([]);
  const [quickResolving, setQuickResolving] = useState(false);
  const [quickResult, setQuickResult] = useState(null);

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
  }, []);

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
