def test_context_card_generation(context_service):
    """Test ContextCard synthesis for a given topic."""
    card = context_service.get_context_card("yapay-zeka-egitim")
    assert card is not None
    assert card.topic_id == "yapay-zeka-egitim"
    assert len(card.summary) > 30
    assert len(card.key_themes) > 0
    assert len(card.perspectives) >= 2
    assert len(card.timeline) > 0
    assert len(card.sources) > 0
    assert card.pipeline_timing_ms is not None
    assert "total_pipeline_ms" in card.pipeline_timing_ms
    assert card.sources[0].relevance_score is not None


def test_context_card_perspectives(context_service):
    """Verify that opposing/alternative perspectives are represented."""
    card = context_service.get_context_card("yapay-zeka-egitim")
    persp_types = [p.perspective_type for p in card.perspectives]

    # Check for presence of both supportive and critical views
    assert "supportive" in persp_types
    assert "critical" in persp_types

    for p in card.perspectives:
        assert p.post_count > 0
        assert len(p.supporting_post_ids) > 0
        assert len(p.summary) > 0


def test_context_card_non_existent_topic(context_service):
    """Test handling of invalid topic ID."""
    card = context_service.get_context_card("non-existent-topic-xyz")
    assert card is None
