import { defineConfig, devices } from "@playwright/test";

/**
 * End-to-end tests run the real backend (in-memory store, local signing
 * keys) and the Vite dev server in local auth mode. Tokens come from
 * e2e/.tokens.json, written by e2e/prepare.sh before the run.
 */
const FRONTEND_PORT = 5174;
const BACKEND_PORT = 8010;
const frontendUrl = `http://localhost:${String(FRONTEND_PORT)}`;
const backendUrl = `http://localhost:${String(BACKEND_PORT)}`;
const chromiumPath = process.env.PW_CHROMIUM_PATH;

export default defineConfig({
  testDir: "e2e",
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [["github"], ["html", { open: "never" }]] : "list",
  use: {
    baseURL: frontendUrl,
    trace: "retain-on-failure",
    ...(chromiumPath ? { launchOptions: { executablePath: chromiumPath } } : {}),
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      command: `cd ../backend && .venv/bin/uvicorn app.main:app --port ${String(BACKEND_PORT)}`,
      url: `${backendUrl}/health`,
      reuseExistingServer: !process.env.CI,
      env: {
        APP_ENV: "local",
        LOG_LEVEL: "WARNING",
        LOG_FORMAT: "console",
        STORE_BACKEND: "memory",
        AUTH_LOCAL_JWKS_FILE: ".local/dev-jwks.json",
      },
    },
    {
      command: `npx vite --port ${String(FRONTEND_PORT)} --strictPort`,
      url: frontendUrl,
      reuseExistingServer: !process.env.CI,
      env: {
        VITE_AUTH_MODE: "local",
        VITE_API_URL: "/api",
        VITE_BACKEND_PORT: String(BACKEND_PORT),
      },
    },
  ],
});
