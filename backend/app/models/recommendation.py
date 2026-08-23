from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.post import Post


class ScoreFactor(BaseModel):
    factor_name: str
    label: str
    weight: float = Field(..., description="Configured weight for this factor")
    raw_score: float = Field(..., ge=0.0, le=1.0, description="Normalized score 0.0-1.0")
    weighted_impact: float = Field(
        ..., description="Signed weighted impact on the final score"
    )
    is_penalty: bool = False
    explanation: str


class RecommendationExplanation(BaseModel):
    post_id: str
    final_score: float = Field(..., ge=0.0, le=100.0)
    summary_reason: str
    factors: List[ScoreFactor] = Field(default_factory=list)


class RecommendedPost(BaseModel):
    post: Post
    explanation: RecommendationExplanation
