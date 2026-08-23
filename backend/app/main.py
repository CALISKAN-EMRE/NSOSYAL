import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.adapters.json_adapter import JsonDemoAdapter
from app.services.safety_service import SafetyService
from app.services.context_service import ContextService
from app.services.recommendation_service import RecommendationService
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
    logger.info("Initializing NSosyal Pusula Data Adapter and Intelligence Services...")

    # Initialize data source adapter based on configuration
    if settings.DATA_SOURCE_TYPE == "json":
        data_adapter = JsonDemoAdapter(data_path=settings.DEMO_DATA_PATH)
    else:
        # Fallback to demo JSON adapter if unknown
        logger.warning(
            f"Unknown DATA_SOURCE_TYPE '{settings.DATA_SOURCE_TYPE}', falling back to JsonDemoAdapter."
        )
        data_adapter = JsonDemoAdapter(data_path=settings.DEMO_DATA_PATH)

    # Initialize domain services
    safety_service = SafetyService()
    context_service = ContextService(data_adapter=data_adapter)
    recommendation_service = RecommendationService(
        data_adapter=data_adapter, safety_service=safety_service
    )

    # Attach to application state
    app.state.data_adapter = data_adapter
    app.state.safety_service = safety_service
    app.state.context_service = context_service
    app.state.recommendation_service = recommendation_service

    logger.info(
        f"NSosyal Pusula Backend ready. Loaded {len(data_adapter.get_posts())} demo posts."
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
            "(TEKNOFEST 2026 Prototipi - Faz 1)"
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
