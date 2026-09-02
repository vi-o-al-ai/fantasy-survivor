import { Auth0Provider } from "@auth0/auth0-react";
import type { ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { config } from "@/config";

/** Wraps the app in Auth0 and returns users to where they were after login. */
export function AuthProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate();
  return (
    <Auth0Provider
      domain={config.auth0.domain}
      clientId={config.auth0.clientId}
      authorizationParams={{
        audience: config.auth0.audience,
        redirect_uri: window.location.origin,
      }}
      cacheLocation="memory"
      useRefreshTokens
      onRedirectCallback={(appState) => {
        void navigate(appState?.returnTo ?? "/", { replace: true });
      }}
    >
      {children}
    </Auth0Provider>
  );
}
