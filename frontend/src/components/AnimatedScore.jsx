/**
 * AnimatedScore — Live score number transition animation
 * Numbers slide up when score changes, with neon glow pulse
 */
import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export function AnimatedScore({ value, className = '', style = {}, glowColor = '#FFD700' }) {
  const [displayValue, setDisplayValue] = useState(value);
  const [isChanging, setIsChanging] = useState(false);
  const prevValue = useRef(value);

  useEffect(() => {
    if (value !== prevValue.current) {
      setIsChanging(true);
      const t = setTimeout(() => {
        setDisplayValue(value);
        prevValue.current = value;
      }, 150);
      const t2 = setTimeout(() => setIsChanging(false), 600);
      return () => { clearTimeout(t); clearTimeout(t2); };
    }
  }, [value]);

  return (
    <span className={`inline-flex items-center relative ${className}`} style={style}>
      <AnimatePresence mode="popLayout">
        <motion.span
          key={displayValue}
          initial={{ y: 20, opacity: 0, filter: 'blur(4px)' }}
          animate={{
            y: 0,
            opacity: 1,
            filter: 'blur(0px)',
            textShadow: isChanging
              ? `0 0 20px ${glowColor}88, 0 0 40px ${glowColor}44`
              : '0 0 0px transparent',
          }}
          exit={{ y: -20, opacity: 0, filter: 'blur(4px)' }}
          transition={{ duration: 0.3, ease: [0.22, 0.61, 0.36, 1] }}>
          {displayValue}
        </motion.span>
      </AnimatePresence>
      {isChanging && (
        <motion.span
          className="absolute inset-0 rounded"
          style={{ boxShadow: `0 0 12px ${glowColor}44` }}
          initial={{ opacity: 0 }}
          animate={{ opacity: [0, 0.6, 0] }}
          transition={{ duration: 0.5 }}
        />
      )}
    </span>
  );
}

/**
 * ScoreBadge — Animated score display for match cards
 * Shows runs/wickets with overs, glows on update
 */
export function ScoreBadge({ runs, wickets, overs, teamColor = '#FFD700', compact = false }) {
  return (
    <span className={`inline-flex items-baseline gap-0.5 font-black ${compact ? 'text-xs' : 'text-sm'}`}
      style={{ fontFamily: "'Rajdhani', sans-serif", color: '#fff' }}>
      <AnimatedScore value={runs || 0} glowColor={teamColor} />
      <span style={{ color: 'rgba(255,255,255,0.4)' }}>/</span>
      <AnimatedScore value={wickets || 0} glowColor={teamColor} />
      {overs && (
        <span className="text-[10px] font-medium ml-1" style={{ color: 'rgba(255,255,255,0.5)' }}>
          ({overs})
        </span>
      )}
    </span>
  );
}
