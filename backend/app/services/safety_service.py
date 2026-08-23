import re
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


class SafetyService:
    """Heuristic Safety & Moderation Signal Engine (Phase 1 Prototype).

    IMPORTANT NOTE:
    This service produces probabilistic risk signals and moderation review indicators.
    It does NOT make definitive claims about hate speech, illegality, or malicious intent.
    In Phase 1, it operates purely via deterministic rules and heuristics; ML-based Turkish
    toxicity and classification models will be integrated in Phase 2.
    """

    # Non-definitive indicator wordlists for heuristic inspection
    _HEURISTIC_RISK_KEYWORDS = {
        "dolandırıcı": 0.5,
        "sahtekar": 0.5,
        "ahmak": 0.4,
        "aptal": 0.4,
        "rezil": 0.3,
        "bedava kazanç": 0.7,
        "hemen tıkla": 0.7,
        "şifresiz takipçi": 0.8,
        "garantili para": 0.8,
    }

    _SPAM_URL_PATTERNS = [
        r"https?://bit\.ly/\S+",
        r"https?://t\.co/\S+",
        r"https?://\S+\.(?:xyz|site|top|click)/\S*",
    ]

    def analyze_text(
        self,
        request: SafetyAnalysisRequest,
        existing_posts: Optional[List[Post]] = None,
    ) -> SafetyAnalysisResponse:
        """Run deterministic heuristic safety checks on input text."""
        text = request.text
        signals: List[SafetySignal] = []

        # 1. Format Anomaly & Uppercase Check
        uppercase_ratio = self._calculate_uppercase_ratio(text)
        if uppercase_ratio > 0.45 and len(text) > 20:
            signals.append(
                SafetySignal(
                    rule_id="RULE-FMT-001",
                    category="format_anomaly",
                    description="Yüksek oranda büyük harf kullanımı tespit edildi (Bağırma/Dikkat çekme formatı).",
                    severity="warning",
                    confidence=min(1.0, uppercase_ratio),
                    detail=f"Büyük harf oranı: %{uppercase_ratio * 100:.1f}",
                )
            )

        # 2. Spam & Link Density Check
        link_count = len(re.findall(r"https?://\S+", text))
        has_suspicious_url = any(
            re.search(pat, text, re.IGNORECASE) for pat in self._SPAM_URL_PATTERNS
        )
        spam_score = 0.0

        if link_count >= 2 or has_suspicious_url:
            spam_score = min(1.0, 0.4 + (link_count * 0.2) + (0.3 if has_suspicious_url else 0.0))
            signals.append(
                SafetySignal(
                    rule_id="RULE-SPAM-001",
                    category="spam",
                    description="Yüksek bağlantı yoğunluğu veya şüpheli yönlendirme linkleri tespit edildi.",
                    severity="critical" if spam_score > 0.7 else "warning",
                    confidence=spam_score,
                    detail=f"Tespit edilen bağlantı sayısı: {link_count}",
                )
            )

        # 3. Repetitive Word / Character Patterns Check
        repeated_word_ratio = self._calculate_word_repetition(text)
        if repeated_word_ratio > 0.35 and len(text.split()) >= 4:
            signals.append(
                SafetySignal(
                    rule_id="RULE-REP-001",
                    category="repetition",
                    description="Metin içinde aşırı tekrarlayan kelime kalıbı saptandı.",
                    severity="warning",
                    confidence=repeated_word_ratio,
                    detail=f"Tekrar eden kelime yoğunluğu: %{repeated_word_ratio * 100:.1f}",
                )
            )

        # 4. Cross-Post Exact/Fuzzy Duplicate & Coordination Check
        repetition_score = 0.0
        coordination_score = 0.0

        if existing_posts:
            dup_count, is_cross_author = self._check_corpus_duplicates(
                text=text,
                current_post_id=request.post_id,
                current_author_id=request.author_id,
                existing_posts=existing_posts,
            )

            if dup_count > 0:
                repetition_score = min(1.0, dup_count * 0.4)
                signals.append(
                    SafetySignal(
                        rule_id="RULE-CORP-001",
                        category="repetition",
                        description="Benzer veya birebir aynı metin yakın zamanlı başka paylaşımlarda bulundu.",
                        severity="warning",
                        confidence=repetition_score,
                        detail=f"Eşleşen paylaşım sayısı: {dup_count}",
                    )
                )

                if is_cross_author:
                    coordination_score = min(1.0, 0.5 + (dup_count * 0.25))
                    signals.append(
                        SafetySignal(
                            rule_id="RULE-COORD-001",
                            category="coordination",
                            description="Farklı hesaplardan aynı şablon metnin paylaşılması (Olası koordineli yayın şüphesi).",
                            severity="critical",
                            confidence=coordination_score,
                            detail="Farklı kullanıcılar tarafından paylaşılan eş metin.",
                        )
                    )

        # 5. Heuristic Language & Sensitivity Check (Non-definitive indicator)
        toxicity_score = 0.0
        matched_indicators = []
        lower_text = text.lower()

        for kw, weight in self._HEURISTIC_RISK_KEYWORDS.items():
            if kw in lower_text:
                matched_indicators.append(kw)
                toxicity_score = max(toxicity_score, weight)

        if matched_indicators:
            signals.append(
                SafetySignal(
                    rule_id="RULE-LANG-001",
                    category="language_risk_indicator",
                    description="Metinde moderasyon incelemesi önerilen sert/riskli dil kalıpları saptandı (Sezgisel Sinyal).",
                    severity="warning" if toxicity_score < 0.6 else "critical",
                    confidence=toxicity_score,
                    detail=f"İnceleme önerilen kalıplar: {', '.join(matched_indicators)}",
                )
            )

        # Aggregate Risk Vector
        overall_risk = max(
            spam_score * 0.8,
            repetition_score * 0.6,
            coordination_score * 0.9,
            toxicity_score * 0.7,
            (spam_score + repetition_score + coordination_score + toxicity_score) / 3.0,
        )
        overall_risk = min(1.0, max(0.0, overall_risk))

        if overall_risk >= 0.65:
            risk_level = RiskLevel.HIGH
        elif overall_risk >= 0.30:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        human_review = risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH] or len(signals) > 0

        risk_vector = SafetyRiskVector(
            spam_score=round(spam_score, 2),
            repetition_score=round(repetition_score, 2),
            coordination_score=round(coordination_score, 2),
            toxicity_score=round(toxicity_score, 2),
            hate_speech_score=0.0,  # Explicitly 0.0 in Phase 1; requires trained ML model
            overall_risk_score=round(overall_risk, 2),
            risk_level=risk_level,
            signals=signals,
            is_actionable=overall_risk >= 0.4,
            human_review_recommended=human_review,
        )

        return SafetyAnalysisResponse(
            text_length=len(text),
            risk_vector=risk_vector,
            analyzed_at=datetime.now(timezone.utc).isoformat(),
        )

    def _calculate_uppercase_ratio(self, text: str) -> float:
        letters = [c for c in text if c.isalpha()]
        if not letters:
            return 0.0
        upper_letters = [c for c in letters if c.isupper()]
        return len(upper_letters) / len(letters)

    def _calculate_word_repetition(self, text: str) -> float:
        words = [w.lower().strip(".,!?:;\"'()") for w in text.split()]
        words = [w for w in words if len(w) > 2]
        if not words:
            return 0.0
        unique_words = set(words)
        return 1.0 - (len(unique_words) / len(words))

    def _check_corpus_duplicates(
        self,
        text: str,
        current_post_id: Optional[str],
        current_author_id: Optional[str],
        existing_posts: List[Post],
    ) -> tuple[int, bool]:
        normalized_current = self._normalize_for_comparison(text)
        duplicates = 0
        is_cross_author = False

        for p in existing_posts:
            if current_post_id and p.id == current_post_id:
                continue
            normalized_p = self._normalize_for_comparison(p.text)
            if normalized_current == normalized_p or (
                len(normalized_current) > 30 and normalized_current in normalized_p
            ):
                duplicates += 1
                if current_author_id and p.author.id != current_author_id:
                    is_cross_author = True

        return duplicates, is_cross_author

    def _normalize_for_comparison(self, text: str) -> str:
        text = re.sub(r"https?://\S+", "", text)
        text = re.sub(r"[^\w\s]", "", text)
        return " ".join(text.lower().split())
