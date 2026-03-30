import { useState, useRef } from 'react';
import html2canvas from 'html2canvas';
import { COLORS } from '../constants/design';
import { getTeamLogo, getTeamGradient } from '../constants/teams';
import { Share2, Download, X } from 'lucide-react';

export default function ShareCard({ match, rank, totalPlayers, score, totalPoints, correctAnswers, totalQuestions, onClose }) {
  const cardRef = useRef(null);
  const [sharing, setSharing] = useState(false);

  const teamA = match?.team_a || {};
  const teamB = match?.team_b || {};

  const handleShare = async () => {
    if (!cardRef.current) return;
    setSharing(true);
    try {
      const canvas = await html2canvas(cardRef.current, { scale: 2, useCORS: true, backgroundColor: '#0a0e1a' });
      const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
      const file = new File([blob], 'bharat11-result.png', { type: 'image/png' });

      if (navigator.canShare?.({ files: [file] })) {
        await navigator.share({
          files: [file],
          title: 'Bharat 11 — My Result!',
          text: `I scored ${score}/${totalPoints} points in ${teamA.short_name} vs ${teamB.short_name}! Rank #${rank}/${totalPlayers}. Play on Bharat 11!`
        });
      } else {
        // Fallback: download image
        const url = canvas.toDataURL('image/png');
        const a = document.createElement('a');
        a.href = url;
        a.download = 'bharat11-result.png';
        a.click();
      }
    } catch (e) {
      console.error('Share error:', e);
    }
    finally { setSharing(false); }
  };

  const percentage = totalPoints > 0 ? Math.round((score / totalPoints) * 100) : 0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: 'rgba(0,0,0,0.7)' }}
      onClick={onClose}>
      <div className="w-full max-w-sm space-y-3 animate-scaleIn" onClick={e => e.stopPropagation()}>
        {/* The Card */}
        <div ref={cardRef} className="rounded-3xl overflow-hidden p-5 space-y-4"
          style={{ background: 'linear-gradient(160deg, #0a0e1a 0%, #1a1f3a 50%, #0a0e1a 100%)' }}>
          {/* Header */}
          <div className="text-center">
            <div className="text-xs font-black tracking-[0.3em] uppercase" style={{ color: COLORS.primary.main }}>BHARAT 11</div>
            <div className="text-[9px] mt-0.5" style={{ color: COLORS.text.tertiary }}>Fantasy Cricket Prediction</div>
          </div>

          {/* Match */}
          <div className="flex items-center justify-center gap-4">
            <div className="flex flex-col items-center gap-1">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center overflow-hidden" style={{ background: getTeamGradient(teamA.short_name) }}>
                {getTeamLogo(teamA.short_name) ? <img src={getTeamLogo(teamA.short_name)} alt="" className="w-9 h-9 object-contain" /> : <span className="text-xs font-bold text-white">{teamA.short_name}</span>}
              </div>
              <span className="text-[10px] font-bold text-white">{teamA.short_name}</span>
            </div>
            <div className="text-xs font-bold px-2.5 py-1 rounded-lg" style={{ background: `${COLORS.primary.main}22`, color: COLORS.primary.main }}>VS</div>
            <div className="flex flex-col items-center gap-1">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center overflow-hidden" style={{ background: getTeamGradient(teamB.short_name) }}>
                {getTeamLogo(teamB.short_name) ? <img src={getTeamLogo(teamB.short_name)} alt="" className="w-9 h-9 object-contain" /> : <span className="text-xs font-bold text-white">{teamB.short_name}</span>}
              </div>
              <span className="text-[10px] font-bold text-white">{teamB.short_name}</span>
            </div>
          </div>

          {/* Rank + Score */}
          <div className="text-center">
            <div className="text-4xl font-black" style={{ color: rank <= 3 ? COLORS.accent.gold : '#fff', fontFamily: "'Rajdhani', sans-serif" }}>
              #{rank}
            </div>
            <div className="text-xs" style={{ color: COLORS.text.tertiary }}>out of {totalPlayers} players</div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-3 gap-2">
            <div className="text-center p-2 rounded-xl" style={{ background: 'rgba(255,255,255,0.05)' }}>
              <div className="text-lg font-black text-white" style={{ fontFamily: "'Rajdhani', sans-serif" }}>{score}</div>
              <div className="text-[8px] uppercase" style={{ color: COLORS.text.tertiary }}>Points</div>
            </div>
            <div className="text-center p-2 rounded-xl" style={{ background: 'rgba(255,255,255,0.05)' }}>
              <div className="text-lg font-black" style={{ color: COLORS.success.main, fontFamily: "'Rajdhani', sans-serif" }}>{correctAnswers}/{totalQuestions}</div>
              <div className="text-[8px] uppercase" style={{ color: COLORS.text.tertiary }}>Correct</div>
            </div>
            <div className="text-center p-2 rounded-xl" style={{ background: 'rgba(255,255,255,0.05)' }}>
              <div className="text-lg font-black" style={{ color: percentage >= 70 ? COLORS.success.main : percentage >= 40 ? COLORS.warning.main : COLORS.error.main, fontFamily: "'Rajdhani', sans-serif" }}>{percentage}%</div>
              <div className="text-[8px] uppercase" style={{ color: COLORS.text.tertiary }}>Accuracy</div>
            </div>
          </div>

          {/* Watermark */}
          <div className="text-center text-[8px]" style={{ color: COLORS.text.tertiary }}>bharat11.app — Play & Predict</div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2">
          <button data-testid="share-whatsapp-btn" onClick={handleShare} disabled={sharing}
            className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl font-bold text-sm text-white disabled:opacity-50"
            style={{ background: '#25D366' }}>
            <Share2 size={16} /> {sharing ? 'Generating...' : 'Share on WhatsApp'}
          </button>
          <button onClick={onClose} className="px-4 py-3 rounded-xl" style={{ background: COLORS.background.card }}>
            <X size={16} color={COLORS.text.secondary} />
          </button>
        </div>
      </div>
    </div>
  );
}
