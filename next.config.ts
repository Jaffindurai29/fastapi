import { createMDX } from "fumadocs-mdx/next";
import type { NextConfig } from "next";

// GitHub Pages serves this project at /fastapi/ (repo name), so the
// production build needs that prefix. Local dev/build stays unprefixed.
const basePath = process.env.GITHUB_ACTIONS ? "/fastapi" : "";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
  basePath,
  assetPrefix: basePath ? `${basePath}/` : undefined,
  env: {
    NEXT_PUBLIC_BASE_PATH: basePath,
  },
};

const withMDX = createMDX();

export default withMDX(nextConfig);
