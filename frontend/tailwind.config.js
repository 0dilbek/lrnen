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
          DEFAULT: 'rgb(var(--surface-rgb) / <alpha-value>)',
          50: 'rgb(var(--surface-50-rgb) / <alpha-value>)',
          100: 'rgb(var(--surface-100-rgb) / <alpha-value>)',
          200: 'rgb(var(--surface-200-rgb) / <alpha-value>)',
          300: 'rgb(var(--surface-300-rgb) / <alpha-value>)',
          400: 'rgb(var(--surface-400-rgb) / <alpha-value>)',
        },
        accent: {
          DEFAULT: '#6366f1',
          hover: '#4f46e5',
          muted: '#312e81',
        },
        border: {
          DEFAULT: 'rgb(var(--border-rgb) / <alpha-value>)',
          light: 'rgb(var(--border-light-rgb) / <alpha-value>)',
        },
      },
      fontFamily: {
        sans: ['"DM Sans"', 'Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'card': 'var(--shadow-card)',
        'card-hover': 'var(--shadow-card-hover)',
      },
    },
  },
  plugins: [],
}