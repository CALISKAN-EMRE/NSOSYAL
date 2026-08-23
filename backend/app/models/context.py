from typing import Dict, List, Optional
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
    relevance_score: Optional[float] = Field(
        default=None, description="Cross-encoder reranked semantic relevance score in [0, 1]"
    )
    dense_score: Optional[float] = Field(
        default=None, description="Initial dense retrieval similarity score"
    )
    rank: Optional[int] = Field(default=None, description="Reranked position (1, 2, ...)")


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
        default="semantic_clustering_and_reranking",
        description="Method used for generation: semantic_clustering_and_reranking or deterministic_aggregation",
    )
    semantic_cluster_id: Optional[str] = None
    cluster_confidence: Optional[float] = None
    pipeline_timing_ms: Optional[Dict[str, float]] = Field(
        default=None, description="Internal pipeline execution timing breakdown in ms"
    )
    model_used: Optional[str] = None
