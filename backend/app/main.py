import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.adapters.json_adapter import JsonDemoAdapter
from app.services.safety_service import SafetyService
from app.services.context_service import ContextService
from app.services.recommendation_service import RecommendationService
from app.services.search_service import SearchService
from app.ml.model_manager import ModelManager
from app.api import health_router, api_v1_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("nsosyal_pusula")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle initialization."""
    logger.info(f"Initializing {settings.APP_NAME} v{settings.APP_VERSION} (SEMANTIC_MODE='{settings.SEMANTIC_MODE}')...")

    # 1. Initialize data source adapter
    if settings.DATA_SOURCE_TYPE == "json":
        data_adapter = JsonDemoAdapter(data_path=settings.DEMO_DATA_PATH)
    else:
        logger.warning(
            f"Unknown DATA_SOURCE_TYPE '{settings.DATA_SOURCE_TYPE}', falling back to JsonDemoAdapter."
        )
        data_adapter = JsonDemoAdapter(data_path=settings.DEMO_DATA_PATH)

    # 2. Initialize ML Model Manager (Single load on GPU / CPU)
    model_manager = ModelManager.get_instance()
    model_manager.initialize()

    # 3. Initialize domain services with injected model manager
    safety_service = SafetyService(fusion_service=model_manager.moderation_service)
    context_service = ContextService(data_adapter=data_adapter, model_manager=model_manager)
    recommendation_service = RecommendationService(
        data_adapter=data_adapter, safety_service=safety_service, model_manager=model_manager
    )
    search_service = SearchService(data_adapter=data_adapter, model_manager=model_manager)

    # Attach to application state
    app.state.data_adapter = data_adapter
    app.state.model_manager = model_manager
    app.state.safety_service = safety_service
    app.state.context_service = context_service
    app.state.recommendation_service = recommendation_service
    app.state.search_service = search_service

    logger.info(
        f"NSosyal Pusula Backend ready. Loaded {len(data_adapter.get_posts())} posts. ML Status: {model_manager.mode} on {model_manager.device}."
    )
    yield
    logger.info("Shutting down NSosyal Pusula Backend...")


def create_app() -> FastAPI:
    """FastAPI Application Factory."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "NSosyal Pusula - Yapay Zekâ Destekli Bağlam ve Şeffaf Öneri Sistemi REST API. "
            "(TEKNOFEST 2026 - Faz 2B Üretim Semantik Mimarisi)"
        ),
        lifespan=lifespan,
    )

    # Add CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include Routers
    app.include_router(health_router)
    app.include_router(api_v1_router)

    return app


app = create_app()
