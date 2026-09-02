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
- [ ] **3. Auth0 on the backend.** JWT verification against the Auth0 JWKS,
  `get_current_user` dependency, `GET /me`, tests using a locally generated
  RSA key pair (no Auth0 account needed in CI).
- [ ] **4. Domain and storage.** Models for season, contestant, episode,
  episode stats, and user roster. Repository interface with in-memory and
  DynamoDB implementations. Scoring service with unit tests.
- [ ] **5. API endpoints.** Contestants, episode stat entry, user picks,
  leaderboard. OpenAPI spec committed as the client contract.
- [ ] **6. Terraform (dev).** Modules for DynamoDB, Lambda + API Gateway,
  S3 + CloudFront. `dev` environment root, remote state, `fmt`/`validate`
  in CI.
- [ ] **7. Frontend skeleton.** React + TypeScript + Vite, Auth0 login, API
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
