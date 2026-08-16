from src.analytics.nlp import (
    build_nlp_records,
    build_topic_candidates,
    extract_aspects,
    score_sentiment,
)


def test_score_sentiment_is_transparent_and_handles_missing_text():
    positive = score_sentiment("Amazing delicious food and excellent service")
    negative = score_sentiment("Terrible slow service and cold food")
    missing = score_sentiment(None)

    assert positive["sentiment_label"] == "Positive"
    assert positive["sentiment_positive_hits"] == 3
    assert negative["sentiment_label"] == "Negative"
    assert negative["sentiment_negative_hits"] == 3
    assert missing["sentiment_label"] == "Neutral"
    assert missing["sentiment_status"] == "derived_unvalidated"


def test_extract_aspects_returns_only_observed_aspects():
    aspects = extract_aspects("The food was delicious but the service was slow")

    assert {row["aspect"] for row in aspects} == {"food_quality", "service", "waiting_time"}
    assert all(row["aspect_method"] == "keyword_baseline_v1" for row in aspects)


def test_topic_candidates_are_frequency_ordered():
    records = [
        {"cleaned_text": "great food great service"},
        {"cleaned_text": "food was great"},
    ]

    candidates = build_topic_candidates(records, limit=2)

    assert candidates[0]["term"] == "great"
    assert candidates[0]["document_term_count"] == 3
    assert candidates[1]["term"] == "food"
    assert all(row["topic_status"] == "candidate_requires_review" for row in candidates)


def test_build_nlp_records_preserves_rows_and_creates_aspect_table():
    records = [
        {
            "review_id": "r1",
            "branch_id": "branch_a",
            "review_date": "2026-01-01T00:00:00+00:00",
            "cleaned_text": "Great food",
        },
        {
            "review_id": "r2",
            "branch_id": "branch_a",
            "review_date": "2026-01-02T00:00:00+00:00",
            "cleaned_text": None,
        },
    ]

    enriched, aspect_rows = build_nlp_records(records)

    assert len(enriched) == 2
    assert enriched[0]["sentiment_label"] == "Positive"
    assert enriched[1]["sentiment_label"] == "Neutral"
    assert enriched[0]["aspect_count"] == 1
    assert aspect_rows[0]["review_id"] == "r1"
