# Build plan

The project is built in phases. Each phase is one commit set, lands with
passing checks, and ends with a short status update here. A phase is done
when its box is ticked.

This file is the source of truth for automated runs: pick the first
unchecked phase, do only that phase, tick it, stop.

## Phases

- [x] **1. Repo foundation.** Monorepo layout, `.gitignore`, `.editorconfig`,
  pre-commit, README, conventions, ADRs, CI skeleton, this plan.
- [x] **2. Backend skeleton.** FastAPI app with `/health`, settings from
  environment, structured logging, `ruff` + `mypy --strict` + `pytest`
  configured, one passing test, CI job for the backend.
- [x] **3. Auth0 on the backend.** JWT verification against the Auth0 JWKS,
  `get_current_user` dependency, `GET /me`, tests using a locally generated
  RSA key pair (no Auth0 account needed in CI).
- [x] **4. Domain and storage.** Models for season, contestant, episode,
  episode stats, and user roster. Repository interface with in-memory and
  DynamoDB implementations. Scoring service with unit tests.
- [x] **5. API endpoints.** Contestants, episode stat entry, user picks,
  leaderboard. OpenAPI spec committed as the client contract.
- [x] **6. Terraform (dev).** Modules for DynamoDB, Lambda + API Gateway,
  S3 + CloudFront. `dev` environment root, remote state, `fmt`/`validate`
  in CI.
- [x] **7. Frontend skeleton.** React + TypeScript + Vite, Auth0 login, API
  client that attaches the access token, leaderboard page, CI job.
- [ ] **8. Deploy pipeline.** CI builds and deploys backend and frontend to
  dev on merge to `main`.

## Later (not scheduled)

- Mobile app (reuses the API from phases 3–5).
- Admin UI for entering episode stats.
- Multiple leagues per season, league invites.
- Production environment and promotion flow.

## Status log

- Phase 1 done. Toolchains verified reachable from CI-like environment:
  pip, npm, and Terraform downloads all succeed.
- Phase 2 done. `httpx2` is the test client dependency (Starlette 1.x
  deprecates `httpx`). Coverage gate set at 90%. Root `Makefile` added.
- Phase 3 done. Verified locally: minted token → `/me` returns claims,
  missing token → 401, unconfigured auth → 503. Only RS256 accepted.
- Phase 4 done. Store contract tests run against memory and DynamoDB
  (moto). Docker Compose + `make db db-create` for DynamoDB Local.
  Deferred: conditional writes, GSIs, per-season scoring overrides.
- Phase 5 done. Permissions: `manage:seasons`, `write:stats`. Found and
  fixed a route-shadowing bug (`/seasons/scoring-rules` vs `/{season_id}`)
  via tests; static routes now live outside parameterised prefixes.
- Phase 6 done. `terraform validate` passes for both roots (provider
  5.100.0). Lambda zip builds at ~24 MB with cp312 x86_64 wheels; the
  handler is unit-tested with an API Gateway v2 event. Not yet run:
  `terraform plan/apply` against a real account (needs credentials).
- Phase 7 done. Typed client via openapi-typescript + openapi-fetch from
  the committed spec; CI fails if the generated types drift. Pinned
  TypeScript 5.9 (TS 7 is not yet supported by typescript-eslint).
  Frontend coverage gate: 80% lines. Bundle ~136 kB gzipped.
