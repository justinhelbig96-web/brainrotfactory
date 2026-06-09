/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  eslint: { ignoreDuringBuilds: true },
  typescript: { ignoreBuildErrors: true },
  async rewrites() {
    // Local: http://localhost:8000
    // Production (Vercel): set BACKEND_URL env var to your Railway URL
    let backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    if (backendUrl && !backendUrl.startsWith('http')) {
      backendUrl = 'https://' + backendUrl;
    }
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
