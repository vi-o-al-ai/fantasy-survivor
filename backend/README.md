# Backend

FastAPI service. Runs locally with uvicorn, deploys to AWS Lambda.

## Setup

```sh
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

## Run

```sh
uvicorn app.main:app --reload --port 8000
```

Interactive docs at <http://localhost:8000/docs>.

## Checks

```sh
ruff check . && ruff format --check .
mypy
pytest --cov
```

Or from the repo root: `make backend-check`.

## Layout

| Path             | Purpose                                              |
| ---------------- | ---------------------------------------------------- |
| `app/main.py`    | App factory and module-level `app` for uvicorn/Lambda |
| `app/config.py`  | Settings from environment; the only place that reads env |
| `app/logging.py` | JSON logging in AWS, console logging locally          |
| `app/routers/`   | HTTP layer only. No business logic here.              |
| `tests/`         | pytest; no network, no AWS                            |

## Authentication

Requests to protected routes carry an Auth0 access token as a bearer
token. The API verifies the RS256 signature against the tenant's JWKS,
checks issuer, audience, and expiry, and exposes the caller as
`CurrentUser` (see `app/auth.py`). Permissions come from the token's
`permissions` claim, so enable RBAC and "add permissions in the access
token" on the Auth0 API.

Set `AUTH0_DOMAIN` and `AUTH0_AUDIENCE` in `.env`. Auth0 works locally.

### Working on the API without a browser

Mint a locally signed token and point the API at the matching JWKS:

```sh
python scripts/mint_dev_token.py --permission write:stats   # prints a token
AUTH_LOCAL_JWKS_FILE=.local/dev-jwks.json uvicorn app.main:app --reload
curl -H "Authorization: Bearer <token>" localhost:8000/me
```

The key pair lives in `backend/.local/` (git-ignored). This mode is refused
when `APP_ENV` is `dev` or `prod`.

## API

All routes except `/health` require a bearer token. Writes need an Auth0
permission on the token. The full contract is `docs/openapi.json`;
regenerate it after changing routes (a test fails if it is stale):

```sh
python scripts/export_openapi.py
```

| Method | Path                                                   | Permission       |
| ------ | ------------------------------------------------------ | ---------------- |
| GET    | `/me`                                                  |                  |
| GET    | `/scoring-rules`                                       |                  |
| GET    | `/seasons`, `/seasons/{id}`                            |                  |
| PUT    | `/seasons/{id}`                                        | `manage:seasons` |
| GET    | `/seasons/{id}/contestants`                            |                  |
| PUT    | `/seasons/{id}/contestants/{cid}`                      | `manage:seasons` |
| GET    | `/seasons/{id}/stats`, `.../episodes/{n}/stats`        |                  |
| PUT    | `/seasons/{id}/episodes/{n}/stats/{cid}`               | `write:stats`    |
| GET    | `/seasons/{id}/points`                                 |                  |
| GET    | `/seasons/{id}/leaderboard`                            |                  |
| GET    | `/seasons/{id}/rosters/me`                             |                  |
| PUT    | `/seasons/{id}/rosters/me`                             |                  |

Ids are slugs (`s49`, `boston-rob`) chosen by the commissioner, so
creates are `PUT` upserts. Errors: 401 no/invalid token, 403 missing
permission, 404 unknown entity, 409 league rule broken (draft closed,
wrong roster size, unknown contestant), 422 malformed body.

Layers: `routers/` (HTTP only) → `services/` (rules) → `storage/` (Store)
and `domain/` (entities, scoring). Add rules to services, never routers.
