"""Deterministic analytical tools for agents to call.

Agents must not receive raw datasets. Every function here reads pre-computed,
already-aggregated results from results/tables (or the small preprocessed
review table for text search) and returns compact, JSON-serializable
dictionaries suitable for passing to an LLM.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from src.config.settings import (
    ANOMALY_RESULTS_DIR,
    ASSOCIATION_RESULTS_DIR,
    CRM_RESULTS_DIR,
    FORECAST_RESULTS_DIR,
    INTERIM_DIR,
    NLP_RESULTS_DIR,
    RESULTS_TABLES_DIR,
)


def _read_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as file_handle:
        return list(csv.DictReader(file_handle))


def get_brand_summary() -> dict[str, Any] | None:
    """Return the overall brand-level dataset summary (volume, rating, text coverage)."""
    return _read_json(RESULTS_TABLES_DIR / "dataset_summary.json")


def get_branch_summary(branch_id: str) -> dict[str, Any] | None:
    """Return the volume/rating/text-coverage summary for one branch."""
    rows = _read_csv(RESULTS_TABLES_DIR / "branch_summary.csv")
    for row in rows:
        if row.get("branch_id") == branch_id:
            return row
    return None


def get_sentiment_trend(branch_id: str) -> list[dict[str, Any]]:
    """Return monthly review volume, rating, and sentiment history for one branch."""
    rows = _read_csv(RESULTS_TABLES_DIR / "monthly_summary.csv")
    return [row for row in rows if row.get("branch_id") == branch_id]


def get_branch_performance(branch_ids: list[str], period: str | None = None) -> list[dict[str, Any]]:
    """Return one compact observed-performance row per requested branch and period.

    This is the primary tool for branch comparisons. A missing period is returned
    explicitly instead of being silently replaced with a lifetime summary.
    """
    rows_by_branch = {
        branch_id: get_sentiment_trend(branch_id)
        for branch_id in branch_ids
    }
    performance: list[dict[str, Any]] = []
    for branch_id in branch_ids:
        summary = _read_period_row(rows_by_branch[branch_id], period)
        performance.append(
            {
                "branch_id": branch_id,
                "branch_name": (get_branch_summary(branch_id) or {}).get("branch_name"),
                "period": period,
                "observed": summary is not None,
                "review_count": summary.get("review_count") if summary else None,
                "average_rating": summary.get("average_rating") if summary else None,
                "text_available_count": summary.get("text_available_count") if summary else None,
            }
        )
    return performance


def _read_period_row(rows: list[dict[str, Any]], period: str | None) -> dict[str, Any] | None:
    if not period:
        return None
    return next((row for row in rows if row.get("month") == period), None)


def get_top_topics(limit: int = 5) -> list[dict[str, Any]]:
    """Return the top unsupervised topics with their top terms."""
    model = _read_json(NLP_RESULTS_DIR / "topic_model_nmf.json")
    if not model:
        return []
    return model.get("topics", [])[:limit]


def get_aspect_sentiment(branch_id: str) -> list[dict[str, Any]]:
    """Return aggregated aspect mention counts and average sentiment for one branch."""
    rows = _read_csv(NLP_RESULTS_DIR / "review_aspects_baseline.csv")
    totals: dict[str, dict[str, Any]] = {}
    for row in rows:
        if row.get("branch_id") != branch_id:
            continue
        aspect = row["aspect"]
        bucket = totals.setdefault(aspect, {"aspect": aspect, "mention_count": 0, "score_sum": 0.0})
        bucket["mention_count"] += 1
        bucket["score_sum"] += float(row.get("aspect_sentiment_score") or 0.0)
    return [
        {
            "aspect": bucket["aspect"],
            "mention_count": bucket["mention_count"],
            "average_sentiment_score": round(bucket["score_sum"] / bucket["mention_count"], 4),
        }
        for bucket in sorted(totals.values(), key=lambda b: b["mention_count"], reverse=True)
    ]


def get_anomalies(branch_id: str | None = None) -> list[dict[str, Any]]:
    """Return flagged anomalous months, optionally filtered to one branch."""
    rows = _read_csv(ANOMALY_RESULTS_DIR / "anomalies.csv")
    flagged = [row for row in rows if row.get("is_anomaly") == "True"]
    if branch_id:
        flagged = [row for row in flagged if row.get("branch_id") == branch_id]
    return flagged


def get_forecast(branch_id: str) -> dict[str, Any] | None:
    """Return the rating forecast and risk level for one branch."""
    result = _read_json(FORECAST_RESULTS_DIR / "branch_forecasts.json")
    if not result:
        return None
    for branch in result.get("branches_forecasted", []):
        if branch.get("branch_id") == branch_id:
            return branch
    return None


def get_association_rules(limit: int = 10) -> list[dict[str, Any]]:
    """Return the top association rules ranked by lift."""
    result = _read_json(ASSOCIATION_RESULTS_DIR / "association_rules.json")
    if not result:
        return []
    return result.get("rules", [])[:limit]


def get_crm_cases(branch_id: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
    """Return ranked, deterministic CRM cases with evidence fields."""
    rows = _read_csv(CRM_RESULTS_DIR / "crm_cases.csv")
    if branch_id:
        rows = [row for row in rows if row.get("branch_id") == branch_id]
    return rows[:limit]


def search_feedback(query: str, branch_id: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
    """Return a small sample of reviews whose cleaned text contains the query substring."""
    rows = _read_csv(INTERIM_DIR / "reviews_preprocessed.csv")
    query_lower = query.lower()
    matches = []
    for row in rows:
        text = row.get("cleaned_text") or ""
        if not text or query_lower not in text.lower():
            continue
        if branch_id and row.get("branch_id") != branch_id:
            continue
        matches.append(
            {
                "review_id": row.get("review_id"),
                "branch_id": row.get("branch_id"),
                "rating": row.get("rating"),
                "review_date": row.get("review_date"),
                "cleaned_text": text[:280],
            }
        )
        if len(matches) >= limit:
            break
    return matches
