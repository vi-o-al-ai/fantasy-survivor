#!/usr/bin/env bash
# Build backend/lambda.zip: app code + runtime deps as Lambda-compatible wheels.
# Runs anywhere with Python 3.12 + pip; wheels are fetched for the Lambda
# platform, not the host, so macOS/Windows builds work too.
set -euo pipefail

cd "$(dirname "$0")/.."
PYTHON_VERSION="${LAMBDA_PYTHON_VERSION:-3.12}"
PLATFORM="${LAMBDA_PLATFORM:-manylinux2014_x86_64}"
BUILD_DIR="build/lambda"
OUT="lambda.zip"

rm -rf "$BUILD_DIR" "$OUT"
mkdir -p "$BUILD_DIR"

# Runtime deps only (no dev extras), resolved for the Lambda platform.
pip install \
  --quiet \
  --platform "$PLATFORM" \
  --python-version "$PYTHON_VERSION" \
  --implementation cp \
  --only-binary=:all: \
  --target "$BUILD_DIR" \
  .

# The `pip install .` above also copies the app package; strip what Lambda never needs.
find "$BUILD_DIR" -type d -name "__pycache__" -prune -exec rm -rf {} +
find "$BUILD_DIR" -type d -name "*.dist-info" -prune -exec rm -rf {} +
rm -rf "$BUILD_DIR"/bin

(cd "$BUILD_DIR" && zip -qr "../../$OUT" .)
echo "built $OUT ($(du -h "$OUT" | cut -f1))"
