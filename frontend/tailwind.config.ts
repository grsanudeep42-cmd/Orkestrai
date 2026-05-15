import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Border color
        border: "#3e4850",
        // Design system colors from assets/DESIGN.md
        "tertiary-fixed-dim": "#4edea3",
        "surface-container-highest": "#35343a",
        "on-secondary-container": "#c4abff",
        "primary": "#89ceff",
        "on-surface": "#e4e1e9",
        "error-container": "#93000a",
        "outline-variant": "#3e4850",
        "error": "#ffb4ab",
        "on-tertiary-fixed-variant": "#005236",
        "surface-dim": "#131318",
        "on-primary-fixed": "#001e2f",
        "tertiary-fixed": "#6ffbbe",
        "secondary-fixed": "#e9ddff",
        "on-error-container": "#ffdad6",
        "surface-variant": "#35343a",
        "on-secondary-fixed": "#23005c",
        "on-tertiary-container": "#003b26",
        "primary-fixed": "#c9e6ff",
        "surface": "#131318",
        "outline": "#88929b",
        "tertiary-container": "#00b17b",
        "on-primary-fixed-variant": "#004c6e",
        "background": "#0a0a0f",
        "on-error": "#690005",
        "secondary-container": "#571bc1",
        "on-secondary-fixed-variant": "#5516be",
        "surface-container-low": "#1b1b20",
        "primary-fixed-dim": "#89ceff",
        "on-surface-variant": "#bec8d2",
        "on-primary": "#00344d",
        "secondary-fixed-dim": "#d0bcff",
        "inverse-on-surface": "#303036",
        "surface-container-high": "#2a292f",
        "on-secondary": "#3c0091",
        "inverse-primary": "#006591",
        "primary-container": "#0ea5e9",
        "secondary": "#d0bcff",
        "surface-container": "#1f1f25",
        "tertiary": "#4edea3",
        "inverse-surface": "#e4e1e9",
        "on-background": "#e4e1e9",
        "on-primary-container": "#003751",
        "surface-tint": "#89ceff",
        "surface-bright": "#39383e",
        "surface-container-lowest": "#0e0e13",
        "on-tertiary": "#003824",
        "on-tertiary-fixed": "#002113"
      },
      borderRadius: {
        DEFAULT: "0.125rem",
        lg: "0.25rem",
        xl: "0.5rem",
        full: "0.75rem"
      },
      spacing: {
        "margin": "24px",
        "inspector-width": "320px",
        "unit": "4px",
        "sidebar-width": "260px",
        "gutter": "16px"
      },
      fontFamily: {
        "code-sm": ["JetBrains Mono", "monospace"],
        "label-caps": ["JetBrains Mono", "monospace"],
        "headline-md": ["Inter", "sans-serif"],
        "body-base": ["Inter", "sans-serif"],
        "display-lg": ["Inter", "sans-serif"]
      },
      fontSize: {
        "code-sm": ["13px", { lineHeight: "18px", fontWeight: "400" }],
        "label-caps": ["11px", { lineHeight: "16px", letterSpacing: "0.05em", fontWeight: "600" }],
        "headline-md": ["24px", { lineHeight: "32px", letterSpacing: "-0.01em", fontWeight: "600" }],
        "body-base": ["14px", { lineHeight: "20px", fontWeight: "400" }],
        "display-lg": ["48px", { lineHeight: "56px", letterSpacing: "-0.02em", fontWeight: "700" }]
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'slide-in': 'slideIn 0.3s ease-out',
        'fade-in': 'fadeIn 0.5s ease-out',
      },
      keyframes: {
        slideIn: {
          '0%': { transform: 'translateX(-100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};

export default config;

// Made with Bob
