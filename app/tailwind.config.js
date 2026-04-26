/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        bg: { DEFAULT: "#0a0e14", elev: "#111722", panel: "#161e2c" },
        ink: { DEFAULT: "#e6edf3", muted: "#94a3b8", dim: "#64748b" },
        line: "#1e293b",
        brand: { DEFAULT: "#0e7c5a", glow: "#1ec98c" },
        signal: { ok: "#22c55e", warn: "#f59e0b", bad: "#ef4444" },
      },
      fontFamily: {
        sans: ["system-ui", "-apple-system", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
    },
  },
  plugins: [],
};
