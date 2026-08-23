from datetime import datetime, timezone
from typing import List, Optional
import dateutil.parser

from app.adapters.base import DataSourceAdapter
from app.models.post import Post
from app.models.recommendation import (
    RecommendationExplanation,
    RecommendedPost,
    ScoreFactor,
)
from app.services.safety_service import SafetyService
from app.models.safety import SafetyAnalysisRequest


class RecommendationService:
    """Explainable Recommendation Engine (Phase 1 Prototype).

    Combines multi-factor scoring:
    Score = (w1*Interest + w2*TopicAffinity + w3*Recency + w4*Diversity) - (w5*Repetition + w6*SafetyRisk)
    Generates transparent 'Neden bunu görüyorum?' breakdowns for every recommended item.
    """

    def __init__(self, data_adapter: DataSourceAdapter, safety_service: SafetyService):
        self.adapter = data_adapter
        self.safety_service = safety_service

    def get_recommendations(
        self,
        user_interests: Optional[List[str]] = None,
        preferred_topic_id: Optional[str] = None,
        limit: int = 20,
    ) -> List[RecommendedPost]:
        """Generate explainable recommended feed."""
        if not user_interests:
            user_interests = ["YapayZeka", "Yazılım", "Bilim", "Eğitim", "Teknoloji"]

        all_posts = self.adapter.get_posts(limit=100)
        recommended: List[RecommendedPost] = []

        for post in all_posts:
            # 1. Calculate factor scores
            explanation = self.explain_post_recommendation(
                post=post,
                user_interests=user_interests,
                preferred_topic_id=preferred_topic_id,
                all_posts=all_posts,
            )

            # Update post's safety risk level if calculated
            safety_factor = next(
                (f for f in explanation.factors if f.factor_name == "safety_risk"), None
            )
            if safety_factor and safety_factor.raw_score > 0.6:
                post.safety_risk_level = "HIGH"
            elif safety_factor and safety_factor.raw_score > 0.3:
                post.safety_risk_level = "MEDIUM"
            else:
                post.safety_risk_level = "LOW"

            recommended.append(
                RecommendedPost(
                    post=post,
                    explanation=explanation,
                )
            )

        # Sort by final score descending
        recommended = sorted(
            recommended,
            key=lambda r: r.explanation.final_score,
            reverse=True,
        )

        return recommended[:limit]

    def explain_post_recommendation(
        self,
        post: Post,
        user_interests: List[str],
        preferred_topic_id: Optional[str] = None,
        all_posts: Optional[List[Post]] = None,
    ) -> RecommendationExplanation:
        """Calculate mathematical and natural-language explanation breakdown for a single post."""
        # Factor 1: Semantic Interest Match (w = 30)
        interest_overlap = sum(
            1 for tag in post.tags if any(ui.lower() in tag.lower() for ui in user_interests)
        )
        interest_raw = min(1.0, interest_overlap / max(1, len(post.tags))) if post.tags else 0.4
        interest_weight = 30.0
        interest_impact = interest_raw * interest_weight

        # Factor 2: Topic Affinity (w = 25)
        if preferred_topic_id and post.topic_id == preferred_topic_id:
            affinity_raw = 1.0
        elif post.topic_id in ["yapay-zeka-egitim", "acik-kaynak-yazilim"]:
            affinity_raw = 0.8
        else:
            affinity_raw = 0.5
        affinity_weight = 25.0
        affinity_impact = affinity_raw * affinity_weight

        # Factor 3: Recency Decay (w = 20)
        recency_raw = self._calculate_recency_score(post.created_at)
        recency_weight = 20.0
        recency_impact = recency_raw * recency_weight

        # Factor 4: Diversity & Discovery Boost (w = 15)
        # Boost different perspectives (e.g. academic or critical perspectives for balance)
        diversity_raw = 0.7 if post.perspective in ["critical", "academic", "expert"] else 0.4
        diversity_weight = 15.0
        diversity_impact = diversity_raw * diversity_weight

        # Factor 5 (Penalty): Repetition Penalty (w = -20)
        # Evaluate using safety heuristic
        safety_resp = self.safety_service.analyze_text(
            SafetyAnalysisRequest(
                text=post.text,
                post_id=post.id,
                author_id=post.author.id,
            ),
            existing_posts=all_posts,
        )
        rep_raw = safety_resp.risk_vector.repetition_score
        rep_weight = 20.0
        rep_impact = -(rep_raw * rep_weight)

        # Factor 6 (Penalty): Safety Risk Penalty (w = -30)
        safety_risk_raw = safety_resp.risk_vector.overall_risk_score
        safety_weight = 30.0
        safety_impact = -(safety_risk_raw * safety_weight)

        # Total Calculation
        positive_total = interest_impact + affinity_impact + recency_impact + diversity_impact
        negative_total = abs(rep_impact) + abs(safety_impact)
        final_score = max(0.0, min(100.0, round(positive_total - negative_total, 1)))

        factors = [
            ScoreFactor(
                factor_name="interest_match",
                label="İlgi Alanı Eşleşmesi (Heuristic/Tag Match)",
                weight=interest_weight,
                raw_score=round(interest_raw, 2),
                weighted_impact=round(interest_impact, 1),
                is_penalty=False,
                explanation=f"Takip ettiğiniz etiketlerle (%{interest_raw * 100:.0f}) oranında örtüşüyor.",
            ),
            ScoreFactor(
                factor_name="topic_affinity",
                label="Konu Yakınlığı",
                weight=affinity_weight,
                raw_score=round(affinity_raw, 2),
                weighted_impact=round(affinity_impact, 1),
                is_penalty=False,
                explanation=f"'{post.topic_title}' kategorisine gösterdiğiniz etkileşim geçmişi.",
            ),
            ScoreFactor(
                factor_name="recency",
                label="İçerik Güncelliği",
                weight=recency_weight,
                raw_score=round(recency_raw, 2),
                weighted_impact=round(recency_impact, 1),
                is_penalty=False,
                explanation="Gönderinin yayınlanma zamanı ve tazelik katsayısı.",
            ),
            ScoreFactor(
                factor_name="diversity_boost",
                label="Perspektif Çeşitliliği & Keşif",
                weight=diversity_weight,
                raw_score=round(diversity_raw, 2),
                weighted_impact=round(diversity_impact, 1),
                is_penalty=False,
                explanation="Yankı odası engellemek için farklı bakış açıları (uzman/eleştirel) ödüllendirildi.",
            ),
            ScoreFactor(
                factor_name="repetition_penalty",
                label="Tekrar Eden İçerik Cezası",
                weight=rep_weight,
                raw_score=round(rep_raw, 2),
                weighted_impact=round(rep_impact, 1),
                is_penalty=True,
                explanation="Aynı veya benzer metnin tekrar paylaşılma sıklığı düşürüldü."
                if rep_raw > 0
                else "Tekrar saptanmadı (ceza yok).",
            ),
            ScoreFactor(
                factor_name="safety_risk",
                label="İçerik Güvenliği / Spam Cezası",
                weight=safety_weight,
                raw_score=round(safety_risk_raw, 2),
                weighted_impact=round(safety_impact, 1),
                is_penalty=True,
                explanation=f"Sezgisel moderasyon risk puanı: {safety_risk_raw:.2f}"
                if safety_risk_raw > 0
                else "Güvenlik riski saptanmadı.",
            ),
        ]

        summary_reason = self._generate_summary_reason(
            interest_raw, safety_risk_raw, rep_raw, post.topic_title
        )

        return RecommendationExplanation(
            post_id=post.id,
            final_score=final_score,
            summary_reason=summary_reason,
            factors=factors,
        )

    def _calculate_recency_score(self, created_at_str: str) -> float:
        try:
            dt = dateutil.parser.parse(created_at_str)
            now = datetime.now(timezone.utc)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            diff_hours = (now - dt).total_seconds() / 3600.0
            # Exponential decay over hours
            return max(0.1, min(1.0, 1.0 / (1.0 + (diff_hours / 24.0))))
        except Exception:
            return 0.5

    def _generate_summary_reason(
        self,
        interest_raw: float,
        safety_risk_raw: float,
        rep_raw: float,
        topic_title: str,
    ) -> str:
        if safety_risk_raw > 0.6 or rep_raw > 0.6:
            return "Bu gönderi yüksek oranda spam veya tekrar sinyali içerdiği için puanı önemli ölçüde düşürülmüştür."
        if interest_raw >= 0.7:
            return f"Bu gönderi '{topic_title}' alanındaki ilgi alanlarınız ve yüksek etkileşim potansiyeli nedeniyle önerilmektedir."
        return f"'{topic_title}' başlığındaki dengeli perspektifleri ve güncel gelişmeleri keşfetmeniz için akışınıza eklendi."
