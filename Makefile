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

openapi: ## Regenerate docs/openapi.json from the routes
	cd backend && .venv/bin/python scripts/export_openapi.py

# ---- frontend --------------------------------------------------------------
frontend-setup: ## Install frontend deps
	cd frontend && npm ci
	@test -f frontend/.env.local || cp frontend/.env.example frontend/.env.local

frontend: ## Run the web app on :5173 (proxies /api to :8000)
	cd frontend && npm run dev

frontend-check: ## Lint, format, typecheck, and test the frontend
	cd frontend && npm run check

e2e: ## Run Playwright scenarios against real backend + frontend
	cd frontend && npm run e2e

api-types: ## Regenerate frontend API types from docs/openapi.json
	cd frontend && npm run api:types

check: backend-check frontend-check ## Run every local check

# ---- deploy artefacts / infra ---------------------------------------------
lambda-zip: ## Build backend/lambda.zip for Lambda
	backend/scripts/build_lambda.sh

tf-check: ## terraform fmt + validate on every root
	terraform fmt -check -recursive infra
	@for d in infra/bootstrap infra/envs/dev; do \
	  (cd $$d && terraform init -backend=false -input=false >/dev/null && terraform validate) || exit 1; \
	done

tf-plan-dev: ## Plan the dev environment (needs AWS creds, backend.hcl, dev.tfvars)
	cd infra/envs/dev && terraform init -backend-config=backend.hcl -input=false && terraform plan -var-file=dev.tfvars

# ---- local services --------------------------------------------------------
db: ## Start DynamoDB Local on :8001
	docker compose up -d dynamodb

db-create: ## Create the table in DynamoDB Local
	cd backend && DYNAMODB_ENDPOINT_URL=http://localhost:8001 AWS_ACCESS_KEY_ID=local AWS_SECRET_ACCESS_KEY=local .venv/bin/python scripts/create_table.py

db-down: ## Stop local services
	docker compose down

.PHONY: help backend-setup backend backend-check backend-fix openapi frontend-setup frontend frontend-check e2e api-types check lambda-zip tf-check tf-plan-dev db db-create db-down
