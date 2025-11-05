/** @type {import('next').NextConfig} */
const nextConfig = {
  // Disable React Strict Mode (causes WebSocket double mount in dev)
  reactStrictMode: false,

  // Enable standalone build for Docker
  output: 'standalone',

  // Optimize images
  images: {
    domains: [],
    formats: ['image/webp', 'image/avif'],
  },

  // Bundle analyzer configuration
  ...(process.env.ANALYZE === 'true' && {
    webpack: (config, { isServer }) => {
      if (!isServer) {
        const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
        config.plugins.push(
          new BundleAnalyzerPlugin({
            analyzerMode: 'static',
            openAnalyzer: false,
          })
        );
      }
      return config;
    },
  }),

  // Environment variables validation
  // NOTE: NEXT_PUBLIC_* variables are automatically exposed to the browser
  // Empty string is allowed for NEXT_PUBLIC_API_URL (uses Next.js rewrites proxy)
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL !== undefined
      ? process.env.NEXT_PUBLIC_API_URL
      : 'http://localhost:8000',
    NEXT_PUBLIC_APP_ENV: process.env.NEXT_PUBLIC_APP_ENV || 'development',
  },

  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block'
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin'
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()'
          }
        ]
      }
    ];
  },

  // API route rewrites
  async rewrites() {
    // API_BACKEND_URL: 서버 사이드 전용 (Docker: backend:8000, 로컬: localhost:8000)
    // NEXT_PUBLIC_API_URL: 클라이언트 사이드 (빈 문자열이면 rewrites 사용)
    const apiBackendUrl = process.env.API_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    return [
      {
        source: '/api/:path*',
        destination: `${apiBackendUrl}/api/:path*`,
      },
      {
        source: '/health',
        destination: '/api/health',
      }
    ];
  },

  // Redirect configuration
  async redirects() {
    return [];
  },
};

module.exports = nextConfig;