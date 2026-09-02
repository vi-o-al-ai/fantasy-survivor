import { useAuth0 } from "@auth0/auth0-react";
import { useMemo, type ReactNode } from "react";
import { config } from "@/config";
import { createApiClient, type ApiClient } from "./client";
import { ApiContext } from "./context";

/** Provides one API client wired to Auth0 tokens. */
export function ApiProvider({ children }: { children: ReactNode }) {
  const { getAccessTokenSilently } = useAuth0();
  const client = useMemo(
    () => createApiClient(config.apiUrl, () => getAccessTokenSilently()),
    [getAccessTokenSilently],
  );
  return <ApiContext.Provider value={client}>{children}</ApiContext.Provider>;
}

/** Test seam: supply any client without Auth0. */
export function ApiClientProvider({
  client,
  children,
}: {
  client: ApiClient;
  children: ReactNode;
}) {
  return <ApiContext.Provider value={client}>{children}</ApiContext.Provider>;
}
