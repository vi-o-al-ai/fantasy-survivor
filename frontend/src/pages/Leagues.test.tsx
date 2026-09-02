import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { fakeApi } from "@/test/fakeApi";
import { renderPage } from "@/test/render";
import { LeaguesPage } from "./Leagues";

const league = {
  id: "jeffs-league-abc123",
  season_id: "s49",
  name: "Jeff's League",
  owner_id: "auth0|me",
  roster_size: 3,
  draft_open: true,
  scoring_overrides: {},
  join_code: "ABCD1234",
  is_owner: true,
};
const seasons = [{ id: "s49", name: "Survivor 49", number: 49 }];

describe("LeaguesPage", () => {
  it("lists my leagues with links", async () => {
    const { client } = fakeApi({
      "GET /leagues": { data: [league] },
      "GET /seasons": { data: seasons },
    });
    renderPage(<LeaguesPage />, client);

    const link = await screen.findByRole("link", { name: "Jeff's League" });
    expect(link).toHaveAttribute("href", "/leagues/jeffs-league-abc123");
    expect(screen.getByText("owner")).toBeInTheDocument();
  });

  it("creates a league and reloads", async () => {
    let mine: unknown[] = [];
    const { client, calls } = fakeApi({
      "GET /leagues": () => ({ data: mine }),
      "GET /seasons": { data: seasons },
      "POST /leagues": () => {
        mine = [league];
        return { data: league };
      },
    });
    renderPage(<LeaguesPage />, client);
    expect(await screen.findByText(/not in any leagues/)).toBeInTheDocument();

    await userEvent.type(screen.getByLabelText("League name"), "Jeff's League");
    await userEvent.type(screen.getAllByLabelText("Your name in the league")[0]!, "Jeff");
    await userEvent.click(screen.getByRole("button", { name: "Create" }));

    expect(await screen.findByRole("link", { name: "Jeff's League" })).toBeInTheDocument();
    const create = calls.find((c) => c.key === "POST /leagues");
    expect(create?.opts).toEqual({
      body: { season_id: "s49", name: "Jeff's League", display_name: "Jeff" },
    });
  });

  it("joins a league with a code and shows API errors", async () => {
    const { client, calls } = fakeApi({
      "GET /leagues": { data: [] },
      "GET /seasons": { data: seasons },
      "POST /leagues/{league_id}/members": { error: { detail: "wrong join code" } },
    });
    renderPage(<LeaguesPage />, client);
    await screen.findByText(/not in any leagues/);

    await userEvent.type(screen.getByLabelText("League id"), " jeffs-league-abc123 ");
    await userEvent.type(screen.getByLabelText("Join code"), "abcd1234");
    await userEvent.type(screen.getAllByLabelText("Your name in the league")[1]!, "Pal");
    await userEvent.click(screen.getByRole("button", { name: "Join" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("wrong join code");
    const join = calls.find((c) => c.key === "POST /leagues/{league_id}/members");
    expect(join?.opts).toEqual({
      params: { path: { league_id: "jeffs-league-abc123" } },
      body: { join_code: "ABCD1234", display_name: "Pal" },
    });
  });
});
