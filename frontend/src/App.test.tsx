import type * as Auth0 from "@auth0/auth0-react";
import { useAuth0 } from "@auth0/auth0-react";
import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { MemoryRouter } from "react-router-dom";
import { auth0State } from "@/test/auth0";
import { App } from "./App";

vi.mock("@auth0/auth0-react", async (importOriginal) => {
  const actual = await importOriginal<typeof Auth0>();
  return {
    ...actual,
    Auth0Provider: ({ children }: { children: ReactNode }) => <>{children}</>,
    useAuth0: vi.fn(),
  };
});
const mockedUseAuth0 = vi.mocked(useAuth0);

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

    expect(await screen.findByText(/No seasons yet/)).toBeInTheDocument();
    const request = fetchMock.mock.calls[0]![0] as Request;
    expect(request.url).toBe("http://api.test/seasons");
    expect(request.headers.get("Authorization")).toBe("Bearer tok");
    vi.unstubAllGlobals();
  });
});
