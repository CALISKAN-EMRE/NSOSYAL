from typing import Dict, Optional
from ml.embeddings.base import EmbeddingProvider
from ml.embeddings.hf_provider import HuggingFaceEmbeddingProvider
from ml.embeddings.mock_provider import DeterministicMockEmbeddingProvider


def get_embedding_provider(
    model_name_or_id: str,
    device: Optional[str] = None,
    allow_mock_fallback: bool = True,
) -> EmbeddingProvider:
    """Factory function to instantiate an EmbeddingProvider for any candidate model."""
    if model_name_or_id.startswith("mock") or model_name_or_id.startswith("deterministic"):
        return DeterministicMockEmbeddingProvider(model_name=model_name_or_id)

    try:
        return HuggingFaceEmbeddingProvider(model_id=model_name_or_id, device=device)
    except Exception as e:
        if allow_mock_fallback:
            print(
                f"[WARNING] Could not load model '{model_name_or_id}' ({e}). Falling back to DeterministicMockEmbeddingProvider."
            )
            return DeterministicMockEmbeddingProvider(
                model_name=f"fallback-mock-for-{model_name_or_id}"
            )
        raise e
