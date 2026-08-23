def test_adapter_load_posts(json_adapter):
    """Test that demo posts are parsed into Post models correctly."""
    posts = json_adapter.get_posts(limit=100)
    assert len(posts) >= 10
    first_post = posts[0]
    assert first_post.id is not None
    assert first_post.author.name is not None
    assert first_post.author.handle.startswith("@")
    assert first_post.topic_id is not None
    assert len(first_post.text) > 0


def test_adapter_topic_indexing(json_adapter):
    """Test that topics are correctly aggregated from demo posts."""
    topics = json_adapter.get_topics()
    assert len(topics) >= 3

    topic_ids = [t.id for t in topics]
    assert "yapay-zeka-egitim" in topic_ids
    assert "acik-kaynak-yazilim" in topic_ids

    first_topic = topics[0]
    assert first_topic.post_count > 0
    assert first_topic.participant_count > 0
    assert len(first_topic.tags) > 0


def test_adapter_search_filter(json_adapter):
    """Test filtering and search capabilities in the adapter."""
    ai_posts = json_adapter.get_posts(topic_id="yapay-zeka-egitim")
    assert len(ai_posts) >= 3
    assert all(p.topic_id == "yapay-zeka-egitim" for p in ai_posts)

    search_posts = json_adapter.get_posts(search="şarj")
    assert len(search_posts) > 0
    assert all("şarj" in p.text.lower() or any("şarj" in t.lower() for t in p.tags) for p in search_posts)
