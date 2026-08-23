import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        primary: {
          50: "#eef7ff",
          100: "#d9ecff",
          200: "#bcddff",
          300: "#8ec8ff",
          400: "#59a8ff",
          500: "#3285ff",
          600: "#1a65f5",
          700: "#124ee1",
          800: "#153fb5",
          900: "#17398e",
        },
        navy: {
          800: "#0f172a",
          900: "#0a0f1d",
          950: "#060913",
        },
      },
    },
  },
  plugins: [],
};

export default config;
