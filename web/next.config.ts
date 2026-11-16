import type { NextConfig } from "next";

const isDev = process.env.NODE_ENV !== "production";

// The browser talks to the API directly, so its origin has to be allowed in
// connect-src. Fall back to the same default lib/api.ts uses.
const apiOrigin = (() => {
  try {
    return new URL(process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").origin;
  } catch {
    return "http://localhost:8000";
  }
})();

const gaEnabled = Boolean(process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID);

/**
 * Content-Security-Policy.
 *
 * script-src keeps 'unsafe-inline' because two inline scripts are deliberate:
 * the pre-paint theme script in app/layout.tsx (moving it to a file would
 * reintroduce the flash it exists to prevent) and the gtag bootstrap. Tightening
 * this to nonces means a middleware that generates one per request, which opts
 * every page out of static rendering - a real cost for a site that is otherwise
 * fully static. The headers below are the part that carries weight today; the
 * nonce upgrade is worth doing if inline scripts ever take untrusted input.
 *
 * Dev adds 'unsafe-eval' and websocket connections, which HMR needs.
 */
const csp = [
  `default-src 'self'`,
  `script-src 'self' 'unsafe-inline'${isDev ? " 'unsafe-eval'" : ""}${
    gaEnabled ? " https://www.googletagmanager.com" : ""
  }`,
  `style-src 'self' 'unsafe-inline'`, // Tailwind + framer-motion write style attributes
  `img-src 'self' data: blob:${gaEnabled ? " https://www.google-analytics.com" : ""}`,
  `font-src 'self' data:`, // next/font self-hosts at build time
  `connect-src 'self' ${apiOrigin}${isDev ? " ws: wss:" : ""}${
    gaEnabled ? " https://www.google-analytics.com https://www.googletagmanager.com" : ""
  }`,
  `frame-ancestors 'none'`,
  `base-uri 'self'`,
  `form-action 'self'`,
  `object-src 'none'`,
].join("; ");

const nextConfig: NextConfig = {
  // Required by the Docker runner stage: emits a minimal self-contained server.
  output: "standalone",
  turbopack: {},
  poweredByHeader: false,
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "Content-Security-Policy", value: csp },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=(), interest-cohort=()",
          },
        ],
      },
    ];
  },
};

export default nextConfig;
