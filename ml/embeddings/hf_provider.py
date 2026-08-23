import time
from typing import Any, Dict, List, Optional
import numpy as np
from ml.embeddings.base import EmbeddingProvider


class HuggingFaceEmbeddingProvider(EmbeddingProvider):
    """Hugging Face / SentenceTransformers embedding provider with instruction support."""

    def __init__(
        self,
        model_id: str,
        device: Optional[str] = None,
        instruction_type: Optional[str] = None,
        query_instruction: Optional[str] = None,
        passage_instruction: Optional[str] = None,
    ):
        self.model_id = model_id
        self.instruction_type = instruction_type or "auto"
        self.query_instruction = query_instruction
        self.passage_instruction = passage_instruction

        self._model = None
        self._tokenizer = None
        self._device = device
        self._dim: Optional[int] = None
        self._metadata: Dict[str, Any] = {}

        self._init_model()

    def _init_model(self) -> None:
        """Initialize model using sentence-transformers or transformers."""
        import torch

        if self._device is None:
            self._device = "cuda" if torch.cuda.is_available() else "cpu"

        # Check sentence_transformers first
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_id, device=self._device)
            self._dim = self._model.get_sentence_embedding_dimension()
            self._dtype = str(next(self._model.parameters()).dtype)
            self._backend = "sentence_transformers"
        except Exception:
            # Fallback to direct HuggingFace transformers
            from transformers import AutoModel, AutoTokenizer

            self._tokenizer = AutoTokenizer.from_pretrained(self.model_id)
            self._model = AutoModel.from_pretrained(self.model_id)
            self._model.to(self._device)
            self._model.eval()
            self._dim = self._model.config.hidden_size
            self._dtype = str(next(self._model.parameters()).dtype)
            self._backend = "transformers"

    def encode_documents(self, texts: List[str], batch_size: int = 16) -> np.ndarray:
        """Encode documents with appropriate passage prefix/instruction."""
        formatted_texts = []
        for t in texts:
            if "e5" in self.model_id.lower() and not self.model_id.endswith("-instruct"):
                formatted_texts.append(f"passage: {t}")
            elif self.passage_instruction:
                formatted_texts.append(f"{self.passage_instruction} {t}")
            else:
                formatted_texts.append(t)

        return self._encode_raw(formatted_texts, batch_size=batch_size)

    def encode_queries(self, queries: List[str], batch_size: int = 16) -> np.ndarray:
        """Encode queries with appropriate query prefix/instruction."""
        formatted_queries = []
        for q in queries:
            if "e5" in self.model_id.lower() and not self.model_id.endswith("-instruct"):
                formatted_queries.append(f"query: {q}")
            elif "instruct" in self.model_id.lower():
                formatted_queries.append(
                    f"Instruct: Given a Turkish search query, retrieve relevant social posts\nQuery: {q}"
                )
            elif self.query_instruction:
                formatted_queries.append(f"{self.query_instruction} {q}")
            else:
                formatted_queries.append(q)

        return self._encode_raw(formatted_queries, batch_size=batch_size)

    def _encode_raw(self, texts: List[str], batch_size: int = 16) -> np.ndarray:
        import torch

        if self._backend == "sentence_transformers":
            embeddings = self._model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=False,
                normalize_embeddings=True,
            )
            return np.array(embeddings, dtype=np.float32)
        else:
            # Direct Transformers forward pass with mean pooling
            all_embeddings = []
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i : i + batch_size]
                inputs = self._tokenizer(
                    batch_texts,
                    padding=True,
                    truncation=True,
                    max_length=512,
                    return_tensors="pt",
                ).to(self._device)

                with torch.no_grad():
                    outputs = self._model(**inputs)
                    attention_mask = inputs["attention_mask"].unsqueeze(-1)
                    token_embeddings = outputs[0]  # First element is last_hidden_state
                    # Mean pooling
                    sum_embeddings = torch.sum(token_embeddings * attention_mask, dim=1)
                    sum_mask = torch.clamp(attention_mask.sum(dim=1), min=1e-9)
                    pooled = sum_embeddings / sum_mask
                    # Normalize
                    normalized = torch.nn.functional.normalize(pooled, p=2, dim=1)
                    all_embeddings.append(normalized.cpu().numpy())

            return np.vstack(all_embeddings).astype(np.float32)

    def embedding_dimension(self) -> int:
        return self._dim or 768

    def model_metadata(self) -> Dict[str, Any]:
        param_count = sum(p.numel() for p in self._model.parameters()) if self._model else 0
        return {
            "model_id": self.model_id,
            "parameter_count": f"{param_count / 1e6:.1f}M",
            "embedding_dimension": self.embedding_dimension(),
            "device": self._device,
            "dtype": getattr(self, "_dtype", "float32"),
            "backend": getattr(self, "_backend", "unknown"),
        }
