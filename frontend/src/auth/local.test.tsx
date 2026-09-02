import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";
import { LocalLoginPage } from "@/pages/LocalLogin";
import { LocalAuthProvider } from "./local";
import { LOCAL_TOKEN_KEY, claimsOf, useLocalAuth } from "./localAuth";

const FAKE_JWT = `x.${btoa(JSON.stringify({ sub: "auth0|u1", email: "u1@example.com" }))}.y`;

function Probe() {
  const auth = useLocalAuth();
  const location = useLocation();
  return (
    <div>
      <p data-testid="state">{auth.isAuthenticated ? (auth.user?.name ?? "?") : "anon"}</p>
      <p data-testid="where">{location.pathname + location.search}</p>
      <button
        onClick={() => {
          void auth.loginWithRedirect({ appState: { returnTo: "/leagues/x" } });
        }}
      >
        go login
      </button>
      <button
        onClick={() => {
          void auth.logout();
        }}
      >
        go logout
      </button>
    </div>
  );
}

function renderLocal(route = "/") {
  return render(
    <MemoryRouter initialEntries={[route]}>
      <LocalAuthProvider>
        <Routes>
          <Route path="/local-login" element={<LocalLoginPage />} />
          <Route path="*" element={<Probe />} />
        </Routes>
      </LocalAuthProvider>
    </MemoryRouter>,
  );
}

describe("local auth mode", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("decodes claims defensively", () => {
    expect(claimsOf(FAKE_JWT)).toEqual({ sub: "auth0|u1", email: "u1@example.com" });
    expect(claimsOf("garbage")).toEqual({});
  });

  it("redirects to the local login page and back, then logs out", async () => {
    renderLocal();
    expect(screen.getByTestId("state")).toHaveTextContent("anon");

    await userEvent.click(screen.getByText("go login"));
    expect(screen.getByRole("heading", { name: "Local login" })).toBeInTheDocument();
    await userEvent.type(screen.getByLabelText("Access token"), FAKE_JWT);
    await userEvent.click(screen.getByRole("button", { name: "Log in" }));

    expect(screen.getByTestId("where")).toHaveTextContent("/leagues/x");
    expect(screen.getByTestId("state")).toHaveTextContent("u1@example.com");
    expect(window.localStorage.getItem(LOCAL_TOKEN_KEY)).toBe(FAKE_JWT);

    await userEvent.click(screen.getByText("go logout"));
    expect(screen.getByTestId("state")).toHaveTextContent("anon");
    expect(window.localStorage.getItem(LOCAL_TOKEN_KEY)).toBeNull();
  });

  it("restores a stored token and serves it to the API client", async () => {
    window.localStorage.setItem(LOCAL_TOKEN_KEY, FAKE_JWT);
    const served: string[] = [];
    function TokenProbe() {
      const auth = useLocalAuth();
      void auth.getAccessTokenSilently().then((t) => {
        served.push(t);
      });
      return null;
    }
    render(
      <MemoryRouter>
        <LocalAuthProvider>
          <TokenProbe />
        </LocalAuthProvider>
      </MemoryRouter>,
    );
    await vi.waitFor(() => {
      expect(served).toEqual([FAKE_JWT]);
    });
  });
});
