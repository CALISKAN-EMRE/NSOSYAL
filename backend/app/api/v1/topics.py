from typing import List
from fastapi import APIRouter, HTTPException, Request
from app.models.topic import Topic

router = APIRouter(prefix="/topics", tags=["Topics"])


@router.get("", response_model=List[Topic])
def list_topics(request: Request):
    adapter = request.app.state.data_adapter
    return adapter.get_topics()


@router.get("/{topic_id}", response_model=Topic)
def get_topic(request: Request, topic_id: str):
    adapter = request.app.state.data_adapter
    topic = adapter.get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic
