import { apiAs, expect, loginAs, test } from "./fixtures";

test.describe("league privacy", () => {
  test("a non-member cannot see a league or its code", async ({ page, request }) => {
    const created = await apiAs(request, "owner").post("/leagues", {
      season_id: "s49",
      name: "Private Club",
      display_name: "Jeff",
    });
    const league = (await created.json()) as { id: string };

    await loginAs(page, "stranger");
    await page.goto(`/leagues/${league.id}`);
    await expect(page.getByRole("alert")).toContainText("not a member");
    await expect(page.getByTestId("join-code")).toHaveCount(0);

    await page.goto("/");
    await expect(page.getByText(/not in any leagues/)).toBeVisible();
    await expect(page.getByRole("link", { name: "Private Club" })).toHaveCount(0);
  });

  test("a wrong join code is rejected", async ({ page, request }) => {
    const created = await apiAs(request, "owner").post("/leagues", {
      season_id: "s49",
      name: "Guarded",
      display_name: "Jeff",
    });
    const league = (await created.json()) as { id: string };

    await loginAs(page, "stranger");
    await page.goto("/");
    await page.getByLabel("League id").fill(league.id);
    await page.getByLabel("Join code").fill("WRONGCODE");
    await page.getByLabel("Your name in the league").nth(1).fill("Sneaky");
    await page.getByRole("button", { name: "Join" }).click();
    await expect(page.getByRole("alert")).toContainText("wrong join code");
  });
});
