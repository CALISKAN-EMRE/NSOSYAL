from typing import List, Optional
from pydantic import BaseModel, Field


class Author(BaseModel):
    id: str
    name: str
    handle: str
    avatar: Optional[str] = None
    badge: Optional[str] = None


class PostMetrics(BaseModel):
    likes: int = 0
    reposts: int = 0
    replies: int = 0


class Post(BaseModel):
    id: str
    author: Author
    text: str
    created_at: str
    topic_id: str
    topic_title: str
    source_type: str = Field(
        default="user",
        description="Source category: user, expert, academic, news_outlet, official_source, community",
    )
    perspective: Optional[str] = Field(
        default="neutral_fact",
        description="Perspective category: supportive, supportive_cautious, critical, neutral_fact",
    )
    tags: List[str] = Field(default_factory=list)
    metrics: PostMetrics = Field(default_factory=PostMetrics)
    safety_risk_level: Optional[str] = Field(
        default="LOW", description="Pre-computed or cached risk level: LOW, MEDIUM, HIGH"
    )
    semantic_cluster_id: Optional[str] = Field(
        default=None, description="Discovered HDBSCAN semantic cluster identifier"
    )
    cluster_membership_prob: Optional[float] = Field(
        default=None, description="HDBSCAN cluster membership probability in [0, 1]"
    )
