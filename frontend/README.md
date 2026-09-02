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
