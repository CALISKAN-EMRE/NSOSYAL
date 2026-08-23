from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Request
from app.models.recommendation import (
    RecommendationExplanation,
    RecommendedPost,
)

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("", response_model=List[RecommendedPost])
def get_recommendations(
    request: Request,
    preferred_topic: Optional[str] = Query(None, description="Preferred topic ID"),
    interests: Optional[str] = Query(
        None, description="Comma-separated interest keywords/tags"
    ),
    limit: int = Query(20, ge=1, le=50),
):
    recommendation_service = request.app.state.recommendation_service
    user_interests = [i.strip() for i in interests.split(",")] if interests else None
    return recommendation_service.get_recommendations(
        user_interests=user_interests,
        preferred_topic_id=preferred_topic,
        limit=limit,
    )


@router.get("/explain/{post_id}", response_model=RecommendationExplanation)
def explain_post(
    request: Request,
    post_id: str,
    interests: Optional[str] = Query(None),
):
    adapter = request.app.state.data_adapter
    recommendation_service = request.app.state.recommendation_service
    post = adapter.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    user_interests = [i.strip() for i in interests.split(",")] if interests else [
        "YapayZeka",
        "Yazılım",
        "Bilim",
        "Eğitim",
    ]
    all_posts = adapter.get_posts(limit=100)
    return recommendation_service.explain_post_recommendation(
        post=post, user_interests=user_interests, all_posts=all_posts
    )
