import logging
from typing import Any, Dict, Optional

from app.config import settings
from app.ml.base import (
    BaseClusterService,
    BaseEmbeddingService,
    BaseRerankerService,
    BaseSimilarityService,
)
from app.ml.embedding_service import (
    DemoEmbeddingService,
    ModernBERTEmbeddingService,
    MultilingualE5EmbeddingService,
)
from app.ml.cluster_service import DemoClusterService, SemanticClusterService
from app.ml.reranker_service import DemoRerankerService, ModernBERTRerankerService
from app.ml.similarity_service import SemanticSimilarityService

logger = logging.getLogger("nsosyal_pusula.ml")


class ModelManager:
    """Singleton ML Model Lifecycle and Registry Manager for NSosyal Pusula."""

    _instance: Optional["ModelManager"] = None

    def __init__(self):
        self.mode: str = settings.SEMANTIC_MODE.lower()
        self.device: Optional[str] = settings.DEVICE
        self.clustering_embedder: Optional[BaseEmbeddingService] = None
        self.search_embedder: Optional[BaseEmbeddingService] = None
        self.context_reranker: Optional[BaseRerankerService] = None
        self.cluster_service: Optional[BaseClusterService] = None
        self.similarity_service: Optional[BaseSimilarityService] = None
        self.is_initialized: bool = False
        self.error_detail: Optional[str] = None

    @property
    def is_gpu_accelerated(self) -> bool:
        return (self.device or "").startswith("cuda")

    @property
    def cuda_vram_gb(self) -> float:
        import torch
        if torch.cuda.is_available():
            return round(torch.cuda.memory_allocated() / (1024**3), 2)
        return 0.0

    @classmethod
    def get_instance(cls) -> "ModelManager":
        if cls._instance is None:
            cls._instance = ModelManager()
        return cls._instance

    def initialize(self):
        """Initialize models once according to configured SEMANTIC_MODE."""
        if self.is_initialized:
            return

        logger.info(f"Initializing ModelManager with SEMANTIC_MODE='{self.mode}'...")

        if self.mode == "ml":
            try:
                import torch

                if self.device is None:
                    self.device = "cuda" if torch.cuda.is_available() else "cpu"

                logger.info(f"Loading production ML transformer models on device='{self.device}'...")

                # 1. ModernBERT TR Embed (Clustering & Context Retrieval)
                logger.info(f"Loading clustering/retrieval model: {settings.MODEL_CLUSTERING_EMBED}")
                self.clustering_embedder = ModernBERTEmbeddingService(
                    model_id=settings.MODEL_CLUSTERING_EMBED, device=self.device
                )

                # 2. Multilingual E5 Large Instruct (Natural Language Search)
                logger.info(f"Loading search model: {settings.MODEL_SEARCH_EMBED}")
                self.search_embedder = MultilingualE5EmbeddingService(
                    model_id=settings.MODEL_SEARCH_EMBED, device=self.device
                )

                # 3. ModernBERT TR Reranker (Cross-Encoder)
                logger.info(f"Loading context reranker model: {settings.MODEL_CONTEXT_RERANKER}")
                self.context_reranker = ModernBERTRerankerService(
                    model_id=settings.MODEL_CONTEXT_RERANKER, device=self.device
                )

                # 4. ModernBERT TR Guardrail (Moderation & Safety)
                logger.info(f"Loading guardrail classifier model: {settings.MODEL_GUARDRAIL}")
                from backend.app.moderation.guardrail_classifier import ModernBERTGuardrailClassifier
                from backend.app.moderation.fusion_service import ModerationFusionService

                self.guardrail_classifier = ModernBERTGuardrailClassifier(device=self.device)
                self.moderation_service = ModerationFusionService(classifier=self.guardrail_classifier)

                # 5. Composite Services
                self.cluster_service = SemanticClusterService(
                    embedding_service=self.clustering_embedder, min_cluster_size=3
                )
                self.similarity_service = SemanticSimilarityService(
                    embedding_service=self.clustering_embedder
                )

                self.is_initialized = True
                logger.info("All production ML models successfully loaded and ready on GPU/CPU.")

            except Exception as e:
                logger.error(f"Failed to initialize ML models on '{self.device}': {e}. Falling back to demo mode.")
                self.mode = "demo_fallback"
                self.error_detail = str(e)
                self._init_demo_services()
        else:
            self._init_demo_services()

    def _init_demo_services(self):
        """Initialize fast deterministic demo services without neural weights."""
        logger.info("Initializing deterministic Demo ML services...")
        self.device = "cpu"
        self.clustering_embedder = DemoEmbeddingService(dimension=384, model_name="demo-wordhash-384")
        self.search_embedder = DemoEmbeddingService(dimension=384, model_name="demo-wordhash-search")
        self.context_reranker = DemoRerankerService()
        from backend.app.moderation.guardrail_classifier import DemoGuardrailClassifier
        from backend.app.moderation.fusion_service import ModerationFusionService
        self.guardrail_classifier = DemoGuardrailClassifier()
        self.moderation_service = ModerationFusionService(classifier=self.guardrail_classifier)
        self.cluster_service = DemoClusterService()
        self.similarity_service = SemanticSimilarityService(embedding_service=self.clustering_embedder)
        self.is_initialized = True

    def get_status(self) -> Dict[str, Any]:
        """Return runtime status for observability without leaking infrastructure secrets."""
        import torch

        cuda_vram_gb = 0.0
        if torch.cuda.is_available():
            cuda_vram_gb = round(torch.cuda.memory_allocated() / (1024**3), 2)

        return {
            "status": "ready" if self.is_initialized else "initializing",
            "semantic_mode": self.mode,
            "device": self.device,
            "is_gpu_accelerated": (self.device or "").startswith("cuda"),
            "cuda_vram_allocated_gb": cuda_vram_gb,
            "models_loaded": {
                "clustering_model": settings.MODEL_CLUSTERING_EMBED if self.mode == "ml" else "demo_baseline",
                "search_model": settings.MODEL_SEARCH_EMBED if self.mode == "ml" else "demo_baseline",
                "reranker_model": settings.MODEL_CONTEXT_RERANKER if self.mode == "ml" else "demo_baseline",
                "guardrail_model": settings.MODEL_GUARDRAIL if self.mode == "ml" else "demo_baseline",
            },
            "error_detail": self.error_detail,
        }
