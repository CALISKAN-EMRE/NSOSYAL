import time
from typing import Any, Dict, List, Optional
import numpy as np
from pydantic import BaseModel, Field

from app.adapters.base import DataSourceAdapter
from app.models.post import Post
from app.ml.model_manager import ModelManager


class SearchResultItem(BaseModel):
    post: Post
    relevance_score: float = Field(..., description="Cosine similarity score in [0.0, 1.0]")
    rank: int = Field(..., description="Rank in search result list")
    matched_highlights: List[str] = Field(default_factory=list)


class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResultItem]
    model_used: str
    search_latency_ms: float


class SearchService:
    """Natural Language Semantic Search Service using Multilingual-E5-Large-Instruct."""

    def __init__(self, data_adapter: DataSourceAdapter, model_manager: Optional[ModelManager] = None):
        self.adapter = data_adapter
        self.model_manager = model_manager or ModelManager.get_instance()

    def search(self, query: str, limit: int = 20) -> SearchResponse:
        """Perform instruction-guided semantic dense search across posts."""
        t_start = time.perf_counter()

        if not query or not query.strip():
            return SearchResponse(
                query="",
                total_results=0,
                results=[],
                model_used="none",
                search_latency_ms=0.0,
            )

        self.model_manager.initialize()
        all_posts = self.adapter.get_posts(limit=200)

        if not all_posts:
            return SearchResponse(
                query=query,
                total_results=0,
                results=[],
                model_used="none",
                search_latency_ms=0.0,
            )

        embedder = self.model_manager.search_embedder
        post_texts = [p.text for p in all_posts]

        if embedder:
            # 1. Encode query with task instruction and documents with embedder
            query_vec = embedder.encode_queries([query.strip()])[0]
            doc_vecs = embedder.encode_documents(post_texts)

            # 2. Compute cosine similarity
            sims = np.dot(doc_vecs, query_vec) / (
                np.linalg.norm(doc_vecs, axis=1) * np.linalg.norm(query_vec) + 1e-12
            )

            # Map to [0, 1] scale
            norm_scores = [(float(s) + 1.0) / 2.0 for s in sims]
        else:
            # Lexical fallback
            q_words = set(query.lower().split())
            norm_scores = []
            for t in post_texts:
                t_words = set(t.lower().split())
                overlap = len(q_words & t_words) / max(1, len(q_words | t_words))
                norm_scores.append(overlap)

        # Pair scores with posts
        paired = []
        for idx, post in enumerate(all_posts):
            score = round(norm_scores[idx], 4)
            if score >= 0.35 or not embedder:  # Filter low relevance
                paired.append((post, score))

        # Sort by relevance score descending
        paired.sort(key=lambda x: x[1], reverse=True)
        top_results = paired[:limit]

        result_items = []
        for rank, (post, score) in enumerate(top_results, 1):
            result_items.append(
                SearchResultItem(
                    post=post,
                    relevance_score=score,
                    rank=rank,
                    matched_highlights=[post.text[:120] + "..."],
                )
            )

        latency_ms = round((time.perf_counter() - t_start) * 1000.0, 2)
        model_name = (
            embedder.model_metadata()["model_id"]
            if embedder
            else "demo_lexical_search"
        )

        return SearchResponse(
            query=query,
            total_results=len(result_items),
            results=result_items,
            model_used=model_name,
            search_latency_ms=latency_ms,
        )
