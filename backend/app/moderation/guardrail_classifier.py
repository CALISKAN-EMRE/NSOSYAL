"""Guardrail classifier implementations: ModernBERT-TR Guardrail & Demo Fallback."""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import torch

from backend.app.moderation.base import HazardScores, HazardCategory

logger = logging.getLogger("nsosyal_pusula.moderation.guardrail")


class BaseGuardrailClassifier(ABC):
    """Abstract interface for Turkish guardrail safety classifier."""

    @abstractmethod
    def classify(self, text: str) -> HazardScores:
        """Classify a single text and return continuous hazard probabilities in [0, 1]."""
        pass

    @abstractmethod
    def batch_classify(self, texts: List[str]) -> List[HazardScores]:
        """Classify a batch of texts."""
        pass


class ModernBERTGuardrailClassifier(BaseGuardrailClassifier):
    """Production ModernBERT Turkish Guardrail Classifier.
    
    Model: ytu-ce-cosmos/modernbert-tr-guardrail (149M params, Apache-2.0)
    Taxonomy: 11 multi-label sigmoid probabilities.
    """

    MODEL_ID = "ytu-ce-cosmos/modernbert-tr-guardrail"

    def __init__(self, device: Optional[str] = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.tokenizer = None
        self.config = None
        self._load_model()

    def _load_model(self) -> None:
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoConfig

            logger.info(f"Loading ModernBERT Guardrail from '{self.MODEL_ID}' on {self.device}...")
            self.config = AutoConfig.from_pretrained(self.MODEL_ID)
            self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_ID)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.MODEL_ID)
            self.model.to(self.device).eval()
            logger.info(f"Successfully loaded '{self.MODEL_ID}' (11-label head).")
        except Exception as e:
            logger.error(f"Failed to load ModernBERT Guardrail '{self.MODEL_ID}': {e}. Fallback required.")
            self.model = None

    def classify(self, text: str) -> HazardScores:
        if self.model is None or self.tokenizer is None:
            return DemoGuardrailClassifier().classify(text)

        with torch.no_grad():
            inputs = self.tokenizer(
                text,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            ).to(self.device)

            logits = self.model(**inputs).logits
            probs = torch.sigmoid(logits)[0].cpu().numpy()

        return self._map_probs_to_hazard_scores(probs)

    def batch_classify(self, texts: List[str]) -> List[HazardScores]:
        if not texts:
            return []
        if self.model is None or self.tokenizer is None:
            return DemoGuardrailClassifier().batch_classify(texts)

        with torch.no_grad():
            inputs = self.tokenizer(
                texts,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            ).to(self.device)

            logits = self.model(**inputs).logits
            probs = torch.sigmoid(logits).cpu().numpy()

        return [self._map_probs_to_hazard_scores(p) for p in probs]

    def _map_probs_to_hazard_scores(self, probs: Any) -> HazardScores:
        id2label = getattr(self.config, "id2label", {})
        scores_dict = {}
        for idx, p in enumerate(probs):
            lbl_name = id2label.get(str(idx), id2label.get(idx, ""))
            if lbl_name:
                scores_dict[lbl_name] = float(p)

        return HazardScores(
            unsafe=scores_dict.get("unsafe", 0.0),
            VIOLENT_CRIMES=scores_dict.get("VIOLENT_CRIMES", 0.0),
            NON_VIOLENT_CRIMES=scores_dict.get("NON_VIOLENT_CRIMES", 0.0),
            HATE_DISCRIMINATION=scores_dict.get("HATE_DISCRIMINATION", 0.0),
            HARASSMENT_OFFENSIVE=scores_dict.get("HARASSMENT_OFFENSIVE", 0.0),
            SEXUAL_CONTENT_ADULT=scores_dict.get("SEXUAL_CONTENT_ADULT", 0.0),
            CSAE=scores_dict.get("CSAE", 0.0),
            SELF_HARM_SUICIDE=scores_dict.get("SELF_HARM_SUICIDE", 0.0),
            INJECTION_JAILBREAK=scores_dict.get("INJECTION_JAILBREAK", 0.0),
            MISINFORMATION_POLITICAL=scores_dict.get("MISINFORMATION_POLITICAL", 0.0),
            PRIVACY_VIOLATION=scores_dict.get("PRIVACY_VIOLATION", 0.0),
        )


class DemoGuardrailClassifier(BaseGuardrailClassifier):
    """Deterministic, lightweight guardrail classifier for testing without deep models."""

    # Heuristic hazard triggers for unit tests and local dev
    _HAZARD_TRIGGERS = {
        HazardCategory.CSAE.value: ["çocuk istismarı", "çocuk porno", "csae"],
        HazardCategory.SELF_HARM_SUICIDE.value: ["intihar etmek", "kendimi öldür", "canıma kıy", "bileklerimi kes"],
        HazardCategory.VIOLENT_CRIMES.value: ["molotof", "bomba yapımı", "patlayıcı hazırla", "öldüreceğim", "katliam yap"],
        HazardCategory.NON_VIOLENT_CRIMES.value: ["kredi kartı çal", "kart kopyalama", "sahte fatura düzenle", "hackle"],
        HazardCategory.HATE_DISCRIMINATION.value: ["etnik kökene sahip insanlardan nefret", "hepsi sürülmeli", "aşağılık ırk", "soykırım hak"],
        HazardCategory.HARASSMENT_OFFENSIVE.value: ["sahtekar", "rezil", "aptal", "salak", "pislik", "şerefsiz", "aşağılık"],
        HazardCategory.SEXUAL_CONTENT_ADULT.value: ["müstehcen içerik", "pornografik video", "erotik hikaye"],
        HazardCategory.INJECTION_JAILBREAK.value: ["ignore previous instructions", "sistem talimatlarını unut", "jailbreak mode"],
        HazardCategory.MISINFORMATION_POLITICAL.value: ["seçimlerde sahte oy", "dezenformasyon kampanyası başlat"],
        HazardCategory.PRIVACY_VIOLATION.value: ["tc kimlik no paylaş", "adresini sızdır", "doxx et", "telefon numarasını yay"],
    }

    def classify(self, text: str) -> HazardScores:
        lower_t = text.lower()
        scores: Dict[str, float] = {cat.value: 0.02 for cat in HazardCategory}

        matched_any = False
        for cat, keywords in self._HAZARD_TRIGGERS.items():
            for kw in keywords:
                if kw in lower_t:
                    scores[cat] = max(scores[cat], 0.88)
                    matched_any = True

        if matched_any:
            max_hazard = max(scores.values())
            scores["unsafe"] = min(1.0, max_hazard + 0.05)
        else:
            scores["unsafe"] = 0.03

        return HazardScores(**scores)

    def batch_classify(self, texts: List[str]) -> List[HazardScores]:
        return [self.classify(t) for t in texts]
