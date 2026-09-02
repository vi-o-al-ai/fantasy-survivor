/** Build-time configuration. Every value comes from VITE_* env vars. */

function required(name: string): string {
  const value = import.meta.env[name] as string | undefined;
  if (!value) {
    throw new Error(`Missing required environment variable ${name}`);
  }
  return value;
}

export const config = {
  auth0: {
    domain: required("VITE_AUTH0_DOMAIN"),
    clientId: required("VITE_AUTH0_CLIENT_ID"),
    audience: required("VITE_AUTH0_AUDIENCE"),
  },
  apiUrl: (import.meta.env.VITE_API_URL as string | undefined) ?? "/api",
} as const;
