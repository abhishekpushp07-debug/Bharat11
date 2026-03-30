/**
 * Live Scorecard Component - Rich batting/bowling/catching display
 * Shows 20+ stats from CricketData.org Premium API
 */
import { useState } from 'react';
import { COLORS } from '../constants/design';
import { ChevronDown, ChevronUp, Trophy, Target, Zap, Activity, Award } from 'lucide-react';

export default function ScorecardView({ data, compact = false }) {
  const [expandedInnings, setExpandedInnings] = useState(null);

  if (!data || !data.scorecard?.length) {
    return (
      <div className="text-center py-6" style={{ color: COLORS.text.tertiary }}>
        <Activity size={24} className="mx-auto mb-2 opacity-40" />
        <div className="text-xs">Scorecard not available yet</div>
      </div>
    );
  }

  const m = data.metrics || {};
  const scoreSummary = data.score_summary || [];

  // Key metrics grid
  const keyMetrics = [
    { label: '1st Inn', value: `${m.innings_1_total_runs || 0}/${m.innings_1_total_wickets || 0}`, sub: `${m.innings_1_total_overs || 0} ov`, color: '#60a5fa' },
    { label: '2nd Inn', value: `${m.innings_2_total_runs || 0}/${m.innings_2_total_wickets || 0}`, sub: `${m.innings_2_total_overs || 0} ov`, color: '#34d399' },
    { label: 'Sixes', value: m.match_total_sixes || 0, sub: `${m.innings_1_total_sixes || 0} + ${m.innings_2_total_sixes || 0}`, color: '#f59e0b' },
    { label: 'Fours', value: m.match_total_fours || 0, sub: `${m.innings_1_total_fours || 0} + ${m.innings_2_total_fours || 0}`, color: '#a78bfa' },
    { label: 'Extras', value: m.match_total_extras || 0, sub: `${m.innings_1_extras || 0} + ${m.innings_2_extras || 0}`, color: '#f87171' },
    { label: 'Run Rate', value: `${m.innings_1_run_rate || 0}`, sub: `/ ${m.innings_2_run_rate || 0}`, color: '#38bdf8' },
  ];

  return (
    <div data-testid="scorecard-view" className="space-y-3">
      {/* Match Result Banner */}
      {data.status && (
        <div className="p-3 rounded-xl text-center" style={{ background: m.match_completed ? '#10b98115' : '#f59e0b15', border: `1px solid ${m.match_completed ? '#10b98130' : '#f59e0b30'}` }}>
          <div className="text-xs font-bold" style={{ color: m.match_completed ? '#10b981' : '#f59e0b' }}>
            {data.status}
          </div>
          {data.toss_winner && (
            <div className="text-[10px] mt-1" style={{ color: COLORS.text.tertiary }}>
              Toss: {data.toss_winner} ({data.toss_choice})
            </div>
          )}
        </div>
      )}

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-3 gap-1.5">
        {keyMetrics.map((km, i) => (
          <div key={i} className="p-2.5 rounded-xl text-center" style={{ background: COLORS.background.card, border: `1px solid ${km.color}15` }}>
            <div className="text-[9px] uppercase tracking-wider font-bold" style={{ color: km.color + 'aa' }}>{km.label}</div>
            <div className="text-lg font-black mt-0.5" style={{ color: km.color, fontFamily: "'Rajdhani', sans-serif" }}>{km.value}</div>
            <div className="text-[9px]" style={{ color: COLORS.text.tertiary }}>{km.sub}</div>
          </div>
        ))}
      </div>

      {/* Top Performers */}
      {(m.highest_run_scorer || m.best_bowler) && (
        <div className="grid grid-cols-2 gap-2">
          {m.highest_run_scorer && (
            <div className="p-3 rounded-xl flex items-center gap-2.5" style={{ background: '#f59e0b10', border: '1px solid #f59e0b22' }}>
              <Award size={18} color="#f59e0b" />
              <div>
                <div className="text-[9px] uppercase font-bold" style={{ color: '#f59e0b88' }}>Top Scorer</div>
                <div className="text-xs font-bold text-white">{m.highest_run_scorer}</div>
                <div className="text-[10px] font-bold" style={{ color: '#f59e0b' }}>{m.highest_run_scorer_runs} runs</div>
              </div>
            </div>
          )}
          {m.best_bowler && (
            <div className="p-3 rounded-xl flex items-center gap-2.5" style={{ background: '#a78bfa10', border: '1px solid #a78bfa22' }}>
              <Target size={18} color="#a78bfa" />
              <div>
                <div className="text-[9px] uppercase font-bold" style={{ color: '#a78bfa88' }}>Best Bowler</div>
                <div className="text-xs font-bold text-white">{m.best_bowler}</div>
                <div className="text-[10px] font-bold" style={{ color: '#a78bfa' }}>{m.best_bowler_wickets}w</div>
              </div>
            </div>
          )}
        </div>
      )}

      {compact ? null : (
        /* Detailed Innings Scorecards */
        <div className="space-y-2">
          {(data.scorecard || []).map((innings, idx) => {
            const innNum = idx + 1;
            const isExpanded = expandedInnings === innNum;
            const batting = innings.batting || [];
            const bowling = innings.bowling || [];
            const catching = innings.catching || [];
            const totals = innings.totals || {};
            const extras = innings.extras || {};
            const innName = innings.inning || `Innings ${innNum}`;

            // Calculate totals from data if empty
            const innRuns = totals.R || scoreSummary[idx]?.r || batting.reduce((s, b) => s + (b.r || 0), 0);
            const innWickets = totals.W || scoreSummary[idx]?.w || 0;
            const innOvers = totals.O || scoreSummary[idx]?.o || 0;

            return (
              <div key={idx} className="rounded-xl overflow-hidden" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
                {/* Innings Header */}
                <button
                  data-testid={`innings-${innNum}-toggle`}
                  onClick={() => setExpandedInnings(isExpanded ? null : innNum)}
                  className="w-full flex items-center justify-between p-3"
                >
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded-lg flex items-center justify-center text-[10px] font-black" style={{ background: innNum === 1 ? '#60a5fa22' : '#34d39922', color: innNum === 1 ? '#60a5fa' : '#34d399' }}>
                      {innNum}
                    </div>
                    <div className="text-left">
                      <div className="text-xs font-bold text-white">{innName}</div>
                      <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>
                        {batting.length} batsmen | {bowling.length} bowlers
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="text-right">
                      <div className="text-sm font-black" style={{ color: innNum === 1 ? '#60a5fa' : '#34d399', fontFamily: "'Rajdhani', sans-serif" }}>
                        {innRuns}/{innWickets}
                      </div>
                      <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>{innOvers} ov</div>
                    </div>
                    {isExpanded ? <ChevronUp size={14} color={COLORS.text.tertiary} /> : <ChevronDown size={14} color={COLORS.text.tertiary} />}
                  </div>
                </button>

                {isExpanded && (
                  <div className="border-t" style={{ borderColor: COLORS.border.light }}>
                    {/* BATTING TABLE */}
                    <div className="p-3">
                      <div className="text-[10px] font-bold uppercase tracking-wider mb-2" style={{ color: '#f59e0b88' }}>
                        Batting
                      </div>
                      <div className="overflow-x-auto">
                        <table className="w-full text-[10px]">
                          <thead>
                            <tr style={{ color: COLORS.text.tertiary }}>
                              <th className="text-left py-1 pr-2 font-semibold">Batter</th>
                              <th className="text-right py-1 px-1 font-semibold">R</th>
                              <th className="text-right py-1 px-1 font-semibold">B</th>
                              <th className="text-right py-1 px-1 font-semibold">4s</th>
                              <th className="text-right py-1 px-1 font-semibold">6s</th>
                              <th className="text-right py-1 pl-1 font-semibold">SR</th>
                            </tr>
                          </thead>
                          <tbody>
                            {batting.map((b, bi) => {
                              const name = b.batsman?.name || 'Unknown';
                              const dismissed = !!b.dismissal;
                              const isFifty = b.r >= 50;
                              return (
                                <tr key={bi} className="border-t" style={{ borderColor: COLORS.border.light + '44' }}>
                                  <td className="py-1.5 pr-2">
                                    <div className="font-semibold text-white" style={{ fontSize: '11px' }}>
                                      {name} {isFifty && <Zap size={8} className="inline" color="#f59e0b" />}
                                    </div>
                                    {b['dismissal-text'] && (
                                      <div className="text-[9px] truncate max-w-[140px]" style={{ color: COLORS.text.tertiary }}>
                                        {b['dismissal-text']}
                                      </div>
                                    )}
                                    {!dismissed && (
                                      <div className="text-[9px] font-bold" style={{ color: '#10b981' }}>not out</div>
                                    )}
                                  </td>
                                  <td className="text-right py-1.5 px-1 font-black" style={{ color: isFifty ? '#f59e0b' : '#fff' }}>{b.r}</td>
                                  <td className="text-right py-1.5 px-1" style={{ color: COLORS.text.tertiary }}>{b.b}</td>
                                  <td className="text-right py-1.5 px-1" style={{ color: b['4s'] > 0 ? '#60a5fa' : COLORS.text.tertiary }}>{b['4s']}</td>
                                  <td className="text-right py-1.5 px-1" style={{ color: b['6s'] > 0 ? '#f59e0b' : COLORS.text.tertiary }}>{b['6s']}</td>
                                  <td className="text-right py-1.5 pl-1" style={{ color: b.sr > 150 ? '#10b981' : b.sr < 80 ? '#f87171' : COLORS.text.secondary }}>{b.sr}</td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>

                      {/* Extras */}
                      {(extras.r || extras.w || extras.nb) ? (
                        <div className="mt-2 text-[10px] p-2 rounded-lg" style={{ background: COLORS.background.tertiary, color: COLORS.text.tertiary }}>
                          <span className="font-semibold">Extras:</span> {extras.r || 0} (b {extras.b || 0}, lb {extras.lb || 0}, w {extras.w || 0}, nb {extras.nb || 0})
                        </div>
                      ) : null}
                    </div>

                    {/* BOWLING TABLE */}
                    {bowling.length > 0 && (
                      <div className="p-3 border-t" style={{ borderColor: COLORS.border.light }}>
                        <div className="text-[10px] font-bold uppercase tracking-wider mb-2" style={{ color: '#a78bfa88' }}>
                          Bowling
                        </div>
                        <table className="w-full text-[10px]">
                          <thead>
                            <tr style={{ color: COLORS.text.tertiary }}>
                              <th className="text-left py-1 pr-2 font-semibold">Bowler</th>
                              <th className="text-right py-1 px-1 font-semibold">O</th>
                              <th className="text-right py-1 px-1 font-semibold">M</th>
                              <th className="text-right py-1 px-1 font-semibold">R</th>
                              <th className="text-right py-1 px-1 font-semibold">W</th>
                              <th className="text-right py-1 pl-1 font-semibold">Eco</th>
                            </tr>
                          </thead>
                          <tbody>
                            {bowling.map((bw, bi) => {
                              const hasWickets = bw.w > 0;
                              return (
                                <tr key={bi} className="border-t" style={{ borderColor: COLORS.border.light + '44' }}>
                                  <td className="py-1.5 pr-2 font-semibold text-white" style={{ fontSize: '11px' }}>
                                    {bw.bowler?.name || 'Unknown'}
                                  </td>
                                  <td className="text-right py-1.5 px-1" style={{ color: COLORS.text.tertiary }}>{bw.o}</td>
                                  <td className="text-right py-1.5 px-1" style={{ color: bw.m > 0 ? '#10b981' : COLORS.text.tertiary }}>{bw.m}</td>
                                  <td className="text-right py-1.5 px-1 text-white">{bw.r}</td>
                                  <td className="text-right py-1.5 px-1 font-black" style={{ color: hasWickets ? '#a78bfa' : COLORS.text.tertiary }}>{bw.w}</td>
                                  <td className="text-right py-1.5 pl-1" style={{ color: bw.eco > 10 ? '#f87171' : bw.eco < 7 ? '#10b981' : COLORS.text.secondary }}>{bw.eco}</td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    )}

                    {/* CATCHING/FIELDING */}
                    {catching.length > 0 && (
                      <div className="p-3 border-t" style={{ borderColor: COLORS.border.light }}>
                        <div className="text-[10px] font-bold uppercase tracking-wider mb-1.5" style={{ color: '#38bdf888' }}>
                          Fielding
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                          {catching.map((c, ci) => (
                            <div key={ci} className="text-[10px] px-2 py-1 rounded-lg" style={{ background: COLORS.background.tertiary }}>
                              <span className="text-white font-semibold">{c.catcher?.name || '?'}</span>
                              <span style={{ color: COLORS.text.tertiary }}>
                                {c.catch > 0 && ` ${c.catch}c`}
                                {c.runout > 0 && ` ${c.runout}ro`}
                                {c.stumped > 0 && ` ${c.stumped}st`}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Additional Stats */}
      <div className="grid grid-cols-2 gap-1.5">
        {[
          { l: '1st Inn Highest', v: `${m.innings_1_highest_scorer || '-'} (${m.innings_1_highest_score || 0})` },
          { l: '2nd Inn Highest', v: `${m.innings_2_highest_scorer || '-'} (${m.innings_2_highest_score || 0})` },
          { l: '1st Inn Fifties', v: m.innings_1_fifties || 0 },
          { l: '2nd Inn Fifties', v: m.innings_2_fifties || 0 },
          { l: '1st Inn Ducks', v: m.innings_1_ducks || 0 },
          { l: '1st Inn Maidens', v: m.innings_1_maiden_overs || 0 },
          { l: 'Total Catches', v: (m.innings_1_catches || 0) + (m.innings_2_catches || 0) },
          { l: 'Total Runouts', v: (m.innings_1_runouts || 0) + (m.innings_2_runouts || 0) },
        ].map((s, i) => (
          <div key={i} className="flex justify-between items-center p-2 rounded-lg text-[10px]" style={{ background: COLORS.background.tertiary }}>
            <span style={{ color: COLORS.text.tertiary }}>{s.l}</span>
            <span className="font-bold text-white">{s.v}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
