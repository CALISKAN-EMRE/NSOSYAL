from typing import Any, Dict, List, Optional
import numpy as np

from app.ml.base import BaseEmbeddingService, BaseSimilarityService


class SemanticSimilarityService(BaseSimilarityService):
    """Computes semantic similarity for transparent recommendation affinity using embeddings."""

    def __init__(self, embedding_service: BaseEmbeddingService):
        self.embedding_service = embedding_service
        self._user_profile_cache: Dict[str, np.ndarray] = {}

    def compute_similarity(self, text_a: str, text_b: str) -> float:
        embs = self.embedding_service.encode_documents([text_a, text_b])
        if len(embs) < 2:
            return 0.5
        v_a, v_b = embs[0], embs[1]
        sim = float(np.dot(v_a, v_b) / (np.linalg.norm(v_a) * np.linalg.norm(v_b) + 1e-12))
        return max(0.0, min(1.0, (sim + 1.0) / 2.0))

    def compute_profile_similarity(
        self, user_interests: List[str], post_text: str, post_tags: Optional[List[str]] = None
    ) -> float:
        """Compute semantic match score between a user's interest profile and a post."""
        if not user_interests:
            return 0.5

        # Format user interest profile into a representative semantic query
        profile_key = "|".join(sorted(user_interests))
        if profile_key in self._user_profile_cache:
            profile_vec = self._user_profile_cache[profile_key]
        else:
            profile_text = f"İlgi alanları: {', '.join(user_interests)}. Bilimsel, teknolojik ve güncel gelişmeler."
            profile_vec = self.embedding_service.encode_queries([profile_text])[0]
            self._user_profile_cache[profile_key] = profile_vec

        # Post representation (combining tags + text)
        tag_str = f" Etiketler: {', '.join(post_tags)}." if post_tags else ""
        content_to_encode = post_text[:300] + tag_str

        post_vec = self.embedding_service.encode_documents([content_to_encode])[0]

        # Cosine similarity
        cos_sim = float(
            np.dot(profile_vec, post_vec)
            / (np.linalg.norm(profile_vec) * np.linalg.norm(post_vec) + 1e-12)
        )

        # Scale cosine similarity [-1, 1] to [0, 1] score
        score = max(0.0, min(1.0, (cos_sim + 0.3) / 1.3))
        return round(score, 3)
