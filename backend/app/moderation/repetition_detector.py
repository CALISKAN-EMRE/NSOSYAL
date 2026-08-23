"""Repetition and near-duplicate detector for NSosyal Pusula."""

import re
from typing import List, Optional, Any
try:
    from app.moderation.base import RepetitionEvidence, EvidenceSignal
except ImportError:
    from backend.app.moderation.base import RepetitionEvidence, EvidenceSignal


class RepetitionDetector:
    """Detects within-text repetitive spam and cross-corpus duplicate templates."""

    def analyze(
        self,
        text: str,
        current_post_id: Optional[str] = None,
        existing_posts: Optional[List[Any]] = None,
    ) -> RepetitionEvidence:
        signals: List[EvidenceSignal] = []

        # 1. Within-text word repetition ratio
        words = [w.lower().strip(".,!?:;\"'()[]{}") for w in text.split()]
        meaningful_words = [w for w in words if len(w) > 2]
        within_rep_ratio = 0.0

        if len(meaningful_words) >= 4:
            unique_words = set(meaningful_words)
            within_rep_ratio = 1.0 - (len(unique_words) / len(meaningful_words))
            if within_rep_ratio > 0.40:
                signals.append(
                    EvidenceSignal(
                        rule_id="RULE-REP-TEXT",
                        category="repetition",
                        description="Metin içinde aşırı tekrarlayan kelime/cümlecik kalıbı saptandı.",
                        severity="warning",
                        confidence=round(within_rep_ratio, 3),
                        detail=f"Tekrarlayan kelime yoğunluğu: %{within_rep_ratio * 100:.1f}",
                    )
                )

        # 2. Cross-post exact and fuzzy duplicate matching
        duplicate_post_ids: List[str] = []
        normalized_current = self._normalize_text(text)

        if existing_posts and len(normalized_current) > 15:
            for p in existing_posts:
                p_id = getattr(p, "id", None) or (p.get("id") if isinstance(p, dict) else None)
                p_text = getattr(p, "text", None) or (p.get("text") if isinstance(p, dict) else None)

                if not p_text or (current_post_id and p_id == current_post_id):
                    continue

                normalized_p = self._normalize_text(p_text)
                if normalized_current == normalized_p or (
                    len(normalized_current) > 30 and normalized_current in normalized_p
                ) or (
                    len(normalized_p) > 30 and normalized_p in normalized_current
                ):
                    if p_id:
                        duplicate_post_ids.append(str(p_id))

        corpus_dup_count = len(duplicate_post_ids)
        corpus_score = min(1.0, corpus_dup_count * 0.45) if corpus_dup_count > 0 else 0.0

        if corpus_dup_count > 0:
            signals.append(
                EvidenceSignal(
                    rule_id="RULE-REP-CORPUS",
                    category="repetition",
                    description="Benzer veya birebir aynı metin yakın zamanlı başka paylaşımlarda bulundu.",
                    severity="warning" if corpus_dup_count == 1 else "critical",
                    confidence=round(corpus_score, 3),
                    detail=f"Eşleşen paylaşım sayısı: {corpus_dup_count} (ID: {', '.join(duplicate_post_ids[:3])})",
                )
            )

        final_repetition_score = max(within_rep_ratio * 0.70, corpus_score)

        return RepetitionEvidence(
            repetition_score=round(min(1.0, final_repetition_score), 4),
            within_text_word_repetition=round(within_rep_ratio, 4),
            corpus_duplicate_count=corpus_dup_count,
            duplicate_post_ids=duplicate_post_ids,
            signals=signals,
        )

    def _normalize_text(self, text: str) -> str:
        text = re.sub(r"https?://\S+", "", text)
        text = re.sub(r"[^\w\s]", "", text)
        return " ".join(text.lower().split())
