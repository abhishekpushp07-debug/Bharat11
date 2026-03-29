/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        // CrickPredict Primary Colors
        primary: {
          DEFAULT: '#FF3B3B',
          light: '#FF6B6B',
          dark: '#CC2F2F',
        },
        // Background Colors
        bg: {
          primary: '#0D0D0D',
          secondary: '#1A1A1A',
          tertiary: '#252525',
          card: '#1E1E1E',
          elevated: '#2A2A2A',
        },
        // Text Colors
        text: {
          primary: '#FFFFFF',
          secondary: '#B0B0B0',
          tertiary: '#707070',
        },
        // Status Colors
        success: '#00C853',
        warning: '#FFB300',
        info: '#2196F3',
        // Accent
        gold: '#FFD700',
        silver: '#C0C0C0',
        bronze: '#CD7F32',
        // ShadCN compatibility
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))'
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))'
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))'
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))'
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))'
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))'
        },
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
      },
      fontFamily: {
        sans: ['Poppins', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        display: ['Orbitron', 'Poppins', 'sans-serif'],
        numbers: ['Rajdhani', 'Poppins', 'sans-serif'],
        hindi: ['Noto Sans Devanagari', 'Poppins', 'sans-serif'],
      },
      fontSize: {
        'xxs': '0.625rem', // 10px
      },
      spacing: {
        'safe-top': 'env(safe-area-inset-top, 0px)',
        'safe-bottom': 'env(safe-area-inset-bottom, 0px)',
        'nav': '64px',
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)'
      },
      boxShadow: {
        'glow-red': '0 0 20px rgba(255, 59, 59, 0.5)',
        'glow-green': '0 0 20px rgba(0, 200, 83, 0.5)',
        'glow-gold': '0 0 20px rgba(255, 215, 0, 0.5)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease',
        'fade-in-up': 'fadeInUp 0.4s ease',
        'slide-up': 'slideUp 0.3s ease',
        'glow': 'glow 2s ease-in-out infinite',
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out'
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(100%)' },
          '100%': { transform: 'translateY(0)' },
        },
        glow: {
          '0%, 100%': { boxShadow: '0 0 5px var(--color-primary)' },
          '50%': { boxShadow: '0 0 20px var(--color-primary), 0 0 30px var(--color-primary)' },
        },
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' }
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' }
        }
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #FF3B3B 0%, #FF6B6B 100%)',
        'gradient-card': 'linear-gradient(180deg, #1E1E1E 0%, #1A1A1A 100%)',
        'team-red': 'linear-gradient(135deg, #FF3B3B 0%, #FF6B6B 100%)',
        'team-blue': 'linear-gradient(135deg, #1E88E5 0%, #42A5F5 100%)',
        'team-purple': 'linear-gradient(135deg, #7B1FA2 0%, #AB47BC 100%)',
        'team-orange': 'linear-gradient(135deg, #FF6F00 0%, #FFA726 100%)',
        'team-yellow': 'linear-gradient(135deg, #FDD835 0%, #FFEE58 100%)',
        'team-green': 'linear-gradient(135deg, #43A047 0%, #66BB6A 100%)',
        'team-pink': 'linear-gradient(135deg, #E91E63 0%, #F48FB1 100%)',
        'team-teal': 'linear-gradient(135deg, #00897B 0%, #26A69A 100%)',
      },
    }
  },
  plugins: [require("tailwindcss-animate")],
};
