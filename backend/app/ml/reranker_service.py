from typing import Any, Dict, List, Optional
import numpy as np

from app.ml.base import BaseRerankerService, RerankCandidate


class ModernBERTRerankerService(BaseRerankerService):
    """Production Cross-Encoder reranker using ytu-ce-cosmos/modernbert-tr-reranker."""

    def __init__(
        self,
        model_id: str = "ytu-ce-cosmos/modernbert-tr-reranker",
        device: Optional[str] = None,
    ):
        self.model_id = model_id
        self.device = device
        self._model = None
        self._init_model()

    def _init_model(self):
        import torch
        from sentence_transformers import CrossEncoder

        if self.device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self._model = CrossEncoder(self.model_id, device=self.device)

    def rerank(
        self, query: str, candidates: List[RerankCandidate], top_k: int = 15
    ) -> List[RerankCandidate]:
        """Rerank candidate items using ModernBERT Cross-Encoder."""
        if not candidates:
            return []

        # Select top-k for reranking
        selected_candidates = candidates[:top_k]
        pairs = [(query, c.text) for c in selected_candidates]

        # Predict cross-encoder relevance scores
        scores = self._model.predict(pairs, show_progress_bar=False)

        # Convert logits/probabilities to normalized float scores
        for idx, cand in enumerate(selected_candidates):
            raw_s = float(scores[idx])
            # Sigmoid normalization if scores are logits
            norm_s = 1.0 / (1.0 + np.exp(-raw_s)) if abs(raw_s) > 1.0 else max(0.0, min(1.0, raw_s))
            cand.reranked_score = round(norm_s, 4)

        # Sort selected candidates by reranked score descending
        reranked_sorted = sorted(
            selected_candidates,
            key=lambda c: c.reranked_score if c.reranked_score is not None else -1.0,
            reverse=True,
        )

        # Re-assign ranks
        for r_idx, cand in enumerate(reranked_sorted, 1):
            cand.rank = r_idx

        # Append remaining un-reranked candidates if any
        remaining = candidates[top_k:]
        for r_idx, cand in enumerate(remaining, len(reranked_sorted) + 1):
            cand.rank = r_idx
            cand.reranked_score = cand.initial_dense_score

        return reranked_sorted + remaining


class DemoRerankerService(BaseRerankerService):
    """Deterministic lexical reranker for demo mode and unit testing."""

    def rerank(
        self, query: str, candidates: List[RerankCandidate], top_k: int = 15
    ) -> List[RerankCandidate]:
        if not candidates:
            return []

        q_words = set(query.lower().split())
        selected = candidates[:top_k]

        for cand in selected:
            c_words = set(cand.text.lower().split())
            overlap = len(q_words & c_words) / max(1, len(q_words | c_words))
            cand.reranked_score = round(min(1.0, cand.initial_dense_score * 0.5 + overlap * 0.5), 4)

        sorted_cands = sorted(
            selected,
            key=lambda c: c.reranked_score if c.reranked_score is not None else 0.0,
            reverse=True,
        )

        for rank, cand in enumerate(sorted_cands, 1):
            cand.rank = rank

        return sorted_cands + candidates[top_k:]
