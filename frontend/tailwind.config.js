/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        clinical: {
          bg: '#F7F9FC',
          panel: '#FFFFFF',
          border: '#E5E7EB',
          text: '#111827',
          muted: '#6B7280',
          primary: '#0F766E',
          danger: '#B91C1C',
          warning: '#B45309',
          success: '#047857',
        },
      },
    },
  },
  plugins: [],
}

