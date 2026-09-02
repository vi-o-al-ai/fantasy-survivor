# Fantasy Survivor

A fantasy league for the TV show *Survivor*. Players draft castaways, earn
points from what happens each episode, and compete on a league leaderboard.

## Layout

| Path        | What lives here                                              |
| ----------- | ------------------------------------------------------------ |
| `backend/`  | Python API (FastAPI), deployed to AWS Lambda                 |
| `frontend/` | Web client (React + TypeScript), deployed to S3 + CloudFront |
| `infra/`    | Terraform for all AWS resources                              |
| `docs/`     | Plan, conventions, and architecture decision records (ADRs)  |

The API is the contract. A future mobile app talks to the same backend.

## Status

The project is built in small phases. See [`docs/PLAN.md`](docs/PLAN.md)
for what is done and what is next.

## Getting started

Each subproject has its own README with setup steps once that phase lands.
Repo-wide tooling:

```sh
pip install pre-commit
pre-commit install
```

## Contributing

Read [`docs/CONVENTIONS.md`](docs/CONVENTIONS.md) before opening a change.
Significant technical choices are recorded in [`docs/adr/`](docs/adr/).
