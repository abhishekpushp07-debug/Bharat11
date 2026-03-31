/**
 * CelebrationOverlay — Heavy animations for sixes, wickets, fours
 * Shows dramatic visual effects overlaid on the screen
 */
import { useState, useEffect } from 'react';

const CELEBRATION_TYPES = {
  six: {
    emoji: '6',
    title: 'MAXIMUM!',
    particles: 12,
    colors: ['#FF3B3B', '#FF6B6B', '#FFD700', '#f97316', '#ef4444'],
    bgGlow: 'radial-gradient(circle, rgba(255,59,59,0.3) 0%, transparent 70%)',
    ringColor: '#FF3B3B',
  },
  four: {
    emoji: '4',
    title: 'BOUNDARY!',
    particles: 8,
    colors: ['#3b82f6', '#60a5fa', '#22c55e', '#06b6d4', '#818cf8'],
    bgGlow: 'radial-gradient(circle, rgba(59,130,246,0.25) 0%, transparent 70%)',
    ringColor: '#3b82f6',
  },
  wicket: {
    emoji: 'W',
    title: 'WICKET!',
    particles: 10,
    colors: ['#a855f7', '#c084fc', '#f472b6', '#e879f9', '#d946ef'],
    bgGlow: 'radial-gradient(circle, rgba(168,85,247,0.25) 0%, transparent 70%)',
    ringColor: '#a855f7',
  },
};

function Particle({ delay, color, type }) {
  const angle = Math.random() * 360;
  const distance = 80 + Math.random() * 120;
  const size = 3 + Math.random() * 5;
  const duration = 0.8 + Math.random() * 0.6;
  const shape = Math.random() > 0.5 ? '50%' : '2px';

  return (
    <div
      className="absolute"
      style={{
        left: '50%', top: '50%',
        width: `${size}px`, height: `${size}px`,
        borderRadius: shape,
        background: color,
        animation: `celebParticle ${duration}s ease-out ${delay}s forwards`,
        '--angle': `${angle}deg`,
        '--dist': `${distance}px`,
        boxShadow: `0 0 ${size * 2}px ${color}88`,
      }}
    />
  );
}

function ShockRing({ delay, color }) {
  return (
    <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full"
      style={{
        width: '20px', height: '20px',
        border: `2px solid ${color}`,
        animation: `celebRing 0.8s ease-out ${delay}s forwards`,
        opacity: 0,
      }}
    />
  );
}

export default function CelebrationOverlay({ type, onComplete }) {
  const [visible, setVisible] = useState(true);
  const config = CELEBRATION_TYPES[type] || CELEBRATION_TYPES.six;

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
      onComplete?.();
    }, 2200);
    return () => clearTimeout(timer);
  }, [onComplete]);

  if (!visible) return null;

  return (
    <div data-testid={`celebration-${type}`}
      className="fixed inset-0 z-[100] flex items-center justify-center pointer-events-none"
      style={{ animation: 'celebFadeOut 0.4s ease-in 1.8s forwards' }}>

      {/* Background glow */}
      <div className="absolute inset-0" style={{ background: config.bgGlow, animation: 'celebPulse 0.6s ease-out' }} />

      {/* Shock rings */}
      <ShockRing delay={0} color={config.ringColor} />
      <ShockRing delay={0.1} color={`${config.ringColor}88`} />
      <ShockRing delay={0.2} color={`${config.ringColor}44`} />

      {/* Particles */}
      {Array.from({ length: config.particles }).map((_, i) => (
        <Particle key={i} delay={i * 0.03} color={config.colors[i % config.colors.length]} type={type} />
      ))}

      {/* Center badge */}
      <div className="relative flex flex-col items-center" style={{ animation: 'celebBounceIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards' }}>
        <div className="w-20 h-20 rounded-full flex items-center justify-center shadow-2xl"
          style={{
            background: `linear-gradient(135deg, ${config.colors[0]}, ${config.colors[1]})`,
            boxShadow: `0 0 40px ${config.ringColor}66, 0 0 80px ${config.ringColor}33`,
          }}>
          <span className="text-3xl font-black text-white" style={{ fontFamily: "'Rajdhani', sans-serif", textShadow: '0 2px 8px rgba(0,0,0,0.5)' }}>
            {config.emoji}
          </span>
        </div>
        <div className="mt-2 text-lg font-black tracking-[4px] text-white"
          style={{ fontFamily: "'Orbitron', sans-serif", textShadow: `0 0 20px ${config.ringColor}88` }}>
          {config.title}
        </div>
      </div>
    </div>
  );
}
