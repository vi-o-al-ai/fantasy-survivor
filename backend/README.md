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
