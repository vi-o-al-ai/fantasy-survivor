/**
 * Local auth mode for development without Auth0 and for end-to-end tests.
 *
 * A bearer token (minted by backend/scripts/mint_dev_token.py) is kept in
 * localStorage. The backend verifies it against the same local key file.
 * Never enabled in production builds; see ``config.ts``.
 */

import { createContext, useContext } from "react";
import type { AuthState } from "./useAuth";

export const LOCAL_TOKEN_KEY = "fantasy-survivor.local-token";
export const LOCAL_LOGIN_PATH = "/local-login";

export type LocalAuthState = AuthState & { login: (token: string) => void };

export const LocalAuthContext = createContext<LocalAuthState | null>(null);

export function readStoredToken(): string | null {
  try {
    return window.localStorage.getItem(LOCAL_TOKEN_KEY);
  } catch {
    return null;
  }
}

/** Best-effort claims from an unverified JWT payload, for display only. */
export function claimsOf(token: string): { sub?: string; email?: string } {
  try {
    const payload = token.split(".")[1] ?? "";
    const json = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(json) as { sub?: string; email?: string };
  } catch {
    return {};
  }
}

function useLocalAuthContext(): LocalAuthState {
  const value = useContext(LocalAuthContext);
  if (!value) {
    throw new Error("local auth hooks must be used inside <LocalAuthProvider>");
  }
  return value;
}

export function useLocalAuth(): AuthState {
  return useLocalAuthContext();
}

export function useLocalLogin(): (token: string) => void {
  return useLocalAuthContext().login;
}
