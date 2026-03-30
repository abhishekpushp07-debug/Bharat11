/**
 * Admin Content Page - Questions + Templates management
 * Sub-tabs for Questions and Templates
 */
import { useState } from 'react';
import { COLORS } from '../../constants/design';
import { HelpCircle, FileText } from 'lucide-react';
import AdminQuestionsTab from './AdminQuestionsTab';
import AdminTemplatesTab from './AdminTemplatesTab';

const SUB_TABS = [
  { id: 'questions', label: 'Questions', Icon: HelpCircle },
  { id: 'templates', label: 'Templates', Icon: FileText },
];

export default function AdminContentPage() {
  const [subTab, setSubTab] = useState('questions');

  return (
    <div data-testid="admin-content-page" className="space-y-3">
      {/* Sub-tab selector */}
      <div className="flex gap-2">
        {SUB_TABS.map(({ id, label, Icon }) => (
          <button key={id} data-testid={`content-tab-${id}`}
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
      {subTab === 'questions' && <AdminQuestionsTab />}
      {subTab === 'templates' && <AdminTemplatesTab />}
    </div>
  );
}
