import createClient, { type Middleware } from "openapi-fetch";
import type { paths } from "./schema";

export type ApiClient = ReturnType<typeof createClient<paths>>;
export type TokenGetter = () => Promise<string>;

/**
 * Typed API client. Every path, parameter, and response shape comes from
 * docs/openapi.json (regenerate `schema.d.ts` with `npm run api:types`).
 */
export function createApiClient(baseUrl: string, getToken: TokenGetter): ApiClient {
  const client = createClient<paths>({ baseUrl });
  const auth: Middleware = {
    async onRequest({ request }) {
      request.headers.set("Authorization", `Bearer ${await getToken()}`);
      return request;
    },
  };
  client.use(auth);
  return client;
}

/** Error shape the backend returns for 4xx/5xx. */
export interface ApiError {
  detail: string | unknown[];
}

export function errorMessage(error: unknown, fallback = "Something went wrong"): string {
  if (error && typeof error === "object" && "detail" in error) {
    const detail = (error as ApiError).detail;
    return typeof detail === "string" ? detail : fallback;
  }
  return fallback;
}
