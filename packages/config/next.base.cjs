// Shared Next.js config base. Apps extend this with their own asset prefixes,
// rewrites, and per-app tweaks.

/** @type {import('next').NextConfig} */
const baseConfig = {
  reactStrictMode: true,
  experimental: {
    // Keep this list intentionally small — opt in per-app where needed.
  },
  transpilePackages: [
    "@offside/ui",
    "@offside/ai",
    "@offside/auth-utils",
    "@offside/workflows-sdk",
    "@offside/api-client",
  ],
  poweredByHeader: false,
};

module.exports = baseConfig;
