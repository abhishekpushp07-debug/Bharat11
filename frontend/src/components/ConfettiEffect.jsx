/**
 * ConfettiEffect — Premium Gold Confetti Rain for Celebrations
 * Used in ShareCard (top-3 finishes) and Prize celebrations
 */
import { useEffect, useState, useMemo } from 'react';
import { motion } from 'framer-motion';

const CONFETTI_COLORS = ['#FFD700', '#FFA500', '#FF3B3B', '#22c55e', '#a855f7', '#3b82f6', '#ec4899', '#06b6d4', '#FFCC00', '#FF8C00'];

function ConfettiPiece({ index, total }) {
  const color = CONFETTI_COLORS[index % CONFETTI_COLORS.length];
  const left = (index / total) * 100 + (Math.random() * 10 - 5);
  const delay = Math.random() * 2;
  const duration = 2.5 + Math.random() * 2;
  const size = 4 + Math.random() * 8;
  const isRect = Math.random() > 0.35;
  const swayAmount = (Math.random() - 0.5) * 80;

  return (
    <motion.div
      className="absolute"
      style={{
        left: `${Math.max(0, Math.min(100, left))}%`,
        width: isRect ? `${size}px` : `${size * 0.6}px`,
        height: isRect ? `${size * 0.5}px` : `${size}px`,
        background: color,
        borderRadius: isRect ? '1px' : '50%',
        boxShadow: `0 0 ${size}px ${color}44`,
      }}
      initial={{ y: -20, rotate: 0, opacity: 0 }}
      animate={{
        y: typeof window !== 'undefined' ? window.innerHeight + 30 : 900,
        rotate: Math.random() * 1080 - 540,
        x: swayAmount,
        opacity: [0, 1, 1, 1, 0.5, 0],
      }}
      transition={{
        duration,
        delay,
        ease: [0.22, 0.61, 0.36, 1],
      }}
    />
  );
}

export default function ConfettiEffect({ active = true, count = 50, gold = false }) {
  const [pieces, setPieces] = useState([]);

  const colors = useMemo(() => {
    if (gold) return ['#FFD700', '#FFA500', '#FFCC00', '#FFE066', '#F5C542', '#DAA520', '#FFB347', '#CD853F'];
    return CONFETTI_COLORS;
  }, [gold]);

  useEffect(() => {
    if (active) {
      setPieces(Array.from({ length: count }, (_, i) => i));
      const t = setTimeout(() => setPieces([]), 6000);
      return () => clearTimeout(t);
    }
    setPieces([]);
  }, [active, count]);

  if (!pieces.length) return null;

  return (
    <div data-testid="confetti-effect" className="absolute inset-0 overflow-hidden pointer-events-none z-10">
      {pieces.map(i => <ConfettiPiece key={i} index={i} total={count} />)}
    </div>
  );
}
