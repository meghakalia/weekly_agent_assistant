/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  // Vercel-specific optimizations
  output: 'standalone',
  
  // API routes configuration
  async rewrites() {
    return [
      {
        source: '/api/process-inventory',
        destination: '/api/process_inventory',
      },
      {
        source: '/api/generate-shopping-list',
        destination: '/api/generate_shopping_list',
      },
    ]
  },
  
  // Environment variables available to the browser
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || '',
  },
}

export default nextConfig
