from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class SafetySignal(BaseModel):
    rule_id: str
    category: str = Field(
        ..., description="spam, repetition, coordination, toxicity, format_anomaly"
    )
    description: str
    severity: str = Field(default="info", description="info, warning, critical")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    detail: Optional[str] = None


class SafetyRiskVector(BaseModel):
    spam_score: float = Field(default=0.0, ge=0.0, le=1.0)
    repetition_score: float = Field(default=0.0, ge=0.0, le=1.0)
    coordination_score: float = Field(default=0.0, ge=0.0, le=1.0)
    toxicity_score: float = Field(default=0.0, ge=0.0, le=1.0)
    hate_speech_score: float = Field(default=0.0, ge=0.0, le=1.0)
    overall_risk_score: float = Field(default=0.0, ge=0.0, le=1.0)
    risk_level: RiskLevel = RiskLevel.LOW
    review_priority: str = Field(default="LOW", description="LOW, MEDIUM, HIGH, CRITICAL")
    hazard_scores: Optional[dict] = Field(default=None, description="Exact 11-category ModernBERT probabilities")
    summary_explanation: Optional[str] = Field(default=None, description="Grounded non-definitive Turkish explanation")
    signals: List[SafetySignal] = Field(default_factory=list)
    coordination_evidence: Optional[dict] = None
    spam_evidence: Optional[dict] = None
    repetition_evidence: Optional[dict] = None
    is_actionable: bool = False
    human_review_recommended: bool = False


class SafetyAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    post_id: Optional[str] = None
    author_id: Optional[str] = None


class SafetyAnalysisResponse(BaseModel):
    text_length: int
    risk_vector: SafetyRiskVector
    analyzed_at: str
