from app.models.safety import SafetyAnalysisRequest, RiskLevel


def test_safety_clean_post(safety_service, json_adapter):
    """Test that a normal constructive post yields LOW risk."""
    clean_text = (
        "Yapay zekâ destekli öğrenme araçlarının sınıf içi etkileşimi artırdığını "
        "gözlemliyoruz. Öğretmenlerimize yönelik eğitim seminerleri bu hafta başlıyor."
    )
    posts = json_adapter.get_posts()
    resp = safety_service.analyze_text(
        SafetyAnalysisRequest(text=clean_text), existing_posts=posts
    )

    assert resp.risk_vector.risk_level == RiskLevel.LOW
    assert resp.risk_vector.overall_risk_score < 0.35
    assert not resp.risk_vector.human_review_recommended


def test_safety_spam_links_and_uppercase(safety_service, json_adapter):
    """Test spam link density and aggressive uppercase detection."""
    spam_text = (
        "BEDAVA KAZANÇ FIRSATI!!! HEMEN TIKLA VE KAZAN: "
        "http://bit.ly/bedava-hediye-2026 http://link-spam.xyz BEDAVA BEDAVA!!!"
    )
    posts = json_adapter.get_posts()
    resp = safety_service.analyze_text(
        SafetyAnalysisRequest(text=spam_text), existing_posts=posts
    )

    assert resp.risk_vector.spam_score > 0.6
    assert resp.risk_vector.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH]
    assert resp.risk_vector.human_review_recommended

    rule_ids = [s.rule_id for s in resp.risk_vector.signals]
    assert "RULE-SPAM-001" in rule_ids or "RULE-FMT-001" in rule_ids


def test_safety_repetition_and_coordination(safety_service, json_adapter):
    """Test duplicate detection across distinct accounts."""
    duplicate_text = (
        "İNANILMAZ KAZANÇ FIRSATI!!! HEMEN TIKLA VE KAZAN: "
        "http://bit.ly/bedava-hediye-2026 http://link-spam.xyz http://promo-fake.site BEDAVA BEDAVA BEDAVA!!!"
    )
    posts = json_adapter.get_posts()
    resp = safety_service.analyze_text(
        SafetyAnalysisRequest(
            text=duplicate_text,
            post_id="new-post-test",
            author_id="different-user-999",
        ),
        existing_posts=posts,
    )

    assert resp.risk_vector.repetition_score > 0.3
    assert resp.risk_vector.coordination_score > 0.4
    categories = [s.category for s in resp.risk_vector.signals]
    assert "coordination" in categories
    assert "repetition" in categories


def test_safety_language_risk_indicator_non_definitive(safety_service, json_adapter):
    """Verify that language heuristics flag review indicators without claiming definitive hate speech."""
    provocative_text = "Bu yapılan tam bir sahtekar yaklaşımıdır, rezil bir durum."
    posts = json_adapter.get_posts()
    resp = safety_service.analyze_text(
        SafetyAnalysisRequest(text=provocative_text), existing_posts=posts
    )

    assert resp.risk_vector.toxicity_score > 0.3
    assert resp.risk_vector.hate_speech_score == 0.0  # Phase 1: Not claiming ML hate speech
    assert resp.risk_vector.human_review_recommended

    lang_signals = [s for s in resp.risk_vector.signals if s.category == "language_risk_indicator"]
    assert len(lang_signals) > 0
    # Must indicate review recommendation
    assert "incelemesi önerilen" in lang_signals[0].description
