import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Required by the Docker runner stage: emits a minimal self-contained server.
  output: "standalone",
  turbopack: {},
};

export default nextConfig;
