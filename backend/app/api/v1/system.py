from typing import Any, Dict
from fastapi import APIRouter, Request
from app.ml.model_manager import ModelManager

router = APIRouter(prefix="/system", tags=["System & ML Status"])


@router.get("/status", response_model=Dict[str, Any])
async def get_system_status(request: Request):
    """Expose ML model readiness, active device, and runtime mode for frontend observability."""
    model_mgr = getattr(request.app.state, "model_manager", None) or ModelManager.get_instance()
    status = model_mgr.get_status()
    return {
        "app_name": "NSosyal Pusula",
        "version": "0.2.0 (Phase 2B Production Semantic ML)",
        "model_manager": status,
        "pipelines": {
            "clustering": "ytu-ce-cosmos/modernbert-tr-embed + HDBSCAN",
            "context_retrieval": "ytu-ce-cosmos/modernbert-tr-embed (Dense)",
            "context_reranking": "ytu-ce-cosmos/modernbert-tr-reranker (Cross-Encoder)",
            "semantic_search": "intfloat/multilingual-e5-large-instruct (Instruct-tuned)",
            "recommendation_affinity": "ModernBERT Cosine Similarity",
            "moderation": "Multi-signal Heuristic Safety Analyzer",
        },
    }
