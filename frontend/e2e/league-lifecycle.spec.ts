import { apiAs, expect, loginAs, test } from "./fixtures";

test.describe("league lifecycle", () => {
  test("owner creates, friend joins, stats score the leaderboard, rules re-score it", async ({
    browser,
    page,
    request,
  }) => {
    // --- owner creates a league in the UI ------------------------------------
    // The backend under test keeps state for the whole run, so names are unique.
    const name = `Island Buddies ${String(Date.now())}`;
    await loginAs(page, "owner");
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "My leagues" })).toBeVisible();

    await page.getByLabel("League name").fill(name);
    await page.getByLabel("Your name in the league").first().fill("Jeff");
    await page.getByRole("button", { name: "Create" }).click();

    const link = page.getByRole("link", { name });
    await expect(link).toBeVisible();
    await link.click();
    await expect(page.getByRole("heading", { name })).toBeVisible();
    const leagueId = page.url().split("/leagues/")[1]!;
    const joinCode = (await page.getByTestId("join-code").textContent())!.trim();
    expect(joinCode).toHaveLength(8);

    // --- owner picks a roster ---------------------------------------------------
    await page.getByLabel(/Amy/).check();
    await page.getByLabel(/Bob/).check();
    await page.getByLabel(/Cal/).check();
    await expect(page.getByLabel(/Dee/)).toBeDisabled();
    await page.getByRole("button", { name: "Save roster" }).click();
    await expect(page.getByText("Roster saved.")).toBeVisible();

    // --- friend joins with the code in a separate browser context ---------------
    const friendContext = await browser.newContext();
    const friend = await friendContext.newPage();
    await loginAs(friend, "friend");
    await friend.goto("/");
    await friend.getByLabel("League id").fill(leagueId);
    await friend.getByLabel("Join code").fill(joinCode.toLowerCase());
    await friend.getByLabel("Your name in the league").nth(1).fill("Pal");
    await friend.getByRole("button", { name: "Join" }).click();
    await friend.getByRole("link", { name }).click();
    await expect(friend.getByRole("heading", { name })).toBeVisible();
    await expect(friend.getByRole("heading", { name: "League settings" })).toHaveCount(0);

    await friend.getByLabel(/Bob/).check();
    await friend.getByLabel(/Cal/).check();
    await friend.getByLabel(/Dee/).check();
    await friend.getByRole("button", { name: "Save roster" }).click();
    await expect(friend.getByText("Roster saved.")).toBeVisible();

    // --- commissioner records the truth once ------------------------------------
    const commissioner = apiAs(request, "commissioner");
    await commissioner.put("/seasons/s49/episodes/1/stats/amy", {
      events: { survived_episode: 1, individual_immunity: 1 },
    });
    await commissioner.put("/seasons/s49/episodes/1/stats/dee", { events: { voted_out: 1 } });

    // --- leaderboard reflects default rules -------------------------------------
    await page.reload();
    const rows = page.getByRole("row");
    await expect(rows.nth(1)).toContainText("Jeff");
    await expect(rows.nth(1)).toContainText("12");
    await expect(rows.nth(2)).toContainText("Pal");
    await expect(rows.nth(2)).toContainText("-5");

    // --- owner tweaks this league's point values --------------------------------
    const immunity = page.getByLabel("individual immunity");
    await immunity.fill("50");
    const votedOut = page.getByLabel("voted out");
    await votedOut.fill("0");
    await page.getByRole("button", { name: "Save settings" }).click();
    await expect(page.getByText("Settings saved.")).toBeVisible();

    await page.reload();
    await expect(page.getByRole("row").nth(1)).toContainText("52");
    await expect(page.getByRole("row").nth(2)).toContainText("Pal");
    await expect(page.getByRole("row").nth(2)).not.toContainText("-5");

    // The friend sees the same re-scored board; the shared truth is unchanged.
    await friend.reload();
    await expect(friend.getByRole("row").nth(1)).toContainText("52");
    const shared = await apiAs(request, "friend").get("/seasons/s49/points");
    expect(await shared.json()).toEqual({ points: { amy: 12, dee: -5 } });

    await friendContext.close();
  });

  test("closing the draft locks rosters for members", async ({ browser, page, request }) => {
    const owner = apiAs(request, "owner");
    const league = (await (
      await owner.post("/leagues", { season_id: "s49", name: "Locked", display_name: "Jeff" })
    ).json()) as { id: string; join_code: string };
    await apiAs(request, "friend").post(`/leagues/${league.id}/members`, {
      join_code: league.join_code,
      display_name: "Pal",
    });

    await loginAs(page, "owner");
    await page.goto(`/leagues/${league.id}`);
    await page.getByLabel(/Draft open/).uncheck();
    await page.getByRole("button", { name: "Save settings" }).click();
    await expect(page.getByText("Settings saved.")).toBeVisible();

    const friendContext = await browser.newContext();
    const friend = await friendContext.newPage();
    await loginAs(friend, "friend");
    await friend.goto(`/leagues/${league.id}`);
    await expect(friend.getByText(/draft is closed/)).toBeVisible();
    await expect(friend.getByRole("button", { name: "Save roster" })).toBeDisabled();
    await expect(friend.getByLabel(/Amy/)).toBeDisabled();
    await friendContext.close();
  });
});
