from abc import ABC, abstractmethod
from typing import Any, Dict, List


class ToxicityClassifier(ABC):
    """Abstract interface for Turkish toxicity & discrimination classifiers (Phase 2B Research Layer)."""

    @abstractmethod
    def predict_risk_score(self, text: str) -> float:
        """Return probabilistic toxicity / harassment risk score in [0.0, 1.0]."""
        pass

    @abstractmethod
    def model_metadata(self) -> Dict[str, Any]:
        """Return model metadata."""
        pass
