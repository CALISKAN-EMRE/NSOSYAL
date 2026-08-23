"""Comprehensive unit tests for the Phase 2C Moderation, Spam, Repetition, and Coordination Pipeline."""

import pytest
from datetime import datetime, timezone
from app.models.post import Post, Author, PostMetrics
from backend.app.moderation.base import (
    HazardCategory,
    HazardScores,
    ReviewPriority,
    ModerationAnalysisRequest,
)
from backend.app.moderation.guardrail_classifier import DemoGuardrailClassifier
from backend.app.moderation.spam_detector import SpamDetector
from backend.app.moderation.repetition_detector import RepetitionDetector
from backend.app.moderation.coordination_detector import CoordinationDetector
from backend.app.moderation.policy import ModerationPolicy, DEFAULT_CALIBRATED_THRESHOLDS
from backend.app.moderation.fusion_service import ModerationFusionService
from backend.app.services.safety_service import SafetyService
from app.models.safety import SafetyAnalysisRequest


@pytest.fixture
def demo_guardrail():
    return DemoGuardrailClassifier()


@pytest.fixture
def moderation_policy():
    return ModerationPolicy()


@pytest.fixture
def fusion_service(demo_guardrail, moderation_policy):
    return ModerationFusionService(classifier=demo_guardrail, policy=moderation_policy)


@pytest.fixture
def sample_clean_posts():
    return [
        Post(
            id="p-1",
            author=Author(id="u-1", name="Öğretmen Ali", handle="@ali_ogretmen"),
            text="Eğitimde yapay zekâ araçlarının doğru kullanımı öğrenci motivasyonunu artırıyor.",
            created_at="2026-08-23T10:00:00Z",
            topic_id="egitim",
            topic_title="Eğitim ve Teknoloji",
            metrics=PostMetrics(likes=10, reposts=2, replies=1),
        ),
        Post(
            id="p-2",
            author=Author(id="u-2", name="Mühendis Veli", handle="@veli_dev"),
            text="Pardus ve açık kaynak yazılımlar kamu bilişim altyapısında güvenlik sağlıyor.",
            created_at="2026-08-23T10:05:00Z",
            topic_id="kamu-bt",
            topic_title="Açık Kaynak",
            metrics=PostMetrics(likes=20, reposts=5, replies=2),
        ),
    ]


def test_guardrail_classifier_interface(demo_guardrail):
    """Test that guardrail classifier returns all 11 exact taxonomy labels."""
    scores = demo_guardrail.classify("Bu tamamen zararsız normal bir tartışma metnidir.")
    assert isinstance(scores, HazardScores)
    scores_dict = scores.to_dict()

    expected_labels = [cat.value for cat in HazardCategory]
    for lbl in expected_labels:
        assert lbl in scores_dict
        assert 0.0 <= scores_dict[lbl] <= 1.0

    assert scores.unsafe < 0.20


def test_no_arbitrary_hazard_label_invention(demo_guardrail):
    """Verify that hazard scores only contain official ModernBERT-TR Guardrail categories."""
    scores = demo_guardrail.classify("Tehdit ve hakaret içeren metin.")
    valid_categories = {cat.value for cat in HazardCategory}
    for field_name in HazardScores.model_fields.keys():
        assert field_name in valid_categories


def test_calibrated_threshold_loading(moderation_policy):
    """Verify that policy correctly loads thresholds and defaults."""
    for cat in HazardCategory:
        thresh = moderation_policy.get_threshold(cat.value)
        assert 0.10 <= thresh <= 0.90
        assert thresh == DEFAULT_CALIBRATED_THRESHOLDS[cat.value]


def test_spam_detector_features():
    """Verify spam detector link density, TLD, uppercase, and promotional keywords."""
    detector = SpamDetector()

    # Clean text
    clean_ev = detector.analyze("Yarın saat 14:00'te yapay zekâ konferansı başlayacak.")
    assert clean_ev.spam_score < 0.20
    assert clean_ev.link_count == 0

    # Spam text with suspicious URLs and uppercase
    spam_text = "İNANILMAZ KAZANÇ FIRSATI!!! HEMEN TIKLA http://link-spam.xyz http://promo-fake.site BEDAVA KAZAN!!!"
    spam_ev = detector.analyze(spam_text)
    assert spam_ev.spam_score >= 0.70
    assert spam_ev.link_count >= 2
    assert spam_ev.suspicious_tld_detected is True
    assert spam_ev.uppercase_ratio > 0.40
    assert len(spam_ev.signals) >= 2


def test_repetition_detector_within_and_corpus(sample_clean_posts):
    """Verify within-text repetition and cross-corpus duplicate detection."""
    detector = RepetitionDetector()

    # Within text repetition
    rep_text = "kazan kazan kazan kazan hediye hediye hediye hediye tıkla tıkla tıkla tıkla"
    rep_ev = detector.analyze(rep_text)
    assert rep_ev.within_text_word_repetition > 0.50

    # Cross-corpus duplicate
    dup_text = "Eğitimde yapay zekâ araçlarının doğru kullanımı öğrenci motivasyonunu artırıyor."
    dup_ev = detector.analyze(dup_text, existing_posts=sample_clean_posts)
    assert dup_ev.corpus_duplicate_count >= 1
    assert "p-1" in dup_ev.duplicate_post_ids
    assert dup_ev.repetition_score >= 0.40


def test_coordination_detector_evidence(sample_clean_posts):
    """Verify that distinct accounts posting identical text in short windows trigger coordination risk."""
    detector = CoordinationDetector()

    target_text = "Eğitimde yapay zekâ araçlarının doğru kullanımı öğrenci motivasyonunu artırıyor."
    coord_ev = detector.analyze(
        text=target_text,
        current_post_id="p-new",
        current_author_id="user-different-99",
        current_created_at=datetime.now(timezone.utc),
        existing_posts=sample_clean_posts,
    )

    assert coord_ev.suspected_coordination_score >= 0.50
    assert len(coord_ev.participating_authors) >= 1
    assert "u-1" in coord_ev.participating_authors
    assert len(coord_ev.signals) >= 1
    assert coord_ev.signals[0].category == "coordination"


def test_moderation_fusion_transparency(fusion_service, sample_clean_posts):
    """Verify transparent multi-dimensional output without opaque single-score masking."""
    req = ModerationAnalysisRequest(
        text="Sen tam bir sahtekar ve rezil bir yalancısın!",
        post_id="test-tox",
        author_id="user-t1",
    )
    resp = fusion_service.analyze(req, existing_posts=sample_clean_posts)
    r_vec = resp.risk_vector

    assert r_vec.review_priority in [ReviewPriority.HIGH, ReviewPriority.MEDIUM]
    assert r_vec.human_review_recommended is True
    assert r_vec.hazard_scores.HARASSMENT_OFFENSIVE >= 0.40
    assert len(r_vec.summary_explanation) > 0
    assert "Moderasyon İnceleme Önceliği" in r_vec.summary_explanation


def test_human_review_flag_behavior(fusion_service):
    """Test that clean posts do not trigger human review while severe posts do."""
    # Clean
    clean_req = ModerationAnalysisRequest(text="Bugün hava çok güzel, kütüphanede ders çalışıyorum.")
    clean_resp = fusion_service.analyze(clean_req)
    assert clean_resp.risk_vector.human_review_recommended is False
    assert clean_resp.risk_vector.review_priority == ReviewPriority.LOW

    # Severe insult/threat
    tox_req = ModerationAnalysisRequest(text="Seni bulup öldüreceğim, rezil pislik!")
    tox_resp = fusion_service.analyze(tox_req)
    assert tox_resp.risk_vector.human_review_recommended is True
    assert tox_resp.risk_vector.review_priority in [ReviewPriority.HIGH, ReviewPriority.CRITICAL]


def test_safety_service_legacy_api_bridge(fusion_service, sample_clean_posts):
    """Verify that SafetyService correctly bridges the legacy API schema to the new moderation vector."""
    safety_svc = SafetyService(fusion_service=fusion_service)
    req = SafetyAnalysisRequest(
        text="Ücretsiz 500 USDT airdrop hemen tıkla http://link-spam.xyz",
        post_id="spam-p",
        author_id="bot-1",
    )
    resp = safety_svc.analyze_text(req, existing_posts=sample_clean_posts)

    assert resp.risk_vector.spam_score >= 0.50
    assert resp.risk_vector.human_review_recommended is True
    assert resp.risk_vector.review_priority in ["HIGH", "CRITICAL", "MEDIUM"]
    assert resp.risk_vector.hazard_scores is not None
    assert "unsafe" in resp.risk_vector.hazard_scores
