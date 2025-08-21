import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  eslint: {
    // Only run ESLint on these directories during production builds
    dirs: ['pages', 'utils', 'lib', 'components'],
    // Ignore ESLint errors during production builds
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Also ignore TypeScript errors during builds for now
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
