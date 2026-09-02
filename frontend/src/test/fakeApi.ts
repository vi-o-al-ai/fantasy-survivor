import type { ApiClient } from "@/api/client";

type Handler = (opts: unknown) => { data?: unknown; error?: unknown };

/**
 * A stub API client keyed by "METHOD path" so page tests can script
 * responses without HTTP. Unknown routes fail loudly.
 */
export function fakeApi(routes: Record<string, Handler | { data?: unknown; error?: unknown }>) {
  const calls: { key: string; opts: unknown }[] = [];
  const method = (verb: string) =>
    vi.fn((path: string, opts?: unknown) => {
      const key = `${verb} ${path}`;
      calls.push({ key, opts });
      const route = routes[key];
      if (!route) throw new Error(`fakeApi: no route for ${key}`);
      const result = typeof route === "function" ? route(opts) : route;
      return Promise.resolve(result);
    });
  const client = {
    GET: method("GET"),
    POST: method("POST"),
    PUT: method("PUT"),
    PATCH: method("PATCH"),
  } as unknown as ApiClient;
  return { client, calls };
}
