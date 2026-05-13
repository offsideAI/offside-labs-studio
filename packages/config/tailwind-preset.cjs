// Offside Studio Tailwind preset.
// Token contract lives in packages/ui/src/styles/tokens.css — those CSS variables
// are referenced here as `var(--brand-*)`. Numeric scale values are static fallbacks
// for cases where CSS-variable interpolation is awkward (e.g., gradient stops).

/** @type {import('tailwindcss').Config} */
module.exports = {
  // Dark mode toggles via the `[data-theme="dark"]` attribute on <html>.
  // Most components don't need explicit `dark:` variants because the
  // semantic CSS vars (--brand-bone, --brand-ink, --brand-rule, etc.)
  // are redefined inside the [data-theme="dark"] block in tokens.css —
  // so `bg-bone`, `text-ink`, `hairline` auto-invert. Use `dark:` only
  // when you need a *different* token in dark (e.g. a glow effect that
  // doesn't apply in light).
  darkMode: ["selector", '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        tan: {
          DEFAULT: "var(--brand-tan)",
          text: "var(--brand-tan-text)",
          50: "#FAF1EA",
          100: "#F0DFD0",
          200: "#E5CCB6",
          300: "#D9B89B",
          400: "#CDA482",
          500: "#C9A389",
          600: "#B8916F",
          700: "#9C7853",
          800: "#7A5F44",
          900: "#5A4630",
        },
        ink: {
          DEFAULT: "var(--brand-ink)",
          50: "#F4F4F4",
          100: "#E0E0E0",
          200: "#BDBDBD",
          300: "#9E9E9E",
          400: "#757575",
          500: "#616161",
          600: "#424242",
          700: "#303030",
          800: "#212121",
          900: "#1E1E1E",
        },
        bone: {
          DEFAULT: "var(--brand-bone)",
        },
        rule: "var(--brand-rule)",
        "fg-muted": "var(--brand-muted)",
        render: {
          purple: "#9b51e0",
          purpleLight: "#b870f4",
          purpleGradient: "linear-gradient(135deg, #9b51e0, #b870f4)",
          green: "#45E67A",
          greenHover: "#5cff8f",
          dark: "#0A0A0A",
          gray: "#1E1E1E",
        },
      },
      fontFamily: {
        styrene: ['"Styrene A"', '"Söhne"', '"Inter"', "ui-sans-serif", "system-ui", "sans-serif"],
        // Editorial serif for hero headlines — Resend-inspired. Newsreader is
        // a Google Fonts variable serif with sharp brackets + tight tracking.
        // Wired via next/font/google in app/layout.tsx → exposes --font-newsreader.
        serif: ['var(--font-newsreader)', '"Newsreader"', "Georgia", "ui-serif", "serif"],
        sans: ['"Roboto"', "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ['"JetBrains Mono"', "ui-monospace", "monospace"],
      },
      borderRadius: {
        none: "0",
        xs: "2px",
        sm: "4px",
        md: "8px",
        lg: "12px",
        xl: "16px",
        "2xl": "20px",
        full: "9999px",
      },
      boxShadow: {
        "soft-1": "0 1px 2px rgba(30, 30, 30, 0.04)",
        "soft-2": "0 4px 12px rgba(30, 30, 30, 0.06)",
        "soft-3": "0 8px 24px rgba(30, 30, 30, 0.08)",
        "soft-4": "0 16px 48px rgba(30, 30, 30, 0.10)",
      },
      letterSpacing: {
        eyebrow: "0.18em",
      },
      transitionTimingFunction: {
        "out-quint": "cubic-bezier(0.16, 1, 0.3, 1)",
      },
      maxWidth: {
        editorial: "1280px",
      },
      spacing: {
        gutter: "1.5rem",
        "gutter-lg": "5.5rem",
      },
      backgroundImage: {
        'render-glow': 'radial-gradient(circle at top right, rgba(155, 81, 224, 0.15), transparent 50%)',
      },
      keyframes: {
        "fade-in-up": {
          "0%": { opacity: "0", transform: "translateY(20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "pulse-glow": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.6" },
        },
        "float": {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-10px)" },
        },
        "marquee": {
          from: { transform: "translateX(0)" },
          to: { transform: "translateX(calc(-100% - 2rem))" },
        }
      },
      animation: {
        "fade-in-up": "fade-in-up 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards",
        "pulse-glow": "pulse-glow 3s infinite ease-in-out",
        "float": "float 6s infinite ease-in-out",
        "marquee": "marquee 40s linear infinite",
      },
    },
  },
  plugins: [],
};
