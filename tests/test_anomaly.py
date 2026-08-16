from src.analytics.anomaly import build_monthly_branch_features, detect_anomalies


def _nlp_records():
    records = []
    for month in range(1, 11):
        for _ in range(5):
            records.append(
                {
                    "branch_id": "branch_a",
                    "review_date": f"2025-{month:02d}-01T00:00:00+00:00",
                    "rating": 4.0,
                    "sentiment_label": "Positive",
                    "sentiment_score": 0.5,
                }
            )
    # one anomalous month with a rating/sentiment collapse
    for _ in range(20):
        records.append(
            {
                "branch_id": "branch_a",
                "review_date": "2025-11-01T00:00:00+00:00",
                "rating": 1.0,
                "sentiment_label": "Negative",
                "sentiment_score": -0.5,
            }
        )
    return records


def test_build_monthly_branch_features_aggregates_correctly():
    features = build_monthly_branch_features(_nlp_records())

    assert len(features) == 11
    november = next(row for row in features if row["month"] == "2025-11")
    assert november["review_count"] == 20
    assert november["average_rating"] == 1.0


def test_detect_anomalies_flags_the_outlier_month():
    features = build_monthly_branch_features(_nlp_records())

    result = detect_anomalies(features, contamination=0.1, min_rows=5)

    assert result["method"] == "isolation_forest_v1"
    flagged_months = {row["month"] for row in result["rows"] if row["is_anomaly"]}
    assert "2025-11" in flagged_months


def test_detect_anomalies_raises_when_too_few_rows():
    try:
        detect_anomalies([{"branch_id": "a", "month": "2025-01", "review_count": 1,
                           "average_rating": 4.0, "average_sentiment_score": 0.1, "negative_ratio": 0.0}],
                          min_rows=5)
        assert False, "expected ValueError"
    except ValueError:
        pass
