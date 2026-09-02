import { act, renderHook, waitFor } from "@testing-library/react";
import { useAsync } from "./useAsync";

describe("useAsync", () => {
  it("loads data, exposes errors, and reloads", async () => {
    let value = 1;
    const loader = vi.fn(() => Promise.resolve({ data: value }));
    const { result } = renderHook(() => useAsync(loader));

    await waitFor(() => {
      expect(result.current.data).toBe(1);
    });
    value = 2;
    act(() => {
      result.current.reload();
    });
    await waitFor(() => {
      expect(result.current.data).toBe(2);
    });
    expect(loader).toHaveBeenCalledTimes(2);
  });

  it("maps API errors and thrown errors to messages", async () => {
    const { result: api } = renderHook(() =>
      useAsync(() => Promise.resolve({ error: { detail: "nope" } })),
    );
    await waitFor(() => {
      expect(api.current.error).toBe("nope");
    });

    const { result: thrown } = renderHook(() =>
      useAsync(() => Promise.reject(new Error("network"))),
    );
    await waitFor(() => {
      expect(thrown.current.error).toBe("Something went wrong");
    });
  });
});
