#!/usr/bin/env bash
# =========================================================================
# NSosyal Pusula - Production Semantic ML Mode Runner (POSIX / Linux / macOS)
# Runs FastAPI backend with local transformer models on GPU/CPU
# =========================================================================

set -e
echo "[NSosyal Pusula] Starting in Full ML mode (Production Turkish Transformers)..."

export SEMANTIC_MODE="ml"
export PYTHONPATH="$(pwd)/backend:$(pwd):${PYTHONPATH:-}"

python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
