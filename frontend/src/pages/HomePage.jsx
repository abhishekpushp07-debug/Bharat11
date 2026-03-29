import { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';
import apiClient from '../api/client';
import { COLORS } from '../constants/design';
import { Coins, ChevronRight, Clock, Users, Trophy } from 'lucide-react';

export default function HomePage() {
  const { user } = useAuthStore();
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchMatches(); }, []);

  const fetchMatches = async () => {
    try {
      // Matches API will be in Stage 6, using seed data for now
      setLoading(false);
    } catch (e) {
      setLoading(false);
    }
  };

  const formatTime = (d) => {
    const date = new Date(d);
    const now = new Date();
    const diff = date - now;
    const hours = Math.floor(diff / 3600000);
    const mins = Math.floor((diff % 3600000) / 60000);
    if (diff < 0) return 'LIVE';
    if (hours > 24) return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
    return `${hours}h ${mins}m`;
  };

  // Team color mappings
  const TEAM_COLORS = {
    MI: ['#004BA0', '#00599E'], CSK: ['#F9CD05', '#F3A012'],
    RCB: ['#D4213D', '#A0171F'], KKR: ['#3A225D', '#552583'],
    DC: ['#0078BC', '#17479E'], PBKS: ['#ED1B24', '#AA1019'],
    SRH: ['#FF822A', '#E35205'], RR: ['#EA1A85', '#C51D70'],
    GT: ['#1C1C2B', '#0B4F6C'], LSG: ['#2E90A8', '#1B7B93'],
  };

  const getTeamGrad = (short) => {
    const c = TEAM_COLORS[short] || ['#555', '#333'];
    return `linear-gradient(135deg, ${c[0]}, ${c[1]})`;
  };

  // Demo matches from seed data
  const demoMatches = [
    { id: 1, team_a: { name: 'Mumbai Indians', short_name: 'MI' }, team_b: { name: 'Chennai Super Kings', short_name: 'CSK' }, venue: 'Wankhede Stadium', status: 'upcoming', start_time: new Date(Date.now() + 7200000).toISOString(), contests_count: 3 },
    { id: 2, team_a: { name: 'Royal Challengers', short_name: 'RCB' }, team_b: { name: 'Kolkata Knight Riders', short_name: 'KKR' }, venue: 'Chinnaswamy Stadium', status: 'upcoming', start_time: new Date(Date.now() + 86400000).toISOString(), contests_count: 3 },
    { id: 3, team_a: { name: 'Delhi Capitals', short_name: 'DC' }, team_b: { name: 'Punjab Kings', short_name: 'PBKS' }, venue: 'Arun Jaitley Stadium', status: 'upcoming', start_time: new Date(Date.now() + 172800000).toISOString(), contests_count: 3 },
  ];

  return (
    <div data-testid="home-page" className="pb-4 space-y-4">
      {/* Greeting + Balance Bar */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Hey, {user?.username || 'Player'}!</h1>
          <p className="text-xs mt-0.5" style={{ color: COLORS.text.secondary }}>Predict & Win Virtual Coins</p>
        </div>
        <div data-testid="home-balance" className="flex items-center gap-1.5 px-3 py-1.5 rounded-full" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
          <Coins size={14} color="#FFD700" />
          <span className="text-sm font-bold text-white" style={{ fontFamily: "'Rajdhani', sans-serif" }}>{(user?.coins_balance || 0).toLocaleString()}</span>
        </div>
      </div>

      {/* Live / Upcoming Section */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-base font-semibold text-white">Upcoming Matches</h2>
          <span className="text-xs" style={{ color: COLORS.text.tertiary }}>{demoMatches.length} matches</span>
        </div>

        <div className="space-y-3">
          {demoMatches.map(match => (
            <div data-testid={`match-card-${match.id}`} key={match.id} className="rounded-2xl overflow-hidden" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
              {/* Match Header */}
              <div className="px-4 py-2.5 flex items-center justify-between" style={{ borderBottom: `1px solid ${COLORS.border.light}` }}>
                <span className="text-xs font-medium" style={{ color: COLORS.text.secondary }}>{match.venue}</span>
                <div className="flex items-center gap-1.5">
                  <Clock size={12} color={COLORS.warning.main} />
                  <span className="text-xs font-semibold" style={{ color: COLORS.warning.main }}>{formatTime(match.start_time)}</span>
                </div>
              </div>

              {/* Teams */}
              <div className="px-4 py-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-11 h-11 rounded-xl flex items-center justify-center text-sm font-black text-white" style={{ background: getTeamGrad(match.team_a.short_name) }}>
                    {match.team_a.short_name}
                  </div>
                  <div>
                    <div className="text-sm font-bold text-white">{match.team_a.short_name}</div>
                    <div className="text-xs" style={{ color: COLORS.text.tertiary }}>{match.team_a.name}</div>
                  </div>
                </div>

                <div className="px-3 py-1 rounded-lg text-xs font-bold" style={{ background: COLORS.primary.gradient, color: '#fff' }}>VS</div>

                <div className="flex items-center gap-3 flex-row-reverse">
                  <div className="w-11 h-11 rounded-xl flex items-center justify-center text-sm font-black text-white" style={{ background: getTeamGrad(match.team_b.short_name) }}>
                    {match.team_b.short_name}
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold text-white">{match.team_b.short_name}</div>
                    <div className="text-xs" style={{ color: COLORS.text.tertiary }}>{match.team_b.name}</div>
                  </div>
                </div>
              </div>

              {/* Footer */}
              <div className="px-4 py-2.5 flex items-center justify-between" style={{ background: COLORS.background.tertiary }}>
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1">
                    <Trophy size={12} color={COLORS.accent.gold} />
                    <span className="text-xs" style={{ color: COLORS.text.secondary }}>{match.contests_count} Contests</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Users size={12} color={COLORS.info.main} />
                    <span className="text-xs" style={{ color: COLORS.text.secondary }}>Open</span>
                  </div>
                </div>
                <div className="flex items-center gap-1 text-xs font-semibold" style={{ color: COLORS.primary.main }}>
                  Predict Now <ChevronRight size={14} />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Hot Contests Section */}
      <div>
        <h2 className="text-base font-semibold text-white mb-3">Hot Contests</h2>
        <div className="space-y-2">
          {[
            { name: 'Free Contest', fee: 0, pool: 1000, participants: '0/100' },
            { name: 'Mini Contest', fee: 100, pool: 5000, participants: '0/50' },
            { name: 'Mega Contest', fee: 500, pool: 25000, participants: '0/100' },
          ].map((c, i) => (
            <div data-testid={`contest-card-${i}`} key={i} className="flex items-center justify-between p-3.5 rounded-xl" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
              <div>
                <div className="text-sm font-semibold text-white">{c.name}</div>
                <div className="flex items-center gap-3 mt-1">
                  <span className="text-xs" style={{ color: COLORS.text.secondary }}>Entry: {c.fee === 0 ? 'FREE' : `${c.fee} coins`}</span>
                  <span className="text-xs" style={{ color: COLORS.accent.gold }}>Pool: {c.pool.toLocaleString()}</span>
                </div>
              </div>
              <button className="px-3 py-1.5 rounded-lg text-xs font-bold" style={{ background: c.fee === 0 ? COLORS.success.bg : COLORS.primary.gradient, color: c.fee === 0 ? COLORS.success.main : '#fff' }}>
                {c.fee === 0 ? 'FREE' : 'Join'}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
