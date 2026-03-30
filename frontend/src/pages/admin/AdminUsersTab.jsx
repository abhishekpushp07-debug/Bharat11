/**
 * Admin Users Tab — User Management
 * Search, ban/unban, coin adjustment, prediction history
 */
import { useState, useEffect, useCallback } from 'react';
import apiClient from '../../api/client';
import { COLORS } from '../../constants/design';
import { Search, User, Ban, Coins, ChevronRight, ChevronLeft, ArrowLeft, Shield, TrendingUp, Target, Flame, X, Check, AlertCircle, Loader2 } from 'lucide-react';

function UserDetailModal({ userId, onClose }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [coinAmount, setCoinAmount] = useState('');
  const [coinReason, setCoinReason] = useState('');
  const [adjusting, setAdjusting] = useState(false);
  const [banning, setBanning] = useState(false);
  const [actionResult, setActionResult] = useState(null);

  useEffect(() => {
    apiClient.get(`/admin/users/${userId}`)
      .then(res => setData(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [userId]);

  const handleBan = async () => {
    setBanning(true);
    try {
      const res = await apiClient.post(`/admin/users/${userId}/ban`);
      setActionResult({ type: 'success', msg: `User ${res.data.action}` });
      setData(prev => ({
        ...prev,
        user: { ...prev.user, is_banned: res.data.is_banned }
      }));
    } catch (e) {
      setActionResult({ type: 'error', msg: e?.response?.data?.detail || 'Failed' });
    }
    setBanning(false);
  };

  const handleCoinAdjust = async () => {
    if (!coinAmount) return;
    setAdjusting(true);
    try {
      const res = await apiClient.post(`/admin/users/${userId}/adjust-coins`, {
        amount: parseInt(coinAmount),
        reason: coinReason || 'Admin adjustment'
      });
      setActionResult({ type: 'success', msg: `Coins adjusted: ${res.data.amount > 0 ? '+' : ''}${res.data.amount}. New balance: ${res.data.new_balance}` });
      setData(prev => ({
        ...prev,
        user: { ...prev.user, coins_balance: res.data.new_balance }
      }));
      setCoinAmount('');
      setCoinReason('');
    } catch (e) {
      setActionResult({ type: 'error', msg: e?.response?.data?.detail || 'Failed' });
    }
    setAdjusting(false);
  };

  if (loading) {
    return (
      <div className="fixed inset-0 z-50 flex items-end justify-center" style={{ background: 'rgba(0,0,0,0.7)' }}>
        <div className="w-full max-w-lg rounded-t-3xl p-6" style={{ background: COLORS.background.secondary }}>
          <div className="flex justify-center py-10">
            <Loader2 className="animate-spin" size={24} color={COLORS.accent.gold} />
          </div>
        </div>
      </div>
    );
  }

  const user = data?.user;
  const stats = data?.stats;

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center" style={{ background: 'rgba(0,0,0,0.7)' }} onClick={onClose}>
      <div className="w-full max-w-lg rounded-t-3xl overflow-hidden" style={{ background: COLORS.background.secondary, maxHeight: '85vh' }}
        onClick={e => e.stopPropagation()}>

        {/* Header */}
        <div className="p-4 flex items-center justify-between" style={{ borderBottom: `1px solid ${COLORS.border.light}` }}>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ background: COLORS.primary.main + '20' }}>
              <User size={18} color={COLORS.primary.main} />
            </div>
            <div>
              <h3 data-testid="user-detail-name" className="text-sm font-bold text-white">{user?.username || 'Unknown'}</h3>
              <p className="text-[10px]" style={{ color: COLORS.text.tertiary }}>{user?.phone} | ID: {user?.id?.slice(0, 8)}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 rounded-lg" style={{ background: COLORS.background.card }}>
            <X size={16} color={COLORS.text.tertiary} />
          </button>
        </div>

        <div className="overflow-y-auto p-4 space-y-3" style={{ maxHeight: 'calc(85vh - 60px)' }}>
          {/* Action Result */}
          {actionResult && (
            <div className="flex items-center gap-2 p-2.5 rounded-lg text-xs" style={{
              background: actionResult.type === 'success' ? COLORS.success.bg : COLORS.error.bg,
              color: actionResult.type === 'success' ? COLORS.success.main : COLORS.error.main,
            }}>
              {actionResult.type === 'success' ? <Check size={14} /> : <AlertCircle size={14} />}
              {actionResult.msg}
            </div>
          )}

          {/* Quick Stats */}
          <div className="grid grid-cols-4 gap-2">
            {[
              { label: 'Coins', value: user?.coins_balance?.toLocaleString() || '0', Icon: Coins, color: COLORS.accent.gold },
              { label: 'Contests', value: stats?.total_contests || 0, Icon: Target, color: COLORS.info.main },
              { label: 'Accuracy', value: `${stats?.accuracy || 0}%`, Icon: TrendingUp, color: COLORS.success.main },
              { label: 'Streak', value: user?.prediction_streak || 0, Icon: Flame, color: '#FF6B00' },
            ].map(({ label, value, Icon, color }) => (
              <div key={label} className="rounded-xl p-2.5 text-center" style={{ background: COLORS.background.card }}>
                <Icon size={14} color={color} className="mx-auto mb-1" />
                <div className="text-sm font-bold text-white">{value}</div>
                <div className="text-[8px]" style={{ color: COLORS.text.tertiary }}>{label}</div>
              </div>
            ))}
          </div>

          {/* Ban Status */}
          <div className="rounded-xl p-3 flex items-center justify-between" style={{
            background: user?.is_banned ? COLORS.error.bg : COLORS.background.card,
            border: `1px solid ${user?.is_banned ? COLORS.error.main + '33' : COLORS.border.light}`
          }}>
            <div className="flex items-center gap-2">
              <Ban size={14} color={user?.is_banned ? COLORS.error.main : COLORS.text.tertiary} />
              <span className="text-xs font-medium" style={{ color: user?.is_banned ? COLORS.error.main : COLORS.text.secondary }}>
                {user?.is_banned ? 'BANNED' : 'Active'}
              </span>
            </div>
            <button data-testid="ban-toggle" onClick={handleBan} disabled={banning}
              className="px-3 py-1.5 rounded-lg text-[10px] font-bold"
              style={{
                background: user?.is_banned ? COLORS.success.main + '20' : COLORS.error.main + '20',
                color: user?.is_banned ? COLORS.success.main : COLORS.error.main,
              }}>
              {banning ? '...' : user?.is_banned ? 'UNBAN' : 'BAN'}
            </button>
          </div>

          {/* Coin Adjustment */}
          <div className="rounded-xl p-3 space-y-2" style={{ background: COLORS.background.card }}>
            <div className="flex items-center gap-2 mb-1">
              <Coins size={14} color={COLORS.accent.gold} />
              <span className="text-xs font-bold text-white">Adjust Coins</span>
            </div>
            <div className="flex gap-2">
              <input data-testid="coin-amount-input" type="number" value={coinAmount} onChange={e => setCoinAmount(e.target.value)}
                placeholder="Amount (+/-)" className="flex-1 text-xs px-3 py-2 rounded-lg outline-none"
                style={{ background: COLORS.background.tertiary, color: 'white', border: `1px solid ${COLORS.border.light}` }} />
              <input type="text" value={coinReason} onChange={e => setCoinReason(e.target.value)}
                placeholder="Reason" className="flex-1 text-xs px-3 py-2 rounded-lg outline-none"
                style={{ background: COLORS.background.tertiary, color: 'white', border: `1px solid ${COLORS.border.light}` }} />
            </div>
            <button data-testid="adjust-coins-btn" onClick={handleCoinAdjust} disabled={adjusting || !coinAmount}
              className="w-full py-2 rounded-lg text-xs font-bold transition-all"
              style={{
                background: coinAmount ? COLORS.accent.gold + '20' : COLORS.background.tertiary,
                color: coinAmount ? COLORS.accent.gold : COLORS.text.tertiary,
              }}>
              {adjusting ? 'Processing...' : 'Apply Adjustment'}
            </button>
          </div>

          {/* Recent Entries */}
          {data?.recent_entries?.length > 0 && (
            <div className="space-y-1.5">
              <h4 className="text-xs font-bold text-white">Recent Predictions</h4>
              {data.recent_entries.slice(0, 5).map((entry, i) => (
                <div key={i} className="rounded-lg p-2.5 flex items-center justify-between" style={{ background: COLORS.background.card }}>
                  <div>
                    <div className="text-[10px]" style={{ color: COLORS.text.secondary }}>
                      Contest: {entry.contest_id?.slice(0, 8)}...
                    </div>
                    <div className="text-xs font-medium text-white">
                      {entry.predictions?.length || 0} predictions | {entry.total_points || 0} pts
                    </div>
                  </div>
                  <div className="text-[9px] font-bold" style={{ color: COLORS.text.tertiary }}>
                    #{entry.rank || '-'}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function AdminUsersTab() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [bannedOnly, setBannedOnly] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState(null);

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: '15',
        sort_by: '-created_at',
      });
      if (search) params.set('search', search);
      if (bannedOnly) params.set('banned_only', 'true');

      const res = await apiClient.get(`/admin/users?${params}`);
      setUsers(res.data.users || []);
      setTotalPages(res.data.pages || 1);
      setTotal(res.data.total || 0);
    } catch (_) {}
    finally { setLoading(false); }
  }, [page, search, bannedOnly]);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);

  // Debounced search
  const [searchInput, setSearchInput] = useState('');
  useEffect(() => {
    const timer = setTimeout(() => {
      setSearch(searchInput);
      setPage(1);
    }, 400);
    return () => clearTimeout(timer);
  }, [searchInput]);

  return (
    <div data-testid="admin-users-tab" className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-white">User Management</h2>
        <span className="text-xs px-2.5 py-1 rounded-full" style={{ background: COLORS.background.card, color: COLORS.text.secondary }}>
          {total} users
        </span>
      </div>

      {/* Search + Filter */}
      <div className="flex gap-2">
        <div className="flex-1 relative">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2" color={COLORS.text.tertiary} />
          <input data-testid="user-search-input" type="text" value={searchInput} onChange={e => setSearchInput(e.target.value)}
            placeholder="Search username or phone..."
            className="w-full pl-9 pr-3 py-2.5 rounded-xl text-xs outline-none"
            style={{ background: COLORS.background.card, color: 'white', border: `1px solid ${COLORS.border.light}` }} />
        </div>
        <button data-testid="banned-filter"
          onClick={() => { setBannedOnly(!bannedOnly); setPage(1); }}
          className="px-3 py-2.5 rounded-xl text-[10px] font-bold shrink-0"
          style={{
            background: bannedOnly ? COLORS.error.bg : COLORS.background.card,
            color: bannedOnly ? COLORS.error.main : COLORS.text.tertiary,
            border: `1px solid ${bannedOnly ? COLORS.error.main + '33' : COLORS.border.light}`,
          }}>
          <Ban size={12} className="inline mr-1" />
          Banned
        </button>
      </div>

      {/* User List */}
      {loading ? (
        <div className="flex justify-center py-10">
          <Loader2 className="animate-spin" size={24} color={COLORS.accent.gold} />
        </div>
      ) : users.length === 0 ? (
        <div className="text-center py-10">
          <User size={32} color={COLORS.text.tertiary} className="mx-auto mb-2" />
          <p className="text-xs" style={{ color: COLORS.text.tertiary }}>No users found</p>
        </div>
      ) : (
        <div className="space-y-1.5">
          {users.map((u) => (
            <button key={u.id} data-testid={`user-row-${u.id?.slice(0, 8)}`}
              onClick={() => setSelectedUserId(u.id)}
              className="w-full flex items-center gap-3 p-3 rounded-xl text-left transition-all hover:opacity-80"
              style={{
                background: COLORS.background.card,
                border: `1px solid ${u.is_banned ? COLORS.error.main + '33' : COLORS.border.light}`,
              }}>
              <div className="w-9 h-9 rounded-full flex items-center justify-center shrink-0" style={{
                background: u.is_admin ? COLORS.accent.gold + '20' : COLORS.primary.main + '20'
              }}>
                {u.is_admin ? <Shield size={14} color={COLORS.accent.gold} /> : <User size={14} color={COLORS.primary.main} />}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1.5">
                  <span className="text-xs font-bold text-white truncate">{u.username}</span>
                  {u.is_banned && (
                    <span className="text-[8px] font-bold px-1.5 py-0.5 rounded" style={{ background: COLORS.error.bg, color: COLORS.error.main }}>BANNED</span>
                  )}
                  {u.is_admin && (
                    <span className="text-[8px] font-bold px-1.5 py-0.5 rounded" style={{ background: COLORS.accent.gold + '20', color: COLORS.accent.gold }}>ADMIN</span>
                  )}
                </div>
                <div className="flex items-center gap-3 mt-0.5">
                  <span className="text-[10px]" style={{ color: COLORS.text.tertiary }}>{u.phone}</span>
                  <span className="text-[10px] flex items-center gap-0.5" style={{ color: COLORS.accent.gold }}>
                    <Coins size={9} /> {u.coins_balance?.toLocaleString() || 0}
                  </span>
                  {(u.prediction_streak || 0) >= 3 && (
                    <span className="text-[10px] flex items-center gap-0.5" style={{ color: '#FF6B00' }}>
                      <Flame size={9} /> {u.prediction_streak}
                    </span>
                  )}
                </div>
              </div>

              <ChevronRight size={14} color={COLORS.text.tertiary} />
            </button>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-3 py-2">
          <button disabled={page <= 1} onClick={() => setPage(p => Math.max(1, p - 1))}
            className="p-2 rounded-lg" style={{ background: COLORS.background.card, opacity: page <= 1 ? 0.3 : 1 }}>
            <ChevronLeft size={14} color={COLORS.text.secondary} />
          </button>
          <span className="text-xs font-medium" style={{ color: COLORS.text.secondary }}>
            Page {page} of {totalPages}
          </span>
          <button disabled={page >= totalPages} onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            className="p-2 rounded-lg" style={{ background: COLORS.background.card, opacity: page >= totalPages ? 0.3 : 1 }}>
            <ChevronRight size={14} color={COLORS.text.secondary} />
          </button>
        </div>
      )}

      {/* User Detail Modal */}
      {selectedUserId && (
        <UserDetailModal userId={selectedUserId} onClose={() => { setSelectedUserId(null); fetchUsers(); }} />
      )}
    </div>
  );
}
