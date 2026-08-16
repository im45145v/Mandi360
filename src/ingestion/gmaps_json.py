"""Ingestion for raw Google Maps review exports (e.g. Apify-style scraper output).

The raw exports observed in data/raw/ use two schema variants for the same
review concept:

- "flat": older exports (e.g. BanjaraHillsBranch.json, GachibowliBranch.json)
  where reviewer, place, and rating fields live directly on the record
  (name, reviewerId, stars/rating, responseFromOwnerText, ...).
- "nested": newer exports (e.g. JubileeHillsBranch.json) where reviewer and
  place information are grouped under `author`/`place` sub-objects and the
  owner response lives under `ownerResponse`.

This module auto-detects which shape a record uses and maps both into one
normalized schema. Raw files are only ever read, never written to.
"""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional, Union

PathLike = Union[str, Path]

NORMALIZED_FIELDS = [
    "review_id",
    "brand_id",
    "branch_id",
    "branch_name",
    "place_name_raw",
    "source",
    "review_date",
    "rating",
    "review_text",
    "language",
    "owner_response_text",
    "owner_response_date",
    "review_url",
    "reviewer_id",
    "reviewer_name",
    "raw_source_file",
    "review_id_is_generated",
]


@dataclass(frozen=True)
class SourceSpec:
    """Describes one raw branch export and how its records should be labelled.

    Callers supply branch/brand identifiers explicitly so this module is not
    hardcoded to any particular filename or branch.
    """

    path: PathLike
    branch_id: str
    branch_name: str
    brand_id: str = "one_mandi"


def load_raw_records(path: PathLike) -> list[dict[str, Any]]:
    """Load a raw JSON export as-is. The source file is only opened for reading."""
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(
            f"Expected a top-level JSON list in {path}, got {type(data).__name__}"
        )
    return data


def _parse_iso_datetime(value: Optional[str]) -> Optional[str]:
    """Parse an ISO-8601 timestamp (as used by both observed schemas) to UTC ISO-8601."""
    if not value or not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.isoformat()


def _coerce_rating(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _stable_fallback_id(raw: dict[str, Any], branch_id: str) -> str:
    """Derive a deterministic review_id when the record has no usable reviewId.

    Not observed in the current raw exports (reviewId was present and unique
    for all 33,275 records), but kept as a safety net for future/other exports.
    """
    basis = "|".join(
        str(raw.get(key))
        for key in ("reviewerId", "author", "text", "publishedAtDate", "publishedAt")
    )
    digest = hashlib.sha256(f"{branch_id}|{basis}".encode("utf-8")).hexdigest()
    return f"generated-{digest[:24]}"


def normalize_record(
    raw: dict[str, Any], source: SourceSpec, source_file_name: str
) -> dict[str, Any]:
    """Map one raw record (flat or nested schema) into the normalized review schema."""
    is_nested = "place" in raw or "author" in raw

    if is_nested:
        place = raw.get("place") or {}
        author = raw.get("author") or {}
        owner_response = raw.get("ownerResponse") or {}
        review_url = raw.get("url")
        review_date_raw = raw.get("publishedAt")
        rating = _coerce_rating(raw.get("rating"))
        reviewer_id = author.get("id") if isinstance(author, dict) else None
        reviewer_name = author.get("name") if isinstance(author, dict) else None
        owner_response_text = (
            owner_response.get("text") if isinstance(owner_response, dict) else None
        )
        owner_response_date_raw = (
            owner_response.get("date") if isinstance(owner_response, dict) else None
        )
        place_name = place.get("name") if isinstance(place, dict) else None
    else:
        review_url = raw.get("reviewUrl")
        review_date_raw = raw.get("publishedAtDate")
        rating = _coerce_rating(raw.get("rating"))
        if rating is None:
            rating = _coerce_rating(raw.get("stars"))
        reviewer_id = raw.get("reviewerId")
        reviewer_name = raw.get("name")
        owner_response_text = raw.get("responseFromOwnerText")
        owner_response_date_raw = raw.get("responseFromOwnerDate")
        place_name = raw.get("title")

    raw_review_id = raw.get("reviewId")
    review_id_is_generated = not raw_review_id
    review_id = raw_review_id or _stable_fallback_id(raw, source.branch_id)

    review_text = raw.get("text")
    if review_text is not None and not isinstance(review_text, str):
        review_text = str(review_text)

    return {
        "review_id": review_id,
        "brand_id": source.brand_id,
        "branch_id": source.branch_id,
        "branch_name": source.branch_name,
        "place_name_raw": place_name,
        "source": "google_maps",
        "review_date": _parse_iso_datetime(review_date_raw),
        "rating": rating,
        "review_text": review_text,
        "language": raw.get("language"),
        "owner_response_text": owner_response_text,
        "owner_response_date": _parse_iso_datetime(owner_response_date_raw),
        "review_url": review_url,
        "reviewer_id": reviewer_id,
        "reviewer_name": reviewer_name,
        "raw_source_file": source_file_name,
        "review_id_is_generated": review_id_is_generated,
    }


def ingest_gmaps_reviews(sources: Iterable[SourceSpec]) -> list[dict[str, Any]]:
    """Ingest one or more raw branch exports into a single normalized review list.

    Schema-tolerant: auto-detects the flat vs nested record shape per record.
    Reusable across any set of branch files; never modifies the raw sources.
    """
    normalized: list[dict[str, Any]] = []
    for source in sources:
        path = Path(source.path)
        raw_records = load_raw_records(path)
        for raw in raw_records:
            if not isinstance(raw, dict):
                continue
            normalized.append(normalize_record(raw, source, path.name))
    return normalized


def write_normalized_csv(records: list[dict[str, Any]], output_path: PathLike) -> None:
    """Write normalized records to CSV, creating parent directories as needed."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=NORMALIZED_FIELDS)
        writer.writeheader()
        for record in records:
            writer.writerow(record)
