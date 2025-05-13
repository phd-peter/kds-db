import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:5001/:path*',  // Python 서버 포트를 5000으로 설정
      },
    ];
  },
};

export default nextConfig;
