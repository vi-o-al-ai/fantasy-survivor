/** Build-time configuration. Every value comes from VITE_* env vars. */

function required(name: string): string {
  const value = import.meta.env[name] as string | undefined;
  if (!value) {
    throw new Error(`Missing required environment variable ${name}`);
  }
  return value;
}

type AuthMode = "auth0" | "local";

function authMode(): AuthMode {
  const mode = (import.meta.env.VITE_AUTH_MODE as string | undefined) ?? "auth0";
  if (mode === "local") {
    if (import.meta.env.PROD) {
      throw new Error("VITE_AUTH_MODE=local is not allowed in production builds");
    }
    return "local";
  }
  return "auth0";
}

const mode = authMode();

export const config = {
  authMode: mode,
  auth0:
    mode === "auth0"
      ? {
          domain: required("VITE_AUTH0_DOMAIN"),
          clientId: required("VITE_AUTH0_CLIENT_ID"),
          audience: required("VITE_AUTH0_AUDIENCE"),
        }
      : { domain: "", clientId: "", audience: "" },
  apiUrl: (import.meta.env.VITE_API_URL as string | undefined) ?? "/api",
} as const;
