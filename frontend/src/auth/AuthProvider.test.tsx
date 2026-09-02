import type { AppState } from "@auth0/auth0-react";
import { act, render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";
import { AuthProvider } from "./AuthProvider";

interface CapturedProps {
  domain: string;
  clientId: string;
  authorizationParams?: { audience?: string };
  onRedirectCallback?: (appState?: AppState) => void;
  children?: ReactNode;
}

const captured: { props?: CapturedProps } = {};
vi.mock("@auth0/auth0-react", () => ({
  Auth0Provider: (props: CapturedProps) => {
    captured.props = props;
    return <>{props.children}</>;
  },
}));

function Where() {
  return <p data-testid="where">{useLocation().pathname}</p>;
}

describe("AuthProvider", () => {
  it("configures Auth0 from env and returns users to their page after login", () => {
    render(
      <MemoryRouter initialEntries={["/"]}>
        <AuthProvider>
          <Routes>
            <Route path="*" element={<Where />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>,
    );

    expect(captured.props?.domain).toBe("test.auth0.local");
    expect(captured.props?.clientId).toBe("test-client");
    expect(captured.props?.authorizationParams?.audience).toBe("https://api.test");

    act(() => {
      captured.props?.onRedirectCallback?.({ returnTo: "/seasons/s49" });
    });
    expect(screen.getByTestId("where")).toHaveTextContent("/seasons/s49");

    act(() => {
      captured.props?.onRedirectCallback?.(undefined);
    });
    expect(screen.getByTestId("where")).toHaveTextContent("/");
  });
});
