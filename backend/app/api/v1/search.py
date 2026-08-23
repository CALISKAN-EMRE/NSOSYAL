from fastapi import APIRouter, Query, Request
from app.services.search_service import SearchResponse

router = APIRouter(tags=["Semantic Search"])


@router.get("/search", response_model=SearchResponse)
async def semantic_search(
    request: Request,
    q: str = Query(..., description="Natural language Turkish search query"),
    limit: int = Query(20, ge=1, le=100, description="Max results to return"),
):
    """Perform instruction-guided natural-language semantic search across posts."""
    search_service = getattr(request.app.state, "search_service", None)
    if not search_service:
        # Lazy fallback
        from app.services.search_service import SearchService
        search_service = SearchService(data_adapter=request.app.state.data_adapter)

    return search_service.search(query=q, limit=limit)
