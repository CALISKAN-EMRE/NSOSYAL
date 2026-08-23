def test_health_endpoint(client):
    """Test that /health returns 200, valid structure and honest prototype metadata."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert "app_name" in data
    assert "version" in data
    assert "data_source_adapter" in data
    assert data["data_source_adapter"]["status"] == "healthy"
    assert data["data_source_adapter"]["cached_posts_count"] > 0
    assert "disclaimer" in data
    assert "Phase 1 prototype" in data["disclaimer"]
