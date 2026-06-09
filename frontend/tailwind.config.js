/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  '#fff0f9',
          100: '#ffe3f5',
          200: '#ffc6ec',
          300: '#ff96dc',
          400: '#ff55c4',
          500: '#ff2aac',
          600: '#f0068c',
          700: '#d10072',
          800: '#ac005d',
          900: '#8e004e',
        },
      },
      animation: {
        'pulse-fast': 'pulse 0.8s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 3s linear infinite',
      },
    },
  },
  plugins: [],
};
