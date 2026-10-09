#!/usr/bin/env sh
# GreenScan on macOS/Linux: first run installs, then serves http://localhost:8000.
# Needs Python 3.11+ and, once, Node.js 20+ to build the web UI.
set -e
cd "$(dirname "$0")"

if [ ! -x .venv/bin/python ]; then
  echo "[1/3] Creating the Python environment (first run only)..."
  python3 -m venv .venv
  .venv/bin/python -m pip install --upgrade pip
  .venv/bin/python -m pip install -e .
fi

if [ ! -f frontend/dist/index.html ]; then
  echo "[2/3] Building the web UI (first run only)..."
  (cd frontend && npm ci && npm run build)
fi

[ -f .env ] || { [ -f .env.example ] && cp .env.example .env; }

echo "[3/3] Starting GreenScan at http://localhost:8000 ..."
exec .venv/bin/python -m quantum_gw.cli app
