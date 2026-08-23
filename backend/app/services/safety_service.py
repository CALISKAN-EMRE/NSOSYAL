"""Production Safety & Moderation Service wrapping the Moderation Fusion Engine."""

from datetime import datetime, timezone
from typing import List, Optional
from app.models.post import Post
from app.models.safety import (
    RiskLevel,
    SafetyAnalysisRequest,
    SafetyAnalysisResponse,
    SafetyRiskVector,
    SafetySignal,
)
from backend.app.moderation.base import (
    ModerationAnalysisRequest,
    ReviewPriority,
    HazardCategory,
)
from backend.app.moderation.fusion_service import ModerationFusionService


class SafetyService:
    """Production Safety & Moderation Service for NSosyal Pusula.
    
    Delegates to ModerationFusionService, combining deep ModernBERT Guardrail hazard probabilities
    with deterministic spam, repetition, and coordination-risk heuristic detectors.
    """

    def __init__(self, fusion_service: Optional[ModerationFusionService] = None):
        self.fusion_service = fusion_service or ModerationFusionService()

    def analyze_text(
        self,
        request: SafetyAnalysisRequest,
        existing_posts: Optional[List[Post]] = None,
    ) -> SafetyAnalysisResponse:
        """Run multi-dimensional moderation analysis on input text."""
        mod_req = ModerationAnalysisRequest(
            text=request.text,
            post_id=request.post_id,
            author_id=request.author_id,
        )

        mod_resp = self.fusion_service.analyze(mod_req, existing_posts=existing_posts)
        r_vec = mod_resp.risk_vector

        # Map ReviewPriority to RiskLevel
        if r_vec.review_priority in [ReviewPriority.CRITICAL, ReviewPriority.HIGH]:
            risk_level = RiskLevel.HIGH
        elif r_vec.review_priority == ReviewPriority.MEDIUM:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        # Map signals to legacy SafetySignal
        safety_signals: List[SafetySignal] = [
            SafetySignal(
                rule_id=s.rule_id,
                category=s.category,
                description=s.description,
                severity=s.severity,
                confidence=s.confidence,
                detail=s.detail,
            )
            for s in r_vec.signals
        ]

        overall_risk_score = round(
            max(
                r_vec.overall_unsafe_probability,
                r_vec.spam_score,
                r_vec.repetition_score,
                r_vec.suspected_coordination_score,
            ),
            4,
        )

        legacy_vector = SafetyRiskVector(
            spam_score=r_vec.spam_score,
            repetition_score=r_vec.repetition_score,
            coordination_score=r_vec.suspected_coordination_score,
            toxicity_score=r_vec.profanity_signal,
            hate_speech_score=r_vec.hazard_scores.HATE_DISCRIMINATION,
            overall_risk_score=overall_risk_score,
            risk_level=risk_level,
            review_priority=r_vec.review_priority.value,
            hazard_scores=r_vec.hazard_scores.to_dict(),
            summary_explanation=r_vec.summary_explanation,
            signals=safety_signals,
            coordination_evidence=r_vec.coordination_evidence.model_dump() if r_vec.coordination_evidence else None,
            spam_evidence=r_vec.spam_evidence.model_dump() if r_vec.spam_evidence else None,
            repetition_evidence=r_vec.repetition_evidence.model_dump() if r_vec.repetition_evidence else None,
            is_actionable=r_vec.is_actionable,
            human_review_recommended=r_vec.human_review_recommended,
        )

        return SafetyAnalysisResponse(
            text_length=len(request.text),
            risk_vector=legacy_vector,
            analyzed_at=datetime.now(timezone.utc).isoformat(),
        )
