/**
 * CrickPredict Design Constants
 * Single source of truth for all design tokens
 */

export const COLORS = {
  // Primary palette
  primary: {
    main: '#FF3B3B',
    light: '#FF6B6B',
    dark: '#CC2F2F',
    gradient: 'linear-gradient(135deg, #FF3B3B 0%, #FF6B6B 100%)',
  },
  
  // Background colors
  background: {
    primary: '#0D0D0D',
    secondary: '#1A1A1A',
    tertiary: '#252525',
    card: '#1E1E1E',
    elevated: '#2A2A2A',
  },
  
  // Text colors
  text: {
    primary: '#FFFFFF',
    secondary: '#B0B0B0',
    tertiary: '#707070',
    disabled: '#505050',
  },
  
  // Status colors
  success: {
    main: '#00C853',
    light: '#69F0AE',
    dark: '#00A043',
    bg: 'rgba(0, 200, 83, 0.15)',
  },
  
  error: {
    main: '#FF3B3B',
    light: '#FF6B6B',
    dark: '#CC2F2F',
    bg: 'rgba(255, 59, 59, 0.15)',
  },
  
  warning: {
    main: '#FFB300',
    light: '#FFCA28',
    dark: '#FF8F00',
    bg: 'rgba(255, 179, 0, 0.15)',
  },
  
  info: {
    main: '#2196F3',
    light: '#64B5F6',
    dark: '#1976D2',
    bg: 'rgba(33, 150, 243, 0.15)',
  },
  
  // Accent colors
  accent: {
    gold: '#FFD700',
    silver: '#C0C0C0',
    bronze: '#CD7F32',
    purple: '#9C27B0',
    blue: '#2196F3',
    cyan: '#00BCD4',
  },
  
  // Team gradients (custom, no official logos)
  teams: {
    red: 'linear-gradient(135deg, #FF3B3B 0%, #FF6B6B 100%)',
    blue: 'linear-gradient(135deg, #1E88E5 0%, #42A5F5 100%)',
    purple: 'linear-gradient(135deg, #7B1FA2 0%, #AB47BC 100%)',
    orange: 'linear-gradient(135deg, #FF6F00 0%, #FFA726 100%)',
    yellow: 'linear-gradient(135deg, #FDD835 0%, #FFEE58 100%)',
    green: 'linear-gradient(135deg, #43A047 0%, #66BB6A 100%)',
    pink: 'linear-gradient(135deg, #E91E63 0%, #F48FB1 100%)',
    teal: 'linear-gradient(135deg, #00897B 0%, #26A69A 100%)',
  },
  
  // Borders
  border: {
    light: 'rgba(255, 255, 255, 0.1)',
    medium: 'rgba(255, 255, 255, 0.2)',
    focus: '#FF3B3B',
  },
};

export const FONTS = {
  primary: "'Poppins', -apple-system, BlinkMacSystemFont, sans-serif",
  display: "'Orbitron', 'Poppins', sans-serif",
  numbers: "'Rajdhani', 'Poppins', sans-serif",
  hindi: "'Noto Sans Devanagari', 'Poppins', sans-serif",
};

export const FONT_SIZES = {
  xs: '0.75rem',    // 12px
  sm: '0.875rem',   // 14px
  base: '1rem',     // 16px
  lg: '1.125rem',   // 18px
  xl: '1.25rem',    // 20px
  '2xl': '1.5rem',  // 24px
  '3xl': '1.875rem', // 30px
  '4xl': '2.25rem', // 36px
};

export const SPACING = {
  xs: '0.25rem',   // 4px
  sm: '0.5rem',    // 8px
  md: '1rem',      // 16px
  lg: '1.5rem',    // 24px
  xl: '2rem',      // 32px
  '2xl': '3rem',   // 48px
  '3xl': '4rem',   // 64px
};

export const BORDER_RADIUS = {
  sm: '0.375rem',  // 6px
  md: '0.5rem',    // 8px
  lg: '0.75rem',   // 12px
  xl: '1rem',      // 16px
  '2xl': '1.5rem', // 24px
  full: '9999px',
};

export const SHADOWS = {
  sm: '0 1px 2px rgba(0, 0, 0, 0.3)',
  md: '0 4px 6px rgba(0, 0, 0, 0.4)',
  lg: '0 10px 15px rgba(0, 0, 0, 0.5)',
  xl: '0 20px 25px rgba(0, 0, 0, 0.6)',
  glow: {
    red: '0 0 20px rgba(255, 59, 59, 0.5)',
    green: '0 0 20px rgba(0, 200, 83, 0.5)',
    gold: '0 0 20px rgba(255, 215, 0, 0.5)',
  },
};

export const ANIMATIONS = {
  fast: '150ms',
  normal: '300ms',
  slow: '500ms',
  easeOut: 'cubic-bezier(0.16, 1, 0.3, 1)',
  easeIn: 'cubic-bezier(0.7, 0, 0.84, 0)',
  bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
};

export const Z_INDEX = {
  base: 0,
  dropdown: 10,
  sticky: 20,
  fixed: 30,
  modalBackdrop: 40,
  modal: 50,
  toast: 60,
  tooltip: 70,
};

// Rank configuration
export const RANKS = {
  ROOKIE: { name: 'Rookie', minPoints: 0, color: '#B0B0B0' },
  PRO: { name: 'Pro', minPoints: 1000, color: '#2196F3' },
  EXPERT: { name: 'Expert', minPoints: 5000, color: '#9C27B0' },
  LEGEND: { name: 'Legend', minPoints: 15000, color: '#FF6F00' },
  GOAT: { name: 'GOAT', minPoints: 50000, color: '#FFD700' },
};

// Default avatars
export const AVATARS = [
  '/avatars/avatar-1.png',
  '/avatars/avatar-2.png',
  '/avatars/avatar-3.png',
  '/avatars/avatar-4.png',
  '/avatars/avatar-5.png',
  '/avatars/avatar-6.png',
];
