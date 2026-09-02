import type * as Auth0 from "@auth0/auth0-react";
import { render, screen } from "@testing-library/react";
import { useAuth } from "@/auth/useAuth";
import type { ReactNode } from "react";
import { MemoryRouter } from "react-router-dom";
import { auth0State } from "@/test/auth0";
import { App } from "./App";

vi.mock("@auth0/auth0-react", async (importOriginal) => {
  const actual = await importOriginal<typeof Auth0>();
  return {
    ...actual,
    Auth0Provider: ({ children }: { children: ReactNode }) => <>{children}</>,
  };
});
vi.mock("@/auth/useAuth");
const mockedUseAuth0 = vi.mocked(useAuth);

describe("App", () => {
  it("routes a logged-in user to the seasons page and calls the API", async () => {
    mockedUseAuth0.mockReturnValue(auth0State({ isAuthenticated: true }));
    const fetchMock = vi.fn((_input: RequestInfo | URL) =>
      Promise.resolve(
        new Response(JSON.stringify([]), { headers: { "Content-Type": "application/json" } }),
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    render(
      <MemoryRouter initialEntries={["/"]}>
        <App />
      </MemoryRouter>,
    );

    expect(await screen.findByText(/not in any leagues yet/)).toBeInTheDocument();
    const request = fetchMock.mock.calls[0]![0] as Request;
    expect(request.url).toBe("http://api.test/leagues");
    expect(request.headers.get("Authorization")).toBe("Bearer tok");
    vi.unstubAllGlobals();
  });
});
