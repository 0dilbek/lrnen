/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        surface: {
          DEFAULT: '#0c1222',
          50: '#111827',
          100: '#151d2e',
          200: '#1a2332',
          300: '#243044',
          400: '#2d3a50',
        },
        accent: {
          DEFAULT: '#6366f1',
          hover: '#4f46e5',
          muted: '#312e81',
        },
        border: {
          DEFAULT: '#2a3548',
          light: '#1e293b',
        },
      },
      fontFamily: {
        sans: ['"DM Sans"', 'Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 1px 3px rgba(0,0,0,0.4), 0 4px 12px rgba(0,0,0,0.25)',
        'card-hover': '0 4px 20px rgba(0,0,0,0.45), 0 0 0 1px rgba(99,102,241,0.15)',
      },
    },
  },
  plugins: [],
}