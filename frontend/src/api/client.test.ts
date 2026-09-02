import { createApiClient, errorMessage } from "./client";

describe("createApiClient", () => {
  it("attaches the bearer token to every request", async () => {
    const fetchMock = vi.fn((req: Request) => {
      expect(req.headers.get("Authorization")).toBe("Bearer tok-123");
      return Promise.resolve(
        new Response(JSON.stringify({ status: "ok", env: "test" }), {
          headers: { "Content-Type": "application/json" },
        }),
      );
    });
    vi.stubGlobal("fetch", fetchMock);

    const client = createApiClient("http://api.test", () => Promise.resolve("tok-123"));
    const { data } = await client.GET("/health");

    expect(fetchMock).toHaveBeenCalledOnce();
    expect(data?.status).toBe("ok");
    vi.unstubAllGlobals();
  });
});

describe("errorMessage", () => {
  it("uses the backend detail string", () => {
    expect(errorMessage({ detail: "season 'x' not found" })).toBe("season 'x' not found");
  });
  it("falls back for validation error arrays and unknown shapes", () => {
    expect(errorMessage({ detail: [{ loc: [] }] })).toBe("Something went wrong");
    expect(errorMessage(undefined, "nope")).toBe("nope");
  });
});
