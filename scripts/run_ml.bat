@echo off
REM =========================================================================
REM NSosyal Pusula - Production Semantic ML Mode Runner (Windows)
REM Runs FastAPI backend with local transformer models on GPU/CPU
REM =========================================================================

echo [NSosyal Pusula] Starting in Full ML mode (Production Turkish Transformers)...
set SEMANTIC_MODE=ml
set PYTHONPATH=%CD%\backend;%CD%

python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
