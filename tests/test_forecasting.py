from src.analytics.forecasting import forecast_branch_ratings


def _declining_branch_features():
    rows = []
    rating = 4.5
    for month in range(1, 9):
        rating -= 0.1
        rows.append(
            {
                "branch_id": "branch_a",
                "month": f"2025-{month:02d}",
                "review_count": 10,
                "average_rating": round(rating, 2),
                "average_sentiment_score": 0.1,
                "negative_ratio": 0.1,
            }
        )
    return rows


def test_forecast_branch_ratings_produces_forecast_and_risk():
    result = forecast_branch_ratings(_declining_branch_features(), horizon=2, min_history=6, holdout=2)

    assert result["method"] == "linear_trend_v1"
    assert len(result["branches_forecasted"]) == 1
    branch = result["branches_forecasted"][0]
    assert branch["risk_level"] == "elevated"
    assert len(branch["forecast"]) == 2
    assert branch["evaluation"] is not None
    assert branch["evaluation"]["mae"] >= 0


def test_forecast_branch_ratings_skips_branches_with_insufficient_history():
    short_rows = [
        {
            "branch_id": "branch_b",
            "month": "2025-01",
            "review_count": 5,
            "average_rating": 4.0,
            "average_sentiment_score": 0.1,
            "negative_ratio": 0.1,
        }
    ]

    result = forecast_branch_ratings(short_rows, min_history=6)

    assert result["branches_forecasted"] == []
    assert result["branches_skipped_insufficient_history"][0]["branch_id"] == "branch_b"
