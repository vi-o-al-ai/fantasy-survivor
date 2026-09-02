import { render, screen } from "@testing-library/react";
import { useAuth } from "@/auth/useAuth";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { auth0State } from "@/test/auth0";
import { Layout } from "./Layout";

vi.mock("@/auth/useAuth");
const mockedUseAuth0 = vi.mocked(useAuth);

function renderLayout() {
  return render(
    <MemoryRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<p>page body</p>} />
        </Route>
      </Routes>
    </MemoryRouter>,
  );
}

describe("Layout", () => {
  it("offers login when logged out", async () => {
    const state = auth0State();
    mockedUseAuth0.mockReturnValue(state);
    renderLayout();

    expect(screen.getByText("page body")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Log in" }));
    expect(state.loginWithRedirect).toHaveBeenCalled();
  });

  it("shows the user and offers logout when logged in", async () => {
    const state = auth0State({ isAuthenticated: true, user: { name: "Jeff" } });
    mockedUseAuth0.mockReturnValue(state);
    renderLayout();

    expect(screen.getByText("Jeff")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Log out" }));
    expect(state.logout).toHaveBeenCalledWith({
      logoutParams: { returnTo: window.location.origin },
    });
  });
});
