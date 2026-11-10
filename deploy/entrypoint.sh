#!/bin/sh
# GreenScan container start (2026-11-09).
# QUANTUM_HOME is where runs, uploaded documents and review decisions live
# (default /app/.quantum; point it at a persistent disk such as /data to keep
# them across restarts). The API installs the seeded demo runs from deploy/seed/
# on start (src/quantum_gw/storage/seed.py; nothing already in the store is
# overwritten), then serves the API and the web UI on $PORT. Hugging Face
# Spaces, Render and most hosts set PORT; the default is 8000.
set -e
HOME_DIR="${QUANTUM_HOME:-/app/.quantum}"
export QUANTUM_RUNS_DIR="${QUANTUM_RUNS_DIR:-$HOME_DIR/runs}"
export QUANTUM_DOCUMENTS_DIR="${QUANTUM_DOCUMENTS_DIR:-$HOME_DIR/documents}"
export QUANTUM_REVIEWS_FILE="${QUANTUM_REVIEWS_FILE:-$HOME_DIR/reviews/decisions.jsonl}"
mkdir -p "$QUANTUM_RUNS_DIR" "$QUANTUM_DOCUMENTS_DIR" "$(dirname "$QUANTUM_REVIEWS_FILE")"
exec uvicorn quantum_gw.api:app --host 0.0.0.0 --port "${PORT:-8000}" --workers 1
