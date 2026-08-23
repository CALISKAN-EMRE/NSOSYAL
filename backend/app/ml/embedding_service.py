import hashlib
from typing import Any, Dict, List, Optional
import numpy as np

from app.ml.base import BaseEmbeddingService


class ModernBERTEmbeddingService(BaseEmbeddingService):
    """Production embedding service using ytu-ce-cosmos/modernbert-tr-embed."""

    def __init__(self, model_id: str = "ytu-ce-cosmos/modernbert-tr-embed", device: Optional[str] = None):
        self.model_id = model_id
        self.device = device
        self._dim = 768
        self._model = None
        self._init_model()

    def _init_model(self):
        import torch
        from sentence_transformers import SentenceTransformer

        if self.device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self._model = SentenceTransformer(self.model_id, device=self.device)
        try:
            self._dim = self._model.get_embedding_dimension()
        except AttributeError:
            self._dim = self._model.get_sentence_embedding_dimension()

    def encode_documents(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, self._dim), dtype=np.float32)
        embeddings = self._model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return np.asarray(embeddings, dtype=np.float32)

    def encode_queries(self, queries: List[str]) -> np.ndarray:
        return self.encode_documents(queries)

    def dimension(self) -> int:
        return self._dim

    def model_metadata(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "architecture": "ModernBERT TR Embed",
            "dimension": self._dim,
            "device": self.device,
            "max_context_length": 8192,
            "provider": "sentence_transformers",
        }


class MultilingualE5EmbeddingService(BaseEmbeddingService):
    """Production embedding service using intfloat/multilingual-e5-large-instruct with task instructions."""

    DEFAULT_INSTRUCTION = (
        "Given a Turkish search query, retrieve relevant passages written in Turkish that best answer the query"
    )

    def __init__(
        self,
        model_id: str = "intfloat/multilingual-e5-large-instruct",
        device: Optional[str] = None,
        task_instruction: Optional[str] = None,
    ):
        self.model_id = model_id
        self.device = device
        self.task_instruction = task_instruction or self.DEFAULT_INSTRUCTION
        self._dim = 1024
        self._model = None
        self._init_model()

    def _init_model(self):
        import torch
        from sentence_transformers import SentenceTransformer

        if self.device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self._model = SentenceTransformer(self.model_id, device=self.device)
        try:
            self._dim = self._model.get_embedding_dimension()
        except AttributeError:
            self._dim = self._model.get_sentence_embedding_dimension()

    def encode_documents(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, self._dim), dtype=np.float32)
        # E5 documents don't require task prefix if using sentence-transformers, but we keep standard encoding
        embeddings = self._model.encode(
            texts,
            batch_size=16,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return np.asarray(embeddings, dtype=np.float32)

    def encode_queries(self, queries: List[str]) -> np.ndarray:
        if not queries:
            return np.empty((0, self._dim), dtype=np.float32)
        # Format with instruction
        formatted = [f"Instruct: {self.task_instruction}\nQuery: {q}" for q in queries]
        embeddings = self._model.encode(
            formatted,
            batch_size=16,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return np.asarray(embeddings, dtype=np.float32)

    def dimension(self) -> int:
        return self._dim

    def model_metadata(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "architecture": "Multilingual-E5-Large-Instruct",
            "dimension": self._dim,
            "device": self.device,
            "max_context_length": 512,
            "provider": "sentence_transformers",
        }


class DemoEmbeddingService(BaseEmbeddingService):
    """Deterministic, lightweight embedding service for demo mode and unit testing."""

    def __init__(self, dimension: int = 384, model_name: str = "demo-deterministic-baseline"):
        self._dim = dimension
        self.model_name = model_name

    def _hash_to_vector(self, text: str) -> np.ndarray:
        vec = np.zeros(self._dim, dtype=np.float32)
        words = text.lower().split()
        for i, word in enumerate(words):
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            for d in range(self._dim):
                slot = (h + d * 31) % self._dim
                val = ((h >> (d % 24)) & 0xFF) / 128.0 - 1.0
                vec[slot] += val / (1.0 + i * 0.1)

        norm = np.linalg.norm(vec)
        return vec / (norm + 1e-12) if norm > 0 else vec

    def encode_documents(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, self._dim), dtype=np.float32)
        return np.vstack([self._hash_to_vector(t) for t in texts])

    def encode_queries(self, queries: List[str]) -> np.ndarray:
        return self.encode_documents(queries)

    def dimension(self) -> int:
        return self._dim

    def model_metadata(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_name,
            "architecture": "Deterministic Word-Hash Mock",
            "dimension": self._dim,
            "device": "cpu",
            "provider": "demo_baseline",
        }
