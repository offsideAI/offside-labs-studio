import type { Metadata } from "next";
import { Roboto, JetBrains_Mono, Newsreader } from "next/font/google";

import { Providers } from "./providers";
import "./globals.css";

const roboto = Roboto({
  subsets: ["latin"],
  weight: ["300", "400", "500", "700"],
  variable: "--font-roboto",
  display: "swap",
});

const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
  display: "swap",
});

// Resend-inspired editorial serif. Variable font — we pull the full weight
// axis so hero headlines can use 300/400/500/600 without separate requests.
const newsreader = Newsreader({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600"],
  style: ["normal", "italic"],
  variable: "--font-newsreader",
  display: "swap",
});

// Inline script that runs *before* React hydrates. Reads the persisted
// theme from localStorage (or falls back to prefers-color-scheme) and
// sets `data-theme` on <html> synchronously. Without this, the page
// would flash light-then-dark on every cold load.
const THEME_BOOTSTRAP = `
  (function() {
    try {
      var stored = localStorage.getItem('offside-theme');
      var theme = stored || 'dark';
      document.documentElement.setAttribute('data-theme', theme);
    } catch (e) {
      document.documentElement.setAttribute('data-theme', 'dark');
    }
  })();
`;

export const metadata: Metadata = {
  title: "OffsideStudio — Agent Marketplace",
  description:
    "OffsideStudio — Agent Marketplace. Install pre-built agents that automate your full ecommerce funnel — marketing campaigns, AEO, ads, landing pages, email, cart recovery, payments — against your CRM. Product 01 in the Offside Studio Suite.",
  icons: {
    icon: "/favicon.svg",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      // The bootstrap script overwrites this synchronously before paint.
      // We default to dark here so SSR markup matches what the bootstrap
      // emits for first-time visitors with no system preference.
      data-theme="dark"
      className={`${roboto.variable} ${jetbrains.variable} ${newsreader.variable} bg-render-dark`}
      suppressHydrationWarning
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_BOOTSTRAP }} />
      </head>
      <body>
        <a className="skip-link" href="#main">
          Skip to content
        </a>
        <Providers>
          <main id="main">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
