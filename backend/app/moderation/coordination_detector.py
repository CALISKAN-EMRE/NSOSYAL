"""Coordination and coordinated inauthentic behavior detector for NSosyal Pusula."""

import re
from datetime import datetime
from typing import List, Optional, Any, Dict
from backend.app.moderation.base import CoordinationEvidence, EvidenceSignal


class CoordinationDetector:
    """Detects suspected coordinated inauthentic activity across distinct social accounts."""

    def analyze(
        self,
        text: str,
        current_post_id: Optional[str] = None,
        current_author_id: Optional[str] = None,
        current_created_at: Optional[datetime] = None,
        existing_posts: Optional[List[Any]] = None,
    ) -> CoordinationEvidence:
        signals: List[EvidenceSignal] = []
        similar_post_ids: List[str] = []
        participating_authors: List[str] = []
        shared_urls: List[str] = []

        if not existing_posts:
            return CoordinationEvidence()

        normalized_current = self._normalize_text(text)
        current_urls = set(re.findall(r"https?://\S+", text))
        time_deltas_minutes: List[float] = []

        for p in existing_posts:
            p_id = getattr(p, "id", None) or (p.get("id") if isinstance(p, dict) else None)
            p_text = getattr(p, "text", None) or (p.get("text") if isinstance(p, dict) else None)
            p_author_obj = getattr(p, "author", None) or (p.get("author") if isinstance(p, dict) else None)
            
            p_author_id = getattr(p_author_obj, "id", None) if p_author_obj else (p_author_obj.get("id") if isinstance(p_author_obj, dict) else None)
            p_created_at = getattr(p, "created_at", None) or (p.get("created_at") if isinstance(p, dict) else None)

            if not p_text or (current_post_id and p_id == current_post_id):
                continue

            normalized_p = self._normalize_text(p_text)
            is_text_match = (
                normalized_current == normalized_p
                or (len(normalized_current) > 30 and normalized_current in normalized_p)
                or (len(normalized_p) > 30 and normalized_p in normalized_current)
            )

            p_urls = set(re.findall(r"https?://\S+", p_text))
            common_urls = current_urls.intersection(p_urls)

            # Check if this represents cross-account activity
            is_different_author = (
                current_author_id is not None
                and p_author_id is not None
                and current_author_id != p_author_id
            )

            if (is_text_match or (common_urls and len(common_urls) >= 2)) and is_different_author:
                if p_id:
                    similar_post_ids.append(str(p_id))
                if p_author_id:
                    participating_authors.append(str(p_author_id))
                for u in common_urls:
                    shared_urls.append(u)

                # Compute time delta if timestamps are parseable
                if current_created_at and p_created_at:
                    try:
                        t1 = current_created_at if isinstance(current_created_at, datetime) else datetime.fromisoformat(str(current_created_at).replace("Z", "+00:00"))
                        t2 = p_created_at if isinstance(p_created_at, datetime) else datetime.fromisoformat(str(p_created_at).replace("Z", "+00:00"))
                        delta_min = abs((t1 - t2).total_seconds()) / 60.0
                        time_deltas_minutes.append(delta_min)
                    except Exception:
                        pass

        distinct_authors_count = len(set(participating_authors))
        coordination_score = 0.0
        avg_time_window: Optional[float] = None

        if distinct_authors_count >= 1:
            base_score = 0.50 + (min(distinct_authors_count, 5) * 0.10)
            if time_deltas_minutes:
                avg_time_window = round(sum(time_deltas_minutes) / len(time_deltas_minutes), 1)
                if avg_time_window < 120.0:  # within 2 hours
                    base_score += 0.15

            coordination_score = min(1.0, base_score)
            signals.append(
                EvidenceSignal(
                    rule_id="RULE-COORD-001",
                    category="coordination",
                    description="Farklı hesaplardan eşzamanlı benzer şablon metin/link paylaşımı (Olası koordineli yayın şüphesi).",
                    severity="critical" if coordination_score > 0.70 else "warning",
                    confidence=round(coordination_score, 3),
                    detail=f"Farklı hesap sayısı: {distinct_authors_count}, Eşleşen ID'ler: {', '.join(similar_post_ids[:3])}",
                )
            )

        return CoordinationEvidence(
            suspected_coordination_score=round(coordination_score, 4),
            similar_post_ids=similar_post_ids,
            participating_authors=list(set(participating_authors)),
            time_window_minutes=avg_time_window,
            shared_urls_or_domains=list(set(shared_urls)),
            signals=signals,
        )

    def _normalize_text(self, text: str) -> str:
        text = re.sub(r"https?://\S+", "", text)
        text = re.sub(r"[^\w\s]", "", text)
        return " ".join(text.lower().split())
