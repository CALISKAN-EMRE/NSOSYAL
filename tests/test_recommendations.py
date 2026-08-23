def test_recommendation_feed_generation(recommendation_service):
    """Test generating explainable recommendations."""
    recommendations = recommendation_service.get_recommendations(
        user_interests=["YapayZeka", "Eğitim"],
        preferred_topic_id="yapay-zeka-egitim",
        limit=10,
    )

    assert len(recommendations) > 0
    top_rec = recommendations[0]
    assert top_rec.post is not None
    assert top_rec.explanation is not None
    assert top_rec.explanation.final_score >= 0.0
    assert top_rec.explanation.final_score <= 100.0
    assert len(top_rec.explanation.factors) >= 5
    assert len(top_rec.explanation.summary_reason) > 0


def test_recommendation_penalty_application(recommendation_service, json_adapter):
    """Test that spam posts receive safety penalties and lower scores."""
    spam_post = json_adapter.get_post_by_id("post-009")
    assert spam_post is not None

    explanation = recommendation_service.explain_post_recommendation(
        post=spam_post,
        user_interests=["AçıkKaynak", "Yazılım"],
        all_posts=json_adapter.get_posts(),
    )

    # Check for negative penalty factors
    safety_factor = next(
        (f for f in explanation.factors if f.factor_name == "safety_risk"), None
    )
    assert safety_factor is not None
    assert safety_factor.is_penalty is True
    assert safety_factor.raw_score > 0.4
    assert safety_factor.weighted_impact < 0

    # The final score should be heavily penalized
    assert explanation.final_score < 40.0
