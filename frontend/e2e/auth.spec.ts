import { apiAs, expect, loginAs, test, tokens } from "./fixtures";

test.describe("authentication", () => {
  test("an anonymous visitor is sent to login and returned afterwards", async ({
    page,
    request,
  }) => {
    const created = await apiAs(request, "owner").post("/leagues", {
      season_id: "s49",
      name: "Return trip",
      display_name: "Owner",
    });
    const league = (await created.json()) as { id: string };

    await page.goto(`/leagues/${league.id}`);
    await expect(page).toHaveURL(/\/local-login\?returnTo=%2Fleagues%2F/);
    await expect(page.getByRole("heading", { name: "Local login" })).toBeVisible();

    await page.getByLabel("Access token").fill(tokens.owner);
    await page.getByRole("main").getByRole("button", { name: "Log in" }).click();

    await expect(page).toHaveURL(`/leagues/${league.id}`);
    await expect(page.getByRole("heading", { name: "Return trip" })).toBeVisible();
    await expect(page.getByText("owner@example.com")).toBeVisible();
  });

  test("logging out clears the session", async ({ page }) => {
    await loginAs(page, "friend");
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "My leagues" })).toBeVisible();

    await page.getByRole("button", { name: "Log out" }).click();
    await expect(
      page.getByRole("navigation").getByRole("button", { name: "Log in" }),
    ).toBeVisible();
    await page.goto("/seasons");
    await expect(page).toHaveURL(/\/local-login/);
  });
});
