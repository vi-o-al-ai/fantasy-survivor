import type { Auth0ContextInterface } from "@auth0/auth0-react";

/** A useAuth0() return value with sensible defaults; override what a test needs. */
export function auth0State(overrides: Partial<Auth0ContextInterface> = {}) {
  return {
    isAuthenticated: false,
    isLoading: false,
    user: undefined,
    error: undefined,
    loginWithRedirect: vi.fn().mockResolvedValue(undefined),
    logout: vi.fn().mockResolvedValue(undefined),
    getAccessTokenSilently: vi.fn().mockResolvedValue("tok"),
    getAccessTokenWithPopup: vi.fn(),
    getIdTokenClaims: vi.fn(),
    loginWithPopup: vi.fn(),
    handleRedirectCallback: vi.fn(),
    ...overrides,
  } as unknown as Auth0ContextInterface;
}
