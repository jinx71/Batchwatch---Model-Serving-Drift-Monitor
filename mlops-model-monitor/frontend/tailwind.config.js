/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Deep-slate instrument console palette.
        base: '#0B1220',
        surface: '#111B2E',
        raised: '#16223A',
        line: '#1E2D49',
        ink: '#E6EDF5',
        muted: '#8A99B0',
        faint: '#5C6B85',
        // Signal + status.
        signal: '#34D6C3', // phosphor teal (primary trace)
        pass: '#46C28A',
        warn: '#E0A23C',
        fail: '#E5564E',
      },
      fontFamily: {
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace'],
        sans: ['"IBM Plex Sans"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        panel: '0 1px 0 0 rgba(255,255,255,0.03) inset, 0 8px 30px -12px rgba(0,0,0,0.6)',
      },
      keyframes: {
        lamp: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.35' },
        },
      },
      animation: {
        lamp: 'lamp 2s ease-in-out infinite',
      },
    },
  },
  plugins: [],
};
