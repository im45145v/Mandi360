"""Dependency-light exploratory summaries for normalized review records."""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


def build_dataset_summary(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Return overall volume, rating, date, branch, and text coverage metrics."""
    rows = list(records)
    dates = [_parse_date(record.get("review_date")) for record in rows]
    dates = [date for date in dates if date is not None]
    ratings = [float(record["rating"]) for record in rows if record.get("rating") is not None]
    text_lengths = [len(record["cleaned_text"]) for record in rows if record.get("cleaned_text")]
    return {
        "record_count": len(rows),
        "branch_count": len({record.get("branch_id") for record in rows if record.get("branch_id")}),
        "date_range_start": min(dates).isoformat() if dates else None,
        "date_range_end": max(dates).isoformat() if dates else None,
        "average_rating": round(sum(ratings) / len(ratings), 4) if ratings else None,
        "rating_distribution": dict(sorted(Counter(str(rating) for rating in ratings).items())),
        "text_available_count": sum(1 for record in rows if record.get("cleaned_text")),
        "text_missing_count": sum(1 for record in rows if not record.get("cleaned_text")),
        "average_text_length_chars": round(sum(text_lengths) / len(text_lengths), 2) if text_lengths else None,
    }


def build_branch_summary(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return comparable volume, rating, and text coverage metrics by branch."""
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[str(record.get("branch_id") or "<missing>")].append(record)
    summaries = []
    for branch_id, rows in sorted(groups.items()):
        ratings = [float(row["rating"]) for row in rows if row.get("rating") is not None]
        summaries.append(
            {
                "branch_id": branch_id,
                "branch_name": rows[0].get("branch_name"),
                "review_count": len(rows),
                "average_rating": round(sum(ratings) / len(ratings), 4) if ratings else None,
                "text_available_count": sum(1 for row in rows if row.get("cleaned_text")),
                "text_missing_count": sum(1 for row in rows if not row.get("cleaned_text")),
            }
        )
    return summaries


def build_monthly_summary(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate reviews on a complete branch-month calendar.

    Empty months are retained with null metrics so consumers can distinguish
    zero activity from a missing observation without fabricating a rating.
    """
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    branch_names: dict[str, str | None] = {}
    parsed_dates: list[datetime] = []
    for record in records:
        date = _parse_date(record.get("review_date"))
        if date is not None:
            branch_id = str(record.get("branch_id") or "<missing>")
            groups[(date.strftime("%Y-%m"), branch_id)].append(record)
            branch_names.setdefault(branch_id, record.get("branch_name"))
            parsed_dates.append(date)
    if not parsed_dates:
        return []

    months = _month_range(min(parsed_dates), max(parsed_dates))
    summaries = []
    for branch_id in sorted(branch_names):
        for month in months:
            rows = groups.get((month, branch_id), [])
            ratings = [float(row["rating"]) for row in rows if row.get("rating") is not None]
            summaries.append(
                {
                    "month": month,
                    "branch_id": branch_id,
                    "branch_name": branch_names[branch_id],
                    "review_count": len(rows),
                    "average_rating": round(sum(ratings) / len(ratings), 4) if ratings else None,
                    "text_available_count": sum(1 for row in rows if row.get("cleaned_text")),
                    "is_zero_volume": not rows,
                    "is_observed": bool(rows),
                }
            )
    return summaries


def write_eda_artifacts(records: list[dict[str, Any]], output_dir: str | Path) -> None:
    """Write JSON/CSV EDA outputs for reports and downstream consumers."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "dataset_summary.json").write_text(
        json.dumps(build_dataset_summary(records), indent=2), encoding="utf-8"
    )
    _write_csv(output / "branch_summary.csv", build_branch_summary(records))
    _write_csv(output / "monthly_summary.csv", build_monthly_summary(records))


def _parse_date(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _month_range(start: datetime, end: datetime) -> list[str]:
    """Return inclusive YYYY-MM values between two dates."""
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


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("\n", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
