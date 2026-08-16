from src.analytics.crm import build_crm_cases


def test_build_crm_cases_prioritizes_negative_aspects_with_alert_support():
    aspects = [
        {"branch_id": "branch_a", "aspect": "service", "aspect_sentiment_score": -0.8}
        for _ in range(8)
    ]
    alerts = [
        {
            "branch_id": "branch_a",
            "is_anomaly": True,
            "alert_severity": "high",
        }
    ]

    result = build_crm_cases(aspects, alerts)

    assert result["status"] == "derived_actionable"
    assert result["cases"][0]["priority"] == "high"
    assert result["cases"][0]["recommended_action"]
    assert result["cases"][0]["status"] == "open"


def test_build_crm_cases_ignores_low_volume_aspects():
    result = build_crm_cases(
        [{"branch_id": "branch_a", "aspect": "food", "aspect_sentiment_score": -1.0}],
        [],
        min_mentions=3,
    )

    assert result["case_count"] == 0