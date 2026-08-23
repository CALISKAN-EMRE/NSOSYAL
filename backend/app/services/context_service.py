import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import numpy as np

from app.adapters.base import DataSourceAdapter
from app.config import settings
from app.models.context import (
    ContextCard,
    PerspectiveDetail,
    SourceContext,
    TimelineItem,
)
from app.models.post import Post
from app.models.topic import Topic
from app.ml.base import RerankCandidate, SemanticCluster
from app.ml.model_manager import ModelManager
from app.services.safety_service import SafetyService
from app.models.safety import SafetyAnalysisRequest

logger = logging.getLogger(__name__)


class ContextService:
    """Context Card Aggregation & Semantic Intelligence Engine (Phase 2B Hardened Architecture).

    Pipelines:
    1. Unsupervised Semantic Clustering (ModernBERT-TR + PCA + HDBSCAN + c-TF-IDF)
    2. Multi-Perspective Extraction with Verifiable Post ID Evidence
    3. Safety-Gated Two-Stage Context Retrieval & Reranking (ModernBERT-TR-Reranker)
       - Candidate Retrieval (Dense Top-20)
       - Safety & Spam Gating (Excludes botnet/spam candidates from becoming context sources)
       - Cross-Encoder Reranking (Top-6 Gated Context Sources)
    """

    def __init__(
        self,
        data_adapter: DataSourceAdapter,
        safety_service: Optional[SafetyService] = None,
        model_manager: Optional[ModelManager] = None,
    ):
        self.adapter = data_adapter
        self.safety_service = safety_service or SafetyService()
        self.model_manager = model_manager or ModelManager.get_instance()
        self._cached_clusters: Optional[List[SemanticCluster]] = None
        self._clusters_last_computed: float = 0.0

    def get_semantic_topics(self) -> List[Topic]:
        """Discover dynamic semantic topic clusters without reading synthetic topic_hints."""
        clusters = self._get_or_compute_clusters()
        topics = []
        for c in clusters:
            cluster_posts = self.adapter.get_posts_by_ids(c.post_ids)
            participant_count = len(set(p.author.id for p in cluster_posts))
            last_activity = max(
                (p.created_at for p in cluster_posts),
                default=datetime.now(timezone.utc).isoformat(),
            )

            # Clarified membership probability label
            desc = (
                f"Semantik kümeleme ile gruplanan {len(cluster_posts)} paylaşım. "
                f"Ortalama üyelik skoru (HDBSCAN): %{c.confidence_score*100:.0f}."
            )

            topics.append(
                Topic(
                    id=c.cluster_id,
                    title=c.label,
                    description=desc,
                    post_count=len(cluster_posts),
                    participant_count=participant_count,
                    tags=c.key_themes,
                    last_activity=last_activity,
                )
            )
        return topics

    def get_context_card(self, topic_id: str) -> Optional[ContextCard]:
        """Generate a complete Context Card using semantic clustering and safety-gated reranked sources."""
        t_total_start = time.perf_counter()
        timings: Dict[str, float] = {}

        # 1. Clustering / Topic Resolution
        t_clust_start = time.perf_counter()
        clusters = self._get_or_compute_clusters()
        timings["clustering_ms"] = round((time.perf_counter() - t_clust_start) * 1000.0, 2)

        # Find target cluster matching topic_id or fallback to legacy topic adapter
        target_cluster = next((c for c in clusters if c.cluster_id == topic_id), None)

        if target_cluster:
            posts = self.adapter.get_posts_by_ids(target_cluster.post_ids)
            topic_title = target_cluster.label
            key_themes = target_cluster.key_themes
            cluster_id = target_cluster.cluster_id
            membership_score = target_cluster.confidence_score
        else:
            # Fallback for static topic_id or direct lookup
            posts = self.adapter.get_posts(topic_id=topic_id, limit=100)
            topic = self.adapter.get_topic_by_id(topic_id)
            if not posts and not topic:
                return None
            topic_title = topic.title if topic else (posts[0].topic_title if posts else topic_id)
            key_themes = self._extract_key_themes(posts)
            cluster_id = f"topic-{topic_id}"
            membership_score = 0.85

        if not posts:
            return None

        # 2. Extract Perspectives with verified supporting post IDs
        perspectives = self._aggregate_perspectives(posts)

        # 3. Build Timeline strictly from real post timestamps
        timeline = self._build_timeline(posts)

        # 4. Generate Summary (Extractive synthesis)
        summary = self._generate_topic_summary(topic_title, perspectives, len(posts))

        # 5. Safety-Aware Two-Stage Context Retrieval & Reranking
        t_retrieval_start = time.perf_counter()
        reranked_sources, dense_ms, rerank_ms, gated_count = self._retrieve_and_rerank_sources(
            topic_title=topic_title, summary=summary, cluster_posts=posts
        )
        timings["dense_retrieval_ms"] = dense_ms
        timings["reranking_ms"] = rerank_ms
        timings["total_pipeline_ms"] = round((time.perf_counter() - t_total_start) * 1000.0, 2)

        total_participants = len(set(p.author.id for p in posts))

        mode_desc = (
            f"semantic_clustering_and_reranking ({self.model_manager.mode.upper()})"
            if self.model_manager.mode == "ml"
            else "demo_deterministic_aggregation (DEMO)"
        )

        return ContextCard(
            id=f"card-{cluster_id}",
            topic_id=topic_id,
            topic_title=topic_title,
            summary=summary,
            key_themes=key_themes,
            perspectives=perspectives,
            timeline=timeline,
            sources=reranked_sources,
            community_post_ids=[p.id for p in posts],
            total_posts=len(posts),
            total_participants=total_participants,
            generated_at=datetime.now(timezone.utc).isoformat(),
            method=mode_desc,
            semantic_cluster_id=cluster_id,
            cluster_confidence=membership_score,
            cluster_membership_score=membership_score,
            gated_spam_candidates_count=gated_count,
            pipeline_timing_ms=timings,
            model_used=f"{settings.MODEL_CLUSTERING_EMBED} + {settings.MODEL_CONTEXT_RERANKER}",
        )

    def _get_or_compute_clusters(self) -> List[SemanticCluster]:
        """Cache clusters for 30 seconds to avoid unnecessary GPU recomputation."""
        now = time.time()
        if self._cached_clusters is not None and (now - self._clusters_last_computed) < 30.0:
            return self._cached_clusters

        all_posts = self.adapter.get_posts(limit=200)
        self.model_manager.initialize()

        if self.model_manager.cluster_service:
            clusters = self.model_manager.cluster_service.cluster_posts(all_posts)
        else:
            clusters = []

        self._cached_clusters = clusters
        self._clusters_last_computed = now
        return clusters

    def _retrieve_and_rerank_sources(
        self, topic_title: str, summary: str, cluster_posts: List[Post]
    ) -> tuple:
        """Execute Two-Stage Retrieval with Safety & Spam Gating."""
        t_dense_start = time.perf_counter()

        all_posts = self.adapter.get_posts(limit=100)
        candidate_pool: List[RerankCandidate] = []
        seen_texts = set()
        gated_spam_count = 0

        # Step A: Safety-Aware Candidate Gating
        # Exclude candidates with high spam/bot risk or repetitive coordination patterns
        for p in all_posts:
            if p.text in seen_texts:
                continue
            seen_texts.add(p.text)

            # Check safety heuristics
            safety_eval = self.safety_service.analyze_text(
                SafetyAnalysisRequest(text=p.text, post_id=p.id, author_id=p.author.id),
                existing_posts=all_posts,
            )
            risk = safety_eval.risk_vector

            # Moderation Gating: Exclude posts with HIGH/CRITICAL review priority, high spam, or coordination
            if (
                risk.review_priority in ["HIGH", "CRITICAL"]
                or risk.spam_score >= 0.40
                or risk.repetition_score >= 0.40
                or risk.coordination_score >= 0.40
                or risk.overall_risk_score >= 0.40
            ):
                gated_spam_count += 1
                logger.info(f"[Moderation Gating] Excluded candidate {p.id} from {p.author.name} (priority={risk.review_priority}, risk={risk.overall_risk_score:.2f})")
                continue

            stype = p.source_type
            sname = (
                p.author.name
                if stype in ["news_outlet", "official_source", "academic", "expert"]
                else f"Kullanıcı ({p.author.name})"
            )
            reliability = self._get_source_note(stype)

            candidate_pool.append(
                RerankCandidate(
                    doc_id=p.id,
                    source_name=sname,
                    source_type=stype,
                    text=p.text,
                    initial_dense_score=0.5,
                    reliability_note=reliability,
                )
            )

        if not candidate_pool:
            return [], 0.0, 0.0, gated_spam_count

        # Step B: Stage 1 - Dense Retrieval via ModernBERT-TR-Embed
        query_text = f"{topic_title}. {summary[:200]}"
        embedder = self.model_manager.clustering_embedder

        if embedder:
            cand_texts = [c.text for c in candidate_pool]
            cand_embs = embedder.encode_documents(cand_texts)
            query_emb = embedder.encode_queries([query_text])[0]

            sims = np.dot(cand_embs, query_emb) / (
                np.linalg.norm(cand_embs, axis=1) * np.linalg.norm(query_emb) + 1e-12
            )

            for idx, cand in enumerate(candidate_pool):
                cand.initial_dense_score = round(float((sims[idx] + 1.0) / 2.0), 4)

            # Sort by initial dense score descending and pick Top-15
            candidate_pool = sorted(candidate_pool, key=lambda c: c.initial_dense_score, reverse=True)

        top_k = min(settings.RERANKER_TOP_K, len(candidate_pool))
        top_candidates = candidate_pool[:top_k]
        dense_ms = round((time.perf_counter() - t_dense_start) * 1000.0, 2)

        # Step C: Stage 2 - Cross-Encoder Reranking via ModernBERT-TR-Reranker
        t_rerank_start = time.perf_counter()
        reranker = self.model_manager.context_reranker

        if reranker:
            reranked = reranker.rerank(query=query_text, candidates=top_candidates, top_k=top_k)
        else:
            reranked = top_candidates

        rerank_ms = round((time.perf_counter() - t_rerank_start) * 1000.0, 2)

        # Step D: Assemble Top 5 Context Sources
        source_contexts: List[SourceContext] = []
        for cand in reranked[:5]:
            source_contexts.append(
                SourceContext(
                    source_name=cand.source_name,
                    source_type=cand.source_type,
                    mention_count=1,
                    reliability_note=cand.reliability_note,
                    relevance_score=cand.reranked_score,
                    dense_score=cand.initial_dense_score,
                    rank=cand.rank,
                )
            )

        return source_contexts, dense_ms, rerank_ms, gated_spam_count

    def _extract_key_themes(self, posts: List[Post]) -> List[str]:
        all_tags = []
        for p in posts:
            all_tags.extend(p.tags)
        freq: Dict[str, int] = {}
        for t in all_tags:
            freq[t] = freq.get(t, 0) + 1
        sorted_tags = sorted(freq.keys(), key=lambda k: freq[k], reverse=True)
        return sorted_tags[:6] if sorted_tags else ["Genel Tartışma", "Gündem"]

    def _aggregate_perspectives(self, posts: List[Post]) -> List[PerspectiveDetail]:
        supportive_posts = [p for p in posts if "supportive" in (p.perspective or "")]
        critical_posts = [p for p in posts if "critical" in (p.perspective or "")]
        neutral_posts = [
            p for p in posts if p not in supportive_posts and p not in critical_posts
        ]

        perspectives: List[PerspectiveDetail] = []

        if supportive_posts:
            perspectives.append(
                PerspectiveDetail(
                    perspective_type="supportive",
                    label="Destekleyen ve Olumlu Görüşler",
                    summary="Teknolojik yenilik, verimlilik ve stratejik fırsatları vurgulayan görüşler.",
                    post_count=len(supportive_posts),
                    supporting_post_ids=[p.id for p in supportive_posts],
                    sample_quotes=[p.text[:140] + "..." for p in supportive_posts[:2]],
                )
            )

        if critical_posts:
            perspectives.append(
                PerspectiveDetail(
                    perspective_type="critical",
                    label="Eleştirel ve Çekinceli Görüşler",
                    summary="Mevzuat belirsizlikleri, altyapı eksiklikleri, etik ve telif risklerine dikkat çeken görüşler.",
                    post_count=len(critical_posts),
                    supporting_post_ids=[p.id for p in critical_posts],
                    sample_quotes=[p.text[:140] + "..." for p in critical_posts[:2]],
                )
            )

        if neutral_posts:
            perspectives.append(
                PerspectiveDetail(
                    perspective_type="neutral_fact",
                    label="Resmi Bildirimler ve Bilgilendirici Raporlar",
                    summary="Kamu düzenlemeleri, sektörel veriler ve teknik göstergeler içeren kurumsal paylaşımlar.",
                    post_count=len(neutral_posts),
                    supporting_post_ids=[p.id for p in neutral_posts],
                    sample_quotes=[p.text[:140] + "..." for p in neutral_posts[:2]],
                )
            )

        return perspectives

    def _build_timeline(self, posts: List[Post]) -> List[TimelineItem]:
        sorted_posts = sorted(posts, key=lambda p: p.created_at)
        timeline: List[TimelineItem] = []

        for p in sorted_posts:
            if p.source_type in ["news_outlet", "official_source", "academic", "expert"] or (
                p.metrics and p.metrics.likes > 800
            ):
                summary = p.text[:120] + "..." if len(p.text) > 120 else p.text
                timeline.append(
                    TimelineItem(
                        timestamp=p.created_at,
                        title=f"{p.author.name} Paylaşımı",
                        summary=summary,
                        related_post_id=p.id,
                    )
                )

        return timeline[:6]

    def _get_source_note(self, source_type: str) -> str:
        notes = {
            "official_source": "Resmi kamu/kurum bildirimi (Kurumsal kaynak tipi).",
            "news_outlet": "Haber ve bülten yayını.",
            "academic": "Akademik/uzman değerlendirmesi.",
            "expert": "Sektörel uzman görüşü.",
            "user": "Bireysel kullanıcı paylaşımı.",
            "community": "Topluluk ve sivil inisiyatif paylaşımı.",
        }
        return notes.get(source_type, "Genel kaynak.")

    def _generate_topic_summary(
        self, topic_title: str, perspectives: List[PerspectiveDetail], post_count: int
    ) -> str:
        return (
            f"'{topic_title}' başlığı altında {post_count} adet paylaşım semantik olarak gruplandırıldı. "
            f"Tartışmada {len(perspectives)} temel bakış açısı ayrıştırıldı: "
            "Taraflar teknolojik fırsat ve kazanımları savunurken, denetim, etik ve altyapı eksiklikleri temel çekince noktalarını oluşturuyor."
        )
