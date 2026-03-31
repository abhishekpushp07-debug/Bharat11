/**
 * CelebrationOverlay — WORLD'S BEST Cricket Celebrations
 * Canvas-based particle engine + Framer Motion for IPL broadcast quality
 * 
 * SIX: 200 fire embers, golden explosion, screen shake, "MAXIMUM!" 
 * FOUR: Blue light beams, wave particles, "BOUNDARY!" momentum slide
 * WICKET: Stumps shattering, dust debris, red flash, "WICKET!" slam
 * PRIZE: 300 gold confetti with physics, firework bursts, "WINNER!"
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { playCelebrationSound } from './CelebrationSounds';

// ============ CANVAS PARTICLE ENGINE ============
class Particle {
  constructor(x, y, config) {
    this.x = x;
    this.y = y;
    const angle = config.angle ?? (Math.random() * Math.PI * 2);
    const speed = config.speed ?? (2 + Math.random() * 8);
    this.vx = Math.cos(angle) * speed * (config.speedX ?? 1);
    this.vy = Math.sin(angle) * speed * (config.speedY ?? 1);
    this.gravity = config.gravity ?? 0.15;
    this.friction = config.friction ?? 0.98;
    this.life = 1;
    this.decay = config.decay ?? (0.008 + Math.random() * 0.012);
    this.size = config.size ?? (2 + Math.random() * 4);
    this.color = config.color;
    this.rotation = Math.random() * 360;
    this.rotSpeed = (Math.random() - 0.5) * 10;
    this.shape = config.shape ?? 'circle'; // circle, rect, ember, stump, confetti
    this.trail = config.trail ?? false;
    this.prevX = x;
    this.prevY = y;
    this.wind = config.wind ?? 0;
    this.wobble = config.wobble ?? 0;
    this.wobblePhase = Math.random() * Math.PI * 2;
  }

  update() {
    this.prevX = this.x;
    this.prevY = this.y;
    this.vx *= this.friction;
    this.vy *= this.friction;
    this.vy += this.gravity;
    this.vx += this.wind;
    if (this.wobble) {
      this.wobblePhase += 0.05;
      this.vx += Math.sin(this.wobblePhase) * this.wobble;
    }
    this.x += this.vx;
    this.y += this.vy;
    this.life -= this.decay;
    this.rotation += this.rotSpeed;
    return this.life > 0;
  }

  draw(ctx) {
    const alpha = Math.max(0, this.life);
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.translate(this.x, this.y);
    ctx.rotate((this.rotation * Math.PI) / 180);

    if (this.trail && alpha > 0.3) {
      ctx.beginPath();
      ctx.strokeStyle = this.color;
      ctx.lineWidth = this.size * 0.5;
      ctx.globalAlpha = alpha * 0.3;
      ctx.moveTo(0, 0);
      ctx.lineTo(this.prevX - this.x, this.prevY - this.y);
      ctx.stroke();
      ctx.globalAlpha = alpha;
    }

    if (this.shape === 'ember') {
      // Fire ember — elongated, glowing
      const grad = ctx.createRadialGradient(0, 0, 0, 0, 0, this.size * 1.5);
      grad.addColorStop(0, this.color);
      grad.addColorStop(0.4, this.color);
      grad.addColorStop(1, 'transparent');
      ctx.fillStyle = grad;
      ctx.fillRect(-this.size * 1.5, -this.size * 0.5, this.size * 3, this.size);
    } else if (this.shape === 'stump') {
      // Stump piece
      ctx.fillStyle = this.color;
      ctx.fillRect(-2, -this.size, 4, this.size * 2);
      ctx.fillStyle = '#8B6914';
      ctx.fillRect(-2, -this.size, 4, this.size * 0.3);
    } else if (this.shape === 'confetti') {
      // Confetti — flat rectangle that tumbles
      ctx.fillStyle = this.color;
      const w = this.size * 1.2;
      const h = this.size * 0.6;
      ctx.fillRect(-w / 2, -h / 2, w, h);
    } else if (this.shape === 'spark') {
      // Tiny bright spark
      ctx.fillStyle = '#fff';
      ctx.shadowColor = this.color;
      ctx.shadowBlur = this.size * 3;
      ctx.beginPath();
      ctx.arc(0, 0, this.size * 0.4, 0, Math.PI * 2);
      ctx.fill();
    } else if (this.shape === 'firework') {
      // Star-like firework particle
      ctx.fillStyle = this.color;
      ctx.shadowColor = this.color;
      ctx.shadowBlur = this.size * 4;
      ctx.beginPath();
      for (let i = 0; i < 5; i++) {
        const a = (i * 72 * Math.PI) / 180;
        const r = i % 2 === 0 ? this.size : this.size * 0.4;
        ctx.lineTo(Math.cos(a) * r, Math.sin(a) * r);
      }
      ctx.closePath();
      ctx.fill();
    } else {
      // Circle (default)
      ctx.fillStyle = this.color;
      ctx.shadowColor = this.color;
      ctx.shadowBlur = this.size * 2;
      ctx.beginPath();
      ctx.arc(0, 0, this.size, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  }
}

class ParticleEngine {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.particles = [];
    this.running = false;
    this.onComplete = null;
  }

  resize() {
    this.canvas.width = this.canvas.offsetWidth * (window.devicePixelRatio || 1);
    this.canvas.height = this.canvas.offsetHeight * (window.devicePixelRatio || 1);
    this.ctx.scale(window.devicePixelRatio || 1, window.devicePixelRatio || 1);
  }

  emit(count, config) {
    const cx = config.x ?? this.canvas.offsetWidth / 2;
    const cy = config.y ?? this.canvas.offsetHeight / 2;
    for (let i = 0; i < count; i++) {
      const angle = config.angleRange
        ? config.angleRange[0] + Math.random() * (config.angleRange[1] - config.angleRange[0])
        : Math.random() * Math.PI * 2;
      const color = Array.isArray(config.colors)
        ? config.colors[Math.floor(Math.random() * config.colors.length)]
        : config.color ?? '#FFD700';
      this.particles.push(new Particle(cx, cy, { ...config, angle, color }));
    }
  }

  // Emit from top (confetti rain)
  emitRain(count, config) {
    const w = this.canvas.offsetWidth;
    for (let i = 0; i < count; i++) {
      const x = Math.random() * w;
      const y = -20 - Math.random() * 100;
      const color = Array.isArray(config.colors)
        ? config.colors[Math.floor(Math.random() * config.colors.length)]
        : '#FFD700';
      this.particles.push(new Particle(x, y, {
        ...config,
        angle: Math.PI / 2 + (Math.random() - 0.5) * 0.5,
        speed: 1 + Math.random() * 2,
        color,
      }));
    }
  }

  // Firework burst at random position
  firework(x, y, colors) {
    for (let i = 0; i < 40; i++) {
      const angle = (Math.PI * 2 * i) / 40;
      const color = colors[Math.floor(Math.random() * colors.length)];
      this.particles.push(new Particle(x, y, {
        angle,
        speed: 3 + Math.random() * 5,
        gravity: 0.08,
        friction: 0.96,
        decay: 0.015 + Math.random() * 0.01,
        size: 2 + Math.random() * 3,
        color,
        shape: 'firework',
        trail: true,
      }));
    }
  }

  start() {
    this.running = true;
    this.resize();
    this.loop();
  }

  stop() {
    this.running = false;
  }

  loop = () => {
    if (!this.running) return;
    const ctx = this.ctx;
    const w = this.canvas.offsetWidth;
    const h = this.canvas.offsetHeight;
    ctx.clearRect(0, 0, w * 2, h * 2);
    ctx.setTransform(1, 0, 0, 1, 0, 0);

    this.particles = this.particles.filter(p => p.update());
    this.particles.forEach(p => p.draw(ctx));

    if (this.particles.length > 0 || this.running) {
      requestAnimationFrame(this.loop);
    } else {
      this.onComplete?.();
    }
  };
}

// ============ CELEBRATION CONFIGS ============
const CELEBRATIONS = {
  six: {
    duration: 3500,
    number: '6',
    title: 'MAXIMUM!',
    subtitle: 'OUT OF THE PARK',
    gradient: 'linear-gradient(135deg, #FFD700, #FF6B00, #FF3B3B, #FF0000)',
    textGlow: '#FFD700',
    bgFlash: 'rgba(255, 150, 0, 0.4)',
    shakeIntensity: 12,
    particles: (engine) => {
      const cx = engine.canvas.offsetWidth / 2;
      const cy = engine.canvas.offsetHeight / 2;
      const fireColors = ['#FFD700', '#FF6B00', '#FF3B3B', '#FFA500', '#FFCC00', '#FF4500', '#FF8C00', '#FFFFFF'];
      // Wave 1: Central explosion — fire embers
      engine.emit(120, {
        x: cx, y: cy,
        colors: fireColors,
        speed: 12 + Math.random() * 6,
        gravity: 0.12,
        friction: 0.97,
        decay: 0.006,
        size: 4,
        shape: 'ember',
        trail: true,
      });
      // Wave 2: Sparks (brighter, faster)
      setTimeout(() => {
        engine.emit(80, {
          x: cx, y: cy,
          colors: ['#FFFFFF', '#FFE4B5', '#FFD700', '#FFFACD'],
          speed: 15 + Math.random() * 5,
          gravity: 0.08,
          friction: 0.95,
          decay: 0.012,
          size: 2,
          shape: 'spark',
          trail: true,
        });
      }, 100);
      // Wave 3: Slow floating embers
      setTimeout(() => {
        engine.emit(60, {
          x: cx, y: cy,
          colors: fireColors,
          speed: 3 + Math.random() * 4,
          gravity: -0.03,
          friction: 0.99,
          decay: 0.004,
          size: 3,
          shape: 'ember',
          wobble: 0.3,
        });
      }, 400);
    },
  },

  four: {
    duration: 3000,
    number: '4',
    title: 'BOUNDARY!',
    subtitle: 'RACING TO THE FENCE',
    gradient: 'linear-gradient(135deg, #00D4FF, #007AFF, #0040FF, #00D4FF)',
    textGlow: '#00D4FF',
    bgFlash: 'rgba(0, 180, 255, 0.35)',
    shakeIntensity: 10,
    particles: (engine) => {
      const cx = engine.canvas.offsetWidth / 2;
      const cy = engine.canvas.offsetHeight / 2;
      const w = engine.canvas.offsetWidth;
      const blueColors = ['#00D4FF', '#007AFF', '#0040FF', '#00BFFF', '#1E90FF', '#87CEEB', '#FFFFFF', '#00FFFF'];
      // Wave 1: Massive central explosion — electric blue embers
      engine.emit(140, {
        x: cx, y: cy,
        colors: blueColors,
        speed: 14 + Math.random() * 5,
        gravity: 0.1,
        friction: 0.97,
        decay: 0.006,
        size: 4,
        shape: 'ember',
        trail: true,
      });
      // Wave 2: Bright white sparks
      setTimeout(() => {
        engine.emit(60, {
          x: cx, y: cy,
          colors: ['#FFFFFF', '#E0F7FF', '#B3E8FF', '#00FFFF'],
          speed: 16,
          gravity: 0.06,
          friction: 0.95,
          decay: 0.012,
          size: 2.5,
          shape: 'spark',
          trail: true,
        });
      }, 80);
      // Wave 3: Horizontal sweep particles (boundary feel)
      setTimeout(() => {
        for (let side = -1; side <= 1; side += 2) {
          engine.emit(30, {
            x: cx, y: cy,
            colors: blueColors,
            angleRange: side > 0 ? [-0.3, 0.3] : [Math.PI - 0.3, Math.PI + 0.3],
            speed: 12,
            speedX: 2,
            speedY: 0.3,
            gravity: 0.04,
            friction: 0.98,
            decay: 0.005,
            size: 3.5,
            shape: 'ember',
            trail: true,
          });
        }
      }, 150);
      // Wave 4: Floating blue particles (ambient)
      setTimeout(() => {
        engine.emit(40, {
          x: cx, y: cy,
          colors: blueColors,
          speed: 3,
          gravity: -0.02,
          friction: 0.99,
          decay: 0.004,
          size: 2.5,
          shape: 'circle',
          wobble: 0.4,
        });
      }, 300);
    },
  },

  wicket: {
    duration: 3200,
    number: 'W',
    title: 'WICKET!',
    subtitle: 'TIMBER!',
    gradient: 'linear-gradient(135deg, #FF3B3B, #DC2626, #7F1D1D, #450A0A)',
    textGlow: '#FF3B3B',
    bgFlash: 'rgba(220, 38, 38, 0.45)',
    shakeIntensity: 18,
    particles: (engine) => {
      const cx = engine.canvas.offsetWidth / 2;
      const cy = engine.canvas.offsetHeight * 0.5;
      const redColors = ['#DC2626', '#EF4444', '#B91C1C', '#FF6B6B', '#991B1B', '#7F1D1D'];
      // Stump pieces flying
      engine.emit(12, {
        x: cx, y: cy,
        colors: ['#D4A574', '#C4954A', '#8B6914', '#A67B3D'],
        speed: 8,
        gravity: 0.25,
        friction: 0.97,
        decay: 0.005,
        size: 15,
        shape: 'stump',
      });
      // Dust/debris
      engine.emit(100, {
        x: cx, y: cy,
        colors: [...redColors, '#D4A574', '#8B6914', '#555'],
        speed: 10,
        gravity: 0.18,
        friction: 0.96,
        decay: 0.007,
        size: 3,
        shape: 'circle',
        trail: false,
      });
      // Red sparks
      setTimeout(() => {
        engine.emit(50, {
          x: cx, y: cy,
          colors: ['#FF3B3B', '#FF0000', '#FF6666', '#FFFFFF'],
          speed: 12,
          gravity: 0.05,
          friction: 0.95,
          decay: 0.015,
          size: 2,
          shape: 'spark',
          trail: true,
        });
      }, 100);
    },
  },

  prize: {
    duration: 4000,
    number: '1st',
    title: 'CHAMPION!',
    subtitle: 'VICTORY ROYALE',
    gradient: 'linear-gradient(135deg, #FFD700, #FFA500, #FF8C00, #FFD700)',
    textGlow: '#FFD700',
    bgFlash: 'rgba(255, 215, 0, 0.2)',
    shakeIntensity: 4,
    particles: (engine) => {
      const w = engine.canvas.offsetWidth;
      const h = engine.canvas.offsetHeight;
      const goldColors = ['#FFD700', '#FFA500', '#FFCC00', '#FFE066', '#F5C542', '#DAA520', '#FFB347', '#CD853F'];
      const festiveColors = [...goldColors, '#FF3B3B', '#22c55e', '#a855f7', '#3b82f6', '#ec4899', '#06b6d4'];
      // Confetti rain wave 1
      engine.emitRain(150, {
        colors: festiveColors,
        gravity: 0.06,
        friction: 0.995,
        decay: 0.003,
        size: 6,
        shape: 'confetti',
        wobble: 0.5,
        wind: (Math.random() - 0.5) * 0.1,
      });
      // Confetti wave 2
      setTimeout(() => {
        engine.emitRain(100, {
          colors: festiveColors,
          gravity: 0.05,
          friction: 0.995,
          decay: 0.003,
          size: 5,
          shape: 'confetti',
          wobble: 0.4,
          wind: (Math.random() - 0.5) * 0.1,
        });
      }, 500);
      // Firework bursts
      setTimeout(() => engine.firework(w * 0.3, h * 0.3, goldColors), 300);
      setTimeout(() => engine.firework(w * 0.7, h * 0.25, festiveColors), 700);
      setTimeout(() => engine.firework(w * 0.5, h * 0.2, goldColors), 1200);
      // Gold sparkles from center
      setTimeout(() => {
        engine.emit(40, {
          x: w / 2, y: h / 2,
          colors: ['#FFD700', '#FFFFFF', '#FFCC00'],
          speed: 5,
          gravity: -0.02,
          friction: 0.99,
          decay: 0.006,
          size: 2,
          shape: 'spark',
        });
      }, 400);
    },
  },
};

// ============ SCREEN SHAKE ============
function useScreenShake(intensity, duration = 500) {
  const [shake, setShake] = useState({ x: 0, y: 0 });
  const frameRef = useRef(null);

  useEffect(() => {
    if (!intensity) return;
    const start = Date.now();
    const animate = () => {
      const elapsed = Date.now() - start;
      if (elapsed > duration) {
        setShake({ x: 0, y: 0 });
        return;
      }
      const progress = 1 - elapsed / duration;
      const amp = intensity * progress;
      setShake({
        x: (Math.random() - 0.5) * amp * 2,
        y: (Math.random() - 0.5) * amp * 2,
      });
      frameRef.current = requestAnimationFrame(animate);
    };
    frameRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frameRef.current);
  }, [intensity, duration]);

  return shake;
}

// ============ SHOCKWAVE RINGS (SVG) ============
function ShockwaveRings({ color, count = 3 }) {
  return (
    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
      {Array.from({ length: count }, (_, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full"
          style={{
            border: `2.5px solid ${color}`,
            width: 40, height: 40,
            boxShadow: `0 0 20px ${color}44, inset 0 0 20px ${color}22`,
          }}
          initial={{ scale: 0, opacity: 0.9 }}
          animate={{ scale: 18 + i * 5, opacity: 0 }}
          transition={{ duration: 1 + i * 0.15, delay: i * 0.08, ease: 'easeOut' }}
        />
      ))}
    </div>
  );
}

// ============ LIGHT RAYS (for SIX) ============
function LightRays({ color }) {
  return (
    <div className="absolute inset-0 flex items-center justify-center pointer-events-none overflow-hidden">
      {Array.from({ length: 12 }, (_, i) => (
        <motion.div
          key={i}
          className="absolute"
          style={{
            width: '3px',
            height: '120%',
            background: `linear-gradient(to bottom, transparent, ${color}33, transparent)`,
            transformOrigin: 'center center',
            transform: `rotate(${i * 30}deg)`,
          }}
          initial={{ opacity: 0, scaleY: 0 }}
          animate={{ opacity: [0, 0.6, 0], scaleY: [0, 1, 1.2] }}
          transition={{ duration: 1, delay: 0.1 + i * 0.03, ease: 'easeOut' }}
        />
      ))}
    </div>
  );
}

// ============ BOUNDARY STREAK (for FOUR) ============
function BoundaryStreaks() {
  return (
    <>
      {[0, 1, 2].map(i => (
        <motion.div
          key={i}
          className="absolute"
          style={{
            left: '-110%',
            top: `${42 + i * 4}%`,
            width: '220%',
            height: `${3 - i}px`,
            background: `linear-gradient(90deg, transparent 0%, #00D4FF${i === 0 ? 'CC' : '66'} 30%, #007AFF${i === 0 ? 'FF' : '88'} 50%, #00D4FF${i === 0 ? 'CC' : '66'} 70%, transparent 100%)`,
            boxShadow: i === 0 ? '0 0 30px #007AFF88, 0 0 60px #00D4FF44' : 'none',
          }}
          initial={{ x: '-100%', opacity: 0 }}
          animate={{ x: '100%', opacity: [0, 1, 1, 0] }}
          transition={{ duration: 0.5, delay: i * 0.06, ease: [0.22, 0.61, 0.36, 1] }}
        />
      ))}
    </>
  );
}

// ============ MAIN COMPONENT ============
export default function CelebrationOverlay({ type, onComplete }) {
  const canvasRef = useRef(null);
  const engineRef = useRef(null);
  const [phase, setPhase] = useState('flash'); // flash -> main -> fadeout
  const [visible, setVisible] = useState(true);
  const config = CELEBRATIONS[type] || CELEBRATIONS.six;
  const shake = useScreenShake(phase === 'flash' ? config.shakeIntensity : 0, 600);

  const dismiss = useCallback(() => {
    setVisible(false);
    engineRef.current?.stop();
    onComplete?.();
  }, [onComplete]);

  useEffect(() => {
    // Phase transitions
    const t1 = setTimeout(() => setPhase('main'), 150);
    const t2 = setTimeout(() => setPhase('fadeout'), config.duration - 500);
    const t3 = setTimeout(dismiss, config.duration);
    return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3); };
  }, [config.duration, dismiss]);

  useEffect(() => {
    if (!canvasRef.current) return;
    const engine = new ParticleEngine(canvasRef.current);
    engineRef.current = engine;
    engine.start();
    // Fire particles after a tiny delay for the flash to register
    setTimeout(() => config.particles(engine), 80);
    // Play celebration sound effect
    playCelebrationSound(type);
    return () => engine.stop();
  }, [type]);

  if (!visible) return null;

  return (
    <AnimatePresence>
      <motion.div
        data-testid={`celebration-${type}`}
        className="fixed inset-0 z-[200] pointer-events-none overflow-hidden"
        style={{
          transform: `translate(${shake.x}px, ${shake.y}px)`,
        }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.15 }}>

        {/* Canvas particle layer */}
        <canvas
          ref={canvasRef}
          className="absolute inset-0 w-full h-full"
          style={{ zIndex: 1 }}
        />

        {/* Screen flash */}
        <motion.div
          className="absolute inset-0"
          style={{ background: config.bgFlash, zIndex: 0 }}
          initial={{ opacity: 0 }}
          animate={{ opacity: phase === 'flash' ? [0, 1, 0.3] : 0 }}
          transition={{ duration: 0.25 }}
        />

        {/* Radial glow */}
        <motion.div
          className="absolute inset-0"
          style={{
            background: `radial-gradient(circle at 50% 50%, ${config.textGlow}30 0%, ${config.textGlow}10 30%, transparent 65%)`,
            zIndex: 0,
          }}
          initial={{ scale: 0 }}
          animate={{ scale: phase === 'main' ? [0.3, 2] : 2, opacity: phase === 'fadeout' ? 0 : 1 }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
        />

        {/* Shockwave rings */}
        {phase !== 'fadeout' && <ShockwaveRings color={config.textGlow} count={4} />}

        {/* Type-specific effects */}
        {type === 'six' && <LightRays color="#FFD700" />}
        {type === 'four' && (
          <>
            <LightRays color="#00D4FF" />
            <BoundaryStreaks />
          </>
        )}

        {/* Dark vignette for WICKET */}
        {type === 'wicket' && (
          <motion.div
            className="absolute inset-0"
            style={{
              background: 'radial-gradient(circle at 50% 50%, transparent 30%, rgba(0,0,0,0.6) 100%)',
              zIndex: 0,
            }}
            initial={{ opacity: 0 }}
            animate={{ opacity: phase === 'main' ? 1 : 0 }}
            transition={{ duration: 0.5 }}
          />
        )}

        {/* ======= CENTER BADGE + TEXT ======= */}
        <div className="absolute inset-0 flex flex-col items-center justify-center" style={{ zIndex: 10 }}>
          {/* HUGE number */}
          <motion.div
            className="relative"
            initial={{ scale: 0, opacity: 0 }}
            animate={phase !== 'fadeout' ? {
              scale: [0, 1.6, 1.2],
              opacity: 1,
            } : { scale: 0.8, opacity: 0 }}
            transition={{
              type: 'spring',
              stiffness: 200,
              damping: 12,
              delay: 0.1,
            }}>

            {/* Outer glow ring */}
            <motion.div
              className="absolute -inset-6 rounded-full"
              style={{
                background: `conic-gradient(from 0deg, ${config.textGlow}22, transparent, ${config.textGlow}22, transparent, ${config.textGlow}22, transparent)`,
              }}
              animate={{ rotate: 360 }}
              transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
            />

            {/* Number circle */}
            <div className="relative w-28 h-28 rounded-full flex items-center justify-center"
              style={{
                background: config.gradient,
                boxShadow: `
                  0 0 60px ${config.textGlow}88,
                  0 0 120px ${config.textGlow}44,
                  0 0 200px ${config.textGlow}22,
                  inset 0 0 40px rgba(255,255,255,0.15)
                `,
              }}>
              {/* Inner shimmer */}
              <motion.div
                className="absolute inset-0 rounded-full"
                style={{
                  background: 'linear-gradient(135deg, rgba(255,255,255,0.3) 0%, transparent 50%, rgba(255,255,255,0.1) 100%)',
                }}
                animate={{ rotate: [0, 360] }}
                transition={{ duration: 4, repeat: Infinity, ease: 'linear' }}
              />
              <span className="text-5xl font-black text-white relative z-10"
                style={{
                  fontFamily: "'Rajdhani', sans-serif",
                  textShadow: `0 2px 20px rgba(0,0,0,0.5), 0 0 40px ${config.textGlow}66`,
                }}>
                {config.number}
              </span>
            </div>

            {/* Pulsing glow */}
            <motion.div
              className="absolute -inset-3 rounded-full"
              style={{
                border: `2px solid ${config.textGlow}44`,
                boxShadow: `0 0 30px ${config.textGlow}33`,
              }}
              animate={{
                scale: [1, 1.3, 1],
                opacity: [0.6, 0, 0.6],
              }}
              transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
            />
          </motion.div>

          {/* Title text */}
          {type === 'wicket' ? (
            // SLAM from top with impact shake
            <motion.h1
              className="mt-4 text-3xl font-black tracking-[8px]"
              style={{
                fontFamily: "'Orbitron', sans-serif",
                background: 'linear-gradient(to right, #FF3B3B, #FF6B6B, #FF3B3B)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
                filter: `drop-shadow(0 0 30px #FF3B3B88)`,
              }}
              initial={{ y: -200, scaleY: 3, opacity: 0 }}
              animate={{
                y: [null, 0, 3, -2, 1, 0],
                scaleY: [3, 1, 0.9, 1.05, 1],
                opacity: 1,
              }}
              transition={{ duration: 0.6, delay: 0.2, ease: [0.22, 0.61, 0.36, 1] }}>
              {config.title}
            </motion.h1>
          ) : type === 'four' ? (
            // Slide from left with momentum
            <motion.h1
              className="mt-4 text-3xl font-black tracking-[8px]"
              style={{
                fontFamily: "'Orbitron', sans-serif",
                background: 'linear-gradient(to right, #00D4FF, #007AFF, #00D4FF)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
                filter: `drop-shadow(0 0 30px #007AFF88)`,
              }}
              initial={{ x: -300, opacity: 0, skewX: -25 }}
              animate={{
                x: [null, 0],
                opacity: 1,
                skewX: [null, 8, -3, 0],
              }}
              transition={{ duration: 0.5, delay: 0.15, ease: [0.22, 0.61, 0.36, 1] }}>
              {config.title}
            </motion.h1>
          ) : (
            // SIX / PRIZE: Scale explosion
            <motion.h1
              className="mt-4 text-3xl font-black tracking-[8px]"
              style={{
                fontFamily: "'Orbitron', sans-serif",
                background: `linear-gradient(to right, ${config.textGlow}, #fff, ${config.textGlow})`,
                backgroundSize: '200% 100%',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
                filter: `drop-shadow(0 0 30px ${config.textGlow}88)`,
              }}
              initial={{ scale: 0, opacity: 0 }}
              animate={{
                scale: [0, 1.5, 1],
                opacity: 1,
                backgroundPosition: ['0% 50%', '100% 50%'],
              }}
              transition={{ duration: 0.6, delay: 0.2, ease: [0.34, 1.56, 0.64, 1] }}>
              {config.title}
            </motion.h1>
          )}

          {/* Subtitle */}
          <motion.p
            className="mt-1 text-xs font-bold tracking-[4px] uppercase"
            style={{
              color: `${config.textGlow}88`,
              fontFamily: "'Orbitron', sans-serif",
            }}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: phase === 'fadeout' ? 0 : 0.7, y: 0 }}
            transition={{ delay: 0.5, duration: 0.4 }}>
            {config.subtitle}
          </motion.p>
        </div>

        {/* Fadeout overlay */}
        {phase === 'fadeout' && (
          <motion.div
            className="absolute inset-0 bg-black"
            style={{ zIndex: 20 }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.8 }}
            transition={{ duration: 0.5 }}
          />
        )}
      </motion.div>
    </AnimatePresence>
  );
}
