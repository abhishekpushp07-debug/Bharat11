/**
 * Admin Match Page - Matches + Contests management
 * Sub-tabs for Match Control Center and Contest Manager
 */
import { useState } from 'react';
import { COLORS } from '../../constants/design';
import { Calendar, Trophy } from 'lucide-react';
import AdminMatchesTab from './AdminMatchesTab';
import AdminContestsTab from './AdminContestsTab';

const SUB_TABS = [
  { id: 'matches', label: 'Matches', Icon: Calendar },
  { id: 'contests', label: 'Contests', Icon: Trophy },
];

export default function AdminMatchPage() {
  const [subTab, setSubTab] = useState('matches');

  return (
    <div data-testid="admin-match-page" className="space-y-3">
      {/* Sub-tab selector */}
      <div className="flex gap-2">
        {SUB_TABS.map(({ id, label, Icon }) => (
          <button key={id} data-testid={`match-tab-${id}`}
            onClick={() => setSubTab(id)}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold transition-all flex-1 justify-center"
            style={{
              background: subTab === id ? COLORS.accent.gold + '18' : COLORS.background.card,
              color: subTab === id ? COLORS.accent.gold : COLORS.text.tertiary,
              border: `1px solid ${subTab === id ? COLORS.accent.gold + '44' : COLORS.border.light}`
            }}>
            <Icon size={14} />
            {label}
          </button>
        ))}
      </div>

      {/* Content */}
      {subTab === 'matches' && <AdminMatchesTab />}
      {subTab === 'contests' && <AdminContestsTab />}
    </div>
  );
}
