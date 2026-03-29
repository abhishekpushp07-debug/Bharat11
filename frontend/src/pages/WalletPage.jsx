import { useState, useEffect, useCallback } from 'react';
import { useAuthStore } from '../stores/authStore';
import apiClient from '../api/client';
import { COLORS } from '../constants/design';
import { Coins, ArrowUpCircle, ArrowDownCircle, Gift, Clock, ChevronRight } from 'lucide-react';

const REASON_LABELS = {
  signup_bonus: 'Signup Bonus',
  daily_reward: 'Daily Reward',
  contest_entry: 'Contest Entry',
  contest_win: 'Contest Win',
  referral_bonus: 'Referral Bonus',
  admin_credit: 'Admin Credit',
  admin_debit: 'Admin Debit',
  refund: 'Refund',
};

export default function WalletPage() {
  const { user, refreshUser } = useAuthStore();
  const [balance, setBalance] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [total, setTotal] = useState(0);
  const [claiming, setClaiming] = useState(false);
  const [claimResult, setClaimResult] = useState(null);

  useEffect(() => { fetchBalance(); fetchTransactions(1); }, []);

  const fetchBalance = async () => {
    try {
      const res = await apiClient.get('/wallet/balance');
      setBalance(res.data);
    } catch (e) { /* silent */ }
  };

  const fetchTransactions = async (p) => {
    try {
      const res = await apiClient.get(`/wallet/transactions?page=${p}&limit=15`);
      if (p === 1) {
        setTransactions(res.data.transactions);
      } else {
        setTransactions(prev => [...prev, ...res.data.transactions]);
      }
      setHasMore(res.data.has_more);
      setTotal(res.data.total);
      setPage(p);
    } catch (e) { /* silent */ }
  };

  const claimDaily = async () => {
    setClaiming(true);
    setClaimResult(null);
    try {
      const res = await apiClient.post('/wallet/claim-daily');
      setClaimResult(res.data);
      fetchBalance();
      fetchTransactions(1);
      if (refreshUser) refreshUser();
    } catch (e) {
      setClaimResult({ error: e.response?.data?.detail?.message || 'Already claimed today' });
    } finally {
      setClaiming(false);
    }
  };

  const formatDate = (d) => {
    const date = new Date(d);
    return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div data-testid="wallet-page" className="pb-6 space-y-4">
      {/* Balance Card */}
      <div data-testid="balance-card" className="rounded-2xl p-5 relative overflow-hidden" style={{ background: `linear-gradient(135deg, ${COLORS.primary.dark} 0%, ${COLORS.primary.main} 50%, #FF6B6B 100%)` }}>
        <div className="absolute inset-0 opacity-10" style={{ background: 'radial-gradient(circle at 80% 20%, rgba(255,255,255,0.3), transparent 70%)' }} />
        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-1">
            <Coins size={18} color="#FFD700" />
            <span className="text-sm font-medium text-white/80">Total Balance</span>
          </div>
          <div data-testid="balance-amount" className="text-4xl font-bold text-white" style={{ fontFamily: "'Rajdhani', sans-serif" }}>
            {(balance?.balance ?? user?.coins_balance ?? 0).toLocaleString()}
          </div>
          <div className="text-sm text-white/60 mt-1">Virtual Coins</div>
        </div>
      </div>

      {/* Daily Reward */}
      <div data-testid="daily-reward-card" className="rounded-2xl p-4" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: COLORS.warning.bg }}>
              <Gift size={20} color={COLORS.warning.main} />
            </div>
            <div>
              <div className="text-sm font-semibold text-white">Daily Reward</div>
              <div className="text-xs" style={{ color: COLORS.text.secondary }}>
                Streak: {balance?.daily_streak || 0} day{(balance?.daily_streak || 0) !== 1 ? 's' : ''}
              </div>
            </div>
          </div>
          <button
            data-testid="claim-daily-btn"
            onClick={claimDaily}
            disabled={claiming || balance?.can_claim_daily === false}
            className="px-4 py-2 rounded-xl text-sm font-bold transition-all disabled:opacity-50"
            style={{
              background: balance?.can_claim_daily ? COLORS.primary.gradient : COLORS.background.tertiary,
              color: balance?.can_claim_daily ? '#fff' : COLORS.text.tertiary
            }}
          >
            {claiming ? '...' : balance?.can_claim_daily ? 'Claim' : 'Claimed'}
          </button>
        </div>
        {claimResult && !claimResult.error && (
          <div className="mt-3 p-2.5 rounded-lg text-center text-sm" style={{ background: COLORS.success.bg, color: COLORS.success.main }}>
            +{claimResult.reward_amount} coins! Day {claimResult.streak} streak
          </div>
        )}
      </div>

      {/* Transactions */}
      <div className="rounded-2xl overflow-hidden" style={{ background: COLORS.background.card, border: `1px solid ${COLORS.border.light}` }}>
        <div className="px-4 py-3 flex items-center justify-between" style={{ borderBottom: `1px solid ${COLORS.border.light}` }}>
          <span className="text-sm font-semibold text-white">Transaction History</span>
          <span className="text-xs" style={{ color: COLORS.text.tertiary }}>{total} total</span>
        </div>
        
        {transactions.length === 0 ? (
          <div className="py-10 text-center text-sm" style={{ color: COLORS.text.tertiary }}>No transactions yet</div>
        ) : (
          <div data-testid="transactions-list">
            {transactions.map((t, i) => (
              <div key={t.id} className="flex items-center gap-3 px-4 py-3" style={{ borderBottom: i < transactions.length - 1 ? `1px solid ${COLORS.border.light}` : 'none' }}>
                <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ background: t.type === 'credit' ? COLORS.success.bg : COLORS.error.bg }}>
                  {t.type === 'credit' ? <ArrowDownCircle size={18} color={COLORS.success.main} /> : <ArrowUpCircle size={18} color={COLORS.error.main} />}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-white truncate">{REASON_LABELS[t.reason] || t.reason}</div>
                  <div className="text-xs truncate" style={{ color: COLORS.text.tertiary }}>{t.description || formatDate(t.created_at)}</div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-bold" style={{ color: t.type === 'credit' ? COLORS.success.main : COLORS.error.main, fontFamily: "'Rajdhani', sans-serif" }}>
                    {t.type === 'credit' ? '+' : '-'}{t.amount.toLocaleString()}
                  </div>
                  <div className="text-xs" style={{ color: COLORS.text.tertiary }}>{t.balance_after.toLocaleString()}</div>
                </div>
              </div>
            ))}
          </div>
        )}
        
        {hasMore && (
          <button data-testid="load-more-btn" onClick={() => fetchTransactions(page + 1)} className="w-full py-3 text-sm font-medium transition-colors" style={{ color: COLORS.primary.main, borderTop: `1px solid ${COLORS.border.light}` }}>
            Load More
          </button>
        )}
      </div>
    </div>
  );
}
