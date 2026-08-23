from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import numpy as np


class EmbeddingProvider(ABC):
    """Abstract interface for embedding providers in NSosyal Pusula ML research layer.

    Decouples model execution, tokenization, instruction prefixes, and device placement
    from evaluation benchmarks and downstream services.
    """

    @abstractmethod
    def encode_documents(self, texts: List[str], batch_size: int = 16) -> np.ndarray:
        """Encode a list of documents / posts into normalized embedding vectors.

        Automatically applies model-specific document prefixes or formatting (e.g. 'passage: ').
        """
        pass

    @abstractmethod
    def encode_queries(self, queries: List[str], batch_size: int = 16) -> np.ndarray:
        """Encode a list of retrieval / context search queries into normalized embedding vectors.

        Automatically applies model-specific query prefixes or instruction formatting (e.g. 'query: ').
        """
        pass

    @abstractmethod
    def model_metadata(self) -> Dict[str, Any]:
        """Return structured model metadata:

        - model_id: HuggingFace model identifier or local path
        - license: Open source license
        - parameter_count: Approximate number of parameters
        - embedding_dimension: Dimension of output vectors
        - max_context_length: Maximum supported sequence length
        - instruction_format: Required prefix/instruction template
        - device_used: cpu, cuda:0, etc.
        - dtype_used: float32, float16, bfloat16
        """
        pass

    @abstractmethod
    def embedding_dimension(self) -> int:
        """Return the vector dimensionality (e.g. 768, 1024, 1536)."""
        pass
