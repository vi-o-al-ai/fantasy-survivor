# Conventions

These rules keep the project reviewable while it is small and keep it sane
when it is not.

## Workflow

- Work lands as small, sequential commits. One phase from `docs/PLAN.md`
  per commit set; one concern per commit.
- Lint, type checks, and tests pass locally before every push. CI is a
  backstop, not the first place a failure is seen.
- Every phase ends by ticking its box in `docs/PLAN.md` and noting anything
  deferred.

## Commits

Conventional Commits, so history is scannable and changelogs are cheap:

```
<type>(<scope>): <short imperative summary>

<why, not what — the diff shows what>
```

Types: `feat`, `fix`, `chore`, `docs`, `test`, `refactor`, `ci`, `infra`.
Scopes: `backend`, `frontend`, `infra`, `docs`, or omitted for repo-wide.

## Code

- **Backend (Python):** `ruff` for lint and format, `mypy --strict`,
  `pytest`. Type hints everywhere. Frozen Pydantic models for entities
  (they cross both the API and storage boundaries); plain dataclasses
  and functions for rules and computation. No business logic in route
  handlers.
- **Frontend (TypeScript):** `strict` compiler settings, ESLint, Prettier,
  Vitest. Components stay presentational; data access goes through the API
  client module.
- **Infra (Terraform):** `terraform fmt` and `validate` in CI. One module
  per AWS concern, one root per environment. No secrets in state that can
  be avoided; none in the repo, ever.

## Testing

- Unit tests must not need network, AWS, or Auth0. Storage sits behind a
  repository interface with an in-memory implementation for tests.
- Auth tests sign tokens with a locally generated key pair.
- Integration against real AWS is run on demand, not in CI, until the
  project is big enough to justify the cost.

## Decisions

Anything a future contributor might ask "why?" about gets an ADR in
`docs/adr/`. Short is fine. Superseded ADRs are kept and marked as such.
