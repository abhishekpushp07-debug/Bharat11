/**
 * AdminUsersTab — Enhanced User Management for Super Admin
 * Search, view details, ban/unban, adjust coins, reset PIN
 */
import { useState, useEffect, useCallback } from 'react';
import apiClient from '../../api/client';
import { COLORS } from '../../constants/design';
import { Search, User, ChevronRight, Loader2, ArrowLeft, Phone, Shield, Ban, Coins, Lock, X } from 'lucide-react';

// ====== PIN Reset Modal ======
function PinResetModal({ userId, userName, onClose, onDone }) {
  const [pin, setPin] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleReset = async () => {
    if (pin.length !== 4 || !/^\d{4}$/.test(pin)) { setError('4-digit PIN daalo'); return; }
    setLoading(true);
    try {
      await apiClient.post(`/admin/users/${userId}/reset-pin`, { new_pin: pin });
      setSuccess(true);
      setTimeout(() => { onDone(); onClose(); }, 1200);
    } catch (e) { setError(e?.response?.data?.detail || 'Reset failed'); }
    finally { setLoading(false); }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: 'rgba(0,0,0,0.7)' }}>
      <div data-testid="admin-pin-reset-modal" className="w-full max-w-xs rounded-2xl p-4 space-y-3" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.medium}` }}>
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-white">Reset PIN - {userName}</h3>
          <button onClick={onClose} className="p-1 rounded-full" style={{ background: COLORS.background.tertiary }}><X size={14} color={COLORS.text.secondary} /></button>
        </div>
        {success ? (
          <div className="text-center py-4 text-sm font-bold" style={{ color: COLORS.success.main }}>PIN Reset Done!</div>
        ) : (
          <>
            <input data-testid="admin-new-pin-input" type="tel" inputMode="numeric" maxLength={4} value={pin}
              onChange={e => { setPin(e.target.value.replace(/\D/g, '').slice(0, 4)); setError(''); }}
              placeholder="New 4-digit PIN"
              className="w-full px-3 py-2.5 rounded-xl text-sm text-white text-center tracking-[0.3em] font-bold bg-transparent outline-none"
              style={{ background: COLORS.background.tertiary, border: `1px solid ${error ? COLORS.error.main : COLORS.border.light}` }} />
            {error && <p className="text-[10px]" style={{ color: COLORS.error.main }}>{error}</p>}
            <button data-testid="admin-reset-pin-confirm" onClick={handleReset} disabled={loading || pin.length !== 4}
              className="w-full py-2.5 rounded-xl text-xs font-bold text-white flex items-center justify-center gap-2 disabled:opacity-50"
              style={{ background: COLORS.warning.main }}>
              {loading ? <Loader2 size={14} className="animate-spin" /> : <Lock size={14} />}
              Reset PIN
            </button>
          </>
        )}
      </div>
    </div>
  );
}

// ====== Coin Adjust Modal ======
function CoinAdjustModal({ userId, userName, currentBalance, onClose, onDone }) {
  const [amount, setAmount] = useState('');
  const [reason, setReason] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAdjust = async () => {
    const amt = parseInt(amount);
    if (isNaN(amt) || amt === 0) { setError('Amount enter karo'); return; }
    if (!reason.trim()) { setError('Reason daalo'); return; }
    setLoading(true);
    try {
      await apiClient.post(`/admin/users/${userId}/adjust-coins`, { amount: amt, reason: reason.trim() });
      onDone();
      onClose();
    } catch (e) { setError(e?.response?.data?.detail || 'Failed'); }
    finally { setLoading(false); }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: 'rgba(0,0,0,0.7)' }}>
      <div data-testid="coin-adjust-modal" className="w-full max-w-xs rounded-2xl p-4 space-y-3" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.medium}` }}>
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-white">Adjust Coins - {userName}</h3>
          <button onClick={onClose} className="p-1 rounded-full" style={{ background: COLORS.background.tertiary }}><X size={14} color={COLORS.text.secondary} /></button>
        </div>
        <div className="text-xs" style={{ color: COLORS.text.secondary }}>Current: <span className="font-bold" style={{ color: '#f59e0b' }}>{currentBalance} coins</span></div>
        <input data-testid="coin-amount-input" type="number" value={amount} onChange={e => { setAmount(e.target.value); setError(''); }}
          placeholder="Amount (+500 or -200)"
          className="w-full px-3 py-2.5 rounded-xl text-sm text-white bg-transparent outline-none"
          style={{ background: COLORS.background.tertiary, border: `1px solid ${error ? COLORS.error.main : COLORS.border.light}` }} />
        <input data-testid="coin-reason-input" value={reason} onChange={e => setReason(e.target.value)}
          placeholder="Reason (e.g., Bonus, Penalty)"
          className="w-full px-3 py-2.5 rounded-xl text-sm text-white bg-transparent outline-none"
          style={{ background: COLORS.background.tertiary, border: `1px solid ${COLORS.border.light}` }} />
        {error && <p className="text-[10px]" style={{ color: COLORS.error.main }}>{error}</p>}
        <div className="grid grid-cols-2 gap-2">
          {[500, 1000, -500, -1000].map(v => (
            <button key={v} onClick={() => setAmount(String(v))}
              className="py-1.5 rounded-lg text-[10px] font-bold transition-all"
              style={{ background: v > 0 ? '#22c55e18' : '#ef444418', color: v > 0 ? '#22c55e' : '#ef4444', border: `1px solid ${v > 0 ? '#22c55e30' : '#ef444430'}` }}>
              {v > 0 ? '+' : ''}{v}
            </button>
          ))}
        </div>
        <button data-testid="coin-adjust-confirm" onClick={handleAdjust} disabled={loading}
          className="w-full py-2.5 rounded-xl text-xs font-bold text-white flex items-center justify-center gap-2 disabled:opacity-50"
          style={{ background: COLORS.primary.main }}>
          {loading ? <Loader2 size={14} className="animate-spin" /> : <Coins size={14} />}
          Adjust Coins
        </button>
      </div>
    </div>
  );
}

// ====== User Detail View ======
function UserDetail({ userId, onBack }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [banLoading, setBanLoading] = useState(false);
  const [showPinReset, setShowPinReset] = useState(false);
  const [showCoinAdjust, setShowCoinAdjust] = useState(false);

  const fetchUser = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiClient.get(`/admin/users/${userId}`);
      setData(res.data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [userId]);

  useEffect(() => { fetchUser(); }, [fetchUser]);

  const handleBan = async () => {
    setBanLoading(true);
    try {
      await apiClient.post(`/admin/users/${userId}/ban`);
      fetchUser();
    } catch (e) { alert(e?.response?.data?.detail || 'Action failed'); }
    finally { setBanLoading(false); }
  };

  if (loading) return <div className="flex justify-center py-10"><Loader2 className="animate-spin" size={20} color={COLORS.primary.main} /></div>;
  if (!data) return <div className="text-center py-6 text-xs" style={{ color: COLORS.text.tertiary }}>User not found</div>;

  const { user, stats } = data;
  const isBanned = user.is_banned;

  return (
    <div className="space-y-3">
      <button data-testid="user-detail-back" onClick={onBack} className="flex items-center gap-1 text-xs" style={{ color: COLORS.primary.main }}>
        <ArrowLeft size={14} /> Back to Users
      </button>

      <div className="p-4 rounded-2xl space-y-3" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full flex items-center justify-center" style={{ background: `${COLORS.primary.main}22` }}>
            <User size={20} color={COLORS.primary.main} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-1.5">
              <span className="text-sm font-bold text-white truncate">{user.username || user.name || 'No Name'}</span>
              {user.is_admin && <span className="text-[7px] px-1.5 py-0.5 rounded-full font-bold" style={{ background: '#FFD70022', color: '#FFD700' }}>ADMIN</span>}
              {isBanned && <span className="text-[7px] px-1.5 py-0.5 rounded-full font-bold" style={{ background: '#ef444422', color: '#ef4444' }}>BANNED</span>}
            </div>
            <div className="flex items-center gap-1 text-[10px]" style={{ color: COLORS.text.tertiary }}>
              <Phone size={10} /> {user.phone}
            </div>
            <div className="text-[9px] mt-0.5" style={{ color: COLORS.text.tertiary }}>Joined: {new Date(user.created_at).toLocaleDateString()}</div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-3 gap-2">
          {[
            { label: 'Predictions', val: stats.recent_total || stats.total_predictions || 0, color: '#3b82f6' },
            { label: 'Correct', val: stats.recent_correct || stats.correct_predictions || 0, color: '#22c55e' },
            { label: 'Accuracy', val: `${stats.accuracy || 0}%`, color: (stats.accuracy || 0) >= 50 ? '#22c55e' : '#ef4444' },
          ].map(s => (
            <div key={s.label} className="text-center p-2 rounded-xl" style={{ background: `${s.color}11`, border: `1px solid ${s.color}22` }}>
              <div className="text-sm font-bold" style={{ color: s.color, fontFamily: "'Rajdhani', sans-serif" }}>{s.val}</div>
              <div className="text-[8px] font-bold uppercase" style={{ color: COLORS.text.tertiary }}>{s.label}</div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-2 gap-2">
          {[
            { label: 'Wallet', val: user.wallet_balance || user.coins_balance || 0, color: '#f59e0b' },
            { label: 'Rank', val: user.rank_title || 'Rookie', color: '#a855f7' },
            { label: 'Total Points', val: user.total_points || 0, color: '#FFD700' },
            { label: 'Entries', val: stats.total_contests || stats.total_entries || 0, color: '#06b6d4' },
          ].map(s => (
            <div key={s.label} className="text-center p-2 rounded-xl" style={{ background: `${s.color}11`, border: `1px solid ${s.color}22` }}>
              <div className="text-sm font-bold" style={{ color: s.color, fontFamily: "'Rajdhani', sans-serif" }}>{s.val}</div>
              <div className="text-[8px] font-bold uppercase" style={{ color: COLORS.text.tertiary }}>{s.label}</div>
            </div>
          ))}
        </div>

        {/* Admin Action Buttons */}
        <div className="grid grid-cols-3 gap-2 pt-2 border-t" style={{ borderColor: COLORS.border.light }}>
          <button data-testid="admin-ban-btn" onClick={handleBan} disabled={banLoading || user.is_admin}
            className="flex flex-col items-center gap-1 py-2.5 rounded-xl text-[10px] font-bold transition-all disabled:opacity-30"
            style={{ background: isBanned ? '#22c55e15' : '#ef444415', color: isBanned ? '#22c55e' : '#ef4444', border: `1px solid ${isBanned ? '#22c55e30' : '#ef444430'}` }}>
            {banLoading ? <Loader2 size={14} className="animate-spin" /> : <Ban size={14} />}
            {isBanned ? 'Unban' : 'Ban'}
          </button>
          <button data-testid="admin-coin-btn" onClick={() => setShowCoinAdjust(true)}
            className="flex flex-col items-center gap-1 py-2.5 rounded-xl text-[10px] font-bold transition-all"
            style={{ background: '#f59e0b15', color: '#f59e0b', border: '1px solid #f59e0b30' }}>
            <Coins size={14} /> Coins
          </button>
          <button data-testid="admin-pin-reset-btn" onClick={() => setShowPinReset(true)}
            className="flex flex-col items-center gap-1 py-2.5 rounded-xl text-[10px] font-bold transition-all"
            style={{ background: `${COLORS.warning.main}15`, color: COLORS.warning.main, border: `1px solid ${COLORS.warning.main}30` }}>
            <Lock size={14} /> PIN Reset
          </button>
        </div>
      </div>

      {/* Recent entries */}
      {(data.recent_entries || data.entries || []).length > 0 && (
        <div className="space-y-1.5">
          <div className="text-[10px] font-bold uppercase tracking-wider" style={{ color: COLORS.text.tertiary }}>Recent Contest Entries</div>
          {(data.recent_entries || data.entries || []).slice(0, 10).map(e => (
            <div key={e.id || e.contest_id} className="flex items-center justify-between p-2.5 rounded-xl" style={{ background: COLORS.background.card }}>
              <div>
                <div className="text-[11px] font-bold text-white">{e.contest_name || e.contest_id}</div>
                <div className="text-[9px]" style={{ color: COLORS.text.tertiary }}>{new Date(e.created_at).toLocaleDateString()}</div>
              </div>
              <div className="text-right">
                <div className="text-xs font-bold" style={{ color: COLORS.primary.main }}>{e.score || 0} pts</div>
                <div className="text-[9px]" style={{ color: e.rank ? '#22c55e' : COLORS.text.tertiary }}>
                  {e.rank ? `#${e.rank}` : 'Active'}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modals */}
      {showPinReset && <PinResetModal userId={userId} userName={user.username || user.name || ''} onClose={() => setShowPinReset(false)} onDone={fetchUser} />}
      {showCoinAdjust && <CoinAdjustModal userId={userId} userName={user.username || user.name || ''} currentBalance={user.coins_balance || 0} onClose={() => setShowCoinAdjust(false)} onDone={fetchUser} />}
    </div>
  );
}

// ====== Main Users Tab ======
export default function AdminUsersTab() {
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedUserId, setSelectedUserId] = useState(null);
  const [filter, setFilter] = useState('all'); // all, banned

  const fetchUsers = useCallback(async (q = '', bannedOnly = false) => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ search: q, limit: '100' });
      if (bannedOnly) params.append('banned_only', 'true');
      const res = await apiClient.get(`/admin/users?${params}`);
      setUsers(res.data.users);
      setTotal(res.data.total);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchUsers('', filter === 'banned'); }, [fetchUsers, filter]);

  const handleSearch = (val) => {
    setSearch(val);
    const t = setTimeout(() => fetchUsers(val, filter === 'banned'), 300);
    return () => clearTimeout(t);
  };

  if (selectedUserId) return <UserDetail userId={selectedUserId} onBack={() => { setSelectedUserId(null); fetchUsers(search, filter === 'banned'); }} />;

  return (
    <div data-testid="admin-users-tab" className="space-y-3">
      {/* Search */}
      <div className="relative">
        <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2" color={COLORS.text.tertiary} />
        <input
          data-testid="user-search-input"
          value={search}
          onChange={e => handleSearch(e.target.value)}
          placeholder="Search by name or phone..."
          className="w-full pl-9 pr-3 py-2.5 rounded-xl text-xs text-white bg-transparent outline-none"
          style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}
        />
      </div>

      {/* Filters */}
      <div className="flex items-center gap-2">
        {['all', 'banned'].map(f => (
          <button key={f} data-testid={`filter-${f}`} onClick={() => setFilter(f)}
            className="px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase transition-all"
            style={{
              background: filter === f ? COLORS.primary.main : COLORS.background.tertiary,
              color: filter === f ? '#fff' : COLORS.text.secondary,
            }}>
            {f === 'all' ? `All (${total})` : 'Banned'}
          </button>
        ))}
      </div>

      {/* Users List */}
      {loading ? (
        <div className="flex justify-center py-8"><Loader2 className="animate-spin" size={20} color={COLORS.primary.main} /></div>
      ) : users.length === 0 ? (
        <div className="text-center py-8 text-xs" style={{ color: COLORS.text.tertiary }}>No users found</div>
      ) : (
        <div className="space-y-1.5">
          {users.map(u => (
            <button key={u.id} data-testid={`user-row-${u.id}`}
              onClick={() => setSelectedUserId(u.id)}
              className="w-full flex items-center gap-3 p-3 rounded-xl text-left transition-all active:scale-[0.98]"
              style={{ background: COLORS.background.card, border: `1px solid ${u.is_banned ? '#ef444430' : COLORS.border.light}` }}>
              <div className="w-9 h-9 rounded-full flex items-center justify-center shrink-0"
                style={{ background: `${u.is_admin ? '#FFD700' : u.is_banned ? '#ef4444' : COLORS.primary.main}22` }}>
                {u.is_banned ? <Ban size={14} color="#ef4444" /> : <User size={16} color={u.is_admin ? '#FFD700' : COLORS.primary.main} />}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1.5">
                  <span className="text-xs font-bold text-white truncate">{u.username || u.name || 'No Name'}</span>
                  {u.is_admin && <span className="text-[7px] px-1.5 py-0.5 rounded-full font-bold" style={{ background: '#FFD70022', color: '#FFD700' }}>ADMIN</span>}
                  {u.is_banned && <span className="text-[7px] px-1.5 py-0.5 rounded-full font-bold" style={{ background: '#ef444422', color: '#ef4444' }}>BAN</span>}
                </div>
                <div className="text-[10px] flex items-center gap-2" style={{ color: COLORS.text.tertiary }}>
                  <span>{u.phone}</span>
                  <span>{u.rank_title || 'Rookie'}</span>
                </div>
              </div>
              <div className="text-right shrink-0">
                <div className="text-xs font-bold" style={{ color: COLORS.primary.main }}>{u.total_points || 0}</div>
                <div className="text-[8px]" style={{ color: '#f59e0b' }}>{u.coins_balance || 0}c</div>
              </div>
              <ChevronRight size={14} color={COLORS.text.tertiary} />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
