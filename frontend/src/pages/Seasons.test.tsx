import { screen } from "@testing-library/react";
import type { ApiClient } from "@/api/client";
import { renderPage } from "@/test/render";
import { SeasonsPage } from "./Seasons";

describe("SeasonsPage", () => {
  it("lists seasons", async () => {
    const client = {
      GET: vi.fn().mockResolvedValue({
        data: [{ id: "s49", name: "Survivor 49", number: 49 }],
      }),
    } as unknown as ApiClient;

    renderPage(<SeasonsPage />, client);

    expect(await screen.findByText("Survivor 49")).toBeInTheDocument();
  });

  it("shows the empty state", async () => {
    const client = { GET: vi.fn().mockResolvedValue({ data: [] }) } as unknown as ApiClient;
    renderPage(<SeasonsPage />, client);
    expect(await screen.findByText(/No seasons yet/)).toBeInTheDocument();
  });

  it("shows errors", async () => {
    const client = {
      GET: vi.fn().mockResolvedValue({ error: { detail: "boom" } }),
    } as unknown as ApiClient;
    renderPage(<SeasonsPage />, client);
    expect(await screen.findByRole("alert")).toHaveTextContent("boom");
  });
});
