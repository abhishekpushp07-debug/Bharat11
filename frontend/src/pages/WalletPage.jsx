import { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';
import apiClient from '../api/client';
import { COLORS } from '../constants/design';
import { Coins, ArrowUpCircle, ArrowDownCircle, Gift, Scale, Shield, Ban, Gamepad2, Heart, Users, BadgeCheck } from 'lucide-react';

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

const LEGAL_POINTS = [
  {
    icon: Ban,
    title: 'No Real Money Deposits',
    titleHi: 'कोई असली पैसा जमा नहीं',
    desc: 'Bharat 11 does not accept any real money deposits. All coins are virtual and have no monetary value.',
    color: '#FF4444',
  },
  {
    icon: Ban,
    title: 'No Withdrawals',
    titleHi: 'कोई निकासी नहीं',
    desc: 'Virtual coins cannot be withdrawn or converted to real money. This is not a gambling platform.',
    color: '#FF6B35',
  },
  {
    icon: Gamepad2,
    title: 'Entertainment & Skill-Based',
    titleHi: 'मनोरंजन और कौशल-आधारित',
    desc: 'Under the Public Gambling Act, 1867 (Section 12), games of skill are exempt from gambling laws. Cricket prediction requires knowledge and analysis.',
    color: '#4ADE80',
  },
  {
    icon: Heart,
    title: 'Information & Education',
    titleHi: 'जानकारी और शिक्षा',
    desc: 'Platform provides cricket analytics, live scores, and match insights. Focused on enhancing fan engagement and cricket knowledge.',
    color: '#60A5FA',
  },
  {
    icon: Users,
    title: 'Social Gaming',
    titleHi: 'सामाजिक गेमिंग',
    desc: 'Compete with friends and community using virtual points. No stakes, no risk — pure social entertainment like fantasy leagues.',
    color: '#C084FC',
  },
  {
    icon: BadgeCheck,
    title: 'Compliant with IT Act, 2000',
    titleHi: 'IT अधिनियम 2000 का अनुपालन',
    desc: 'Platform follows Information Technology Act guidelines. User data is encrypted, no unfair practices, transparent scoring system.',
    color: '#FBBF24',
  },
];

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

      {/* ==================== LEGAL SECTION ==================== */}
      <div data-testid="legal-section" className="rounded-2xl overflow-hidden" style={{ background: 'linear-gradient(180deg, #0f1a12 0%, #0a0a0f 100%)', border: '1px solid rgba(74,222,128,0.15)' }}>
        {/* Header */}
        <div className="px-4 py-4 relative overflow-hidden" style={{ background: 'linear-gradient(135deg, rgba(74,222,128,0.08), rgba(34,197,94,0.04))' }}>
          <div className="absolute inset-0 pointer-events-none" style={{
            background: 'radial-gradient(ellipse at 20% 50%, rgba(74,222,128,0.06), transparent 70%)',
          }} />
          <div className="flex items-center gap-3 relative z-10">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'rgba(74,222,128,0.12)', border: '1px solid rgba(74,222,128,0.2)' }}>
              <Scale size={20} color="#4ade80" />
            </div>
            <div>
              <h3 className="text-sm font-black text-white tracking-tight">Why Bharat 11 is 100% Legal</h3>
              <p className="text-[10px] font-bold" style={{ color: '#4ade80' }}>Bharat 11 kyun poori tarah se legal hai</p>
            </div>
          </div>
          <div className="flex items-center gap-1.5 mt-2 relative z-10">
            <Shield size={10} color="rgba(74,222,128,0.6)" />
            <span className="text-[9px] font-bold" style={{ color: 'rgba(74,222,128,0.6)' }}>
              Indian Gaming Law Compliant | Public Gambling Act, 1867
            </span>
          </div>
        </div>

        {/* 6 Legal Points */}
        <div className="px-3 py-3 space-y-2">
          {LEGAL_POINTS.map((point, i) => {
            const Icon = point.icon;
            return (
              <div key={i} data-testid={`legal-point-${i}`}
                className="flex gap-3 p-3 rounded-xl transition-all"
                style={{
                  background: `${point.color}06`,
                  border: `1px solid ${point.color}12`,
                }}>
                <div className="shrink-0 w-8 h-8 rounded-lg flex items-center justify-center mt-0.5" style={{
                  background: `${point.color}15`,
                  border: `1px solid ${point.color}20`,
                }}>
                  <Icon size={16} color={point.color} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5">
                    <span className="text-[10px] font-black uppercase" style={{ color: 'rgba(255,255,255,0.4)' }}>#{i + 1}</span>
                  </div>
                  <div className="text-xs font-black text-white mt-0.5">{point.title}</div>
                  <div className="text-[10px] font-bold mb-1" style={{ color: `${point.color}aa` }}>{point.titleHi}</div>
                  <div className="text-[10px] leading-relaxed" style={{ color: 'rgba(255,255,255,0.55)' }}>{point.desc}</div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Bottom disclaimer */}
        <div className="px-4 py-3" style={{ borderTop: '1px solid rgba(74,222,128,0.08)', background: 'rgba(74,222,128,0.02)' }}>
          <p className="text-[9px] text-center leading-relaxed" style={{ color: 'rgba(255,255,255,0.3)' }}>
            Bharat 11 is a free-to-play social prediction platform. No real money is involved.
            Virtual coins are for entertainment only and hold no monetary value.
            This platform complies with applicable Indian laws including the Public Gambling Act, 1867
            and Information Technology Act, 2000.
          </p>
        </div>
      </div>
    </div>
  );
}
