import { test as base, expect, type APIRequestContext, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";

export type Persona = "commissioner" | "owner" | "friend" | "stranger";

/** Per-persona bearer tokens written by e2e/prepare.sh. */
export const tokens = JSON.parse(
  readFileSync(new URL("./.tokens.json", import.meta.url), "utf8"),
) as Record<Persona, string>;

export const TOKEN_KEY = "fantasy-survivor.local-token";
export const SEASON = "s49";
export const CONTESTANTS = ["amy", "bob", "cal", "dee"];

/**
 * Log a persona in by seeding the token the local auth mode reads. Seeds
 * once per tab (init scripts run on every navigation) so a test can log
 * out and stay logged out.
 */
export async function loginAs(page: Page, persona: Persona) {
  await page.addInitScript(
    ([key, token]) => {
      if (window.sessionStorage.getItem("e2e-seeded") === null) {
        window.localStorage.setItem(key, token);
        window.sessionStorage.setItem("e2e-seeded", "1");
      }
    },
    [TOKEN_KEY, tokens[persona]] as const,
  );
}

/** Direct API access as a persona, for seeding and assertions. */
export function apiAs(request: APIRequestContext, persona: Persona) {
  const headers = { Authorization: `Bearer ${tokens[persona]}` };
  return {
    put: (path: string, data: unknown) => request.put(`/api${path}`, { headers, data }),
    post: (path: string, data: unknown) => request.post(`/api${path}`, { headers, data }),
    get: (path: string) => request.get(`/api${path}`, { headers }),
  };
}

/** Idempotent: the backend is in-memory and PUTs are upserts. */
export async function seedSeason(request: APIRequestContext) {
  const api = apiAs(request, "commissioner");
  expect((await api.put(`/seasons/${SEASON}`, { name: "Survivor 49", number: 49 })).ok()).toBe(
    true,
  );
  for (const id of CONTESTANTS) {
    const name = id[0]!.toUpperCase() + id.slice(1);
    expect((await api.put(`/seasons/${SEASON}/contestants/${id}`, { name })).ok()).toBe(true);
  }
}

export const test = base.extend<{ seeded: void }>({
  seeded: [
    async ({ request }, use) => {
      await seedSeason(request);
      await use();
    },
    { auto: true },
  ],
});

export { expect };
