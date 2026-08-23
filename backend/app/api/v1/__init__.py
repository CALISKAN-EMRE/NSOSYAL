from fastapi import APIRouter
from app.api.v1.posts import router as posts_router
from app.api.v1.topics import router as topics_router
from app.api.v1.context import router as context_router
from app.api.v1.safety import router as safety_router
from app.api.v1.recommendations import router as recommendations_router
from app.api.v1.search import router as search_router
from app.api.v1.system import router as system_router

api_v1_router = APIRouter(prefix="/api")
api_v1_router.include_router(posts_router)
api_v1_router.include_router(topics_router)
api_v1_router.include_router(context_router)
api_v1_router.include_router(safety_router)
api_v1_router.include_router(recommendations_router)
api_v1_router.include_router(search_router)
api_v1_router.include_router(system_router)

__all__ = ["api_v1_router"]
