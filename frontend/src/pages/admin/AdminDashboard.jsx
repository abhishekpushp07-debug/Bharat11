/**
 * Admin Dashboard - Command Center
 * Real-time stats, alerts, quick actions
 */
import { useState, useEffect } from 'react';
import apiClient from '../../api/client';
import { COLORS } from '../../constants/design';
import { Users, HelpCircle, FileText, Calendar, Trophy, Zap, AlertTriangle, Play, ChevronRight, CheckCircle } from 'lucide-react';

export default function AdminDashboard({ onNavigate }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [unresolvedContests, setUnresolvedContests] = useState([]);

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
    { label: 'Users', value: stats?.users || 0, Icon: Users, color: COLORS.primary.main },
    { label: 'Questions', value: stats?.questions || 0, Icon: HelpCircle, color: COLORS.info.main },
    { label: 'Templates', value: stats?.templates || 0, Icon: FileText, color: COLORS.warning.main },
    { label: 'Matches', value: stats?.matches || 0, Icon: Calendar, color: COLORS.success.main },
    { label: 'Contests', value: stats?.contests || 0, Icon: Trophy, color: COLORS.accent.gold },
    { label: 'Entries', value: stats?.active_entries || 0, Icon: Zap, color: COLORS.accent.purple },
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

      {/* Stats Grid */}
      <div className="grid grid-cols-3 gap-2.5">
        {statCards.map(({ label, value, Icon, color }) => (
          <div key={label} className="text-center p-3.5 rounded-xl transition-all" style={{ background: COLORS.background.card, border: `1px solid ${color}18` }}>
            <Icon size={18} color={color} className="mx-auto mb-1.5" strokeWidth={1.5} />
            <div className="text-xl font-bold" style={{ color, fontFamily: "'Rajdhani', sans-serif" }}>{value.toLocaleString()}</div>
            <div className="text-[10px] font-medium mt-0.5" style={{ color: COLORS.text.tertiary }}>{label}</div>
          </div>
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
              className="flex items-center gap-2.5 p-3 rounded-xl text-left transition-all"
              style={{ background: COLORS.background.card, border: `1px solid ${color}18` }}>
              <Icon size={16} color={color} />
              <span className="text-xs font-semibold text-white">{label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Admin Workflow Guide */}
      <div className="p-4 rounded-xl" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
        <h3 className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: COLORS.text.tertiary }}>Admin Workflow</h3>
        <div className="space-y-2.5">
          {[
            { step: 1, text: 'Create questions with bilingual text & points', tab: 'content', color: COLORS.info.main },
            { step: 2, text: 'Build templates (1 Full Match required)', tab: 'content', color: COLORS.warning.main },
            { step: 3, text: 'Create match & assign templates', tab: 'matches', color: COLORS.success.main },
            { step: 4, text: 'Create contests (fee + prize pool)', tab: 'matches', color: COLORS.accent.gold },
            { step: 5, text: 'Set match LIVE when it starts', tab: 'matches', color: '#FF4444' },
            { step: 6, text: 'Resolve questions & finalize prizes', tab: 'resolve', color: COLORS.accent.purple },
          ].map(({ step, text, tab, color }) => (
            <button key={step} onClick={() => onNavigate(tab)} className="flex items-center gap-3 w-full text-left">
              <div className="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0" style={{ background: color + '22', color }}>
                {step}
              </div>
              <span className="text-xs" style={{ color: COLORS.text.secondary }}>{text}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
