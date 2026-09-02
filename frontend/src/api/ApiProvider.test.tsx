import { useAuth0 } from "@auth0/auth0-react";
import { render, screen } from "@testing-library/react";
import { auth0State } from "@/test/auth0";
import { ApiProvider } from "./ApiProvider";
import { useApi } from "./context";

vi.mock("@auth0/auth0-react");
const mockedUseAuth0 = vi.mocked(useAuth0);

function Probe() {
  const api = useApi();
  return <p>{typeof api.GET}</p>;
}

describe("ApiProvider", () => {
  it("provides a client built from the Auth0 token getter", () => {
    mockedUseAuth0.mockReturnValue(auth0State());
    render(
      <ApiProvider>
        <Probe />
      </ApiProvider>,
    );
    expect(screen.getByText("function")).toBeInTheDocument();
  });

  it("useApi throws outside a provider", () => {
    vi.spyOn(console, "error").mockImplementation(() => undefined);
    expect(() => render(<Probe />)).toThrow("useApi must be used inside <ApiProvider>");
    vi.restoreAllMocks();
  });
});
