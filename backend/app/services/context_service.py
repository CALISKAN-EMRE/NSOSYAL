from datetime import datetime, timezone
from typing import Dict, List, Optional
from app.models.post import Post
from app.models.context import (
    ContextCard,
    PerspectiveDetail,
    SourceContext,
    TimelineItem,
)
from app.adapters.base import DataSourceAdapter


class ContextService:
    """Context Card Aggregation & Synthesis Engine (Phase 1 Prototype).

    IMPORTANT NOTE:
    In Phase 1, this service uses deterministic topic indexing and rule-based metadata aggregation.
    It does NOT claim to use live semantic embeddings (e.g. BERT/MiniLM) or unsupervised clustering (HDBSCAN),
    which are scheduled for Phase 2 integration.
    """

    def __init__(self, data_adapter: DataSourceAdapter):
        self.adapter = data_adapter

    def get_context_card(self, topic_id: str) -> Optional[ContextCard]:
        """Generate or retrieve an aggregated Context Card for a topic."""
        posts = self.adapter.get_posts(topic_id=topic_id, limit=100)
        topic = self.adapter.get_topic_by_id(topic_id)

        if not posts and not topic:
            return None

        topic_title = topic.title if topic else (posts[0].topic_title if posts else topic_id)

        # 1. Extract Key Themes from Tags & Word Frequencies
        key_themes = self._extract_key_themes(posts)

        # 2. Group Perspectives (Supportive, Critical, Neutral)
        perspectives = self._aggregate_perspectives(posts)

        # 3. Build Timeline
        timeline = self._build_timeline(posts)

        # 4. Aggregate Sources
        sources = self._aggregate_sources(posts)

        # 5. Generate Concise Summary
        summary = self._generate_topic_summary(topic_title, perspectives, len(posts))

        total_participants = len(set(p.author.id for p in posts))

        return ContextCard(
            id=f"card-{topic_id}",
            topic_id=topic_id,
            topic_title=topic_title,
            summary=summary,
            key_themes=key_themes,
            perspectives=perspectives,
            timeline=timeline,
            sources=sources,
            total_posts=len(posts),
            total_participants=total_participants,
            generated_at=datetime.now(timezone.utc).isoformat(),
            method="deterministic_metadata_aggregation (Phase 1 Prototype)",
        )

    def _extract_key_themes(self, posts: List[Post]) -> List[str]:
        all_tags = []
        for p in posts:
            all_tags.extend(p.tags)

        # Count frequencies
        freq: Dict[str, int] = {}
        for t in all_tags:
            freq[t] = freq.get(t, 0) + 1

        sorted_tags = sorted(freq.keys(), key=lambda k: freq[k], reverse=True)
        return sorted_tags[:6] if sorted_tags else ["Genel Tartışma", "Gündem"]

    def _aggregate_perspectives(self, posts: List[Post]) -> List[PerspectiveDetail]:
        supportive_posts = [p for p in posts if "supportive" in (p.perspective or "")]
        critical_posts = [p for p in posts if "critical" in (p.perspective or "")]
        neutral_posts = [
            p
            for p in posts
            if p not in supportive_posts and p not in critical_posts
        ]

        perspectives: List[PerspectiveDetail] = []

        if supportive_posts:
            perspectives.append(
                PerspectiveDetail(
                    perspective_type="supportive",
                    label="Destekleyen ve Olumlu Görüşler",
                    summary="Uygulamanın verimlilik, hız ve teknolojik ilerleme sağladığı, adaptasyonun teşvik edilmesi gerektiği vurgulanıyor.",
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
                    summary="Etik riskler, altyapı yetersizlikleri, şeffaflık eksikliği ve denetim mekanizmalarının belirsizliği konusunda endişeler dile getiriliyor.",
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
                    summary="Mevzuat duyuruları, kurum açıklamaları ve sektörel göstergeler içeren kurumsal veri akışı.",
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
            # Create timeline milestone for posts with notable engagement or news/academic/official sources
            if p.source_type in ["news_outlet", "official_source", "academic"] or (
                p.metrics and p.metrics.likes > 400
            ):
                summary = p.text[:120] + "..." if len(p.text) > 120 else p.text
                timeline.append(
                    TimelineItem(
                        timestamp=p.created_at,
                        title=f"{p.author.name} Açıklaması / Paylaşımı",
                        summary=summary,
                        related_post_id=p.id,
                    )
                )

        return timeline[:6]

    def _aggregate_sources(self, posts: List[Post]) -> List[SourceContext]:
        source_counts: Dict[str, Dict] = {}
        for p in posts:
            stype = p.source_type
            sname = p.author.name if stype in ["news_outlet", "official_source", "academic"] else "Kullanıcı Deneyimleri"
            key = f"{stype}:{sname}"
            if key not in source_counts:
                source_counts[key] = {
                    "source_name": sname,
                    "source_type": stype,
                    "count": 0,
                    "note": self._get_source_note(stype),
                }
            source_counts[key]["count"] += 1

        return [
            SourceContext(
                source_name=v["source_name"],
                source_type=v["source_type"],
                mention_count=v["count"],
                reliability_note=v["note"],
            )
            for v in source_counts.values()
        ]

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
            f"'{topic_title}' konusu etrafında toplam {post_count} adet paylaşım incelendi. "
            f"Tartışmada {len(perspectives)} temel bakış açısı öne çıkıyor. "
            "Taraflar teknolojik fırsatlar ve kazanımları savunurken, denetim, etik ve altyapı eksiklikleri temel çekince noktalarını oluşturuyor."
        )
