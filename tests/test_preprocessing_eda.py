from src.analytics.eda import (
    build_branch_summary,
    build_dataset_summary,
    build_monthly_summary,
)
from src.preprocessing.text import clean_review_text, preprocess_records


def _records():
    return [
        {
            "review_id": "1",
            "branch_id": "branch_a",
            "branch_name": "Branch A",
            "review_date": "2026-01-15T10:00:00+00:00",
            "rating": 5.0,
            "review_text": "  Great &amp; tasty <b>food</b>!  ",
        },
        {
            "review_id": "2",
            "branch_id": "branch_a",
            "branch_name": "Branch A",
            "review_date": "2026-01-20T10:00:00+00:00",
            "rating": 3.0,
            "review_text": None,
        },
    ]


def test_clean_review_text_normalizes_noise_without_fabricating_text():
    assert clean_review_text("  Great &amp; tasty <b>food</b>!  ") == "Great & tasty food!"
    assert clean_review_text(None) is None
    assert clean_review_text("   ") is None


def test_preprocess_records_preserves_original_text():
    records = _records()
    processed = preprocess_records(records)

    assert processed[0]["review_text"] == records[0]["review_text"]
    assert processed[0]["cleaned_text"] == "Great & tasty food!"
    assert processed[0]["text_available"] is True
    assert processed[1]["preprocessing_status"] == "missing_text"
    assert records[0].get("cleaned_text") is None


def test_eda_summaries_reconcile_counts_and_months():
    processed = preprocess_records(_records())

    dataset = build_dataset_summary(processed)
    branches = build_branch_summary(processed)
    monthly = build_monthly_summary(processed)

    assert dataset["record_count"] == 2
    assert dataset["branch_count"] == 1
    assert dataset["text_available_count"] == 1
    assert dataset["text_missing_count"] == 1
    assert branches[0]["review_count"] == 2
    assert branches[0]["average_rating"] == 4.0
    assert monthly[0]["month"] == "2026-01"
    assert monthly[0]["review_count"] == 2
