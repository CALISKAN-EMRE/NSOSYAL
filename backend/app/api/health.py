from fastapi import APIRouter, Request
from app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
def get_health(request: Request):
    adapter = getattr(request.app.state, "data_adapter", None)
    adapter_health = adapter.health_check() if adapter else {"status": "uninitialized"}

    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "data_source_adapter": adapter_health,
        "ai_pipeline_status": {
            "context_engine": "metadata_heuristic_aggregation (Phase 1 Prototype)",
            "safety_engine": "deterministic_rule_engine (Phase 1 Prototype)",
            "recommendation_engine": "explainable_linear_scoring (Phase 1 Prototype)",
        },
        "disclaimer": "This is a TEKNOFEST 2026 Phase 1 prototype using synthetic demo data. It does not claim direct NSosyal production API access.",
    }
