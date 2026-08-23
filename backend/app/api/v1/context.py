from fastapi import APIRouter, HTTPException, Request
from app.models.context import ContextCard

router = APIRouter(prefix="/context", tags=["Context Cards"])


@router.get("/{topic_id}", response_model=ContextCard)
def get_topic_context(request: Request, topic_id: str):
    context_service = request.app.state.context_service
    card = context_service.get_context_card(topic_id)
    if not card:
        raise HTTPException(
            status_code=404,
            detail=f"Context card for topic '{topic_id}' could not be synthesized or found.",
        )
    return card
