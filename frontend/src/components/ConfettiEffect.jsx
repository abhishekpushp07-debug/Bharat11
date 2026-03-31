/**
 * ConfettiEffect — Falling confetti particles for celebrations
 * Used in ShareCard for top-3 finishes
 */
import { useEffect, useState } from 'react';

const CONFETTI_COLORS = ['#FFD700', '#FF3B3B', '#3b82f6', '#22c55e', '#a855f7', '#f97316', '#ec4899', '#06b6d4'];

function ConfettiPiece({ index }) {
  const color = CONFETTI_COLORS[index % CONFETTI_COLORS.length];
  const left = Math.random() * 100;
  const delay = Math.random() * 2;
  const duration = 2 + Math.random() * 2;
  const size = 4 + Math.random() * 6;
  const rotation = Math.random() * 360;
  const isRect = Math.random() > 0.4;

  return (
    <div
      className="absolute"
      style={{
        left: `${left}%`,
        top: '-10px',
        width: isRect ? `${size}px` : `${size * 0.6}px`,
        height: isRect ? `${size * 0.6}px` : `${size}px`,
        background: color,
        borderRadius: isRect ? '1px' : '50%',
        transform: `rotate(${rotation}deg)`,
        animation: `confettiFall ${duration}s ease-in ${delay}s forwards`,
        opacity: 0,
      }}
    />
  );
}

export default function ConfettiEffect({ active = true, count = 40 }) {
  const [pieces, setPieces] = useState([]);

  useEffect(() => {
    if (active) {
      setPieces(Array.from({ length: count }, (_, i) => i));
      const t = setTimeout(() => setPieces([]), 5000);
      return () => clearTimeout(t);
    }
    setPieces([]);
  }, [active, count]);

  if (!pieces.length) return null;

  return (
    <div data-testid="confetti-effect" className="absolute inset-0 overflow-hidden pointer-events-none z-10">
      {pieces.map(i => <ConfettiPiece key={i} index={i} />)}
    </div>
  );
}
