from typing import List
from fastapi import APIRouter, HTTPException, Request
from app.models.topic import Topic

router = APIRouter(prefix="/topics", tags=["Topics"])


@router.get("", response_model=List[Topic])
def list_topics(request: Request):
    """List topics discovered via semantic clustering (or adapter fallback)."""
    context_service = getattr(request.app.state, "context_service", None)
    if context_service:
        semantic_topics = context_service.get_semantic_topics()
        if semantic_topics:
            return semantic_topics

    adapter = request.app.state.data_adapter
    return adapter.get_topics()


@router.get("/{topic_id}", response_model=Topic)
def get_topic(request: Request, topic_id: str):
    """Get single topic details."""
    context_service = getattr(request.app.state, "context_service", None)
    if context_service:
        for t in context_service.get_semantic_topics():
            if t.id == topic_id:
                return t

    adapter = request.app.state.data_adapter
    topic = adapter.get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic
