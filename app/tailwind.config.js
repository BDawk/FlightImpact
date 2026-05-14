/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Surface ramp — deep blue-black, three elevations
        bg: {
          DEFAULT: "#070b11",       // page
          elev:    "#0f141d",       // panel
          panel:   "#161e2a",       // raised panel
          input:   "#0a1019",       // form fields, inset
        },
        // Hairlines — used for everything that's not a fill
        line: {
          DEFAULT: "#1f2a38",       // primary hairline
          soft:    "#161e2a",       // very subtle divider
          strong:  "#2c3a4d",       // hover/focus accent
        },
        // Text
        ink: {
          DEFAULT: "#e8eef5",
          muted:   "#8a96a3",
          dim:     "#5d6a78",
          faint:   "#3e4a58",
        },
        // Brand mint — matches the screen mockups + logo's green stops
        brand: {
          DEFAULT: "#34d399",
          glow:    "#6ee7b7",
          deep:    "#0f7a59",
          ink:     "#0a3d2c",       // text on brand fill
        },
        // Logo accent colors (for occasional highlights)
        logo: {
          blue:    "#1d8dbc",
          green:   "#34a853",
          yellow:  "#fcb83a",
        },
        // Semantic signal colors (matching the device screen mockups)
        signal: {
          ok:   "#34d399",
          warn: "#fbbf24",
          bad:  "#f87171",
          info: "#60a5fa",
        },
      },
      fontFamily: {
        sans: ['"Inter Variable"', "Inter", "system-ui", "-apple-system", "sans-serif"],
        display: ['"Space Grotesk Variable"', '"Space Grotesk"', "Inter", "sans-serif"],
        mono: ['"JetBrains Mono Variable"', '"JetBrains Mono"', "ui-monospace", "Menlo", "monospace"],
      },
      fontSize: {
        // Tighter type scale — instrument-panel feel
        "2xs": ["10px", { lineHeight: "14px", letterSpacing: "0.08em" }],
        xs:    ["11px", { lineHeight: "16px" }],
        sm:    ["13px", { lineHeight: "18px" }],
        base:  ["14px", { lineHeight: "20px" }],
        lg:    ["16px", { lineHeight: "22px" }],
        xl:    ["20px", { lineHeight: "26px", letterSpacing: "-0.01em" }],
        "2xl": ["28px", { lineHeight: "32px", letterSpacing: "-0.02em" }],
        "3xl": ["40px", { lineHeight: "44px", letterSpacing: "-0.025em" }],
        "4xl": ["56px", { lineHeight: "56px", letterSpacing: "-0.03em" }],
      },
      borderRadius: {
        none: "0",
        sm:   "4px",
        DEFAULT: "6px",
        md:   "8px",
        lg:   "10px",
        xl:   "14px",
      },
      boxShadow: {
        // Panel inner highlight — subtle "etched" look
        panel: "inset 0 1px 0 0 rgba(255,255,255,0.03)",
        glow:  "0 0 0 1px rgba(52, 211, 153, 0.4), 0 0 12px -2px rgba(52, 211, 153, 0.3)",
      },
      letterSpacing: {
        cap: "0.12em",
      },
    },
  },
  plugins: [],
};
