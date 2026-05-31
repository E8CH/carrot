import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'rfsczzcuennvkewtdnba.supabase.co',
      },
    ],
  },
};

export default nextConfig;
