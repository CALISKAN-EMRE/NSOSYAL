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
from app.ml.model_manager import ModelManager


class RecommendationService:
    """Explainable Recommendation Engine (Phase 2B Hardened Architecture).

    Multi-factor Transparent Scoring Formula:
    Score = (w1*SemanticInterest + w2*TopicAffinity + w3*Recency + w4*Diversity) - (w5*Repetition + w6*SafetyRisk)
    
    Generates transparent, strictly grounded 'Neden bunu görüyorum?' breakdowns for every item.
    """

    def __init__(
        self,
        data_adapter: DataSourceAdapter,
        safety_service: SafetyService,
        model_manager: Optional[ModelManager] = None,
    ):
        self.adapter = data_adapter
        self.safety_service = safety_service
        self.model_manager = model_manager or ModelManager.get_instance()

    def get_recommendations(
        self,
        user_interests: Optional[List[str]] = None,
        preferred_topic_id: Optional[str] = None,
        limit: int = 20,
    ) -> List[RecommendedPost]:
        """Generate explainable recommended feed with real embedding affinity scoring."""
        if not user_interests:
            user_interests = ["YapayZeka", "Yazılım", "Bilim", "Eğitim", "Teknoloji"]

        self.model_manager.initialize()
        all_posts = self.adapter.get_posts(limit=100)
        recommended: List[RecommendedPost] = []

        for post in all_posts:
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
        """Calculate mathematical and strictly grounded explanation breakdown for a single post."""
        self.model_manager.initialize()

        # Factor 1: Semantic Interest Match using ModernBERT Embeddings (w = 30)
        if self.model_manager.similarity_service:
            interest_raw = self.model_manager.similarity_service.compute_profile_similarity(
                user_interests=user_interests, post_text=post.text, post_tags=post.tags
            )
        else:
            overlap = sum(
                1 for tag in post.tags if any(ui.lower() in tag.lower() for ui in user_interests)
            )
            interest_raw = min(1.0, overlap / max(1, len(post.tags))) if post.tags else 0.4

        interest_weight = 30.0
        interest_impact = interest_raw * interest_weight

        # Factor 2: Explicit Topic/Cluster Affinity (w = 25)
        # Traceable affinity based strictly on explicit user filter / profile selection
        if preferred_topic_id and (
            post.topic_id == preferred_topic_id
            or (post.semantic_cluster_id and post.semantic_cluster_id == preferred_topic_id)
        ):
            affinity_raw = 1.0
            affinity_explanation = f"Aktif filtrelenen konu/küme ('{preferred_topic_id}') ile doğrudan eşleşti."
        elif preferred_topic_id:
            affinity_raw = 0.20
            affinity_explanation = f"Farklı bir konu/küme alanına ait ('{post.topic_title}')."
        else:
            affinity_raw = 0.50
            affinity_explanation = "Özel bir konu filtresi seçilmediği için standart nötr konu puanı uygulandı."

        affinity_weight = 25.0
        affinity_impact = affinity_raw * affinity_weight

        # Factor 3: Recency Decay (w = 20)
        recency_raw = self._calculate_recency_score(post.created_at)
        recency_weight = 20.0
        recency_impact = recency_raw * recency_weight

        # Factor 4: Diversity & Discovery Boost (w = 15)
        diversity_raw = 0.75 if post.perspective in ["critical", "academic", "expert"] else 0.45
        diversity_weight = 15.0
        diversity_impact = diversity_raw * diversity_weight

        # Factor 5 (Penalty): Repetition Penalty (w = -20)
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

        # Total Score Calculation
        positive_total = interest_impact + affinity_impact + recency_impact + diversity_impact
        negative_total = abs(rep_impact) + abs(safety_impact)
        final_score = max(0.0, min(100.0, round(positive_total - negative_total, 1)))

        mode_label = "ModernBERT Vektör Benzerliği" if self.model_manager.mode == "ml" else "Demo Sezgisel Eşleşme"

        factors = [
            ScoreFactor(
                factor_name="interest_match",
                label=f"Anlamsal İlgi Eşleşmesi ({mode_label})",
                weight=interest_weight,
                raw_score=round(interest_raw, 2),
                weighted_impact=round(interest_impact, 1),
                is_penalty=False,
                explanation=f"Seçili ilgi alanlarınızla anlamsal profil benzerliği: %{interest_raw * 100:.0f}.",
            ),
            ScoreFactor(
                factor_name="topic_affinity",
                label="Konu / Küme Yakınlığı",
                weight=affinity_weight,
                raw_score=round(affinity_raw, 2),
                weighted_impact=round(affinity_impact, 1),
                is_penalty=False,
                explanation=affinity_explanation,
            ),
            ScoreFactor(
                factor_name="recency",
                label="İçerik Güncelliği",
                weight=recency_weight,
                raw_score=round(recency_raw, 2),
                weighted_impact=round(recency_impact, 1),
                is_penalty=False,
                explanation="Gönderinin yayınlanma tazeliği ve zaman sönümleme puanı.",
            ),
            ScoreFactor(
                factor_name="diversity_boost",
                label="Perspektif Çeşitliliği & Keşif",
                weight=diversity_weight,
                raw_score=round(diversity_raw, 2),
                weighted_impact=round(diversity_impact, 1),
                is_penalty=False,
                explanation="Farklı bakış açıları (uzman/eleştirel/akademik) yankı odasını kırmak için ödüllendirildi.",
            ),
            ScoreFactor(
                factor_name="repetition_penalty",
                label="Tekrar Eden İçerik Cezası",
                weight=rep_weight,
                raw_score=round(rep_raw, 2),
                weighted_impact=round(rep_impact, 1),
                is_penalty=True,
                explanation="Aynı veya benzer metin tekrarı saptandığında puan düşürülür."
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
                explanation=f"Moderasyon risk puanı: {safety_risk_raw:.2f}"
                if safety_risk_raw > 0
                else "Güvenlik riski saptanmadı.",
            ),
        ]

        summary_reason = self._generate_summary_reason(
            interest_raw=interest_raw,
            affinity_raw=affinity_raw,
            recency_raw=recency_raw,
            diversity_raw=diversity_raw,
            safety_risk_raw=safety_risk_raw,
            rep_raw=rep_raw,
            topic_title=post.topic_title,
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
            return max(0.1, min(1.0, 1.0 / (1.0 + (diff_hours / 24.0))))
        except Exception:
            return 0.5

    def _generate_summary_reason(
        self,
        interest_raw: float,
        affinity_raw: float,
        recency_raw: float,
        diversity_raw: float,
        safety_risk_raw: float,
        rep_raw: float,
        topic_title: str,
    ) -> str:
        """Generate strictly grounded explanation prose based ONLY on evaluated factors."""
        # Check penalties first
        if safety_risk_raw >= 0.40:
            return f"Bu gönderi güvenlik risk sinyali (%{safety_risk_raw*100:.0f}) içerdiği için cezalandırılmıştır."
        if rep_raw >= 0.40:
            return f"Bu gönderi tekrarlı bot/spam örüntüsü (%{rep_raw*100:.0f}) tespit edildiği için cezalandırılmıştır."

        reasons = []
        if interest_raw >= 0.65:
            reasons.append(f"ilgi profilinizle yüksek anlamsal benzerlik (%{interest_raw*100:.0f})")
        if affinity_raw >= 0.80:
            reasons.append(f"'{topic_title}' kategorisi yakınlığı")
        if diversity_raw >= 0.70:
            reasons.append("farklı uzman/eleştirel bakış açısı ödülü")
        if recency_raw >= 0.75:
            reasons.append("içerik güncelliği")

        if reasons:
            return f"Bu gönderi {', '.join(reasons)} faktörleri doğrultusunda önerilmektedir."
        return f"'{topic_title}' kategorisindeki güncel ve dengeli paylaşımları keşfetmeniz için önerilmektedir."
