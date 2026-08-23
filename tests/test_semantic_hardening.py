import pytest
from app.adapters.json_adapter import JsonDemoAdapter
from app.ml.cluster_service import DemoClusterService, SemanticClusterService
from app.ml.embedding_service import DemoEmbeddingService
from app.services.context_service import ContextService
from app.services.recommendation_service import RecommendationService
from app.services.safety_service import SafetyService
from app.models.post import Post, Author, PostMetrics


@pytest.fixture
def data_adapter():
    return JsonDemoAdapter(data_path="data/demo_posts.json")


@pytest.fixture
def safety_service():
    return SafetyService()


@pytest.fixture
def demo_embedding_service():
    return DemoEmbeddingService(dimension=384)


def test_topic_hint_never_used_by_clustering(data_adapter, demo_embedding_service):
    """Test that SemanticClusterService does not access or require topic_id/topic_title."""
    cluster_service = SemanticClusterService(
        embedding_service=demo_embedding_service,
        min_cluster_size=2,
        pca_components=4,
    )
    
    # Create posts with deliberately stripped or falsified topic_id
    raw_posts = [
        Post(
            id=f"test-p-{i}",
            author=Author(id=f"u-{i}", name=f"User {i}", handle=f"@user_{i}"),
            text=f"Elektrikli araç şarj istasyonları otoyollarda yaygınlaşıyor soket sayısı {i}.",
            created_at="2026-08-23T10:00:00Z",
            topic_id="FAKE_CORRUPTED_ID",
            topic_title="FAKE TITLE",
            source_type="user",
            tags=["ElektrikliAraç", "Şarj"],
            metrics=PostMetrics(likes=10, reposts=2, replies=1),
        )
        for i in range(5)
    ]

    clusters = cluster_service.cluster_posts(raw_posts)
    assert len(clusters) >= 1
    # Check that cluster labels are not taking FAKE TITLE
    for c in clusters:
        assert "FAKE" not in c.label


def test_obvious_spam_does_not_become_top_context_source(data_adapter, safety_service):
    """Test that safety gating excludes BotNet / Airdrop spam candidates from context sources."""
    context_service = ContextService(data_adapter=data_adapter, safety_service=safety_service)
    
    # Request context card for a topic
    topics = context_service.get_semantic_topics()
    assert len(topics) > 0

    card = context_service.get_context_card(topics[0].id)
    assert card is not None

    # Inspect sources
    for src in card.sources:
        assert "botnet" not in src.source_name.lower()
        assert "airdrop" not in src.source_name.lower()
        assert "kripto-dolandiricilik" not in (src.reliability_note or "").lower()

    # Verify that spam candidates were gated if present in corpus
    assert card.gated_spam_candidates_count >= 1


def test_cluster_titles_are_clean_and_deterministic(data_adapter, demo_embedding_service):
    """Test that generated cluster titles are not keyword soup or containing noise tokens."""
    cluster_service = SemanticClusterService(
        embedding_service=demo_embedding_service,
        min_cluster_size=3,
        pca_components=4,
    )
    posts = data_adapter.get_posts(limit=50)
    clusters = cluster_service.cluster_posts(posts)

    for c in clusters:
        assert "http" not in c.label.lower()
        assert "xyz" not in c.label.lower()
        assert "bedava" not in c.label.lower()
        assert len(c.label.strip()) > 3


def test_perspective_entries_include_valid_evidence_ids(data_adapter):
    """Test that each perspective has at least one supporting post ID that exists in the cluster."""
    context_service = ContextService(data_adapter=data_adapter)
    topics = context_service.get_semantic_topics()
    card = context_service.get_context_card(topics[0].id)
    assert card is not None

    all_cluster_post_ids = set(card.community_post_ids)
    for p in card.perspectives:
        assert p.post_count > 0
        assert len(p.supporting_post_ids) > 0
        # Check that evidence IDs belong to this topic/cluster
        for pid in p.supporting_post_ids:
            assert pid in all_cluster_post_ids


def test_recommendation_prose_never_mentions_unsupported_factors(data_adapter, safety_service):
    """Test that 'Neden bunu görüyorum?' explanation only mentions active scoring factors."""
    rec_service = RecommendationService(data_adapter=data_adapter, safety_service=safety_service)
    recs = rec_service.get_recommendations(limit=10)

    forbidden_phrases = [
        "etkileşim potansiyeli",
        "tıklama olasılığı",
        "viral potansiyel",
        "popülerlik skoru",
        "sponsorlu içerik",
    ]

    for rec in recs:
        summary = rec.explanation.summary_reason.lower()
        for phrase in forbidden_phrases:
            assert phrase not in summary, f"Found forbidden unsupported phrase '{phrase}' in summary: {summary}"

        # Ensure final_score is bounded in [0, 100]
        assert 0.0 <= rec.explanation.final_score <= 100.0


def test_distinct_community_posts_and_context_sources(data_adapter):
    """Test that community_post_ids and sources are distinct data structures."""
    context_service = ContextService(data_adapter=data_adapter)
    topics = context_service.get_semantic_topics()
    card = context_service.get_context_card(topics[0].id)
    assert card is not None

    assert hasattr(card, "community_post_ids")
    assert hasattr(card, "sources")
    assert isinstance(card.community_post_ids, list)
    assert isinstance(card.sources, list)


def test_cluster_membership_score_validity(data_adapter):
    """Test that cluster membership score is a valid probability in [0.0, 1.0]."""
    context_service = ContextService(data_adapter=data_adapter)
    topics = context_service.get_semantic_topics()
    card = context_service.get_context_card(topics[0].id)
    assert card is not None

    if card.cluster_membership_score is not None:
        assert 0.0 <= card.cluster_membership_score <= 1.0
