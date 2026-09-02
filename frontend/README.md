# Frontend

React + TypeScript + Vite single-page app. Auth via Auth0; talks to the
backend through a typed client generated from `docs/openapi.json`.

## Setup

```sh
cd frontend
npm ci
cp .env.example .env.local     # fill in the Auth0 SPA application values
npm run dev                    # http://localhost:5173
```

In dev, requests to `/api/*` are proxied to the backend on
`localhost:8000`, so run `make backend` alongside. No CORS config needed.

In Auth0, create a **Single Page Application** and add
`http://localhost:5173` to Allowed Callback, Logout, and Web Origins. Use
the same **API** audience the backend verifies.

## Checks

```sh
npm run check      # lint, format, typecheck, tests with coverage
npm run build      # production bundle in dist/
```

## Running without Auth0

Set `VITE_AUTH_MODE=local` in `.env.local` (dev server only; production
builds refuse it). The app then shows a `/local-login` page that accepts a
token from `python scripts/mint_dev_token.py`, and the backend must run
with `AUTH_LOCAL_JWKS_FILE=.local/dev-jwks.json`.

## End-to-end tests

Playwright drives the real backend (in-memory store, local signing keys)
and the Vite dev server in local auth mode. Scenarios live in `e2e/`:
anonymous redirect and return, logout, create/join/roster/score/re-score
across two browser contexts, draft locking, league privacy, wrong join
codes.

```sh
npm run e2e          # mints test tokens, starts both servers, runs headless
npm run e2e:ui       # same, with the Playwright UI
```

The suite is serial and the backend keeps state for the whole run, so
tests use unique league names and never assert on global emptiness for a
shared persona.

## API types

`src/api/schema.d.ts` is generated from the backend's OpenAPI spec and is
committed. After any backend route change:

```sh
make openapi && cd frontend && npm run api:types
```

CI fails if the generated file is stale.

## Layout

| Path              | Purpose                                           |
| ----------------- | ------------------------------------------------- |
| `src/config.ts`   | The only place that reads `import.meta.env`       |
| `src/auth/`       | Auth0 provider and the `RequireAuth` guard        |
| `src/api/`        | Typed client, provider hook, generated schema     |
| `src/pages/`      | Route components; data loading lives here for now |
| `src/components/` | Shared presentational pieces                      |
| `src/test/`       | Test setup and render helpers                     |
