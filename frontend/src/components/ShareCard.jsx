import { useState, useRef } from 'react';
import html2canvas from 'html2canvas';
import { COLORS } from '../constants/design';
import { getTeamLogo, getTeamGradient, getTeamCardImage } from '../constants/teams';
import { Share2, X } from 'lucide-react';
import { BadgeInline } from './PredictionBadge';
import ConfettiEffect from './ConfettiEffect';

export default function ShareCard({ match, rank, totalPlayers, score, totalPoints, correctAnswers, totalQuestions, onClose, moodData, badgeData }) {
  const cardRef = useRef(null);
  const [sharing, setSharing] = useState(false);

  const teamA = match?.team_a || {};
  const teamB = match?.team_b || {};
  const scores = match?.live_score?.scores || [];

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
          text: `Rank #${rank}/${totalPlayers} in ${teamA.short_name} vs ${teamB.short_name}! ${score}/${totalPoints} pts! Play on Bharat 11!`
        });
      } else {
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
  const isTop3 = rank <= 3;
  const rankColor = rank === 1 ? '#FFD700' : rank === 2 ? '#C0C0C0' : rank === 3 ? '#CD7F32' : '#fff';
  const heroImg = getTeamCardImage(teamA.short_name) || getTeamCardImage(teamB.short_name);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(8px)' }}
      onClick={onClose}>
      <div className="w-full max-w-sm space-y-3 animate-scaleIn" onClick={e => e.stopPropagation()}>
        {/* The Card */}
        <div ref={cardRef} className="rounded-3xl overflow-hidden relative"
          style={{ background: 'linear-gradient(160deg, #0a0e1a 0%, #131836 40%, #0a0e1a 100%)' }}>

          {/* Confetti for top 3 */}
          {isTop3 && <ConfettiEffect active={true} count={30} />}

          {/* Background team image */}
          {heroImg && (
            <div className="absolute inset-0">
              <img src={heroImg} alt="" className="w-full h-full object-cover" style={{ filter: 'brightness(0.12) saturate(1.5)' }} />
              <div className="absolute inset-0" style={{ background: 'linear-gradient(160deg, rgba(10,14,26,0.6), rgba(19,24,54,0.85), rgba(10,14,26,0.95))' }} />
            </div>
          )}

          <div className="relative p-5 space-y-4">
            {/* Bharat 11 Header */}
            <div className="flex items-center justify-between">
              <div>
                <div className="text-xs font-black tracking-[0.25em] uppercase" style={{ color: COLORS.primary.main }}>BHARAT 11</div>
                <div className="text-[8px] uppercase tracking-wider" style={{ color: 'rgba(255,255,255,0.3)' }}>Fantasy Cricket</div>
              </div>
              <div className="text-[9px] px-2 py-1 rounded-full" style={{ background: 'rgba(255,255,255,0.06)', color: 'rgba(255,255,255,0.4)' }}>
                IPL 2026
              </div>
            </div>

            {/* Divider glow line */}
            <div className="h-[1px] w-full" style={{ background: 'linear-gradient(90deg, transparent, rgba(255,59,59,0.5), transparent)' }} />

            {/* Match Teams Row */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-14 h-14 rounded-2xl flex items-center justify-center overflow-hidden shadow-lg" style={{ background: getTeamGradient(teamA.short_name), boxShadow: '0 4px 15px rgba(0,0,0,0.5)' }}>
                  {getTeamLogo(teamA.short_name) ? <img src={getTeamLogo(teamA.short_name)} alt="" className="w-10 h-10 object-contain" /> : <span className="text-sm font-bold text-white">{teamA.short_name}</span>}
                </div>
                <div>
                  <div className="text-sm font-bold text-white">{teamA.short_name}</div>
                  {scores[0] && <div className="text-xs font-bold" style={{ color: COLORS.primary.main }}>{scores[0].r || scores[0].runs}/{scores[0].w || scores[0].wickets}</div>}
                </div>
              </div>

              <div className="px-3 py-1 rounded-xl text-[10px] font-black" style={{ background: 'rgba(255,59,59,0.15)', color: COLORS.primary.main, border: '1px solid rgba(255,59,59,0.2)' }}>VS</div>

              <div className="flex items-center gap-3 flex-row-reverse">
                <div className="w-14 h-14 rounded-2xl flex items-center justify-center overflow-hidden shadow-lg" style={{ background: getTeamGradient(teamB.short_name), boxShadow: '0 4px 15px rgba(0,0,0,0.5)' }}>
                  {getTeamLogo(teamB.short_name) ? <img src={getTeamLogo(teamB.short_name)} alt="" className="w-10 h-10 object-contain" /> : <span className="text-sm font-bold text-white">{teamB.short_name}</span>}
                </div>
                <div className="text-right">
                  <div className="text-sm font-bold text-white">{teamB.short_name}</div>
                  {scores[1] && <div className="text-xs font-bold" style={{ color: COLORS.primary.main }}>{scores[1].r || scores[1].runs}/{scores[1].w || scores[1].wickets}</div>}
                </div>
              </div>
            </div>

            {/* RANK - Big dramatic display */}
            <div className="text-center py-3">
              <div className="text-[10px] font-black uppercase tracking-[0.2em] mb-1" style={{ color: 'rgba(255,255,255,0.3)' }}>MY RANK</div>
              <div className="text-5xl font-black leading-none" style={{ color: rankColor, fontFamily: "'Rajdhani', sans-serif", textShadow: isTop3 ? `0 0 30px ${rankColor}66, 0 0 60px ${rankColor}33` : 'none' }}>
                #{rank}
              </div>
              <div className="text-[10px] mt-1" style={{ color: 'rgba(255,255,255,0.4)' }}>out of {totalPlayers} players</div>
            </div>

            {/* Stats Row */}
            <div className="grid grid-cols-3 gap-2">
              <div className="text-center p-2.5 rounded-xl" style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.06)' }}>
                <div className="text-xl font-black text-white" style={{ fontFamily: "'Rajdhani', sans-serif" }}>{score}</div>
                <div className="text-[8px] font-bold uppercase tracking-wider" style={{ color: 'rgba(255,255,255,0.3)' }}>Points</div>
              </div>
              <div className="text-center p-2.5 rounded-xl" style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.06)' }}>
                <div className="text-xl font-black" style={{ color: COLORS.success.main, fontFamily: "'Rajdhani', sans-serif" }}>{correctAnswers}/{totalQuestions}</div>
                <div className="text-[8px] font-bold uppercase tracking-wider" style={{ color: 'rgba(255,255,255,0.3)' }}>Correct</div>
              </div>
              <div className="text-center p-2.5 rounded-xl" style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.06)' }}>
                <div className="text-xl font-black" style={{
                  color: percentage >= 70 ? COLORS.success.main : percentage >= 40 ? COLORS.warning.main : COLORS.error.main,
                  fontFamily: "'Rajdhani', sans-serif"
                }}>{percentage}%</div>
                <div className="text-[8px] font-bold uppercase tracking-wider" style={{ color: 'rgba(255,255,255,0.3)' }}>Accuracy</div>
              </div>
            </div>

            {/* Mood Meter in card */}
            {moodData && moodData.total_votes > 0 && (
              <div className="space-y-1.5">
                <div className="text-[8px] font-black uppercase tracking-[0.15em] text-center" style={{ color: 'rgba(255,255,255,0.3)' }}>MATCH MOOD</div>
                <div className="flex items-center gap-2">
                  <span className="text-[9px] font-bold text-white">{moodData.team_a}</span>
                  <div className="flex-1 h-2.5 rounded-full overflow-hidden flex" style={{ background: 'rgba(255,255,255,0.06)' }}>
                    <div className="h-full rounded-l-full flex items-center justify-end pr-0.5"
                      style={{ width: `${moodData.team_a_pct}%`, background: getTeamGradient(moodData.team_a) }}>
                      {moodData.team_a_pct > 20 && <span className="text-[7px] font-black text-white">{moodData.team_a_pct}%</span>}
                    </div>
                    <div className="h-full rounded-r-full flex items-center pl-0.5"
                      style={{ width: `${moodData.team_b_pct}%`, background: getTeamGradient(moodData.team_b) }}>
                      {moodData.team_b_pct > 20 && <span className="text-[7px] font-black text-white">{moodData.team_b_pct}%</span>}
                    </div>
                  </div>
                  <span className="text-[9px] font-bold text-white">{moodData.team_b}</span>
                </div>
                <div className="text-center text-[8px]" style={{ color: 'rgba(255,255,255,0.2)' }}>{moodData.total_votes} votes</div>
              </div>
            )}

            {/* Badge */}
            {badgeData && badgeData.badge && <BadgeInline badgeData={badgeData} />}

            {/* Footer */}
            <div className="text-center">
              <div className="h-[1px] w-full mb-2" style={{ background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent)' }} />
              <div className="text-[8px] uppercase tracking-[0.15em]" style={{ color: 'rgba(255,255,255,0.2)' }}>bharat11.app — Play & Predict</div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2">
          <button data-testid="share-whatsapp-btn" onClick={handleShare} disabled={sharing}
            className="flex-1 flex items-center justify-center gap-2 py-3.5 rounded-2xl font-bold text-sm text-white disabled:opacity-50 transition-transform active:scale-95"
            style={{ background: 'linear-gradient(135deg, #25D366, #128C7E)', boxShadow: '0 4px 20px rgba(37,211,102,0.25)' }}>
            <Share2 size={16} /> {sharing ? 'Generating...' : 'Share on WhatsApp'}
          </button>
          <button onClick={onClose} className="px-5 py-3.5 rounded-2xl transition-transform active:scale-95" style={{ background: 'rgba(255,255,255,0.06)' }}>
            <X size={16} color={COLORS.text.secondary} />
          </button>
        </div>
      </div>
    </div>
  );
}
