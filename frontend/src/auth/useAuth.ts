import { useAuth0 } from "@auth0/auth0-react";
import { config } from "@/config";
import { useLocalAuth } from "./localAuth";

/** What the app needs from an auth provider. Auth0 satisfies it directly. */
export interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  user?: { name?: string | undefined; email?: string | undefined } | undefined;
  loginWithRedirect: (options?: { appState?: { returnTo?: string } }) => Promise<void>;
  logout: (options?: { logoutParams?: { returnTo?: string } }) => Promise<void>;
  getAccessTokenSilently: () => Promise<string>;
}

/**
 * The one hook components use for auth. In the default mode it is Auth0;
 * in ``VITE_AUTH_MODE=local`` (dev server and end-to-end tests only) it is
 * a token pasted into the local login page. The mode is fixed at build
 * time, so picking the implementation once here keeps hook order stable.
 */
export const useAuth: () => AuthState = config.authMode === "local" ? useLocalAuth : useAuth0;
