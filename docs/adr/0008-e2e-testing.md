# 0008. End-to-end tests with Playwright and a local auth mode

Date: 2026-09-02
Status: Accepted

## Context

Unit tests on both sides mock the other side. Nothing exercised the real
browser against the real API, and the login flow depends on Auth0's
hosted page, which cannot run in CI.

## Decision

- Playwright runs against the actual backend (in-memory store, local RSA
  keys from `mint_dev_token.py`) and the Vite dev server.
- The frontend gains `VITE_AUTH_MODE=local`, which swaps the Auth0 hook
  for a token kept in localStorage and a `/local-login` page. Components
  only ever call `useAuth()`, so the swap is one line. Production builds
  throw if the flag is set.
- Personas (commissioner, owner, friend, stranger) get pre-minted tokens;
  tests seed them into the browser or call the API directly for setup.
- Scenarios cover the paths a user actually walks, not individual
  components: redirect-and-return, logout, create/join/roster/score,
  re-scoring after a rules change, draft locking, privacy, bad join code.

## Consequences

- The Auth0 redirect itself is still untested end-to-end; it is Auth0's
  SDK and configuration, verified manually after deploy.
- Serial execution and shared backend state: tests avoid global
  assertions on shared personas and use unique names. If the suite grows,
  restart the backend per file or add a reset endpoint gated to local
  mode.
- Local auth mode doubles as a developer convenience for running the app
  with no Auth0 tenant at all.
