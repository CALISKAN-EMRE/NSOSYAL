"""Spam and promotional text detector for NSosyal Pusula."""

import re
from typing import List, Tuple
try:
    from app.moderation.base import SpamEvidence, EvidenceSignal
except ImportError:
    from backend.app.moderation.base import SpamEvidence, EvidenceSignal


class SpamDetector:
    """Deterministic, explainable spam, link-density, and promotional anomaly detector."""

    _SPAM_DOMAINS_TLD = [
        r"https?://\S+\.(?:xyz|site|top|click|link|shop|icu|vip|buzz|cfd|rest|monster)/\S*",
        r"https?://(?:bit\.ly|tinyurl\.com|is\.gd|cutt\.ly|t\.me)/\S*",
        r"http://(?:hediye-sahte|promo-fake|link-spam)\.\w+",
    ]

    _PROMOTIONAL_PHRASES = [
        "ücretsiz hediye", "hediye çeki", "hemen tıkla", "tıklayın ve kazanın",
        "inanılmaz kazanç", "bedava bedava", "bedava bakiye", "link profilde",
        "fırsatı kaçırma", "usdt airdrop", "kripto airdrop", "formu doldurun",
        "dm atın", "anında hesabında", "para kazanma taktiği"
    ]

    def analyze(self, text: str) -> SpamEvidence:
        signals: List[EvidenceSignal] = []
        lower_t = text.lower()

        # 1. Link Count & Suspicious Domains
        links = re.findall(r"https?://\S+", text)
        link_count = len(links)
        has_suspicious_tld = any(
            re.search(pat, text, re.IGNORECASE) for pat in self._SPAM_DOMAINS_TLD
        )

        spam_score = 0.0

        if link_count >= 2 or has_suspicious_tld:
            base_score = 0.35 + (link_count * 0.20) + (0.35 if has_suspicious_tld else 0.0)
            spam_score = min(1.0, base_score)
            signals.append(
                EvidenceSignal(
                    rule_id="RULE-SPAM-001",
                    category="spam",
                    description="Yüksek bağlantı yoğunluğu veya şüpheli/kısaltılmış yönlendirme linki saptandı.",
                    severity="critical" if spam_score > 0.70 else "warning",
                    confidence=round(spam_score, 3),
                    detail=f"Bağlantı sayısı: {link_count}, Şüpheli TLD: {'Var' if has_suspicious_tld else 'Yok'}",
                )
            )

        # 2. Uppercase Shouting Ratio
        letters = [c for c in text if c.isalpha()]
        uppercase_ratio = 0.0
        if letters and len(text) > 20:
            upper_letters = [c for c in letters if c.isupper()]
            uppercase_ratio = len(upper_letters) / len(letters)
            if uppercase_ratio > 0.45:
                fmt_score = min(1.0, uppercase_ratio)
                spam_score = max(spam_score, fmt_score * 0.70)
                signals.append(
                    EvidenceSignal(
                        rule_id="RULE-FMT-001",
                        category="format_anomaly",
                        description="Yüksek oranda büyük harf kullanımı saptandı (Bağırma/Dikkat çekme formatı).",
                        severity="warning",
                        confidence=round(fmt_score, 3),
                        detail=f"Büyük harf oranı: %{uppercase_ratio * 100:.1f}",
                    )
                )

        # 3. Promotional Keyword / Phrase Matches
        matched_promo = [p for p in self._PROMOTIONAL_PHRASES if p in lower_t]
        if matched_promo:
            promo_weight = min(1.0, len(matched_promo) * 0.30)
            spam_score = max(spam_score, promo_weight)
            signals.append(
                EvidenceSignal(
                    rule_id="RULE-SPAM-PROMO",
                    category="spam",
                    description="Metinde tipik spam/promosyon çağrı kalıpları saptandı.",
                    severity="warning" if len(matched_promo) == 1 else "critical",
                    confidence=round(promo_weight, 3),
                    detail=f"Eşleşen kalıplar: {', '.join(matched_promo[:3])}",
                )
            )

        return SpamEvidence(
            spam_score=round(min(1.0, spam_score), 4),
            link_count=link_count,
            suspicious_tld_detected=has_suspicious_tld,
            uppercase_ratio=round(uppercase_ratio, 4),
            promotional_keyword_hits=matched_promo,
            signals=signals,
        )
