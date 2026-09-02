import type { ReactNode } from "react";
import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import { useAuth } from "./useAuth";

/** Renders children only for a logged-in user; otherwise starts the login redirect. */
export function RequireAuth({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading, loginWithRedirect } = useAuth();
  const location = useLocation();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      void loginWithRedirect({ appState: { returnTo: location.pathname } });
    }
  }, [isAuthenticated, isLoading, loginWithRedirect, location.pathname]);

  if (isLoading || !isAuthenticated) {
    return <p role="status">Signing you in…</p>;
  }
  return <>{children}</>;
}
