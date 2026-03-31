/**
 * CelebrationOverlay — World's Best Cricket Animations
 * SIX: Fiery explosion, 50+ radial particles, screen flash, stadium roar
 * FOUR: Neon blue boundary streak, fast horizontal sweep
 * WICKET: Stumps shattering, dark red flash, dramatic slam
 * PRIZE: Gold confetti rain, trophy scale-up, rotating light burst
 */
import { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const CONFIGS = {
  six: {
    text: 'MAXIMUM!',
    number: '6',
    gradient: 'linear-gradient(135deg, #FFD700, #FF6B00, #FF3B3B)',
    textGradient: 'linear-gradient(to right, #FFD700, #FF6B00, #FF3B3B)',
    glowColor: '#FF3B3B',
    particleColors: ['#FFD700', '#FF6B00', '#FF3B3B', '#FF8C00', '#FFA500', '#FFCC00', '#FF4500', '#FF0000'],
    particleCount: 50,
    screenFlash: 'rgba(255, 59, 59, 0.25)',
    ringColors: ['#FFD700', '#FF6B00', '#FF3B3B'],
    duration: 2800,
  },
  four: {
    text: 'BOUNDARY!',
    number: '4',
    gradient: 'linear-gradient(135deg, #00D4FF, #007AFF, #0040FF)',
    textGradient: 'linear-gradient(to right, #00D4FF, #007AFF)',
    glowColor: '#007AFF',
    particleColors: ['#00D4FF', '#007AFF', '#0040FF', '#00BFFF', '#1E90FF', '#4169E1'],
    particleCount: 30,
    screenFlash: 'rgba(0, 122, 255, 0.15)',
    ringColors: ['#00D4FF', '#007AFF', '#0040FF'],
    duration: 2200,
  },
  wicket: {
    text: 'WICKET!',
    number: 'W',
    gradient: 'linear-gradient(135deg, #DC2626, #7F1D1D, #450A0A)',
    textGradient: 'linear-gradient(to right, #FF3B3B, #DC2626)',
    glowColor: '#DC2626',
    particleColors: ['#DC2626', '#EF4444', '#B91C1C', '#FF6B6B', '#991B1B', '#7F1D1D'],
    particleCount: 35,
    screenFlash: 'rgba(127, 29, 29, 0.35)',
    ringColors: ['#DC2626', '#EF4444', '#B91C1C'],
    duration: 2600,
  },
  prize: {
    text: 'WINNER!',
    number: '1st',
    gradient: 'linear-gradient(135deg, #FFD700, #FFA500, #FF8C00)',
    textGradient: 'linear-gradient(to right, #FFD700, #FFA500)',
    glowColor: '#FFD700',
    particleColors: ['#FFD700', '#FFA500', '#FFCC00', '#FFE066', '#F5C542', '#DAA520', '#CD853F', '#FFB347'],
    particleCount: 60,
    screenFlash: 'rgba(255, 215, 0, 0.15)',
    ringColors: ['#FFD700', '#FFA500', '#FFCC00'],
    duration: 3200,
  },
};

// Radial particle that shoots outward from center
function RadialParticle({ angle, distance, delay, color, size, config }) {
  const rad = (angle * Math.PI) / 180;
  const tx = Math.cos(rad) * distance;
  const ty = Math.sin(rad) * distance;
  const s = size || (3 + Math.random() * 5);
  const isRect = Math.random() > 0.5;

  return (
    <motion.div
      className="absolute rounded-full"
      style={{
        left: '50%', top: '50%',
        width: `${s}px`, height: isRect ? `${s * 0.5}px` : `${s}px`,
        background: color,
        borderRadius: isRect ? '2px' : '50%',
        boxShadow: `0 0 ${s * 3}px ${color}`,
        marginLeft: `-${s / 2}px`,
        marginTop: `-${s / 2}px`,
      }}
      initial={{ x: 0, y: 0, opacity: 1, scale: 1 }}
      animate={{
        x: tx,
        y: ty,
        opacity: [1, 1, 0],
        scale: [0, 1.5, 0.5],
        rotate: Math.random() * 720,
      }}
      transition={{
        duration: 0.8 + Math.random() * 0.6,
        delay: delay,
        ease: 'easeOut',
      }}
    />
  );
}

// Expanding shock ring
function ShockRing({ delay, color, maxSize }) {
  return (
    <motion.div
      className="absolute left-1/2 top-1/2 rounded-full"
      style={{
        border: `2px solid ${color}`,
        marginLeft: '-10px', marginTop: '-10px',
        width: '20px', height: '20px',
      }}
      initial={{ scale: 0, opacity: 0.8 }}
      animate={{ scale: maxSize || 15, opacity: 0 }}
      transition={{ duration: 0.9, delay, ease: 'easeOut' }}
    />
  );
}

// Screen flash overlay
function ScreenFlash({ color }) {
  return (
    <motion.div
      className="absolute inset-0"
      style={{ background: color }}
      initial={{ opacity: 0 }}
      animate={{ opacity: [0, 1, 0] }}
      transition={{ duration: 0.4, times: [0, 0.2, 1] }}
    />
  );
}

// Flying stump for WICKET
function FlyingStump({ index }) {
  const directions = [
    { x: -60, y: -120, rotate: -45 },
    { x: 10, y: -140, rotate: 15 },
    { x: 70, y: -100, rotate: 55 },
  ];
  const dir = directions[index] || directions[0];

  return (
    <motion.div
      className="absolute"
      style={{
        left: '50%', bottom: '45%',
        width: '4px', height: '40px',
        background: 'linear-gradient(to bottom, #D4A574, #8B6914)',
        borderRadius: '2px',
        marginLeft: `${(index - 1) * 12}px`,
        transformOrigin: 'bottom center',
        boxShadow: '0 0 8px rgba(212, 165, 116, 0.5)',
      }}
      initial={{ y: 0, x: 0, rotate: 0, opacity: 1 }}
      animate={{
        y: dir.y,
        x: dir.x,
        rotate: dir.rotate + (Math.random() * 60 - 30),
        opacity: [1, 1, 0],
      }}
      transition={{ duration: 1, delay: 0.2, ease: 'easeOut' }}
    />
  );
}

// Bail piece for WICKET
function FlyingBail({ index }) {
  return (
    <motion.div
      className="absolute"
      style={{
        left: '50%', bottom: '48%',
        width: '16px', height: '3px',
        background: '#D4A574',
        borderRadius: '2px',
        marginLeft: `${index * 8 - 8}px`,
        boxShadow: '0 0 6px rgba(212, 165, 116, 0.6)',
      }}
      initial={{ y: 0, x: 0, rotate: 0, opacity: 1 }}
      animate={{
        y: -(100 + Math.random() * 80),
        x: (index === 0 ? -50 : 50) + Math.random() * 40,
        rotate: 360 + Math.random() * 360,
        opacity: [1, 1, 0],
      }}
      transition={{ duration: 1.1, delay: 0.15, ease: 'easeOut' }}
    />
  );
}

// Boundary streak for FOUR
function BoundaryStreak({ color }) {
  return (
    <motion.div
      className="absolute"
      style={{
        left: '-100%', top: '45%',
        width: '200%', height: '3px',
        background: `linear-gradient(90deg, transparent, ${color}, ${color}, transparent)`,
        boxShadow: `0 0 20px ${color}, 0 0 40px ${color}66`,
      }}
      initial={{ x: '-100%', opacity: 0 }}
      animate={{ x: '100%', opacity: [0, 1, 1, 0] }}
      transition={{ duration: 0.6, ease: 'easeInOut' }}
    />
  );
}

// Confetti piece for PRIZE
function ConfettiPiece({ delay, color }) {
  const left = Math.random() * 100;
  const size = 4 + Math.random() * 8;
  const isRect = Math.random() > 0.3;

  return (
    <motion.div
      className="absolute"
      style={{
        left: `${left}%`,
        width: isRect ? `${size}px` : `${size * 0.6}px`,
        height: isRect ? `${size * 0.5}px` : `${size}px`,
        background: color,
        borderRadius: isRect ? '1px' : '50%',
        boxShadow: `0 0 ${size}px ${color}66`,
      }}
      initial={{ y: -20, rotate: 0, opacity: 0 }}
      animate={{
        y: typeof window !== 'undefined' ? window.innerHeight + 50 : 900,
        rotate: Math.random() * 1080,
        x: (Math.random() - 0.5) * 100,
        opacity: [0, 1, 1, 1, 0],
      }}
      transition={{
        duration: 2.5 + Math.random() * 1.5,
        delay: delay,
        ease: [0.22, 0.61, 0.36, 1],
      }}
    />
  );
}

// Rotating light burst for PRIZE
function LightBurst({ color }) {
  return (
    <motion.div
      className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2"
      style={{
        width: '300px', height: '300px',
        background: `conic-gradient(from 0deg, transparent, ${color}15, transparent, ${color}15, transparent, ${color}15, transparent)`,
        borderRadius: '50%',
      }}
      animate={{ rotate: 360 }}
      transition={{ duration: 4, repeat: Infinity, ease: 'linear' }}
    />
  );
}

export default function CelebrationOverlay({ type, onComplete }) {
  const [visible, setVisible] = useState(true);
  const config = CONFIGS[type] || CONFIGS.six;

  // Generate particles once
  const particles = useMemo(() => {
    return Array.from({ length: config.particleCount }, (_, i) => ({
      angle: (360 / config.particleCount) * i + Math.random() * 15,
      distance: 80 + Math.random() * 160,
      delay: Math.random() * 0.15,
      color: config.particleColors[i % config.particleColors.length],
      size: 3 + Math.random() * 6,
    }));
  }, [type]);

  const confettiPieces = useMemo(() => {
    if (type !== 'prize') return [];
    return Array.from({ length: 60 }, (_, i) => ({
      delay: Math.random() * 1.5,
      color: config.particleColors[i % config.particleColors.length],
    }));
  }, [type]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
      onComplete?.();
    }, config.duration);
    return () => clearTimeout(timer);
  }, [config.duration, onComplete]);

  if (!visible) return null;

  return (
    <AnimatePresence>
      <motion.div
        data-testid={`celebration-${type}`}
        className="fixed inset-0 z-[200] flex items-center justify-center pointer-events-none overflow-hidden"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.2 }}>

        {/* Screen flash */}
        <ScreenFlash color={config.screenFlash} />

        {/* Ambient glow */}
        <motion.div
          className="absolute inset-0"
          style={{
            background: `radial-gradient(circle at 50% 50%, ${config.glowColor}25 0%, transparent 60%)`,
          }}
          initial={{ scale: 0.5, opacity: 0 }}
          animate={{ scale: [0.5, 1.5, 1.2], opacity: [0, 0.8, 0.4] }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
        />

        {/* WICKET-specific: Stumps + Bails */}
        {type === 'wicket' && (
          <>
            {[0, 1, 2].map(i => <FlyingStump key={`stump-${i}`} index={i} />)}
            {[0, 1].map(i => <FlyingBail key={`bail-${i}`} index={i} />)}
          </>
        )}

        {/* FOUR-specific: Boundary streak */}
        {type === 'four' && (
          <>
            <BoundaryStreak color="#00D4FF" />
            <motion.div
              className="absolute"
              style={{
                left: '-100%', top: '48%',
                width: '200%', height: '1px',
                background: `linear-gradient(90deg, transparent, #007AFF44, transparent)`,
              }}
              initial={{ x: '-100%' }}
              animate={{ x: '100%' }}
              transition={{ duration: 0.7, delay: 0.1, ease: 'easeInOut' }}
            />
          </>
        )}

        {/* PRIZE-specific: Light burst + Confetti */}
        {type === 'prize' && (
          <>
            <LightBurst color={config.glowColor} />
            {confettiPieces.map((p, i) => (
              <ConfettiPiece key={`conf-${i}`} delay={p.delay} color={p.color} />
            ))}
          </>
        )}

        {/* Shock rings */}
        {config.ringColors.map((c, i) => (
          <ShockRing key={`ring-${i}`} delay={i * 0.1} color={c} maxSize={12 + i * 4} />
        ))}

        {/* Radial particles */}
        {particles.map((p, i) => (
          <RadialParticle key={`p-${i}`} {...p} config={config} />
        ))}

        {/* Center badge */}
        <motion.div
          className="relative flex flex-col items-center z-10"
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: [0, 1.4, 1], opacity: 1 }}
          transition={{
            type: 'spring',
            stiffness: 300,
            damping: 15,
            delay: 0.05,
          }}>

          {/* Number circle */}
          <motion.div
            className="relative w-24 h-24 rounded-full flex items-center justify-center"
            style={{
              background: config.gradient,
              boxShadow: `0 0 60px ${config.glowColor}66, 0 0 120px ${config.glowColor}33, inset 0 0 30px rgba(255,255,255,0.1)`,
            }}
            animate={{
              boxShadow: [
                `0 0 60px ${config.glowColor}66, 0 0 120px ${config.glowColor}33`,
                `0 0 80px ${config.glowColor}88, 0 0 160px ${config.glowColor}55`,
                `0 0 60px ${config.glowColor}66, 0 0 120px ${config.glowColor}33`,
              ],
            }}
            transition={{ duration: 1.5, repeat: 1, ease: 'easeInOut' }}>

            {/* Inner glow */}
            <div className="absolute inset-1 rounded-full"
              style={{ background: 'radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%)' }} />

            <span className="text-4xl font-black text-white relative z-10"
              style={{ fontFamily: "'Rajdhani', sans-serif", textShadow: '0 2px 12px rgba(0,0,0,0.5)' }}>
              {config.number}
            </span>
          </motion.div>

          {/* Title text */}
          <motion.div
            className="mt-3"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.4, ease: 'easeOut' }}>

            {type === 'wicket' ? (
              // WICKET: Slam from top with screen shake
              <motion.span
                className="text-2xl font-black tracking-[6px] block"
                style={{
                  fontFamily: "'Orbitron', sans-serif",
                  background: config.textGradient,
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                  filter: `drop-shadow(0 0 20px ${config.glowColor}88)`,
                }}
                initial={{ y: -100, scaleY: 2 }}
                animate={{
                  y: [null, 0],
                  scaleY: [2, 1],
                  x: [0, -4, 4, -3, 3, -1, 1, 0],
                }}
                transition={{
                  y: { duration: 0.3, ease: 'easeOut' },
                  scaleY: { duration: 0.3, ease: 'easeOut' },
                  x: { duration: 0.5, delay: 0.3, ease: 'easeOut' },
                }}>
                {config.text}
              </motion.span>
            ) : type === 'four' ? (
              // FOUR: Slide from left with skew
              <motion.span
                className="text-2xl font-black tracking-[6px] block"
                style={{
                  fontFamily: "'Orbitron', sans-serif",
                  background: config.textGradient,
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                  filter: `drop-shadow(0 0 20px ${config.glowColor}88)`,
                }}
                initial={{ x: -200, opacity: 0, skewX: -20 }}
                animate={{ x: 0, opacity: 1, skewX: [null, 5, 0] }}
                transition={{ duration: 0.5, ease: [0.22, 0.61, 0.36, 1] }}>
                {config.text}
              </motion.span>
            ) : (
              // SIX / PRIZE: Scale bounce
              <motion.span
                className="text-2xl font-black tracking-[6px] block"
                style={{
                  fontFamily: "'Orbitron', sans-serif",
                  background: config.textGradient,
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                  filter: `drop-shadow(0 0 20px ${config.glowColor}88)`,
                }}
                initial={{ scale: 0 }}
                animate={{ scale: [0, 1.3, 1] }}
                transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}>
                {config.text}
              </motion.span>
            )}
          </motion.div>
        </motion.div>

        {/* Fade out */}
        <motion.div
          className="absolute inset-0 bg-black"
          initial={{ opacity: 0 }}
          animate={{ opacity: 0 }}
          transition={{ delay: config.duration / 1000 - 0.4, duration: 0.4 }}
          onAnimationComplete={() => {}}
        />
      </motion.div>
    </AnimatePresence>
  );
}
