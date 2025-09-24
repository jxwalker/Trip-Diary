/** @type {import('next').NextConfig} */
const nextConfig = {
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
  async rewrites() {
    return [
      {
        source: '/api/proxy/:path*',
        destination: 'http://localhost:8000/api/proxy/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
