import { screen } from "@testing-library/react";
import type { ApiClient } from "@/api/client";
import { renderPage } from "@/test/render";
import { SeasonsPage } from "./Seasons";

describe("SeasonsPage", () => {
  it("lists seasons with links to their leaderboard", async () => {
    const client = {
      GET: vi.fn().mockResolvedValue({
        data: [{ id: "s49", name: "Survivor 49", number: 49, roster_size: 3, draft_open: true }],
      }),
    } as unknown as ApiClient;

    renderPage(<SeasonsPage />, client);

    const link = await screen.findByRole("link", { name: "Survivor 49" });
    expect(link).toHaveAttribute("href", "/seasons/s49");
    expect(screen.getByText("draft open")).toBeInTheDocument();
  });

  it("shows the empty state", async () => {
    const client = { GET: vi.fn().mockResolvedValue({ data: [] }) } as unknown as ApiClient;
    renderPage(<SeasonsPage />, client);
    expect(await screen.findByText(/No seasons yet/)).toBeInTheDocument();
  });
});
