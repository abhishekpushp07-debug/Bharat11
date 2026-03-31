/**
 * AdminUsersTab — User Management for Super Admin
 * View all users, search, view details
 */
import { useState, useEffect, useCallback } from 'react';
import apiClient from '../../api/client';
import { COLORS } from '../../constants/design';
import { Search, User, ChevronRight, Loader2, ArrowLeft, Phone } from 'lucide-react';

function UserDetail({ userId, onBack }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await apiClient.get(`/admin/users/${userId}`);
        setData(res.data);
      } catch (e) { console.error(e); }
      finally { setLoading(false); }
    };
    fetch();
  }, [userId]);

  if (loading) return <div className="flex justify-center py-10"><Loader2 className="animate-spin" size={20} color={COLORS.primary.main} /></div>;
  if (!data) return <div className="text-center py-6 text-xs" style={{ color: COLORS.text.tertiary }}>User not found</div>;

  const { user, stats } = data;
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
          <div>
            <div className="text-sm font-bold text-white">{user.name || 'No Name'}</div>
            <div className="flex items-center gap-1 text-[10px]" style={{ color: COLORS.text.tertiary }}>
              <Phone size={10} /> {user.phone}
            </div>
            <div className="text-[9px] mt-0.5" style={{ color: COLORS.text.tertiary }}>Joined: {new Date(user.created_at).toLocaleDateString()}</div>
          </div>
        </div>

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
      </div>

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
    </div>
  );
}

export default function AdminUsersTab() {
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedUserId, setSelectedUserId] = useState(null);

  const fetchUsers = useCallback(async (q = '') => {
    setLoading(true);
    try {
      const res = await apiClient.get(`/admin/users?q=${encodeURIComponent(q)}&limit=100`);
      setUsers(res.data.users);
      setTotal(res.data.total);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);

  const handleSearch = (val) => {
    setSearch(val);
    const t = setTimeout(() => fetchUsers(val), 300);
    return () => clearTimeout(t);
  };

  if (selectedUserId) return <UserDetail userId={selectedUserId} onBack={() => setSelectedUserId(null)} />;

  return (
    <div data-testid="admin-users-tab" className="space-y-3">
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

      <div className="flex items-center justify-between px-1">
        <div className="text-[10px] font-bold" style={{ color: COLORS.text.tertiary }}>{total} users total</div>
      </div>

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
              style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
              <div className="w-9 h-9 rounded-full flex items-center justify-center shrink-0"
                style={{ background: `${u.is_admin ? '#FFD700' : COLORS.primary.main}22` }}>
                <User size={16} color={u.is_admin ? '#FFD700' : COLORS.primary.main} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1.5">
                  <span className="text-xs font-bold text-white truncate">{u.name || 'No Name'}</span>
                  {u.is_admin && <span className="text-[7px] px-1.5 py-0.5 rounded-full font-bold" style={{ background: '#FFD70022', color: '#FFD700' }}>ADMIN</span>}
                </div>
                <div className="text-[10px] flex items-center gap-2" style={{ color: COLORS.text.tertiary }}>
                  <span>{u.phone}</span>
                  <span>{u.rank_title || 'Rookie'}</span>
                </div>
              </div>
              <div className="text-right shrink-0">
                <div className="text-xs font-bold" style={{ color: COLORS.primary.main }}>{u.total_points || 0}</div>
                <div className="text-[8px]" style={{ color: COLORS.text.tertiary }}>{u.total_entries || 0} entries</div>
              </div>
              <ChevronRight size={14} color={COLORS.text.tertiary} />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
