from typing import List, Optional
from pydantic import BaseModel, Field


class PerspectiveDetail(BaseModel):
    perspective_type: str = Field(
        ..., description="e.g. supportive, critical, neutral_fact"
    )
    label: str = Field(..., description="Human readable label in Turkish")
    summary: str = Field(..., description="Core argument summary")
    post_count: int = 0
    supporting_post_ids: List[str] = Field(default_factory=list)
    sample_quotes: List[str] = Field(default_factory=list)


class TimelineItem(BaseModel):
    timestamp: str
    title: str
    summary: str
    related_post_id: Optional[str] = None


class SourceContext(BaseModel):
    source_name: str
    source_type: str
    mention_count: int = 1
    reliability_note: Optional[str] = None


class ContextCard(BaseModel):
    id: str
    topic_id: str
    topic_title: str
    summary: str
    key_themes: List[str] = Field(default_factory=list)
    perspectives: List[PerspectiveDetail] = Field(default_factory=list)
    timeline: List[TimelineItem] = Field(default_factory=list)
    sources: List[SourceContext] = Field(default_factory=list)
    total_posts: int = 0
    total_participants: int = 0
    generated_at: str
    method: str = Field(
        default="deterministic_aggregation",
        description="Method used for generation: deterministic_aggregation or ai_synthesis",
    )
