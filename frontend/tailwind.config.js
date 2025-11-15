/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        mastercard: {
          orange: '#FF5F00',
          red: '#EB001B',
          yellow: '#F79E1B',
        },
      },
    },
  },
  plugins: [],
}
