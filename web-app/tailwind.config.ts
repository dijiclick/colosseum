import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        background: "#050816",
        surface: "#0f172a",
        accent: "#22c55e"
      }
    }
  },
  plugins: []
};

export default config;


