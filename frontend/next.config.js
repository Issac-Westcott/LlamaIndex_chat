/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  async rewrites() {
    // 运行时从环境变量读取后端地址
    // Docker 环境使用服务名 backend:8000
    // 开发环境使用 localhost:8000
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    console.log('Backend URL:', backendUrl);
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
  // 确保输出为 standalone 模式以便在 Docker 中运行
  output: 'standalone',
};

module.exports = nextConfig;
