@echo off
REM =========================================================================
REM NSosyal Pusula - Demo / Lightweight Mode Runner (Windows)
REM Runs FastAPI backend in deterministic Demo mode (no transformer model downloads)
REM =========================================================================

echo [NSosyal Pusula] Starting in DEMO mode (Lightweight / CPU)...
set SEMANTIC_MODE=demo
set PYTHONPATH=%CD%\backend;%CD%

python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
