"""Anomaly detection over monthly branch-level review aggregates (IsolationForest).

Flags months/branches with unusual combinations of volume, rating, and
sentiment relative to the rest of the dataset. Anomaly flags are model
outputs, not confirmed incidents, and require human review before action.
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from sklearn.ensemble import IsolationForest

ANOMALY_METHOD = "isolation_forest_v1"

FEATURE_NAMES = ["review_count", "average_rating", "average_sentiment_score", "negative_ratio"]


def _parse_date(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def build_monthly_branch_features(nlp_records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate volume, rating, and sentiment on a complete branch calendar."""
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    branch_names: dict[str, str | None] = {}
    parsed_dates: list[datetime] = []
    for record in nlp_records:
        date = _parse_date(record.get("review_date"))
        if date is None:
            continue
        branch_id = str(record.get("branch_id") or "<missing>")
        groups[(branch_id, date.strftime("%Y-%m"))].append(record)
        branch_names.setdefault(branch_id, record.get("branch_name"))
        parsed_dates.append(date)

    if not parsed_dates:
        return []

    rows = []
    for branch_id in sorted(branch_names):
        for month in _month_range(min(parsed_dates), max(parsed_dates)):
            records = groups.get((branch_id, month), [])
            ratings = [float(r["rating"]) for r in records if r.get("rating") is not None]
            scores = [float(r["sentiment_score"]) for r in records if r.get("sentiment_score") is not None]
            negative_count = sum(1 for r in records if r.get("sentiment_label") == "Negative")
            rows.append(
                {
                    "branch_id": branch_id,
                    "branch_name": branch_names[branch_id],
                    "month": month,
                    "review_count": len(records),
                    "average_rating": round(sum(ratings) / len(ratings), 4) if ratings else None,
                    "average_sentiment_score": round(sum(scores) / len(scores), 6) if scores else None,
                    "negative_ratio": round(negative_count / len(records), 4) if records else None,
                    "is_zero_volume": not records,
                    "is_observed": bool(records),
                }
            )
    return rows


def detect_anomalies(
    monthly_features: Iterable[dict[str, Any]],
    contamination: float = 0.1,
    random_state: int = 42,
    min_rows: int = 10,
    min_review_count: int = 5,
) -> dict[str, Any]:
    """Fit IsolationForest over monthly branch feature rows and flag anomalies.

    Raises ValueError if there are too few complete rows to fit meaningfully.
    """
    rows = [
        row
        for row in monthly_features
        if row.get("review_count", 0) >= min_review_count
        and all(row.get(name) is not None for name in FEATURE_NAMES)
    ]
    if len(rows) < min_rows:
        raise ValueError(f"Need at least {min_rows} complete monthly rows, got {len(rows)}")

    matrix = [[row[name] for name in FEATURE_NAMES] for row in rows]
    model = IsolationForest(contamination=contamination, random_state=random_state)
    model.fit(matrix)
    raw_scores = model.decision_function(matrix)
    predictions = model.predict(matrix)

    results = []
    for row, score, prediction in zip(rows, raw_scores, predictions):
        prior_rows = [
            prior for prior in rows
            if prior["branch_id"] == row["branch_id"] and prior["month"] < row["month"]
        ]
        previous = prior_rows[-1] if prior_rows else None
        reasons = []
        if previous is not None and row["average_rating"] <= previous["average_rating"] - 0.5:
            reasons.append("rating_drop_vs_previous_month")
        if previous is not None and row["negative_ratio"] >= previous["negative_ratio"] + 0.2:
            reasons.append("negative_ratio_rise_vs_previous_month")
        if previous is not None and previous["review_count"] > 0:
            volume_ratio = row["review_count"] / previous["review_count"]
            if volume_ratio >= 2.0 or volume_ratio <= 0.5:
                reasons.append("review_volume_shift_vs_previous_month")
        if prediction == -1:
            reasons.append("model_outlier")
        severity = "high" if len(reasons) >= 2 and "model_outlier" in reasons else "medium" if reasons else "low"
        results.append(
            {
                **row,
                "anomaly_score": round(float(score), 6),
                "is_anomaly": bool(prediction == -1),
                "alert_reasons": reasons,
                "alert_severity": severity,
            }
        )
    results.sort(key=lambda row: row["anomaly_score"])

    return {
        "method": ANOMALY_METHOD,
        "status": "derived_ml_unvalidated",
        "params": {
            "feature_names": FEATURE_NAMES,
            "contamination": contamination,
            "random_state": random_state,
            "rows_used": len(rows),
            "min_review_count": min_review_count,
        },
        "anomaly_count": sum(1 for row in results if row["is_anomaly"]),
        "rows": results,
    }


def _month_range(start: datetime, end: datetime) -> list[str]:
    year, month = start.year, start.month
    end_key = (end.year, end.month)
    months = []
    while (year, month) <= end_key:
        months.append(f"{year:04d}-{month:02d}")
        month += 1
        if month == 13:
            year += 1
            month = 1
    return months


def write_anomaly_artifacts(result: dict[str, Any], output_dir: str | Path) -> None:
    """Write anomaly detection results as JSON and CSV."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "anomalies.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    rows = result["rows"]
    csv_path = output / "anomalies.csv"
    if not rows:
        csv_path.write_text("\n", encoding="utf-8")
        return
    with csv_path.open("w", encoding="utf-8", newline="") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
