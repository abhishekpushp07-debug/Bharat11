/**
 * WORLD'S BEST AI Commentary — ESPN+ meets Instagram Stories
 * Immersive cricket commentary with phase analysis, momentum, timeline
 */
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { COLORS } from '../constants/design';
import { Radio, TrendingUp, Zap, Target, Crown, Activity, Star, ChevronDown, ChevronUp } from 'lucide-react';

const EVENT_ICONS = {
  six: { emoji: '6', color: '#F59E0B', label: 'SIX', Icon: Zap },
  four: { emoji: '4', color: '#3B82F6', label: 'FOUR', Icon: TrendingUp },
  wicket: { emoji: 'W', color: '#EF4444', label: 'WICKET', Icon: Target },
  milestone: { emoji: '★', color: '#10B981', label: 'MILESTONE', Icon: Crown },
  bowling: { emoji: '●', color: '#8B5CF6', label: 'BOWLING', Icon: Activity },
  dramatic: { emoji: '!', color: '#A855F7', label: 'KEY', Icon: Star },
};

const MOOD_BG = {
  thriller: '#A855F7', domination: '#3B82F6', upset: '#EF4444',
  classic: '#10B981', heartbreak: '#6366F1',
};

const PHASE_LABELS = {
  powerplay: { label: 'POWERPLAY', overs: '1-6', color: '#3B82F6', icon: Zap },
  middle: { label: 'MIDDLE OVERS', overs: '7-15', color: '#F59E0B', icon: Activity },
  death: { label: 'DEATH OVERS', overs: '16-20', color: '#EF4444', icon: Target },
};

// Categorize moments into phases
function categorizeMoments(moments) {
  const phases = { powerplay: [], middle: [], death: [] };
  for (const m of moments) {
    const over = parseFloat(m.over) || 0;
    if (over <= 6) phases.powerplay.push(m);
    else if (over <= 15) phases.middle.push(m);
    else phases.death.push(m);
  }
  return phases;
}

// Calculate momentum score from key moments
function calculateMomentum(moments) {
  if (!moments.length) return null;
  let score = 50; // neutral
  for (const m of moments) {
    if (m.event_type === 'six') score += m.impact === 'high' ? 8 : 4;
    else if (m.event_type === 'four') score += m.impact === 'high' ? 5 : 2;
    else if (m.event_type === 'wicket') score -= m.impact === 'high' ? 10 : 5;
    else if (m.event_type === 'milestone') score += 6;
    else if (m.event_type === 'bowling') score -= 6;
  }
  return Math.min(100, Math.max(0, score));
}

export default function AICommentaryTab({ data, loading, onCelebrate }) {
  const [activeSection, setActiveSection] = useState('story');
  const [expandedPhase, setExpandedPhase] = useState(null);

  if (loading) return (
    <div className="flex justify-center py-10">
      <div className="w-7 h-7 border-2 rounded-full animate-spin" style={{ borderColor: `${COLORS.primary.main}30`, borderTopColor: COLORS.primary.main }} />
    </div>
  );

  const ai = data?.ai || {};
  const matchPulse = ai.match_pulse;
  const keyMoments = ai.key_moments || [];
  const starPerformers = ai.star_performers || [];
  const turningPoint = ai.turning_point;
  const verdict = ai.verdict;
  const rawCommentary = ai.raw_commentary || ai.commentary || [];
  const scorecard = data?.scorecard?.scorecard || [];

  const hasStructured = matchPulse || keyMoments.length > 0;
  const hasAnyData = hasStructured || rawCommentary.length > 0 || scorecard.length > 0;

  if (!hasAnyData) {
    return (
      <div className="text-center py-14 rounded-2xl relative overflow-hidden" style={{ background: COLORS.background.card }}>
        <div className="absolute inset-0 opacity-5" style={{ background: 'radial-gradient(circle at 50% 30%, #FF3B3B, transparent 70%)' }} />
        <Radio size={36} color={COLORS.text.tertiary} className="mx-auto mb-3 animate-float" />
        <p className="text-sm font-semibold text-white">Commentary Coming Soon</p>
        <p className="text-xs mt-1" style={{ color: COLORS.text.tertiary }}>Available once the match starts</p>
      </div>
    );
  }

  if (!hasStructured) {
    // Fallback raw
    const items = rawCommentary.length > 0 ? rawCommentary : buildFromScorecard(scorecard);
    if (!items.length) {
      return (
        <div className="text-center py-14 rounded-2xl" style={{ background: COLORS.background.card }}>
          <Radio size={36} color={COLORS.text.tertiary} className="mx-auto mb-3 animate-float" />
          <p className="text-sm font-semibold text-white">Commentary Coming Soon</p>
        </div>
      );
    }
    return <RawCommentaryFallback items={items} />;
  }

  const phasedMoments = categorizeMoments(keyMoments);
  const momentum = calculateMomentum(keyMoments);
  const sixCount = keyMoments.filter(m => m.event_type === 'six').length;
  const wicketCount = keyMoments.filter(m => m.event_type === 'wicket').length;

  const tabs = [
    { key: 'story', label: 'Match Story' },
    { key: 'phases', label: 'Phase Analysis' },
    { key: 'moments', label: `Timeline (${keyMoments.length})` },
    { key: 'stars', label: 'MVPs' },
  ];

  return (
    <div data-testid="ai-commentary" className="space-y-4">
      {/* Tab Switcher — Pill style */}
      <div className="flex rounded-xl overflow-hidden" style={{ background: '#141414', border: '1px solid rgba(255,255,255,0.06)' }}>
        {tabs.map(tab => (
          <button key={tab.key} data-testid={`commentary-tab-${tab.key}`}
            onClick={() => setActiveSection(tab.key)}
            className="flex-1 py-2.5 text-[11px] font-bold transition-all relative"
            style={{
              color: activeSection === tab.key ? '#fff' : COLORS.text.tertiary,
              background: activeSection === tab.key ? COLORS.primary.main : 'transparent',
              borderRadius: activeSection === tab.key ? '10px' : '0',
            }}>
            {tab.label}
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {/* ===== MATCH STORY ===== */}
        {activeSection === 'story' && (
          <motion.div key="story" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}
            className="space-y-3">

            {/* Match Pulse Hero */}
            {matchPulse && (
              <div data-testid="match-pulse" className="rounded-2xl overflow-hidden relative">
                <div className="absolute inset-0" style={{ background: 'linear-gradient(160deg, #0d1117 0%, #161b22 50%, #0d1117 100%)' }} />
                <div className="absolute inset-0 opacity-10" style={{
                  background: 'radial-gradient(ellipse at 30% 20%, #FF3B3B, transparent 50%), radial-gradient(ellipse at 70% 80%, #3B82F6, transparent 50%)'
                }} />
                <div className="relative p-5 space-y-3">
                  <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full animate-live-pulse" style={{ background: COLORS.primary.main }} />
                    <span className="text-[9px] font-black tracking-[0.2em] uppercase" style={{ color: COLORS.primary.main }}>MATCH PULSE</span>
                  </div>
                  <h2 className="text-lg font-black text-white leading-tight" style={{ fontFamily: "'Rajdhani', sans-serif" }}>
                    {matchPulse.headline}
                  </h2>
                  <p className="text-xs leading-relaxed" style={{ color: COLORS.text.secondary }}>{matchPulse.sub}</p>
                  {(matchPulse.team_a_score || matchPulse.team_b_score) && (
                    <div className="flex items-center gap-3 pt-1">
                      {matchPulse.team_a_score && (
                        <div className="px-3 py-1.5 rounded-lg text-xs font-bold text-white" style={{ background: 'rgba(255,255,255,0.08)' }}>
                          {matchPulse.team_a_score}
                        </div>
                      )}
                      <span className="text-[10px] font-bold" style={{ color: COLORS.text.tertiary }}>vs</span>
                      {matchPulse.team_b_score && (
                        <div className="px-3 py-1.5 rounded-lg text-xs font-bold text-white" style={{ background: 'rgba(255,255,255,0.08)' }}>
                          {matchPulse.team_b_score}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Momentum + Quick Stats Bar */}
            <div className="grid grid-cols-3 gap-2">
              <div className="p-3 rounded-xl text-center" style={{ background: '#141414', border: '1px solid rgba(245,158,11,0.15)' }}>
                <div className="text-xl font-black" style={{ color: '#F59E0B', fontFamily: "'Rajdhani', sans-serif" }}>{sixCount}</div>
                <div className="text-[8px] font-bold tracking-wider" style={{ color: 'rgba(255,255,255,0.3)' }}>SIXES</div>
              </div>
              <div className="p-3 rounded-xl text-center" style={{ background: '#141414', border: '1px solid rgba(239,68,68,0.15)' }}>
                <div className="text-xl font-black" style={{ color: '#EF4444', fontFamily: "'Rajdhani', sans-serif" }}>{wicketCount}</div>
                <div className="text-[8px] font-bold tracking-wider" style={{ color: 'rgba(255,255,255,0.3)' }}>WICKETS</div>
              </div>
              {momentum !== null && (
                <div className="p-3 rounded-xl text-center" style={{
                  background: '#141414',
                  border: `1px solid ${momentum > 60 ? 'rgba(16,185,129,0.15)' : momentum < 40 ? 'rgba(239,68,68,0.15)' : 'rgba(255,255,255,0.08)'}`,
                }}>
                  <div className="text-xl font-black" style={{
                    color: momentum > 60 ? '#10B981' : momentum < 40 ? '#EF4444' : '#F59E0B',
                    fontFamily: "'Rajdhani', sans-serif",
                  }}>{momentum}</div>
                  <div className="text-[8px] font-bold tracking-wider" style={{ color: 'rgba(255,255,255,0.3)' }}>MOMENTUM</div>
                </div>
              )}
            </div>

            {/* Top 5 Key Moments */}
            {keyMoments.slice(0, 5).map((moment, i) => (
              <MomentCard key={i} moment={moment} index={i} onCelebrate={onCelebrate} showOver />
            ))}

            {/* Turning Point */}
            {turningPoint && <TurningPointCard tp={turningPoint} />}

            {/* Verdict */}
            {verdict && <VerdictCard verdict={verdict} />}
          </motion.div>
        )}

        {/* ===== PHASE ANALYSIS ===== */}
        {activeSection === 'phases' && (
          <motion.div key="phases" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}
            className="space-y-3">

            {Object.entries(PHASE_LABELS).map(([phase, meta]) => {
              const moments = phasedMoments[phase] || [];
              const isExpanded = expandedPhase === phase;
              const phaseSixes = moments.filter(m => m.event_type === 'six').length;
              const phaseWickets = moments.filter(m => m.event_type === 'wicket').length;
              const highImpact = moments.filter(m => m.impact === 'high').length;
              const PhaseIcon = meta.icon;

              return (
                <div key={phase} data-testid={`phase-${phase}`} className="rounded-2xl overflow-hidden"
                  style={{ background: '#141414', border: `1px solid ${meta.color}20` }}>
                  <button onClick={() => setExpandedPhase(isExpanded ? null : phase)}
                    className="w-full p-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl flex items-center justify-center"
                        style={{ background: `${meta.color}15`, border: `1px solid ${meta.color}30` }}>
                        <PhaseIcon size={18} color={meta.color} />
                      </div>
                      <div className="text-left">
                        <div className="text-xs font-black tracking-wider" style={{ color: meta.color }}>{meta.label}</div>
                        <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>Overs {meta.overs}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-2 text-[10px]">
                        {phaseSixes > 0 && <span className="font-bold" style={{ color: '#F59E0B' }}>{phaseSixes}x6</span>}
                        {phaseWickets > 0 && <span className="font-bold" style={{ color: '#EF4444' }}>{phaseWickets}W</span>}
                        {highImpact > 0 && <span className="font-bold" style={{ color: '#A855F7' }}>{highImpact} key</span>}
                      </div>
                      <div className="w-6 h-6 rounded-lg flex items-center justify-center"
                        style={{ background: 'rgba(255,255,255,0.04)' }}>
                        {isExpanded ? <ChevronUp size={14} color={COLORS.text.tertiary} /> : <ChevronDown size={14} color={COLORS.text.tertiary} />}
                      </div>
                    </div>
                  </button>

                  <AnimatePresence>
                    {isExpanded && (
                      <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }}
                        className="overflow-hidden">
                        <div className="px-4 pb-4 space-y-2" style={{ borderTop: `1px solid ${meta.color}15` }}>
                          {moments.length > 0 ? moments.map((m, i) => (
                            <MomentCard key={i} moment={m} index={i} compact onCelebrate={onCelebrate} showOver />
                          )) : (
                            <div className="text-center py-4 text-[11px]" style={{ color: COLORS.text.tertiary }}>
                              No key moments in this phase
                            </div>
                          )}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              );
            })}

            {/* Momentum Bar */}
            {momentum !== null && (
              <div className="p-4 rounded-2xl" style={{ background: '#141414', border: '1px solid rgba(255,255,255,0.06)' }}>
                <div className="text-[9px] font-black tracking-[0.15em] uppercase mb-3" style={{ color: COLORS.text.tertiary }}>
                  BATTING MOMENTUM
                </div>
                <div className="relative h-3 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.06)' }}>
                  <div className="absolute inset-y-0 left-0 rounded-full transition-all" style={{
                    width: `${momentum}%`,
                    background: momentum > 60 ? 'linear-gradient(90deg, #10B981, #34D399)' :
                      momentum < 40 ? 'linear-gradient(90deg, #EF4444, #F87171)' :
                        'linear-gradient(90deg, #F59E0B, #FBBF24)',
                    boxShadow: `0 0 12px ${momentum > 60 ? '#10B98155' : momentum < 40 ? '#EF444455' : '#F59E0B55'}`,
                  }} />
                  {/* Center marker */}
                  <div className="absolute top-0 bottom-0 left-1/2 w-px" style={{ background: 'rgba(255,255,255,0.2)' }} />
                </div>
                <div className="flex justify-between mt-2 text-[9px] font-semibold" style={{ color: COLORS.text.tertiary }}>
                  <span>Bowling</span>
                  <span style={{ color: momentum > 60 ? '#10B981' : momentum < 40 ? '#EF4444' : '#F59E0B' }}>
                    {momentum > 60 ? 'Batting Dominant' : momentum < 40 ? 'Bowling Dominant' : 'Even Contest'}
                  </span>
                  <span>Batting</span>
                </div>
              </div>
            )}
          </motion.div>
        )}

        {/* ===== FULL TIMELINE ===== */}
        {activeSection === 'moments' && (
          <motion.div key="moments" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}
            className="space-y-1">
            {/* Timeline spine */}
            <div className="relative">
              {keyMoments.map((moment, i) => (
                <TimelineMoment key={i} moment={moment} index={i} isLast={i === keyMoments.length - 1} onCelebrate={onCelebrate} />
              ))}
              {keyMoments.length === 0 && (
                <div className="text-center py-8 text-sm" style={{ color: COLORS.text.tertiary }}>No moments recorded yet</div>
              )}
            </div>
          </motion.div>
        )}

        {/* ===== STAR PERFORMERS ===== */}
        {activeSection === 'stars' && (
          <motion.div key="stars" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}
            className="space-y-3">
            {starPerformers.map((star, i) => (
              <StarPerformerCard key={i} star={star} index={i} />
            ))}
            {starPerformers.length === 0 && (
              <div className="text-center py-8 text-sm" style={{ color: COLORS.text.tertiary }}>Star performers will appear here</div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}


// ===== MOMENT CARD =====
function MomentCard({ moment, index, compact, onCelebrate, showOver }) {
  const ev = EVENT_ICONS[moment.event_type] || EVENT_ICONS.dramatic;
  const isHigh = moment.impact === 'high';
  const hasOver = moment.over && moment.over !== '?';

  return (
    <motion.div
      data-testid={`moment-card-${index}`}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06, duration: 0.35 }}
      className={`event-${moment.event_type} rounded-xl overflow-hidden`}
      style={{ padding: compact ? '10px 12px' : '14px 16px' }}>

      <div className="flex gap-3">
        {/* Over number — OVERSIZED */}
        {showOver && hasOver && (
          <div className="shrink-0 flex flex-col items-center">
            <div className="text-2xl font-black leading-none" style={{
              color: `${ev.color}80`, fontFamily: "'Rajdhani', sans-serif",
              minWidth: '32px', textAlign: 'center',
            }}>
              {moment.over}
            </div>
            <div className="text-[7px] font-bold tracking-wider" style={{ color: COLORS.text.tertiary }}>OVER</div>
          </div>
        )}

        {/* Event badge — clickable for celebration */}
        <div className="shrink-0">
          <button
            data-testid={`moment-trigger-${index}`}
            onClick={() => {
              if (['six', 'four', 'wicket'].includes(moment.event_type) && onCelebrate) {
                onCelebrate(moment.event_type);
              }
            }}
            className={`w-9 h-9 rounded-lg flex items-center justify-center text-xs font-black relative overflow-hidden ${
              moment.event_type === 'six' ? 'six-badge-glow' :
              moment.event_type === 'wicket' ? 'wicket-badge-pulse' :
              moment.event_type === 'four' ? 'four-badge-sweep' : ''
            }`}
            style={{ background: `${ev.color}18`, color: ev.color, border: `1px solid ${ev.color}30` }}>
            {/* Inner glow ring for six/wicket */}
            {(moment.event_type === 'six' || moment.event_type === 'wicket') && isHigh && (
              <span className="absolute inset-0 rounded-lg animate-pulse" style={{
                boxShadow: `inset 0 0 12px ${ev.color}33, 0 0 8px ${ev.color}22`,
              }} />
            )}
            <span className="relative z-10">{ev.emoji}</span>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5">
            <span className="text-[9px] font-black tracking-wider uppercase px-1.5 py-0.5 rounded"
              style={{ background: `${ev.color}18`, color: ev.color }}>
              {ev.label}
            </span>
            {isHigh && (
              <span className="text-[8px] font-bold px-1.5 py-0.5 rounded" style={{ background: '#FF3B3B18', color: '#FF3B3B' }}>
                HIGH IMPACT
              </span>
            )}
          </div>
          <h3 className={`font-bold text-white leading-tight ${compact ? 'text-[12px]' : 'text-sm'}`}>{moment.title}</h3>
          <p className="text-[11px] leading-relaxed mt-0.5" style={{ color: COLORS.text.secondary }}>
            {moment.description}
          </p>
          {moment.player && !compact && (
            <span className="inline-block mt-1 text-[10px] font-semibold px-2 py-0.5 rounded-full"
              style={{ background: 'rgba(255,255,255,0.05)', color: COLORS.text.secondary }}>
              {moment.player}
            </span>
          )}
        </div>
      </div>
    </motion.div>
  );
}


// ===== TIMELINE MOMENT (for full timeline view) =====
function TimelineMoment({ moment, index, isLast, onCelebrate }) {
  const ev = EVENT_ICONS[moment.event_type] || EVENT_ICONS.dramatic;
  const isHigh = moment.impact === 'high';
  const hasOver = moment.over && moment.over !== '?';

  return (
    <motion.div
      data-testid={`timeline-${index}`}
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.04 }}
      className="flex gap-3 pb-3 relative">

      {/* Timeline spine */}
      <div className="flex flex-col items-center shrink-0" style={{ width: '36px' }}>
        {/* Over */}
        {hasOver && (
          <div className="text-lg font-black leading-none mb-1" style={{
            color: `${ev.color}90`, fontFamily: "'Rajdhani', sans-serif",
          }}>
            {moment.over}
          </div>
        )}
        {/* Dot */}
        <div className="w-3 h-3 rounded-full relative z-10" style={{
          background: ev.color,
          boxShadow: isHigh ? `0 0 12px ${ev.color}88` : 'none',
        }}>
          {isHigh && (
            <div className="absolute inset-0 rounded-full animate-live-pulse" style={{
              background: ev.color, opacity: 0.4,
            }} />
          )}
        </div>
        {/* Line */}
        {!isLast && (
          <div className="w-px flex-1 mt-1" style={{ background: `${ev.color}25`, minHeight: '20px' }} />
        )}
      </div>

      {/* Content */}
      <div className={`flex-1 min-w-0 event-${moment.event_type} rounded-xl p-3 mb-1`}>
        <div className="flex items-center gap-2 mb-0.5">
          <span className="text-xs font-bold text-white">{moment.title}</span>
          <span className="text-[9px] font-bold px-1.5 py-0.5 rounded" style={{ background: `${ev.color}18`, color: ev.color }}>
            {ev.label}
          </span>
        </div>
        <p className="text-[11px] leading-relaxed" style={{ color: COLORS.text.secondary }}>
          {moment.description}
        </p>
      </div>
    </motion.div>
  );
}


// ===== TURNING POINT CARD =====
function TurningPointCard({ tp }) {
  return (
    <motion.div data-testid="turning-point"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="rounded-2xl overflow-hidden relative"
      style={{ background: 'linear-gradient(135deg, rgba(168,85,247,0.12), rgba(139,92,246,0.06))', border: '1px solid rgba(168,85,247,0.25)' }}>
      <div className="absolute top-0 right-0 w-24 h-24 rounded-full opacity-10" style={{
        background: 'radial-gradient(circle, #A855F7, transparent)', transform: 'translate(30%, -30%)'
      }} />
      <div className="p-4 space-y-2">
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full" style={{ background: '#A855F7', boxShadow: '0 0 8px #A855F7' }} />
          <span className="text-[9px] font-black tracking-[0.15em] uppercase" style={{ color: '#A855F7' }}>TURNING POINT</span>
          {tp.over && tp.over !== '?' && (
            <span className="text-[9px] px-1.5 py-0.5 rounded" style={{ background: '#A855F722', color: '#A855F7' }}>Ov {tp.over}</span>
          )}
        </div>
        <h3 className="text-sm font-bold text-white">{tp.title}</h3>
        <p className="text-xs leading-relaxed" style={{ color: COLORS.text.secondary }}>{tp.description}</p>
      </div>
    </motion.div>
  );
}


// ===== VERDICT CARD =====
function VerdictCard({ verdict }) {
  const moodColor = MOOD_BG[verdict.mood] || MOOD_BG.classic;

  return (
    <motion.div data-testid="match-verdict"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className={`rounded-2xl overflow-hidden relative verdict-${verdict.mood || 'classic'}`}>
      <div className="p-5 space-y-3">
        <div className="flex items-center gap-2">
          <span className="text-[9px] font-black tracking-[0.2em] uppercase" style={{ color: moodColor }}>VERDICT</span>
          {verdict.mood && (
            <span className="text-[8px] font-bold px-1.5 py-0.5 rounded uppercase"
              style={{ background: `${moodColor}22`, color: moodColor }}>
              {verdict.mood}
            </span>
          )}
        </div>
        <h2 className="text-base font-black text-white leading-tight" style={{ fontFamily: "'Rajdhani', sans-serif" }}>
          {verdict.headline}
        </h2>
        <p className="text-xs leading-relaxed" style={{ color: 'rgba(255,255,255,0.7)' }}>{verdict.description}</p>
      </div>
    </motion.div>
  );
}


// ===== STAR PERFORMER CARD =====
function StarPerformerCard({ star, index }) {
  const ratingPct = Math.min(100, (star.rating || 0) * 10);
  const ratingColor = ratingPct >= 85 ? '#FFD700' : ratingPct >= 70 ? '#10B981' : ratingPct >= 50 ? '#3B82F6' : COLORS.text.secondary;
  const roleColor = star.role === 'batting' ? '#F59E0B' : star.role === 'bowling' ? '#8B5CF6' : '#10B981';

  return (
    <motion.div
      data-testid={`star-${index}`}
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="rounded-2xl overflow-hidden"
      style={{ background: '#141414', border: `1px solid ${ratingColor}20` }}>

      <div className="p-4 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {/* Rank badge */}
            <div className="w-12 h-12 rounded-xl flex items-center justify-center text-lg font-black"
              style={{
                background: index === 0 ? 'linear-gradient(135deg, #FFD700, #FFA500)' :
                  index === 1 ? 'linear-gradient(135deg, #C0C0C0, #A0A0A0)' :
                    `${roleColor}15`,
                color: index < 2 ? '#000' : '#fff',
                border: index >= 2 ? `1px solid ${roleColor}30` : 'none',
              }}>
              {index < 2 ? (index + 1) : star.name?.[0] || '?'}
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">{star.name}</h3>
              <span className="text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded"
                style={{ background: `${roleColor}15`, color: roleColor }}>
                {star.role || 'player'}
              </span>
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-black" style={{ color: ratingColor, fontFamily: "'Rajdhani', sans-serif" }}>
              {star.rating?.toFixed(1) || '—'}
            </div>
            <div className="text-[8px] uppercase font-bold" style={{ color: COLORS.text.tertiary }}>RATING</div>
          </div>
        </div>

        {/* Headline */}
        <p className="text-xs italic" style={{ color: COLORS.text.secondary }}>"{star.headline}"</p>

        {/* Stats */}
        {star.stats && (
          <div className="px-3 py-2 rounded-lg text-xs font-mono font-semibold text-center"
            style={{ background: 'rgba(255,255,255,0.04)', color: '#fff', letterSpacing: '0.05em' }}>
            {star.stats}
          </div>
        )}

        {/* Rating Bar */}
        <div className="h-1 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.08)' }}>
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${ratingPct}%` }}
            transition={{ delay: index * 0.1 + 0.3, duration: 0.8 }}
            className="h-full rounded-full"
            style={{ background: `linear-gradient(90deg, ${ratingColor}88, ${ratingColor})` }}
          />
        </div>
      </div>
    </motion.div>
  );
}


// ===== RAW COMMENTARY FALLBACK =====
function RawCommentaryFallback({ items }) {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2 mb-2">
        <Radio size={14} className="animate-live-pulse" color={COLORS.primary.main} />
        <span className="text-[10px] font-black tracking-[0.15em] uppercase" style={{ color: COLORS.primary.main }}>MATCH HIGHLIGHTS</span>
      </div>
      {items.map((item, i) => {
        const ev = EVENT_ICONS[item.type] || { color: COLORS.text.secondary };
        return (
          <motion.div key={i}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.04 }}
            className={`event-${item.type || 'dramatic'} rounded-xl px-3.5 py-2.5`}>
            <p className="text-xs leading-relaxed text-white">{item.text}</p>
          </motion.div>
        );
      })}
    </div>
  );
}


// Build commentary from scorecard
function buildFromScorecard(scorecard) {
  const items = [];
  for (const inn of scorecard) {
    const batting = inn?.batting || [];
    const bowling = inn?.bowling || [];
    for (const b of batting) {
      const runs = parseInt(b.r) || 0;
      const sixes = parseInt(b['6s']) || 0;
      const fours = parseInt(b['4s']) || 0;
      const balls = parseInt(b.b) || 0;
      if (runs >= 100) items.push({ type: 'milestone', text: `CENTURY! ${b.batsman} smashes ${runs} off ${balls} balls! (${fours}x4, ${sixes}x6)` });
      else if (runs >= 50) items.push({ type: 'milestone', text: `FIFTY! ${b.batsman} scores ${runs}(${balls}) — ${fours} fours, ${sixes} sixes!` });
      if (sixes >= 3) items.push({ type: 'six', text: `${b.batsman} hammers ${sixes} MASSIVE SIXES in his innings of ${runs}!` });
      if (b.dismissal && b.dismissal !== 'not out') items.push({ type: 'wicket', text: `OUT! ${b.batsman} ${runs}(${balls}) — ${b.dismissal}` });
    }
    for (const bw of bowling) {
      if ((parseInt(bw.w) || 0) >= 3) items.push({ type: 'bowling', text: `${bw.bowler} picks up ${bw.w}/${bw.r} in ${bw.o} overs! Lethal spell!` });
    }
  }
  return items;
}
