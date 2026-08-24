#!/usr/bin/env bash
# =========================================================================
# NSosyal Pusula - Demo / Lightweight Mode Runner (POSIX / Linux / macOS)
# Runs FastAPI backend in deterministic Demo mode (no transformer model downloads)
# =========================================================================

set -e
echo "[NSosyal Pusula] Starting in DEMO mode (Lightweight / CPU)..."

export SEMANTIC_MODE="demo"
export PYTHONPATH="$(pwd)/backend:$(pwd):${PYTHONPATH:-}"

python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
