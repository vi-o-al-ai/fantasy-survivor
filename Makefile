.DEFAULT_GOAL := help
BACKEND_PY ?= backend/.venv/bin

help: ## Show targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ---- backend ---------------------------------------------------------------
backend-setup: ## Create venv and install backend deps
	python3 -m venv backend/.venv
	$(BACKEND_PY)/pip install -q -e "backend[dev]"
	@test -f backend/.env || cp backend/.env.example backend/.env

backend: ## Run the API locally with reload
	cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000

backend-check: ## Lint, type-check, and test the backend
	cd backend && .venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/mypy && .venv/bin/pytest --cov

backend-fix: ## Auto-fix lint and formatting
	cd backend && .venv/bin/ruff check --fix . && .venv/bin/ruff format .

# ---- local services --------------------------------------------------------
db: ## Start DynamoDB Local on :8001
	docker compose up -d dynamodb

db-create: ## Create the table in DynamoDB Local
	cd backend && DYNAMODB_ENDPOINT_URL=http://localhost:8001 AWS_ACCESS_KEY_ID=local AWS_SECRET_ACCESS_KEY=local .venv/bin/python scripts/create_table.py

db-down: ## Stop local services
	docker compose down

.PHONY: help backend-setup backend backend-check backend-fix db db-create db-down
