import hashlib
from typing import Any, Dict, List
import numpy as np
from ml.embeddings.base import EmbeddingProvider


class DeterministicMockEmbeddingProvider(EmbeddingProvider):
    """Deterministic, reproducible mock embedding provider for tests and benchmark baseline."""

    def __init__(self, dimension: int = 384, model_name: str = "deterministic-baseline-384d"):
        self.dimension = dimension
        self.model_name = model_name

    def _hash_to_vector(self, text: str) -> np.ndarray:
        # Generate pseudo-semantic vector from token n-grams and character hashes
        vec = np.zeros(self.dimension, dtype=np.float32)
        words = text.lower().split()
        for i, word in enumerate(words):
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            for d in range(self.dimension):
                slot = (h + d * 31) % self.dimension
                val = ((h >> (d % 24)) & 0xFF) / 128.0 - 1.0
                vec[slot] += val / (1.0 + i * 0.1)

        norm = np.linalg.norm(vec)
        return vec / (norm + 1e-12) if norm > 0 else vec

    def encode_documents(self, texts: List[str], batch_size: int = 16) -> np.ndarray:
        return np.vstack([self._hash_to_vector(t) for t in texts])

    def encode_queries(self, queries: List[str], batch_size: int = 16) -> np.ndarray:
        return np.vstack([self._hash_to_vector(q) for q in queries])

    def model_metadata(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_name,
            "parameter_count": "0M (Synthetic Deterministic Baseline)",
            "embedding_dimension": self.dimension,
            "device": "cpu",
            "dtype": "float32",
            "backend": "synthetic_baseline",
        }

    def embedding_dimension(self) -> int:
        return self.dimension
