"""Moderation Policy and Threshold Management for NSosyal Pusula."""

import os
import json
from typing import Dict, Any, Optional
from backend.app.moderation.base import HazardCategory, ReviewPriority, HazardScores


# Default conservative thresholds calibrated to prevent false positives on general discourse
DEFAULT_CALIBRATED_THRESHOLDS: Dict[str, float] = {
    HazardCategory.UNSAFE.value: 0.50,
    HazardCategory.CSAE.value: 0.20,  # High sensitivity for critical harms
    HazardCategory.SELF_HARM_SUICIDE.value: 0.30,
    HazardCategory.VIOLENT_CRIMES.value: 0.45,
    HazardCategory.NON_VIOLENT_CRIMES.value: 0.50,
    HazardCategory.HATE_DISCRIMINATION.value: 0.45,
    HazardCategory.HARASSMENT_OFFENSIVE.value: 0.40,
    HazardCategory.SEXUAL_CONTENT_ADULT.value: 0.45,
    HazardCategory.INJECTION_JAILBREAK.value: 0.55,
    HazardCategory.MISINFORMATION_POLITICAL.value: 0.55,
    HazardCategory.PRIVACY_VIOLATION.value: 0.45,
}


class ModerationPolicy:
    """Configurable moderation thresholds, fusion weights, and review priority rules."""

    def __init__(self, thresholds_path: Optional[str] = None):
        self.thresholds: Dict[str, float] = dict(DEFAULT_CALIBRATED_THRESHOLDS)
        if thresholds_path and os.path.exists(thresholds_path):
            try:
                with open(thresholds_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self.thresholds.update(loaded.get("per_category_thresholds", {}))
            except Exception:
                pass

    def get_threshold(self, category: str) -> float:
        return self.thresholds.get(category, 0.50)

    def evaluate_priority(
        self,
        hazard_scores: HazardScores,
        spam_score: float,
        repetition_score: float,
        coordination_score: float,
    ) -> tuple[ReviewPriority, bool, list[str]]:
        """Evaluate multi-dimensional risk scores against policy rules.
        
        Returns:
            (ReviewPriority, human_review_recommended, triggered_reasons)
        """
        reasons: list[str] = []

        # 1. Critical Harms Check (Zero-tolerance high-severity categories)
        if hazard_scores.CSAE >= self.get_threshold(HazardCategory.CSAE.value):
            reasons.append(f"Model Yüksek Öncelikli Risk Sinyali: Çocuk Güvenliği Riski (%{hazard_scores.CSAE*100:.1f})")
            return ReviewPriority.CRITICAL, True, reasons

        if hazard_scores.SELF_HARM_SUICIDE >= self.get_threshold(HazardCategory.SELF_HARM_SUICIDE.value):
            reasons.append(f"Model Yüksek Öncelikli Risk Sinyali: Kendine Zarar Verme/İntihar İntibası (%{hazard_scores.SELF_HARM_SUICIDE*100:.1f})")
            return ReviewPriority.CRITICAL, True, reasons

        if hazard_scores.VIOLENT_CRIMES >= self.get_threshold(HazardCategory.VIOLENT_CRIMES.value):
            reasons.append(f"Model Risk Sinyali: Şiddet Eylemi/Tehdit Riski (%{hazard_scores.VIOLENT_CRIMES*100:.1f})")
            return ReviewPriority.CRITICAL, True, reasons

        # 2. High Severity Categories & Critical Spam/Coordination
        if hazard_scores.HATE_DISCRIMINATION >= self.get_threshold(HazardCategory.HATE_DISCRIMINATION.value):
            reasons.append(f"Model Risk Sinyali: Ayrımcılık/Nefret Söylemi Riski (%{hazard_scores.HATE_DISCRIMINATION*100:.1f})")
        if hazard_scores.HARASSMENT_OFFENSIVE >= self.get_threshold(HazardCategory.HARASSMENT_OFFENSIVE.value):
            reasons.append(f"Model Risk Sinyali: Taciz/Ağır Hakaret Riski (%{hazard_scores.HARASSMENT_OFFENSIVE*100:.1f})")
        if hazard_scores.PRIVACY_VIOLATION >= self.get_threshold(HazardCategory.PRIVACY_VIOLATION.value):
            reasons.append(f"Model Risk Sinyali: Kişisel Veri/Gizlilik İhlali Riski (%{hazard_scores.PRIVACY_VIOLATION*100:.1f})")
        if hazard_scores.INJECTION_JAILBREAK >= self.get_threshold(HazardCategory.INJECTION_JAILBREAK.value):
            reasons.append(f"Model Risk Sinyali: Sistem/Komut Manipülasyonu Riski (%{hazard_scores.INJECTION_JAILBREAK*100:.1f})")

        if spam_score >= 0.70:
            reasons.append(f"Sezgisel Sinyal: Yüksek Yoğunluklu Spam/Sahte Bağlantı (%{spam_score*100:.1f})")
        if coordination_score >= 0.70:
            reasons.append(f"Ağ Sinyali: Şüpheli Eşzamanlı Koordineli Paylaşım Deseni (%{coordination_score*100:.1f})")

        if reasons:
            return ReviewPriority.HIGH, True, reasons

        # 3. Medium Severity / Review Trigger
        if hazard_scores.unsafe >= self.get_threshold(HazardCategory.UNSAFE.value):
            reasons.append(f"Model Genel Güvensizlik İntibası (%{hazard_scores.unsafe*100:.1f})")
        if spam_score >= 0.40:
            reasons.append(f"Spam ve Promosyon Şüphesi (%{spam_score*100:.1f})")
        if repetition_score >= 0.40:
            reasons.append(f"Tekrarlayan Şablon Metin Oranı (%{repetition_score*100:.1f})")
        if coordination_score >= 0.40:
            reasons.append(f"Benzer Hesaplar Arası Metin Eşleşmesi (%{coordination_score*100:.1f})")

        if reasons:
            return ReviewPriority.MEDIUM, True, reasons

        # 4. Low Priority (Safe / Routine content)
        return ReviewPriority.LOW, False, ["İçerikte belirlenen eşikleri aşan güvenlik riski tespit edilmedi."]
