"""Validation checks for normalized Google Maps review records.

Computes data-quality metrics only; it does not mutate or drop records.
"""
from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Union

PathLike = Union[str, Path]

# Google Maps star ratings are whole numbers from 1 to 5.
VALID_RATING_RANGE = (1.0, 5.0)


@dataclass
class ValidationReport:
    total_records: int
    missing_review_text: int
    missing_rating: int
    missing_review_date: int
    invalid_rating: int
    duplicate_review_id_count: int
    duplicate_review_id_samples: list[str]
    generated_review_ids: int
    records_by_branch: dict[str, int]
    date_range_start: str | None
    date_range_end: str | None
    warnings: list[str]
    errors: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def save(self, path: PathLike) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")


def validate_normalized_reviews(records: list[dict[str, Any]]) -> ValidationReport:
    """Compute data-quality metrics for a list of normalized review records."""
    total = len(records)
    missing_text = sum(1 for r in records if not r.get("review_text"))
    missing_rating = sum(1 for r in records if r.get("rating") is None)
    missing_date = sum(1 for r in records if not r.get("review_date"))
    invalid_rating = sum(
        1
        for r in records
        if r.get("rating") is not None
        and not (VALID_RATING_RANGE[0] <= r["rating"] <= VALID_RATING_RANGE[1])
    )
    generated_ids = sum(1 for r in records if r.get("review_id_is_generated"))

    id_counts = Counter(r.get("review_id") for r in records)
    duplicate_ids = [rid for rid, count in id_counts.items() if count > 1]
    duplicate_total = sum(count - 1 for count in id_counts.values() if count > 1)

    branch_counts = Counter(r.get("branch_id") for r in records)

    review_dates = [r["review_date"] for r in records if r.get("review_date")]
    date_range_start = min(review_dates) if review_dates else None
    date_range_end = max(review_dates) if review_dates else None

    warnings: list[str] = []
    errors: list[str] = []

    if missing_text:
        warnings.append(f"{missing_text} records have missing review text.")
    if invalid_rating:
        errors.append(f"{invalid_rating} records have ratings outside the valid range.")
    if duplicate_total:
        errors.append(f"{duplicate_total} duplicate review IDs detected.")
    if not records:
        warnings.append("No records were provided for validation.")

    return ValidationReport(
        total_records=total,
        missing_review_text=missing_text,
        missing_rating=missing_rating,
        missing_review_date=missing_date,
        invalid_rating=invalid_rating,
        duplicate_review_id_count=duplicate_total,
        duplicate_review_id_samples=[str(rid) for rid in duplicate_ids[:10]],
        generated_review_ids=generated_ids,
        records_by_branch=dict(branch_counts),
        date_range_start=date_range_start,
        date_range_end=date_range_end,
        warnings=warnings,
        errors=errors,
    )
