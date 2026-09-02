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

Prerequisites: Python 3.12, Node 22, Docker (only for DynamoDB Local).

```sh
pip install pre-commit && pre-commit install
make backend-setup frontend-setup
make backend      # API on :8000 (in-memory store by default)
make frontend     # web app on :5173, proxies /api to the backend
make check        # unit checks CI runs
make e2e          # Playwright scenarios (real backend + browser)
```

Auth0 setup and the local, no-browser token flow are in
[`backend/README.md`](backend/README.md); Auth0 SPA settings are in
[`frontend/README.md`](frontend/README.md). Deploying is in
[`infra/README.md`](infra/README.md).

## Contributing

Read [`docs/CONVENTIONS.md`](docs/CONVENTIONS.md) before opening a change.
Significant technical choices are recorded in [`docs/adr/`](docs/adr/).
