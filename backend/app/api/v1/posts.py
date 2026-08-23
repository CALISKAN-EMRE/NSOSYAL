from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Request
from app.models.post import Post

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("", response_model=List[Post])
def list_posts(
    request: Request,
    topic_id: Optional[str] = Query(None, description="Filter by topic ID"),
    search: Optional[str] = Query(None, description="Keyword search query"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    adapter = request.app.state.data_adapter
    raw_posts = adapter.get_posts(topic_id=topic_id, limit=limit, offset=offset, search=search)
    context_service = getattr(request.app.state, "context_service", None)
    if context_service:
        return context_service.assign_clusters_to_posts(raw_posts)
    return raw_posts


@router.get("/{post_id}", response_model=Post)
def get_post(request: Request, post_id: str):
    adapter = request.app.state.data_adapter
    post = adapter.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    context_service = getattr(request.app.state, "context_service", None)
    if context_service:
        return context_service.assign_clusters_to_posts([post])[0]
    return post
