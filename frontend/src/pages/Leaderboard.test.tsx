import { screen } from "@testing-library/react";
import type { ApiClient } from "@/api/client";
import { renderPage } from "@/test/render";
import { LeaderboardPage } from "./Leaderboard";

function stubClient(GET: unknown): ApiClient {
  return { GET } as unknown as ApiClient;
}

describe("LeaderboardPage", () => {
  it("renders ranked entries from the API", async () => {
    const GET = vi.fn().mockResolvedValue({
      data: [
        {
          rank: 1,
          user_id: "auth0|1",
          display_name: "Alpha",
          points: 12,
          contestant_points: { amy: 12, bob: 0 },
        },
        { rank: 2, user_id: "auth0|2", display_name: "Bravo", points: -5, contestant_points: {} },
      ],
    });

    renderPage(<LeaderboardPage />, stubClient(GET), {
      path: "/seasons/:seasonId",
      route: "/seasons/s49",
    });

    expect(await screen.findByRole("heading", { name: "Leaderboard" })).toBeInTheDocument();
    expect(GET).toHaveBeenCalledWith("/seasons/{season_id}/leaderboard", {
      params: { path: { season_id: "s49" } },
    });
    expect(screen.getByText("Alpha")).toBeInTheDocument();
    expect(screen.getByText("amy (12), bob (0)")).toBeInTheDocument();
    expect(screen.getAllByRole("row")).toHaveLength(3);
  });

  it("shows the API error message", async () => {
    const GET = vi.fn().mockResolvedValue({ error: { detail: "season 'nope' not found" } });

    renderPage(<LeaderboardPage />, stubClient(GET), {
      path: "/seasons/:seasonId",
      route: "/seasons/nope",
    });

    expect(await screen.findByRole("alert")).toHaveTextContent("season 'nope' not found");
  });

  it("shows an empty state", async () => {
    renderPage(<LeaderboardPage />, stubClient(vi.fn().mockResolvedValue({ data: [] })), {
      path: "/seasons/:seasonId",
      route: "/seasons/s49",
    });

    expect(await screen.findByText("No rosters yet.")).toBeInTheDocument();
  });
});
