from src.agents import tools


def test_get_brand_summary_reads_real_results():
    summary = tools.get_brand_summary()

    assert summary is not None
    assert summary["record_count"] > 0


def test_get_branch_summary_returns_known_branch():
    summary = tools.get_branch_summary("banjara_hills")

    assert summary is not None
    assert summary["branch_id"] == "banjara_hills"


def test_get_branch_summary_returns_none_for_unknown_branch():
    assert tools.get_branch_summary("nonexistent_branch") is None


def test_get_top_topics_returns_limited_topics_with_terms():
    topics = tools.get_top_topics(limit=3)

    assert len(topics) <= 3
    assert all("top_terms" in topic for topic in topics)


def test_get_aspect_sentiment_aggregates_by_aspect():
    aspects = tools.get_aspect_sentiment("banjara_hills")

    assert all("aspect" in row and "mention_count" in row for row in aspects)


def test_get_forecast_returns_branch_forecast():
    forecast = tools.get_forecast("banjara_hills")

    assert forecast is not None
    assert forecast["branch_id"] == "banjara_hills"
    assert "forecast" in forecast


def test_get_association_rules_returns_limited_rules():
    rules = tools.get_association_rules(limit=5)

    assert len(rules) <= 5


def test_search_feedback_finds_matching_reviews():
    matches = tools.search_feedback("food", limit=3)

    assert len(matches) <= 3
    assert all("review_id" in row and "cleaned_text" in row for row in matches)
