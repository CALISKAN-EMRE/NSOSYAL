"""Data models and interfaces for the NSosyal Pusula Moderation & Safety Pipeline."""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ReviewPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class HazardCategory(str, Enum):
    """Exact hazard taxonomy from ytu-ce-cosmos/modernbert-tr-guardrail."""
    UNSAFE = "unsafe"
    VIOLENT_CRIMES = "VIOLENT_CRIMES"
    NON_VIOLENT_CRIMES = "NON_VIOLENT_CRIMES"
    HATE_DISCRIMINATION = "HATE_DISCRIMINATION"
    HARASSMENT_OFFENSIVE = "HARASSMENT_OFFENSIVE"
    SEXUAL_CONTENT_ADULT = "SEXUAL_CONTENT_ADULT"
    CSAE = "CSAE"
    SELF_HARM_SUICIDE = "SELF_HARM_SUICIDE"
    INJECTION_JAILBREAK = "INJECTION_JAILBREAK"
    MISINFORMATION_POLITICAL = "MISINFORMATION_POLITICAL"
    PRIVACY_VIOLATION = "PRIVACY_VIOLATION"


class HazardScores(BaseModel):
    """Multi-label sigmoid probabilities in [0, 1] from the guardrail model."""
    unsafe: float = Field(0.0, ge=0.0, le=1.0, description="Overall probability that text violates safety policy")
    VIOLENT_CRIMES: float = Field(0.0, ge=0.0, le=1.0)
    NON_VIOLENT_CRIMES: float = Field(0.0, ge=0.0, le=1.0)
    HATE_DISCRIMINATION: float = Field(0.0, ge=0.0, le=1.0)
    HARASSMENT_OFFENSIVE: float = Field(0.0, ge=0.0, le=1.0)
    SEXUAL_CONTENT_ADULT: float = Field(0.0, ge=0.0, le=1.0)
    CSAE: float = Field(0.0, ge=0.0, le=1.0, description="Child sexual abuse / exploitation (highest severity)")
    SELF_HARM_SUICIDE: float = Field(0.0, ge=0.0, le=1.0)
    INJECTION_JAILBREAK: float = Field(0.0, ge=0.0, le=1.0)
    MISINFORMATION_POLITICAL: float = Field(0.0, ge=0.0, le=1.0)
    PRIVACY_VIOLATION: float = Field(0.0, ge=0.0, le=1.0)

    def to_dict(self) -> Dict[str, float]:
        return {k: round(v, 4) for k, v in self.model_dump().items()}


class EvidenceSignal(BaseModel):
    """Explainable evidence item backing a moderation or safety risk assessment."""
    rule_id: str = Field(..., description="Unique rule/heuristic/model identifier")
    category: str = Field(..., description="Signal category: model_hazard, spam, repetition, coordination, format")
    description: str = Field(..., description="Human-readable Turkish explanation")
    severity: str = Field(..., description="info, warning, or critical")
    confidence: float = Field(..., ge=0.0, le=1.0)
    detail: Optional[str] = None


class SpamEvidence(BaseModel):
    """Spam detection metrics and extracted features."""
    spam_score: float = Field(0.0, ge=0.0, le=1.0)
    link_count: int = 0
    suspicious_tld_detected: bool = False
    uppercase_ratio: float = 0.0
    promotional_keyword_hits: List[str] = Field(default_factory=list)
    signals: List[EvidenceSignal] = Field(default_factory=list)


class RepetitionEvidence(BaseModel):
    """Repetition and near-duplicate metrics."""
    repetition_score: float = Field(0.0, ge=0.0, le=1.0)
    within_text_word_repetition: float = 0.0
    corpus_duplicate_count: int = 0
    duplicate_post_ids: List[str] = Field(default_factory=list)
    signals: List[EvidenceSignal] = Field(default_factory=list)


class CoordinationEvidence(BaseModel):
    """Suspected coordinated inauthentic activity signals."""
    suspected_coordination_score: float = Field(0.0, ge=0.0, le=1.0)
    similar_post_ids: List[str] = Field(default_factory=list)
    participating_authors: List[str] = Field(default_factory=list)
    time_window_minutes: Optional[float] = None
    shared_urls_or_domains: List[str] = Field(default_factory=list)
    signals: List[EvidenceSignal] = Field(default_factory=list)


class ModerationRiskVector(BaseModel):
    """Structured, multi-dimensional risk vector produced by ModerationFusionService."""
    overall_unsafe_probability: float = Field(..., ge=0.0, le=1.0)
    hazard_scores: HazardScores
    profanity_signal: float = Field(0.0, ge=0.0, le=1.0)
    spam_score: float = Field(..., ge=0.0, le=1.0)
    repetition_score: float = Field(..., ge=0.0, le=1.0)
    suspected_coordination_score: float = Field(..., ge=0.0, le=1.0)
    review_priority: ReviewPriority
    human_review_recommended: bool
    is_actionable: bool
    summary_explanation: str
    signals: List[EvidenceSignal] = Field(default_factory=list)
    coordination_evidence: Optional[CoordinationEvidence] = None
    spam_evidence: Optional[SpamEvidence] = None
    repetition_evidence: Optional[RepetitionEvidence] = None


class ModerationAnalysisRequest(BaseModel):
    """Request payload for moderation analysis."""
    text: str = Field(..., min_length=1, max_length=5000)
    post_id: Optional[str] = None
    author_id: Optional[str] = None
    author_handle: Optional[str] = None
    created_at: Optional[datetime] = None


class ModerationAnalysisResponse(BaseModel):
    """Comprehensive moderation response payload."""
    post_id: Optional[str] = None
    text_length: int
    risk_vector: ModerationRiskVector
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
