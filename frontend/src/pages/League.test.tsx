import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { fakeApi } from "@/test/fakeApi";
import { renderPage } from "@/test/render";
import { LeaguePage } from "./League";

const league = {
  id: "lg-1",
  season_id: "s49",
  name: "Jeff's League",
  owner_id: "auth0|owner",
  roster_size: 2,
  draft_open: true,
  scoring_overrides: { sole_survivor: 100 },
  join_code: "ABCD1234",
  is_owner: true,
};
const contestants = [
  { id: "amy", season_id: "s49", name: "Amy", tribe: "Vati", status: "active" },
  { id: "bob", season_id: "s49", name: "Bob", tribe: null, status: "eliminated" },
  { id: "cal", season_id: "s49", name: "Cal", tribe: null, status: "active" },
];
const entries = [
  {
    rank: 1,
    user_id: "auth0|owner",
    display_name: "Jeff",
    points: 12,
    contestant_points: { amy: 12 },
  },
  { rank: 2, user_id: "auth0|pal", display_name: "Pal", points: 0, contestant_points: {} },
];
const rules = { points: { sole_survivor: 30, individual_immunity: 10 } };

function routes(overrides: Record<string, unknown> = {}) {
  return {
    "GET /leagues/{league_id}": { data: league },
    "GET /leagues/{league_id}/members/me": {
      data: {
        league_id: "lg-1",
        user_id: "auth0|owner",
        display_name: "Jeff",
        contestant_ids: ["amy"],
      },
    },
    "GET /seasons/{season_id}/contestants": { data: contestants },
    "GET /leagues/{league_id}/leaderboard": { data: entries },
    "GET /scoring-rules": { data: rules },
    "PUT /leagues/{league_id}/members/me/roster": { data: {} },
    "PATCH /leagues/{league_id}": { data: league },
    ...overrides,
  } as Parameters<typeof fakeApi>[0];
}

const at = { path: "/leagues/:leagueId", route: "/leagues/lg-1" };

describe("LeaguePage", () => {
  it("shows leaderboard, roster, and owner settings", async () => {
    const { client } = fakeApi(routes());
    renderPage(<LeaguePage />, client, at);

    expect(await screen.findByRole("heading", { name: "Jeff's League" })).toBeInTheDocument();
    const rows = screen.getAllByRole("row");
    expect(within(rows[1]!).getByText("Jeff")).toBeInTheDocument();
    expect(within(rows[2]!).getByText("no picks yet")).toBeInTheDocument();
    expect(screen.getByLabelText(/Amy/)).toBeChecked();
    expect(screen.getByTestId("join-code")).toHaveTextContent("ABCD1234");
    // Override shown against its default.
    expect(await screen.findByLabelText("sole survivor")).toHaveValue(100);
    expect(screen.getByText("(default 30)")).toBeInTheDocument();
  });

  it("saves a roster and enforces the size limit in the UI", async () => {
    const { client, calls } = fakeApi(routes());
    renderPage(<LeaguePage />, client, at);
    await screen.findByRole("heading", { name: "Jeff's League" });

    await userEvent.click(screen.getByLabelText(/Cal/));
    expect(screen.getByLabelText(/Bob/)).toBeDisabled(); // roster full at 2
    await userEvent.click(screen.getByRole("button", { name: "Save roster" }));

    expect(await screen.findByText("Roster saved.")).toBeInTheDocument();
    const save = calls.find((c) => c.key === "PUT /leagues/{league_id}/members/me/roster");
    expect(save?.opts).toEqual({
      params: { path: { league_id: "lg-1" } },
      body: { contestant_ids: ["amy", "cal"] },
    });
  });

  it("hides settings from non-owners and locks a closed draft", async () => {
    const { client } = fakeApi(
      routes({
        "GET /leagues/{league_id}": {
          data: { ...league, is_owner: false, join_code: null, draft_open: false },
        },
      }),
    );
    renderPage(<LeaguePage />, client, at);
    await screen.findByRole("heading", { name: "Jeff's League" });

    expect(screen.queryByRole("heading", { name: "League settings" })).not.toBeInTheDocument();
    expect(screen.getByText(/draft is closed/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Save roster" })).toBeDisabled();
  });

  it("owner saves point overrides and draft state", async () => {
    const { client, calls } = fakeApi(routes());
    renderPage(<LeaguePage />, client, at);
    const immunity = await screen.findByLabelText("individual immunity");

    await userEvent.clear(immunity);
    await userEvent.type(immunity, "25");
    await userEvent.click(screen.getByLabelText(/Draft open/));
    await userEvent.click(screen.getByRole("button", { name: "Save settings" }));

    expect(await screen.findByText("Settings saved.")).toBeInTheDocument();
    const patch = calls.find((c) => c.key === "PATCH /leagues/{league_id}");
    expect(patch?.opts).toEqual({
      params: { path: { league_id: "lg-1" } },
      body: {
        draft_open: false,
        scoring_overrides: { sole_survivor: 100, individual_immunity: 25 },
      },
    });
  });

  it("shows an error for a league the user cannot see", async () => {
    const { client } = fakeApi(
      routes({ "GET /leagues/{league_id}": { error: { detail: "you are not a member" } } }),
    );
    renderPage(<LeaguePage />, client, at);
    expect(await screen.findByRole("alert")).toHaveTextContent("you are not a member");
  });
});
