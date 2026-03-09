/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
  ],
  theme: {
    extend: {
      colors: {
        surm: {
          pink: "#F42B5F",
          pinkDark: "#D91F4F",
          navy: "#000069",
          bg: "#F8FAFC",
          card: "#FFFFFF",
          border: "#E5E7EB",
          muted: "#64748B",
        },
      },
      boxShadow: {
        card: "0 4px 16px rgba(15, 23, 42, 0.06)",
        cardHover: "0 10px 30px rgba(15, 23, 42, 0.10)",
      },
    },
  },
  plugins: [],
};
