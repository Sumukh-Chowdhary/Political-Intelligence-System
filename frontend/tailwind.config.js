/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],

  theme: {
    extend: {
      colors: {
        background: "#07111f",
        card: "#0f172a",
        accent: "#60a5fa",
      },
    },
  },

  plugins: [],
}