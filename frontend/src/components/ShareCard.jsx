import { useState, useRef } from 'react';
import html2canvas from 'html2canvas';
import { COLORS } from '../constants/design';
import { getTeamLogo, getTeamGradient } from '../constants/teams';
import { Share2, X, Download } from 'lucide-react';
import ConfettiEffect from './ConfettiEffect';

/**
 * WORLD'S BEST WhatsApp Share Card — Topps Chrome / NBA Top Shot collectible aesthetic
 * Strict html2canvas rules: NO backdrop-filter, NO rem units, absolute px only.
 * 9:16 portrait ratio (540x960px render → 1080x1920 at 2x scale)
 */
export default function ShareCard({ match, rank, totalPlayers, score, totalPoints, correctAnswers, totalQuestions, onClose, moodData, badgeData }) {
  const cardRef = useRef(null);
  const [sharing, setSharing] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const teamA = match?.team_a || {};
  const teamB = match?.team_b || {};
  const scores = match?.live_score?.scores || [];

  const handleShare = async () => {
    if (!cardRef.current) return;
    setSharing(true);
    try {
      const canvas = await html2canvas(cardRef.current, {
        scale: 2,
        useCORS: true,
        backgroundColor: '#0A0A0A',
        logging: false,
        allowTaint: true,
      });
      const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
      const file = new File([blob], 'bharat11-result.png', { type: 'image/png' });

      if (navigator.canShare?.({ files: [file] })) {
        await navigator.share({
          files: [file],
          title: 'Bharat 11 — My Result!',
          text: `Rank #${rank}/${totalPlayers} in ${teamA.short_name} vs ${teamB.short_name}! ${score} pts! Play on Bharat 11!`
        });
      } else {
        // Fallback: download
        const url = canvas.toDataURL('image/png');
        const a = document.createElement('a');
        a.href = url;
        a.download = 'bharat11-result.png';
        a.click();
      }
    } catch (e) {
      console.error('Share error:', e);
    } finally { setSharing(false); }
  };

  const handleDownload = async () => {
    if (!cardRef.current) return;
    setDownloading(true);
    try {
      const canvas = await html2canvas(cardRef.current, {
        scale: 2,
        useCORS: true,
        backgroundColor: '#0A0A0A',
        logging: false,
        allowTaint: true,
      });
      const url = canvas.toDataURL('image/png');
      const a = document.createElement('a');
      a.href = url;
      a.download = `bharat11-rank${rank}.png`;
      a.click();
    } catch (e) {
      console.error('Download error:', e);
    } finally { setDownloading(false); }
  };

  const percentage = totalPoints > 0 ? Math.round((score / totalPoints) * 100) : 0;
  const isTop3 = rank <= 3;
  const rankColor = rank === 1 ? '#FFD700' : rank === 2 ? '#C0C0C0' : rank === 3 ? '#CD7F32' : '#FFFFFF';
  const rankGlow = rank === 1 ? '0 0 40px rgba(255,215,0,0.6), 0 0 80px rgba(255,215,0,0.3)' :
    rank === 2 ? '0 0 30px rgba(192,192,192,0.5)' :
    rank === 3 ? '0 0 30px rgba(205,127,50,0.5)' : 'none';
  const rankLabel = rank === 1 ? 'CHAMPION' : rank === 2 ? 'RUNNER UP' : rank === 3 ? 'BRONZE' : 'WARRIOR';

  // Team scores
  const teamAScore = scores[0] ? `${scores[0].r || scores[0].runs || '—'}/${scores[0].w || scores[0].wickets || '0'}` : '—';
  const teamBScore = scores[1] ? `${scores[1].r || scores[1].runs || '—'}/${scores[1].w || scores[1].wickets || '0'}` : '—';
  const teamAOvers = scores[0] ? `(${scores[0].o || scores[0].overs || '—'} ov)` : '';
  const teamBOvers = scores[1] ? `(${scores[1].o || scores[1].overs || '—'} ov)` : '';

  // Accuracy bar
  const accuracyPct = totalQuestions > 0 ? Math.round((correctAnswers / totalQuestions) * 100) : 0;
  const accuracyColor = accuracyPct >= 70 ? '#10B981' : accuracyPct >= 40 ? '#F59E0B' : '#EF4444';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3"
      style={{ background: 'rgba(0,0,0,0.92)' }}
      onClick={onClose}>
      <div className="w-full max-w-[360px] space-y-3" style={{ animation: 'scaleIn 0.3s ease' }}
        onClick={e => e.stopPropagation()}>

        {/* ===== THE CARD (html2canvas target) ===== */}
        <div ref={cardRef}
          data-testid="share-card-render"
          style={{
            width: '360px',
            height: '640px',
            position: 'relative',
            overflow: 'hidden',
            borderRadius: '20px',
            border: '1px solid rgba(255,215,0,0.35)',
            boxShadow: `inset 0 0 30px rgba(255,215,0,0.08), 0 0 40px rgba(0,0,0,0.8)`,
            background: '#0A0A0A',
          }}>

          {/* Background gradient (no backdrop-filter!) */}
          <div style={{
            position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
            background: 'linear-gradient(165deg, #0A0A0A 0%, #141420 30%, #0D0D1A 60%, #0A0A0A 100%)',
            zIndex: 0,
          }} />

          {/* Subtle top glow */}
          <div style={{
            position: 'absolute', top: '-60px', left: '50%', transform: 'translateX(-50%)',
            width: '300px', height: '200px',
            background: `radial-gradient(ellipse, ${rankColor}15, transparent 70%)`,
            zIndex: 1,
          }} />

          {/* Bottom glow */}
          <div style={{
            position: 'absolute', bottom: '-40px', left: '50%', transform: 'translateX(-50%)',
            width: '400px', height: '150px',
            background: 'radial-gradient(ellipse, rgba(255,59,59,0.08), transparent 70%)',
            zIndex: 1,
          }} />

          {/* Confetti for top 3 */}
          {isTop3 && <ConfettiEffect active={true} count={40} />}

          {/* Content */}
          <div style={{ position: 'relative', zIndex: 5, padding: '24px 20px', height: '100%', display: 'flex', flexDirection: 'column' }}>

            {/* Header: BHARAT 11 branding */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
              <div>
                <div style={{
                  fontSize: '11px', fontWeight: 900, letterSpacing: '3px',
                  color: '#FF3B3B', fontFamily: "'Rajdhani', sans-serif",
                }}>BHARAT 11</div>
                <div style={{ fontSize: '8px', letterSpacing: '2px', color: 'rgba(255,255,255,0.25)', fontWeight: 600 }}>
                  FANTASY CRICKET
                </div>
              </div>
              <div style={{
                fontSize: '9px', fontWeight: 700, color: 'rgba(255,255,255,0.3)',
                padding: '3px 10px', borderRadius: '20px',
                background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.08)',
              }}>
                IPL 2026
              </div>
            </div>

            {/* Gold divider */}
            <div style={{
              height: '1px', width: '100%', marginBottom: '14px',
              background: 'linear-gradient(90deg, transparent, rgba(255,215,0,0.4), rgba(255,59,59,0.3), transparent)',
            }} />

            {/* Teams Row */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              {/* Team A */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{
                  width: '48px', height: '48px', borderRadius: '14px',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  background: getTeamGradient(teamA.short_name),
                  boxShadow: '0 4px 16px rgba(0,0,0,0.5)',
                  overflow: 'hidden',
                }}>
                  {getTeamLogo(teamA.short_name) ?
                    <img src={getTeamLogo(teamA.short_name)} alt="" style={{ width: '36px', height: '36px', objectFit: 'contain' }} /> :
                    <span style={{ fontSize: '14px', fontWeight: 900, color: '#fff' }}>{teamA.short_name}</span>
                  }
                </div>
                <div>
                  <div style={{ fontSize: '14px', fontWeight: 800, color: '#fff' }}>{teamA.short_name}</div>
                  <div style={{ fontSize: '13px', fontWeight: 900, color: '#FF3B3B', fontFamily: "'Rajdhani', sans-serif" }}>{teamAScore}</div>
                  <div style={{ fontSize: '9px', color: 'rgba(255,255,255,0.35)' }}>{teamAOvers}</div>
                </div>
              </div>

              {/* VS Badge */}
              <div style={{
                padding: '4px 12px', borderRadius: '10px',
                background: 'rgba(255,59,59,0.12)', border: '1px solid rgba(255,59,59,0.25)',
                fontSize: '10px', fontWeight: 900, color: '#FF3B3B',
              }}>VS</div>

              {/* Team B */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexDirection: 'row-reverse' }}>
                <div style={{
                  width: '48px', height: '48px', borderRadius: '14px',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  background: getTeamGradient(teamB.short_name),
                  boxShadow: '0 4px 16px rgba(0,0,0,0.5)',
                  overflow: 'hidden',
                }}>
                  {getTeamLogo(teamB.short_name) ?
                    <img src={getTeamLogo(teamB.short_name)} alt="" style={{ width: '36px', height: '36px', objectFit: 'contain' }} /> :
                    <span style={{ fontSize: '14px', fontWeight: 900, color: '#fff' }}>{teamB.short_name}</span>
                  }
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '14px', fontWeight: 800, color: '#fff' }}>{teamB.short_name}</div>
                  <div style={{ fontSize: '13px', fontWeight: 900, color: '#FF3B3B', fontFamily: "'Rajdhani', sans-serif" }}>{teamBScore}</div>
                  <div style={{ fontSize: '9px', color: 'rgba(255,255,255,0.35)' }}>{teamBOvers}</div>
                </div>
              </div>
            </div>

            {/* ===== THE HERO: RANK ===== */}
            <div style={{ textAlign: 'center', padding: '8px 0 6px', flex: '0 0 auto' }}>
              {/* Rank Label */}
              <div style={{
                fontSize: '9px', fontWeight: 900, letterSpacing: '4px',
                color: rankColor, opacity: 0.7,
                marginBottom: '4px',
              }}>{rankLabel}</div>

              {/* Rank Number */}
              <div style={{
                fontSize: '96px', fontWeight: 900, lineHeight: 0.9,
                fontFamily: "'Rajdhani', sans-serif",
                color: rankColor,
                textShadow: rankGlow,
                letterSpacing: '-3px',
              }}>
                #{rank}
              </div>

              {/* Sub text */}
              <div style={{
                fontSize: '11px', color: 'rgba(255,255,255,0.35)',
                marginTop: '6px', fontWeight: 500,
              }}>
                out of {totalPlayers} players
              </div>
            </div>

            {/* ===== STATS BENTO GRID ===== */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px', marginTop: '16px' }}>
              {/* Points */}
              <div style={{
                textAlign: 'center', padding: '14px 8px', borderRadius: '14px',
                background: '#141414', border: '1px solid rgba(255,215,0,0.15)',
              }}>
                <div style={{
                  fontSize: '28px', fontWeight: 900, color: '#FFD700',
                  fontFamily: "'Rajdhani', sans-serif", lineHeight: 1,
                }}>{score}</div>
                <div style={{ fontSize: '8px', fontWeight: 800, color: 'rgba(255,255,255,0.3)', letterSpacing: '1.5px', marginTop: '4px' }}>POINTS</div>
              </div>

              {/* Accuracy */}
              <div style={{
                textAlign: 'center', padding: '14px 8px', borderRadius: '14px',
                background: '#141414', border: `1px solid ${accuracyColor}25`,
              }}>
                <div style={{
                  fontSize: '28px', fontWeight: 900, color: accuracyColor,
                  fontFamily: "'Rajdhani', sans-serif", lineHeight: 1,
                }}>{accuracyPct}%</div>
                <div style={{ fontSize: '8px', fontWeight: 800, color: 'rgba(255,255,255,0.3)', letterSpacing: '1.5px', marginTop: '4px' }}>ACCURACY</div>
              </div>

              {/* Correct */}
              <div style={{
                textAlign: 'center', padding: '14px 8px', borderRadius: '14px',
                background: '#141414', border: '1px solid rgba(16,185,129,0.15)',
              }}>
                <div style={{
                  fontSize: '28px', fontWeight: 900, color: '#10B981',
                  fontFamily: "'Rajdhani', sans-serif", lineHeight: 1,
                }}>{correctAnswers}<span style={{ fontSize: '16px', color: 'rgba(255,255,255,0.25)' }}>/{totalQuestions}</span></div>
                <div style={{ fontSize: '8px', fontWeight: 800, color: 'rgba(255,255,255,0.3)', letterSpacing: '1.5px', marginTop: '4px' }}>CORRECT</div>
              </div>
            </div>

            {/* Accuracy Progress Bar */}
            <div style={{ marginTop: '10px' }}>
              <div style={{
                height: '4px', borderRadius: '4px', overflow: 'hidden',
                background: 'rgba(255,255,255,0.06)',
              }}>
                <div style={{
                  height: '100%', borderRadius: '4px',
                  width: `${accuracyPct}%`,
                  background: `linear-gradient(90deg, ${accuracyColor}88, ${accuracyColor})`,
                  boxShadow: `0 0 8px ${accuracyColor}55`,
                }} />
              </div>
            </div>

            {/* Mood Meter */}
            {moodData && moodData.total_votes > 0 && (
              <div style={{ marginTop: '14px' }}>
                <div style={{
                  fontSize: '8px', fontWeight: 900, letterSpacing: '2px',
                  color: 'rgba(255,255,255,0.25)', textAlign: 'center', marginBottom: '6px',
                }}>MATCH MOOD</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '10px', fontWeight: 800, color: '#fff', minWidth: '28px', textAlign: 'right' }}>{moodData.team_a}</span>
                  <div style={{
                    flex: 1, height: '6px', borderRadius: '3px', overflow: 'hidden',
                    display: 'flex', background: 'rgba(255,255,255,0.06)',
                  }}>
                    <div style={{
                      height: '100%', borderRadius: '3px 0 0 3px',
                      width: `${moodData.team_a_pct}%`,
                      background: getTeamGradient(moodData.team_a),
                    }} />
                    <div style={{
                      height: '100%', borderRadius: '0 3px 3px 0',
                      width: `${moodData.team_b_pct}%`,
                      background: getTeamGradient(moodData.team_b),
                    }} />
                  </div>
                  <span style={{ fontSize: '10px', fontWeight: 800, color: '#fff', minWidth: '28px' }}>{moodData.team_b}</span>
                </div>
                <div style={{ textAlign: 'center', fontSize: '8px', color: 'rgba(255,255,255,0.2)', marginTop: '4px' }}>
                  {moodData.team_a_pct}% vs {moodData.team_b_pct}% ({moodData.total_votes} votes)
                </div>
              </div>
            )}

            {/* Spacer */}
            <div style={{ flex: 1 }} />

            {/* Footer */}
            <div style={{ textAlign: 'center', paddingTop: '8px' }}>
              <div style={{
                height: '1px', width: '100%', marginBottom: '10px',
                background: 'linear-gradient(90deg, transparent, rgba(255,215,0,0.2), rgba(255,59,59,0.15), transparent)',
              }} />
              <div style={{
                fontSize: '9px', fontWeight: 700, letterSpacing: '2.5px',
                color: 'rgba(255,255,255,0.18)',
              }}>BHARAT11.APP</div>
              <div style={{
                fontSize: '7px', color: 'rgba(255,255,255,0.1)', marginTop: '2px',
                letterSpacing: '1px',
              }}>PLAY &bull; PREDICT &bull; WIN</div>
            </div>
          </div>

          {/* Corner decorations for premium feel */}
          <div style={{
            position: 'absolute', top: 0, left: 0, width: '60px', height: '60px',
            borderTop: `2px solid ${rankColor}30`, borderLeft: `2px solid ${rankColor}30`,
            borderRadius: '20px 0 0 0', zIndex: 6,
          }} />
          <div style={{
            position: 'absolute', top: 0, right: 0, width: '60px', height: '60px',
            borderTop: `2px solid ${rankColor}30`, borderRight: `2px solid ${rankColor}30`,
            borderRadius: '0 20px 0 0', zIndex: 6,
          }} />
          <div style={{
            position: 'absolute', bottom: 0, left: 0, width: '60px', height: '60px',
            borderBottom: `2px solid ${rankColor}30`, borderLeft: `2px solid ${rankColor}30`,
            borderRadius: '0 0 0 20px', zIndex: 6,
          }} />
          <div style={{
            position: 'absolute', bottom: 0, right: 0, width: '60px', height: '60px',
            borderBottom: `2px solid ${rankColor}30`, borderRight: `2px solid ${rankColor}30`,
            borderRadius: '0 0 20px 0', zIndex: 6,
          }} />
        </div>

        {/* ===== ACTION BUTTONS ===== */}
        <div className="flex gap-2">
          <button data-testid="share-whatsapp-btn" onClick={handleShare} disabled={sharing}
            className="flex-1 flex items-center justify-center gap-2 py-3.5 rounded-2xl font-bold text-sm text-white disabled:opacity-50 transition-transform active:scale-95"
            style={{ background: 'linear-gradient(135deg, #25D366, #128C7E)', boxShadow: '0 4px 20px rgba(37,211,102,0.3)' }}>
            <Share2 size={16} /> {sharing ? 'Generating...' : 'Share on WhatsApp'}
          </button>
          <button data-testid="download-card-btn" onClick={handleDownload} disabled={downloading}
            className="px-4 py-3.5 rounded-2xl transition-transform active:scale-95 disabled:opacity-50"
            style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)' }}>
            <Download size={16} color={COLORS.text.secondary} />
          </button>
          <button data-testid="close-share-btn" onClick={onClose}
            className="px-4 py-3.5 rounded-2xl transition-transform active:scale-95"
            style={{ background: 'rgba(255,255,255,0.06)' }}>
            <X size={16} color={COLORS.text.secondary} />
          </button>
        </div>
      </div>
    </div>
  );
}
