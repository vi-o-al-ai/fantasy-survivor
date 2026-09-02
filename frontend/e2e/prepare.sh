#!/usr/bin/env bash
# Mint one locally signed token per test persona. Also creates the local
# signing key + JWKS on first run (backend/.local/), which the backend
# under test verifies against.
set -euo pipefail
cd "$(dirname "$0")/../../backend"
PY=${PYTHON:-.venv/bin/python}
mint() { "$PY" scripts/mint_dev_token.py "$@"; }

cat > ../frontend/e2e/.tokens.json <<JSON
{
  "commissioner": "$(mint --sub commissioner@example.com --permission manage:seasons --permission write:stats)",
  "owner": "$(mint --sub owner@example.com)",
  "friend": "$(mint --sub friend@example.com)",
  "stranger": "$(mint --sub stranger@example.com)"
}
JSON
echo "tokens written to frontend/e2e/.tokens.json"
