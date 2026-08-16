from src.analytics.association import build_transactions, mine_association_rules


def _nlp_records():
    return [
        {"review_id": "r1", "rating": 1, "sentiment_label": "Negative"},
        {"review_id": "r2", "rating": 1, "sentiment_label": "Negative"},
        {"review_id": "r3", "rating": 1, "sentiment_label": "Negative"},
        {"review_id": "r4", "rating": 5, "sentiment_label": "Positive"},
        {"review_id": "r5", "rating": 5, "sentiment_label": "Positive"},
        {"review_id": "r6", "rating": 5, "sentiment_label": "Positive"},
    ]


def _aspect_rows():
    return [
        {"review_id": "r1", "aspect": "service"},
        {"review_id": "r2", "aspect": "service"},
        {"review_id": "r3", "aspect": "service"},
        {"review_id": "r4", "aspect": "food_quality"},
        {"review_id": "r5", "aspect": "food_quality"},
        {"review_id": "r6", "aspect": "food_quality"},
    ]


def test_build_transactions_combines_aspects_sentiment_and_rating():
    transactions = build_transactions(_nlp_records(), _aspect_rows())

    assert len(transactions) == 6
    assert {"aspect:service", "sentiment:Negative", "rating_low"} in transactions


def test_mine_association_rules_finds_expected_high_lift_rule():
    result = mine_association_rules(_nlp_records(), _aspect_rows(), min_support=0.1, min_confidence=0.5)

    assert result["method"] == "apriori_v1"
    assert result["rule_count"] > 0
    top_rule = result["rules"][0]
    assert top_rule["lift"] >= 1.0
    assert all(rule["confidence"] >= 0.5 for rule in result["rules"])


def test_mine_association_rules_raises_on_empty_input():
    try:
        mine_association_rules([], [])
        assert False, "expected ValueError"
    except ValueError:
        pass
