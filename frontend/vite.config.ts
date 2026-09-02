/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath, URL } from "node:url";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) },
  },
  server: {
    port: 5173,
    // Local dev talks to the backend through this proxy, so no CORS setup.
    proxy: { "/api": { target: "http://localhost:8000", rewrite: (p) => p.replace(/^\/api/, "") } },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["src/test/setup.ts"],
    env: {
      VITE_AUTH0_DOMAIN: "test.auth0.local",
      VITE_AUTH0_CLIENT_ID: "test-client",
      VITE_AUTH0_AUDIENCE: "https://api.test",
      VITE_API_URL: "http://api.test",
    },
    css: false,
    coverage: {
      provider: "v8",
      include: ["src/**/*.{ts,tsx}"],
      exclude: ["src/main.tsx", "src/api/schema.d.ts", "src/test/**", "src/**/*.test.{ts,tsx}"],
      thresholds: { lines: 80, functions: 80, branches: 70, statements: 80 },
    },
  },
});
