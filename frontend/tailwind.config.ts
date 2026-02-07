import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      colors: {
        meridian: {
          // Deep navy backgrounds (sidebar, headers)
          navy: {
            DEFAULT: '#1B2A4A',
            50: '#2A3F6B',
            100: '#253861',
            200: '#223354',
            300: '#1F2E4E',
            400: '#1B2A4A',
            500: '#172442',
            600: '#141F3A',
            700: '#111A32',
            800: '#0E152A',
            900: '#0B1022',
            950: '#080C1A',
          },
          // Light surface colors for main content
          surface: {
            DEFAULT: '#F8FAFC',
            50: '#FFFFFF',
            100: '#F8FAFC',
            200: '#F1F5F9',
            300: '#E2E8F0',
            400: '#CBD5E1',
          },
          // Text colors for light backgrounds
          text: {
            DEFAULT: '#1B2A4A',
            heading: '#0F172A',
            body: '#475569',
            muted: '#64748B',
            light: '#94A3B8',
          },
          // Slate/muted text tones (for dark backgrounds)
          slate: {
            DEFAULT: '#94A3B8',
            100: '#CBD5E1',
            200: '#B0BEC5',
            300: '#94A3B8',
            400: '#7B8FA3',
            500: '#64748B',
            600: '#526173',
            700: '#3F4E5C',
          },
          // Crimson accent / CTA
          crimson: {
            DEFAULT: '#DC2626',
            50: '#FEF2F2',
            100: '#FEE2E2',
            200: '#FECACA',
            300: '#F87171',
            400: '#EF4444',
            500: '#DC2626',
            600: '#B91C1C',
            700: '#991B1B',
          },
          // Steel blue secondary accent
          steel: {
            DEFAULT: '#3B82F6',
            50: '#EFF6FF',
            100: '#DBEAFE',
            200: '#BFDBFE',
            300: '#93C5FD',
            400: '#60A5FA',
            500: '#3B82F6',
            600: '#2563EB',
            700: '#1D4ED8',
          },
          // Light border color
          border: {
            DEFAULT: '#E2E8F0',
            light: '#F1F5F9',
            dark: '#CBD5E1',
          },
        },
      },
      backgroundImage: {
        'meridian-gradient': 'linear-gradient(135deg, #1B2A4A 0%, #0E152A 50%, #111A32 100%)',
        'meridian-radial': 'radial-gradient(ellipse at top, #223354 0%, #1B2A4A 50%, #0B1022 100%)',
        'meridian-hero': 'radial-gradient(ellipse at 30% 20%, rgba(59, 130, 246, 0.08) 0%, transparent 50%), radial-gradient(ellipse at 70% 80%, rgba(220, 38, 38, 0.05) 0%, transparent 50%)',
        'meridian-wave': 'linear-gradient(135deg, #1B2A4A 0%, #223354 100%)',
      },
      boxShadow: {
        'meridian': '0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.06)',
        'meridian-md': '0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -2px rgba(0, 0, 0, 0.05)',
        'meridian-lg': '0 10px 25px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.04)',
        'meridian-glow': '0 0 20px rgba(59, 130, 246, 0.15)',
        'meridian-crimson': '0 4px 14px rgba(220, 38, 38, 0.25)',
        'meridian-card': '0 1px 3px rgba(27, 42, 74, 0.06), 0 1px 2px rgba(27, 42, 74, 0.04)',
        'meridian-card-hover': '0 4px 12px rgba(27, 42, 74, 0.1), 0 2px 4px rgba(27, 42, 74, 0.06)',
      },
      borderColor: {
        'meridian-border': '#E2E8F0',
      },
      animation: {
        'wave-slow': 'wave 8s ease-in-out infinite',
        'wave-slower': 'wave 12s ease-in-out infinite reverse',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        wave: {
          '0%, 100%': { transform: 'translateX(0) translateY(0)' },
          '50%': { transform: 'translateX(-20px) translateY(10px)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
};

export default config;
