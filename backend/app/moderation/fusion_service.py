"""Moderation Fusion Service orchestrating multi-dimensional safety and coordination risks."""

import logging
from typing import List, Optional, Any
from datetime import datetime, timezone

try:
    from app.moderation.base import (
        ModerationAnalysisRequest,
        ModerationAnalysisResponse,
        ModerationRiskVector,
        ReviewPriority,
        HazardScores,
        EvidenceSignal,
        HazardCategory,
    )
    from app.moderation.guardrail_classifier import (
        BaseGuardrailClassifier,
        DemoGuardrailClassifier,
        ModernBERTGuardrailClassifier,
    )
    from app.moderation.spam_detector import SpamDetector
    from app.moderation.repetition_detector import RepetitionDetector
    from app.moderation.coordination_detector import CoordinationDetector
    from app.moderation.policy import ModerationPolicy
except ImportError:
    from backend.app.moderation.base import (
        ModerationAnalysisRequest,
        ModerationAnalysisResponse,
        ModerationRiskVector,
        ReviewPriority,
        HazardScores,
        EvidenceSignal,
        HazardCategory,
    )
    from backend.app.moderation.guardrail_classifier import (
        BaseGuardrailClassifier,
        DemoGuardrailClassifier,
        ModernBERTGuardrailClassifier,
    )
    from backend.app.moderation.spam_detector import SpamDetector
    from backend.app.moderation.repetition_detector import RepetitionDetector
    from backend.app.moderation.coordination_detector import CoordinationDetector
    from backend.app.moderation.policy import ModerationPolicy

logger = logging.getLogger("nsosyal_pusula.moderation.fusion")


class ModerationFusionService:
    """Orchestrates deep ML guardrails, heuristic spam detectors, and network coordination signals.
    
    Produces transparent, multi-dimensional risk vectors without single-score opacity.
    """

    def __init__(
        self,
        classifier: Optional[BaseGuardrailClassifier] = None,
        policy: Optional[ModerationPolicy] = None,
    ):
        self.classifier = classifier or DemoGuardrailClassifier()
        self.spam_detector = SpamDetector()
        self.repetition_detector = RepetitionDetector()
        self.coordination_detector = CoordinationDetector()
        self.policy = policy or ModerationPolicy()

    def analyze(
        self,
        request: ModerationAnalysisRequest,
        existing_posts: Optional[List[Any]] = None,
    ) -> ModerationAnalysisResponse:
        text = request.text

        # 1. Model Hazard Classification
        hazard_scores = self.classifier.classify(text)

        # 2. Spam & Link Density Analysis
        spam_evidence = self.spam_detector.analyze(text)

        # 3. Repetition & Duplicate Analysis
        repetition_evidence = self.repetition_detector.analyze(
            text=text,
            current_post_id=request.post_id,
            existing_posts=existing_posts,
        )

        # 4. Coordination & Inauthentic Activity Analysis
        coordination_evidence = self.coordination_detector.analyze(
            text=text,
            current_post_id=request.post_id,
            current_author_id=request.author_id,
            current_created_at=request.created_at,
            existing_posts=existing_posts,
        )

        # 5. Profanity / Abusive Language Signal
        profanity_signal = max(
            hazard_scores.HARASSMENT_OFFENSIVE,
            hazard_scores.HATE_DISCRIMINATION,
        )

        # 6. Policy Evaluation
        priority, human_review, reasons = self.policy.evaluate_priority(
            hazard_scores=hazard_scores,
            spam_score=spam_evidence.spam_score,
            repetition_score=repetition_evidence.repetition_score,
            coordination_score=coordination_evidence.suspected_coordination_score,
        )

        # 7. Collect All Explainable Evidence Signals
        all_signals: List[EvidenceSignal] = []

        # Add model hazard signals if above threshold
        for cat in HazardCategory:
            val = getattr(hazard_scores, cat.value, 0.0)
            thresh = self.policy.get_threshold(cat.value)
            if val >= thresh and cat != HazardCategory.UNSAFE:
                all_signals.append(
                    EvidenceSignal(
                        rule_id=f"MODEL-HAZARD-{cat.name}",
                        category="model_hazard",
                        description=f"Model Güvenlik İhlali Sinyali: {cat.value} eşiği aşıldı.",
                        severity="critical" if cat in [HazardCategory.CSAE, HazardCategory.SELF_HARM_SUICIDE, HazardCategory.VIOLENT_CRIMES] else "warning",
                        confidence=round(val, 3),
                        detail=f"Olasılık: %{val*100:.1f} (Eşik: %{thresh*100:.1f})",
                    )
                )

        all_signals.extend(spam_evidence.signals)
        all_signals.extend(repetition_evidence.signals)
        all_signals.extend(coordination_evidence.signals)

        # 8. Deterministic, Non-Definitive Summary Explanation
        summary_explanation = self._build_summary_explanation(
            priority=priority,
            human_review=human_review,
            reasons=reasons,
            hazard_scores=hazard_scores,
            spam_score=spam_evidence.spam_score,
            coordination_score=coordination_evidence.suspected_coordination_score,
        )

        is_actionable = priority in [ReviewPriority.HIGH, ReviewPriority.CRITICAL]

        risk_vector = ModerationRiskVector(
            overall_unsafe_probability=round(hazard_scores.unsafe, 4),
            hazard_scores=hazard_scores,
            profanity_signal=round(profanity_signal, 4),
            spam_score=round(spam_evidence.spam_score, 4),
            repetition_score=round(repetition_evidence.repetition_score, 4),
            suspected_coordination_score=round(coordination_evidence.suspected_coordination_score, 4),
            review_priority=priority,
            human_review_recommended=human_review,
            is_actionable=is_actionable,
            summary_explanation=summary_explanation,
            signals=all_signals,
            coordination_evidence=coordination_evidence,
            spam_evidence=spam_evidence,
            repetition_evidence=repetition_evidence,
        )

        return ModerationAnalysisResponse(
            post_id=request.post_id,
            text_length=len(text),
            risk_vector=risk_vector,
            analyzed_at=datetime.now(timezone.utc),
        )

    def _build_summary_explanation(
        self,
        priority: ReviewPriority,
        human_review: bool,
        reasons: List[str],
        hazard_scores: HazardScores,
        spam_score: float,
        coordination_score: float,
    ) -> str:
        if priority == ReviewPriority.LOW:
            return "İçerik rutin parametreler dahilindedir. Model ve sezgisel denetimlerde inceleme gerektiren bir risk unsuru saptanmamıştır."

        prefix = f"Moderasyon İnceleme Önceliği: [{priority.value}]."
        reason_str = " | ".join(reasons[:3])
        review_note = " İnsan moderatör incelemesi tavsiye edilmektedir." if human_review else ""

        return f"{prefix} Tespit edilen risk göstergeleri: {reason_str}.{review_note}"
