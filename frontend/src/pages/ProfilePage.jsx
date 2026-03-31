import { useState, useEffect, useRef, useCallback } from 'react';
import { useAuthStore } from '../stores/authStore';
import { api } from '../api/client';
import { COLORS, RANKS } from '../constants/design';
import { Gift, Copy, Check, LogOut, Edit3, Lock, Share2, X, ChevronRight, Shield, Loader2 } from 'lucide-react';

// ====== Edit Name Modal ======
function EditNameModal({ currentName, onSave, onClose }) {
  const [name, setName] = useState(currentName || '');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const inputRef = useRef(null);

  useEffect(() => { inputRef.current?.focus(); }, []);

  const handleSave = async () => {
    const trimmed = name.trim();
    if (trimmed.length < 2) { setError('Kam se kam 2 characters chahiye'); return; }
    if (trimmed.length > 30) { setError('30 characters se zyada nahi'); return; }
    setSaving(true);
    try {
      const res = await api.auth.changeName({ username: trimmed });
      onSave(res.data.username || trimmed);
    } catch (e) {
      setError(e?.response?.data?.detail || e?.message || 'Error saving name');
    } finally { setSaving(false); }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: 'rgba(0,0,0,0.75)' }}>
      <div data-testid="edit-name-modal" className="w-full max-w-sm rounded-2xl p-5 space-y-4" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.medium}` }}>
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-white">Change Name</h3>
          <button data-testid="close-name-modal" onClick={onClose} className="p-1 rounded-full" style={{ background: COLORS.background.tertiary }}>
            <X size={16} color={COLORS.text.secondary} />
          </button>
        </div>
        <input
          ref={inputRef}
          data-testid="name-input"
          value={name}
          onChange={e => { setName(e.target.value); setError(''); }}
          maxLength={30}
          placeholder="Apna naam daalo"
          className="w-full px-4 py-3 rounded-xl text-sm text-white bg-transparent outline-none"
          style={{ background: COLORS.background.tertiary, border: `1px solid ${error ? COLORS.error.main : COLORS.border.light}` }}
        />
        {error && <p className="text-xs" style={{ color: COLORS.error.main }}>{error}</p>}
        <button
          data-testid="save-name-btn"
          onClick={handleSave}
          disabled={saving || name.trim().length < 2}
          className="w-full py-3 rounded-xl text-sm font-bold text-white flex items-center justify-center gap-2 disabled:opacity-50 transition-all"
          style={{ background: COLORS.primary.main }}>
          {saving ? <Loader2 size={16} className="animate-spin" /> : null}
          {saving ? 'Saving...' : 'Save Name'}
        </button>
      </div>
    </div>
  );
}

// ====== Change PIN Modal ======
function ChangePinModal({ onClose, onSuccess }) {
  const [step, setStep] = useState(1); // 1=old, 2=new, 3=confirm
  const [oldPin, setOldPin] = useState('');
  const [newPin, setNewPin] = useState('');
  const [confirmPin, setConfirmPin] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const inputRef = useRef(null);

  useEffect(() => { inputRef.current?.focus(); }, [step]);

  const handleSubmit = async () => {
    if (newPin !== confirmPin) { setError('PIN match nahi kar raha'); return; }
    if (newPin === oldPin) { setError('Naya PIN purane se alag hona chahiye'); return; }
    setSaving(true);
    try {
      const res = await api.auth.changePin({ old_pin: oldPin, new_pin: newPin });
      const token = res.data?.token;
      if (token?.access_token) {
        localStorage.setItem('crickpredict_token', token.access_token);
        localStorage.setItem('crickpredict_refresh_token', token.refresh_token);
      }
      onSuccess();
    } catch (e) {
      setError(e?.response?.data?.detail || e?.message || 'PIN change failed');
      if (step === 3) { setStep(1); setOldPin(''); setNewPin(''); setConfirmPin(''); }
    } finally { setSaving(false); }
  };

  const titles = {
    1: { title: 'Current PIN', sub: 'Apna purana PIN daalo' },
    2: { title: 'New PIN', sub: 'Naya 4-digit PIN banao' },
    3: { title: 'Confirm New PIN', sub: 'Naya PIN dobara daalo' },
  };

  const currentVal = step === 1 ? oldPin : step === 2 ? newPin : confirmPin;
  const setCurrentVal = step === 1 ? setOldPin : step === 2 ? setNewPin : setConfirmPin;

  const handleInput = (val) => {
    const digits = val.replace(/\D/g, '').slice(0, 4);
    setCurrentVal(digits);
    setError('');
    if (digits.length === 4) {
      if (step === 1) setTimeout(() => setStep(2), 200);
      else if (step === 2) setTimeout(() => setStep(3), 200);
      else handleSubmit();
    }
  };

  // Need to call handleSubmit when confirmPin is set and length is 4
  useEffect(() => {
    if (step === 3 && confirmPin.length === 4 && newPin.length === 4) {
      handleSubmit();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [confirmPin]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: 'rgba(0,0,0,0.75)' }}>
      <div data-testid="change-pin-modal" className="w-full max-w-sm rounded-2xl p-5 space-y-4" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.medium}` }}>
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-white">{titles[step].title}</h3>
          <button data-testid="close-pin-modal" onClick={onClose} className="p-1 rounded-full" style={{ background: COLORS.background.tertiary }}>
            <X size={16} color={COLORS.text.secondary} />
          </button>
        </div>
        <p className="text-xs" style={{ color: COLORS.text.secondary }}>{titles[step].sub}</p>

        {/* Step Indicator */}
        <div className="flex gap-2 justify-center">
          {[1, 2, 3].map(s => (
            <div key={s} className="h-1 rounded-full transition-all" style={{
              width: step >= s ? '32px' : '16px',
              background: step >= s ? COLORS.primary.main : COLORS.background.tertiary,
            }} />
          ))}
        </div>

        {/* PIN Input */}
        <div className="flex justify-center gap-3">
          {[0, 1, 2, 3].map(i => (
            <div key={i} className="w-12 h-14 rounded-xl flex items-center justify-center text-lg font-bold transition-all"
              style={{
                background: COLORS.background.tertiary,
                border: `2px solid ${currentVal.length === i ? COLORS.primary.main : currentVal.length > i ? COLORS.success.main : COLORS.border.light}`,
                color: '#fff',
              }}>
              {currentVal[i] ? '\u2022' : ''}
            </div>
          ))}
        </div>
        <input
          ref={inputRef}
          type="tel"
          inputMode="numeric"
          value={currentVal}
          onChange={e => handleInput(e.target.value)}
          className="opacity-0 absolute"
          autoFocus
        />

        {error && <p className="text-xs text-center" style={{ color: COLORS.error.main }}>{error}</p>}
        {saving && <div className="flex justify-center"><Loader2 size={20} className="animate-spin" color={COLORS.primary.main} /></div>}
      </div>
    </div>
  );
}

// ====== WhatsApp Share Card ======
function ShareCardModal({ user, onClose }) {
  const canvasRef = useRef(null);
  const [sharing, setSharing] = useState(false);

  const drawCard = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const w = 600, h = 340;
    canvas.width = w;
    canvas.height = h;

    // Background gradient
    const bg = ctx.createLinearGradient(0, 0, w, h);
    bg.addColorStop(0, '#0D0D0D');
    bg.addColorStop(0.5, '#1a0a0f');
    bg.addColorStop(1, '#0D0D0D');
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, w, h);

    // Red accent bar on top
    const topGrad = ctx.createLinearGradient(0, 0, w, 0);
    topGrad.addColorStop(0, '#FF3B3B');
    topGrad.addColorStop(1, '#FF6B6B');
    ctx.fillStyle = topGrad;
    ctx.fillRect(0, 0, w, 4);

    // "BHARAT 11" branding
    ctx.fillStyle = '#FF3B3B';
    ctx.font = 'bold 28px Rajdhani, sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText('BHARAT 11', 30, 45);
    ctx.fillStyle = '#ffffff55';
    ctx.font = '12px Poppins, sans-serif';
    ctx.fillText('Fantasy Cricket', 30, 62);

    // Avatar circle
    ctx.beginPath();
    ctx.arc(w - 60, 48, 28, 0, Math.PI * 2);
    ctx.fillStyle = '#FF3B3B33';
    ctx.fill();
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 22px Poppins, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText((user?.username || 'P')[0].toUpperCase(), w - 60, 56);

    // Divider
    ctx.strokeStyle = 'rgba(255,255,255,0.08)';
    ctx.beginPath();
    ctx.moveTo(30, 80);
    ctx.lineTo(w - 30, 80);
    ctx.stroke();

    // Username
    ctx.textAlign = 'left';
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 24px Poppins, sans-serif';
    ctx.fillText(user?.username || 'Player', 30, 115);

    // Rank badge
    const rankKey = (user?.rank_title || 'Rookie').toUpperCase();
    const rankColor = RANKS[rankKey]?.color || '#B0B0B0';
    ctx.fillStyle = rankColor + '33';
    ctx.beginPath();
    ctx.roundRect(30, 125, 80, 22, 8);
    ctx.fill();
    ctx.fillStyle = rankColor;
    ctx.font = 'bold 11px Poppins, sans-serif';
    ctx.fillText(user?.rank_title || 'Rookie', 42, 140);

    // Stats grid
    const stats = [
      { label: 'Total Points', value: (user?.total_points || 0).toLocaleString(), color: '#FFD700' },
      { label: 'Coins Balance', value: (user?.coins_balance || 0).toLocaleString(), color: '#f59e0b' },
      { label: 'Matches', value: String(user?.matches_played || 0), color: '#3b82f6' },
      { label: 'Contests Won', value: String(user?.contests_won || 0), color: '#22c55e' },
    ];

    stats.forEach((s, i) => {
      const col = i % 2;
      const row = Math.floor(i / 2);
      const x = 30 + col * 270;
      const y = 170 + row * 64;

      // Card bg
      ctx.fillStyle = s.color + '12';
      ctx.beginPath();
      ctx.roundRect(x, y, 250, 52, 12);
      ctx.fill();
      ctx.strokeStyle = s.color + '30';
      ctx.stroke();

      ctx.fillStyle = s.color;
      ctx.font = 'bold 22px Rajdhani, sans-serif';
      ctx.textAlign = 'left';
      ctx.fillText(s.value, x + 16, y + 28);

      ctx.fillStyle = '#ffffff77';
      ctx.font = '10px Poppins, sans-serif';
      ctx.fillText(s.label.toUpperCase(), x + 16, y + 44);
    });

    // Footer
    ctx.fillStyle = 'rgba(255,255,255,0.04)';
    ctx.fillRect(0, h - 36, w, 36);
    ctx.fillStyle = '#ffffff44';
    ctx.font = '10px Poppins, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Join Bharat 11 - India ka #1 Fantasy Cricket App', w / 2, h - 14);
  }, [user]);

  useEffect(() => { drawCard(); }, [drawCard]);

  const shareToWhatsApp = async () => {
    setSharing(true);
    try {
      const canvas = canvasRef.current;
      const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
      if (navigator.share && blob) {
        const file = new File([blob], 'bharat11-stats.png', { type: 'image/png' });
        await navigator.share({
          title: 'Bharat 11 - My Cricket Stats',
          text: `Check out my stats on Bharat 11! ${user?.total_points || 0} points, ${user?.contests_won || 0} contests won! Join now!`,
          files: [file],
        });
      } else {
        // Fallback: download image
        const url = canvas.toDataURL('image/png');
        const a = document.createElement('a');
        a.href = url;
        a.download = 'bharat11-stats.png';
        a.click();
      }
    } catch (e) { /* user cancelled share */ }
    finally { setSharing(false); }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: 'rgba(0,0,0,0.8)' }}>
      <div data-testid="share-card-modal" className="w-full max-w-md rounded-2xl p-4 space-y-3" style={{ background: COLORS.background.card }}>
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-white">Share Your Stats</h3>
          <button data-testid="close-share-modal" onClick={onClose} className="p-1 rounded-full" style={{ background: COLORS.background.tertiary }}>
            <X size={16} color={COLORS.text.secondary} />
          </button>
        </div>
        <canvas ref={canvasRef} className="w-full rounded-xl" style={{ border: `1px solid ${COLORS.border.light}` }} />
        <button
          data-testid="share-whatsapp-btn"
          onClick={shareToWhatsApp}
          disabled={sharing}
          className="w-full py-3 rounded-xl text-sm font-bold text-white flex items-center justify-center gap-2 transition-all"
          style={{ background: '#25D366' }}>
          {sharing ? <Loader2 size={16} className="animate-spin" /> : <Share2 size={16} />}
          {sharing ? 'Sharing...' : 'Share on WhatsApp'}
        </button>
      </div>
    </div>
  );
}

// ====== Main Profile Page ======
export default function ProfilePage() {
  const { user, logout, updateUser, refreshUser } = useAuthStore();
  const [rankProgress, setRankProgress] = useState(null);
  const [referralStats, setReferralStats] = useState(null);
  const [copied, setCopied] = useState(false);
  const [showEditName, setShowEditName] = useState(false);
  const [showChangePin, setShowChangePin] = useState(false);
  const [showShareCard, setShowShareCard] = useState(false);
  const [pinChanged, setPinChanged] = useState(false);

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    try {
      const [rankRes, refRes] = await Promise.all([
        api.user.getProfile().catch(() => null),
        api.user.getReferralStats().catch(() => null),
      ]);
      // Use rank-progress endpoint
      const rpRes = await api.user.getProfile().catch(() => null);
      if (rpRes) {
        // Calculate rank progress client-side
        const pts = rpRes.data?.total_points || 0;
        const thresholds = [
          { rank: 'Rookie', min: 0, max: 999 },
          { rank: 'Pro', min: 1000, max: 4999 },
          { rank: 'Expert', min: 5000, max: 14999 },
          { rank: 'Legend', min: 15000, max: 49999 },
          { rank: 'GOAT', min: 50000, max: 999999 },
        ];
        const current = thresholds.find(t => pts >= t.min && pts <= t.max) || thresholds[0];
        const idx = thresholds.indexOf(current);
        const next = idx < thresholds.length - 1 ? thresholds[idx + 1] : null;
        const progress = ((pts - current.min) / (current.max - current.min + 1)) * 100;
        setRankProgress({
          current_rank: current.rank,
          total_points: pts,
          progress_percent: Math.min(progress, 100),
          next_rank: next?.rank || null,
          points_to_next: next ? next.min - pts : 0,
        });
      }
      if (refRes) setReferralStats(refRes.data);
    } catch (_) { /* silent */ }
  };

  const copyReferral = () => {
    if (referralStats?.referral_code) {
      navigator.clipboard.writeText(referralStats.referral_code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleNameSave = (newName) => {
    updateUser({ username: newName });
    setShowEditName(false);
    refreshUser();
  };

  const handlePinChanged = () => {
    setShowChangePin(false);
    setPinChanged(true);
    setTimeout(() => setPinChanged(false), 3000);
  };

  const rankKey = (user?.rank_title || 'Rookie').toUpperCase();
  const rankColor = RANKS[rankKey]?.color || '#B0B0B0';

  return (
    <div data-testid="profile-page" className="pb-6 space-y-4">
      {/* PIN Changed Success Toast */}
      {pinChanged && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 px-4 py-2.5 rounded-xl text-sm font-bold flex items-center gap-2 animate-fade-in"
          style={{ background: COLORS.success.main, color: '#fff' }}>
          <Shield size={16} /> PIN changed successfully!
        </div>
      )}

      {/* Profile Card */}
      <div data-testid="profile-card" className="rounded-2xl p-5" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold" style={{ background: COLORS.primary.gradient, color: '#fff' }}>
            {(user?.username || 'P')[0].toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h2 data-testid="profile-username" className="text-lg font-bold text-white truncate">{user?.username}</h2>
              <button data-testid="edit-name-btn" onClick={() => setShowEditName(true)}
                className="p-1.5 rounded-lg shrink-0 transition-all active:scale-90"
                style={{ background: COLORS.background.tertiary }}>
                <Edit3 size={13} color={COLORS.primary.main} />
              </button>
            </div>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full" style={{ background: `${rankColor}22`, color: rankColor }}>{user?.rank_title || 'Rookie'}</span>
              <span className="text-xs" style={{ color: COLORS.text.secondary }}>{user?.phone}</span>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-3 gap-3 mt-5">
          {[
            { label: 'Matches', value: user?.matches_played || 0, color: '#3b82f6' },
            { label: 'Won', value: user?.contests_won || 0, color: '#22c55e' },
            { label: 'Points', value: user?.total_points || 0, color: '#FFD700' },
          ].map(s => (
            <div key={s.label} className="text-center p-3 rounded-xl" style={{ background: `${s.color}11`, border: `1px solid ${s.color}22` }}>
              <div className="text-lg font-bold" style={{ color: s.color, fontFamily: "'Rajdhani', sans-serif" }}>{s.value}</div>
              <div className="text-xs" style={{ color: COLORS.text.secondary }}>{s.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="space-y-2">
        <button data-testid="change-pin-btn" onClick={() => setShowChangePin(true)}
          className="w-full flex items-center gap-3 p-4 rounded-xl transition-all active:scale-[0.98]"
          style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
          <div className="w-9 h-9 rounded-full flex items-center justify-center" style={{ background: `${COLORS.warning.main}15` }}>
            <Lock size={16} color={COLORS.warning.main} />
          </div>
          <div className="flex-1 text-left">
            <div className="text-sm font-semibold text-white">Change PIN</div>
            <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>Update your 4-digit security PIN</div>
          </div>
          <ChevronRight size={16} color={COLORS.text.tertiary} />
        </button>

        <button data-testid="share-stats-btn" onClick={() => setShowShareCard(true)}
          className="w-full flex items-center gap-3 p-4 rounded-xl transition-all active:scale-[0.98]"
          style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
          <div className="w-9 h-9 rounded-full flex items-center justify-center" style={{ background: 'rgba(37,211,102,0.15)' }}>
            <Share2 size={16} color="#25D366" />
          </div>
          <div className="flex-1 text-left">
            <div className="text-sm font-semibold text-white">Share Stats</div>
            <div className="text-[10px]" style={{ color: COLORS.text.tertiary }}>WhatsApp pe apna scorecard share karo</div>
          </div>
          <ChevronRight size={16} color={COLORS.text.tertiary} />
        </button>
      </div>

      {/* Rank Progress */}
      {rankProgress && (
        <div data-testid="rank-progress" className="rounded-2xl p-5" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
          <div className="flex justify-between items-center mb-3">
            <span className="text-sm font-semibold text-white">Rank Progress</span>
            {rankProgress.next_rank && (
              <span className="text-xs" style={{ color: COLORS.text.secondary }}>
                {rankProgress.points_to_next} pts to {rankProgress.next_rank}
              </span>
            )}
          </div>
          <div className="h-2.5 rounded-full overflow-hidden" style={{ background: COLORS.background.tertiary }}>
            <div className="h-full rounded-full transition-all duration-700" style={{ width: `${rankProgress.progress_percent}%`, background: rankColor, boxShadow: `0 0 8px ${rankColor}66` }} />
          </div>
          <div className="flex justify-between mt-2">
            <span className="text-xs font-semibold" style={{ color: rankColor }}>{rankProgress.current_rank}</span>
            {rankProgress.next_rank && <span className="text-xs" style={{ color: COLORS.text.tertiary }}>{rankProgress.next_rank}</span>}
          </div>
        </div>
      )}

      {/* Referral Card */}
      {referralStats && (
        <div data-testid="referral-card" className="rounded-2xl p-5" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
          <div className="flex items-center gap-2 mb-3">
            <Gift size={18} style={{ color: COLORS.primary.main }} />
            <span className="text-sm font-semibold text-white">Invite Friends</span>
          </div>
          <p className="text-xs mb-3" style={{ color: COLORS.text.secondary }}>Share your code & earn {referralStats.bonus_per_referral} coins per referral!</p>
          <div className="flex items-center gap-2">
            <div data-testid="referral-code" className="flex-1 text-center py-2.5 rounded-xl font-mono text-lg font-bold tracking-widest" style={{ background: COLORS.background.tertiary, color: COLORS.primary.main, letterSpacing: '0.2em' }}>
              {referralStats.referral_code}
            </div>
            <button data-testid="copy-referral-btn" onClick={copyReferral} className="p-2.5 rounded-xl transition-colors" style={{ background: copied ? COLORS.success.bg : COLORS.primary.gradient }}>
              {copied ? <Check size={20} color={COLORS.success.main} /> : <Copy size={20} color="#fff" />}
            </button>
          </div>
          <div className="text-xs mt-2" style={{ color: COLORS.text.tertiary }}>
            {referralStats.total_referrals} friend{referralStats.total_referrals !== 1 ? 's' : ''} invited
          </div>
        </div>
      )}

      {/* Logout */}
      <button data-testid="logout-btn" onClick={logout} className="w-full py-3 rounded-xl text-sm font-semibold flex items-center justify-center gap-2 transition-colors" style={{ background: COLORS.error.bg, color: COLORS.error.main, border: `1px solid ${COLORS.error.main}33` }}>
        <LogOut size={16} /> Logout
      </button>

      {/* Modals */}
      {showEditName && <EditNameModal currentName={user?.username} onSave={handleNameSave} onClose={() => setShowEditName(false)} />}
      {showChangePin && <ChangePinModal onClose={() => setShowChangePin(false)} onSuccess={handlePinChanged} />}
      {showShareCard && <ShareCardModal user={user} onClose={() => setShowShareCard(false)} />}
    </div>
  );
}
