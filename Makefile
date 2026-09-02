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

.PHONY: help backend-setup backend backend-check backend-fix
