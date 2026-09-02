import { useCallback, useMemo, useState, type ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import {
  LOCAL_LOGIN_PATH,
  LOCAL_TOKEN_KEY,
  LocalAuthContext,
  claimsOf,
  readStoredToken,
  type LocalAuthState,
} from "./localAuth";

/** Provider for local auth mode. See ``localAuth.ts`` for the contract. */
export function LocalAuthProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate();
  const [token, setToken] = useState<string | null>(readStoredToken);

  const login = useCallback((next: string) => {
    window.localStorage.setItem(LOCAL_TOKEN_KEY, next);
    setToken(next);
  }, []);

  const value = useMemo<LocalAuthState>(() => {
    const claims = token ? claimsOf(token) : {};
    return {
      isAuthenticated: token !== null,
      isLoading: false,
      user: token ? { name: claims.email ?? claims.sub, email: claims.email } : undefined,
      loginWithRedirect: (options) => {
        const returnTo = options?.appState?.returnTo ?? "/";
        void navigate(`${LOCAL_LOGIN_PATH}?returnTo=${encodeURIComponent(returnTo)}`);
        return Promise.resolve();
      },
      logout: () => {
        window.localStorage.removeItem(LOCAL_TOKEN_KEY);
        setToken(null);
        void navigate("/");
        return Promise.resolve();
      },
      getAccessTokenSilently: () =>
        token ? Promise.resolve(token) : Promise.reject(new Error("not logged in")),
      login,
    };
  }, [token, navigate, login]);

  return <LocalAuthContext.Provider value={value}>{children}</LocalAuthContext.Provider>;
}
