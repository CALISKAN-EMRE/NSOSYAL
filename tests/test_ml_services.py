import pytest
from app.ml.embedding_service import DemoEmbeddingService
from app.ml.cluster_service import DemoClusterService
from app.ml.reranker_service import DemoRerankerService
from app.ml.similarity_service import SemanticSimilarityService
from app.ml.base import RerankCandidate
from app.ml.model_manager import ModelManager


def test_demo_embedding_service():
    """Verify demo embedding service generates normalized vectors of expected dimension."""
    service = DemoEmbeddingService(dimension=384)
    embs = service.encode_documents(["Türkçe yapay zeka", "Sosyal medya analizi"])
    assert embs.shape == (2, 384)
    assert service.dimension() == 384
    meta = service.model_metadata()
    assert meta["dimension"] == 384


def test_demo_cluster_service(json_adapter):
    """Verify demo cluster service produces structured SemanticCluster outputs."""
    posts = json_adapter.get_posts(limit=10)
    clusterer = DemoClusterService()
    clusters = clusterer.cluster_posts(posts)
    assert len(clusters) > 0
    for c in clusters:
        assert c.cluster_id is not None
        assert len(c.post_ids) > 0
        assert c.confidence_score > 0.0


def test_demo_reranker_service():
    """Verify reranker modifies ranking and calculates valid scores."""
    reranker = DemoRerankerService()
    candidates = [
        RerankCandidate(
            doc_id="doc-1",
            source_name="Kaynak 1",
            source_type="user",
            text="Bugün hava çok yağmurlu ve rüzgarlı.",
            initial_dense_score=0.9,
        ),
        RerankCandidate(
            doc_id="doc-2",
            source_name="Kaynak 2",
            source_type="news_outlet",
            text="Devlet kurumlarında açık kaynak ve Pardus işletim sistemi yaygınlaştırılıyor.",
            initial_dense_score=0.4,
        ),
    ]

    reranked = reranker.rerank(query="açık kaynak ve pardus işletim sistemi", candidates=candidates, top_k=2)
    assert len(reranked) == 2
    # Document 2 should be boosted above Document 1 because of high lexical overlap
    assert reranked[0].doc_id == "doc-2"
    assert reranked[0].rank == 1
    assert reranked[0].reranked_score is not None


def test_semantic_similarity_service():
    """Verify profile similarity computation returns valid score in [0.0, 1.0]."""
    embedder = DemoEmbeddingService(dimension=128)
    sim_service = SemanticSimilarityService(embedding_service=embedder)

    score = sim_service.compute_profile_similarity(
        user_interests=["YapayZeka", "Eğitim"],
        post_text="Milli Eğitim Bakanlığı yapay zeka rehberini açıkladı.",
        post_tags=["YapayZeka", "Eğitim"],
    )
    assert 0.0 <= score <= 1.0


def test_search_service(search_service):
    """Verify natural-language search returns ranked posts with relevance scores."""
    resp = search_service.search(query="yapay zeka ve eğitim", limit=5)
    assert resp.total_results > 0
    assert len(resp.results) > 0
    assert resp.results[0].rank == 1
    assert resp.results[0].relevance_score > 0.0
    assert resp.search_latency_ms >= 0.0


def test_search_api_endpoint(client):
    """Verify GET /api/search returns valid SearchResponse schema."""
    response = client.get("/api/search?q=elektrikli%20ara%C3%A7lar&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "elektrikli araçlar"
    assert "results" in data
    assert "search_latency_ms" in data


def test_system_status_api_endpoint(client):
    """Verify GET /api/system/status returns model readiness and pipelines."""
    response = client.get("/api/system/status")
    assert response.status_code == 200
    data = response.json()
    assert "model_manager" in data
    assert data["model_manager"]["status"] in ["ready", "demo"]
    assert "pipelines" in data
    assert "clustering" in data["pipelines"]
    assert "context_reranking" in data["pipelines"]


def test_model_manager_fallback():
    """Verify ModelManager handles fallback gracefully."""
    mm = ModelManager()
    mm.mode = "demo"
    mm.initialize()
    status = mm.get_status()
    assert status["status"] == "ready"
    assert status["semantic_mode"] == "demo"


def test_demo_mode_status_without_torch(monkeypatch):
    """Regression test ensuring demo mode and system status work cleanly when torch is not installed."""
    import builtins
    real_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == "torch":
            raise ModuleNotFoundError("No module named 'torch' (simulated lightweight environment)")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)

    mm = ModelManager()
    mm.mode = "demo"
    mm.initialize()
    assert mm.cuda_vram_gb == 0.0
    status = mm.get_status()
    assert status["status"] == "ready"
    assert status["semantic_mode"] == "demo"
    assert status["cuda_vram_allocated_gb"] == 0.0

