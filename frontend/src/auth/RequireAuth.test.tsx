import { useAuth0 } from "@auth0/auth0-react";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { auth0State } from "@/test/auth0";
import { RequireAuth } from "./RequireAuth";

vi.mock("@auth0/auth0-react");
const mockedUseAuth0 = vi.mocked(useAuth0);

function renderGuard(route = "/seasons/s49") {
  return render(
    <MemoryRouter initialEntries={[route]}>
      <RequireAuth>
        <p>secret</p>
      </RequireAuth>
    </MemoryRouter>,
  );
}

describe("RequireAuth", () => {
  it("renders children when authenticated", () => {
    mockedUseAuth0.mockReturnValue(auth0State({ isAuthenticated: true }));
    renderGuard();
    expect(screen.getByText("secret")).toBeInTheDocument();
  });

  it("starts login and remembers where the user was going", () => {
    const state = auth0State({ isAuthenticated: false });
    mockedUseAuth0.mockReturnValue(state);
    renderGuard("/seasons/s49");
    expect(screen.getByRole("status")).toHaveTextContent("Signing you in");
    expect(state.loginWithRedirect).toHaveBeenCalledWith({
      appState: { returnTo: "/seasons/s49" },
    });
  });

  it("waits while Auth0 is loading without redirecting", () => {
    const state = auth0State({ isLoading: true });
    mockedUseAuth0.mockReturnValue(state);
    renderGuard();
    expect(state.loginWithRedirect).not.toHaveBeenCalled();
    expect(screen.queryByText("secret")).not.toBeInTheDocument();
  });
});
