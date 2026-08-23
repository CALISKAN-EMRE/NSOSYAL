from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from pydantic import BaseModel, Field


class SemanticCluster(BaseModel):
    """Represents a discovered semantic cluster of social media posts."""

    cluster_id: str
    label: str
    post_ids: List[str]
    confidence_score: float = 1.0
    key_themes: List[str] = Field(default_factory=list)
    representative_post_ids: List[str] = Field(default_factory=list)
    is_noise: bool = False


class RerankCandidate(BaseModel):
    """Represents a context source candidate with relevance scoring."""

    doc_id: str
    source_name: str
    source_type: str
    text: str
    initial_dense_score: float
    reranked_score: Optional[float] = None
    rank: int = 1
    reliability_note: Optional[str] = None


class BaseEmbeddingService(ABC):
    """Abstract interface for text embedding providers."""

    @abstractmethod
    def encode_documents(self, texts: List[str]) -> np.ndarray:
        """Encode a list of document strings into normalized vectors."""
        pass

    @abstractmethod
    def encode_queries(self, queries: List[str]) -> np.ndarray:
        """Encode a list of query strings (with instructions if applicable)."""
        pass

    @abstractmethod
    def dimension(self) -> int:
        """Return the embedding vector dimension."""
        pass

    @abstractmethod
    def model_metadata(self) -> Dict[str, Any]:
        """Return metadata about the embedding model."""
        pass


class BaseClusterService(ABC):
    """Abstract interface for semantic post clustering."""

    @abstractmethod
    def cluster_posts(self, posts: List[Any]) -> List[SemanticCluster]:
        """Cluster a collection of posts into semantic groups."""
        pass


class BaseRerankerService(ABC):
    """Abstract interface for cross-encoder reranking."""

    @abstractmethod
    def rerank(
        self, query: str, candidates: List[RerankCandidate], top_k: int = 15
    ) -> List[RerankCandidate]:
        """Rerank candidate items using a cross-encoder."""
        pass


class BaseSimilarityService(ABC):
    """Abstract interface for semantic similarity calculation in recommendation scoring."""

    @abstractmethod
    def compute_similarity(self, text_a: str, text_b: str) -> float:
        """Compute cosine similarity between two texts in [0.0, 1.0]."""
        pass

    @abstractmethod
    def compute_profile_similarity(
        self, user_interests: List[str], post_text: str, post_tags: Optional[List[str]] = None
    ) -> float:
        """Compute semantic match score between a user's interest profile and a post."""
        pass
