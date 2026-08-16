"""Auditable NLP baselines for sentiment, aspects, and topic candidates.

These heuristics are derived features, not ground-truth labels. They are useful for
an initial reproducible baseline while a manually labeled evaluation sample is
being prepared.
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from src.preprocessing.text import ANALYTICAL_FIELDS

TOKEN_PATTERN = re.compile(r"[\w']+", re.UNICODE)

POSITIVE_TERMS = {
    "amazing", "awesome", "best", "delicious", "excellent", "good", "great",
    "loved", "love", "nice", "perfect", " tasty", "tasty", "wonderful",
}
NEGATIVE_TERMS = {
    "awful", "bad", "cold", "delay", "delayed", "disappointed", "disappointing",
    "horrible", "late", "poor", "rude", "slow", "terrible", "worst", "waste",
}

ASPECT_TERMS = {
    "food_quality": {"food", "taste", "tasty", "flavor", "flavour", "delicious", "fresh", "cold", "hot"},
    "service": {"service", "staff", "waiter", "waitress", "behavior", "behaviour", "rude", "slow"},
    "waiting_time": {"wait", "waiting", "delay", "delayed", "late", "slow", "time"},
    "price_value": {"price", "prices", "cost", "expensive", "cheap", "value", "worth"},
    "quantity": {"quantity", "portion", "portions", "serving", "large", "small"},
    "hygiene": {"clean", "cleanliness", "dirty", "hygiene", "smell", "washroom"},
    "ambience": {"ambience", "atmosphere", "seating", "music", "parking", "place"},
}

DEFAULT_STOPWORDS = {
    "a", "about", "after", "again", "all", "also", "and", "are", "at", "be", "been",
    "but", "by", "for", "from", "had", "has", "have", "here", "i", "in", "is", "it",
    "its", "me", "my", "of", "on", "or", "our", "that", "the", "their", "there", "this",
    "to", "too", "was", "we", "were", "with", "you", "your",
}


def tokenize(text: str | None) -> list[str]:
    """Tokenize cleaned text into lowercase word-like terms."""
    return [token.lower() for token in TOKEN_PATTERN.findall(text or "")]


def score_sentiment(text: str | None) -> dict[str, Any]:
    """Return a lexicon baseline score and label with transparent components."""
    tokens = tokenize(text)
    positive = sum(token in POSITIVE_TERMS for token in tokens)
    negative = sum(token in NEGATIVE_TERMS for token in tokens)
    score = (positive - negative) / max(len(tokens), 1)
    if positive == 0 and negative == 0:
        label = "Neutral"
    elif score >= 0.05:
        label = "Positive"
    elif score <= -0.05:
        label = "Negative"
    else:
        label = "Neutral"
    return {
        "sentiment_label": label,
        "sentiment_score": round(score, 6),
        "sentiment_positive_hits": positive,
        "sentiment_negative_hits": negative,
        "sentiment_method": "lexicon_baseline_v1",
        "sentiment_status": "derived_unvalidated",
    }


def extract_aspects(text: str | None) -> list[dict[str, Any]]:
    """Return observed aspect mentions and local lexicon polarity."""
    tokens = set(tokenize(text))
    aspects: list[dict[str, Any]] = []
    for aspect, terms in ASPECT_TERMS.items():
        matched_terms = sorted(tokens.intersection(terms))
        if matched_terms:
            polarity = score_sentiment(text)
            aspects.append(
                {
                    "aspect": aspect,
                    "matched_terms": ",".join(matched_terms),
                    "aspect_sentiment_label": polarity["sentiment_label"],
                    "aspect_sentiment_score": polarity["sentiment_score"],
                    "aspect_method": "keyword_baseline_v1",
                    "aspect_status": "derived_unvalidated",
                }
            )
    return aspects


def build_nlp_records(records: Iterable[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Add sentiment to copied review rows and return a normalized aspect table."""
    enriched: list[dict[str, Any]] = []
    aspect_rows: list[dict[str, Any]] = []
    for record in records:
        enriched_record = dict(record)
        sentiment = score_sentiment(record.get("cleaned_text"))
        enriched_record.update(sentiment)
        aspects = extract_aspects(record.get("cleaned_text"))
        enriched_record["aspect_count"] = len(aspects)
        enriched.append(enriched_record)
        for aspect in aspects:
            aspect_rows.append(
                {
                    "review_id": record.get("review_id"),
                    "branch_id": record.get("branch_id"),
                    "review_date": record.get("review_date"),
                    **aspect,
                }
            )
    return enriched, aspect_rows


def build_topic_candidates(records: Iterable[dict[str, Any]], limit: int = 30) -> list[dict[str, Any]]:
    """Return frequent corpus terms as reviewable topic candidates."""
    counts = Counter()
    for record in records:
        counts.update(
            token for token in tokenize(record.get("cleaned_text"))
            if len(token) >= 3 and token not in DEFAULT_STOPWORDS
        )
    return [
        {
            "topic_candidate_id": index,
            "term": term,
            "document_term_count": count,
            "topic_method": "frequency_baseline_v1",
            "topic_status": "candidate_requires_review",
        }
        for index, (term, count) in enumerate(counts.most_common(limit), start=1)
    ]


def write_nlp_artifacts(
    records: list[dict[str, Any]], aspect_rows: list[dict[str, Any]], output_dir: str | Path
) -> None:
    """Write enriched reviews, aspect mentions, and topic candidates."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    safe_fields = ANALYTICAL_FIELDS + [
        "sentiment_label",
        "sentiment_score",
        "sentiment_positive_hits",
        "sentiment_negative_hits",
        "sentiment_method",
        "sentiment_status",
        "aspect_count",
    ]
    safe_records = [
        {field: record.get(field) for field in safe_fields if field in record}
        for record in records
    ]
    _write_csv(output / "reviews_nlp_baseline.csv", safe_records)
    _write_csv(output / "review_aspects_baseline.csv", aspect_rows)
    (output / "topic_candidates_baseline.json").write_text(
        json.dumps(build_topic_candidates(records), indent=2), encoding="utf-8"
    )


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("\n", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
