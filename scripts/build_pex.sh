#!/usr/bin/env bash
set -euo pipefail

# Build a Linux x86_64 CPython 3.8 PEX from this project without installing anything system-wide.
# Usage:
#   ./scripts/build_pex.sh
# Output:
#   dist/bot.pex

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="$PROJECT_ROOT/dist"
mkdir -p "$OUT_DIR"

echo "[build] Using Python: $(python --version 2>&1 || true)"

pip install --upgrade pip
pip install pex -r "$PROJECT_ROOT/requirements.txt"

pex \
  -r "$PROJECT_ROOT/requirements.txt" \
  -D "$PROJECT_ROOT" \
  -m bot.main:main \
  -o "$OUT_DIR/bot.pex" \
  --python=python3.8 \
  --platform manylinux2014_x86_64-cp38-cp38 \
  --strip-pex-env

echo "[build] Wrote $OUT_DIR/bot.pex"


