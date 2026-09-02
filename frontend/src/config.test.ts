describe("config", () => {
  it("throws a clear error when a required variable is missing", async () => {
    vi.stubEnv("VITE_AUTH0_DOMAIN", "");
    await expect(import("./config")).rejects.toThrow("VITE_AUTH0_DOMAIN");
    vi.unstubAllEnvs();
  });
});
