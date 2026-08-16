"""Conservative, reproducible text preprocessing for review records."""
from __future__ import annotations

import csv
import html
import re
import unicodedata
from pathlib import Path
from typing import Any, Iterable

_TAG_PATTERN = re.compile(r"<[^>]+>")
_WHITESPACE_PATTERN = re.compile(r"\s+")
_SPACE_BEFORE_PUNCTUATION_PATTERN = re.compile(r"\s+([,.;:!?])")

ANALYTICAL_FIELDS = [
    "review_id",
    "brand_id",
    "branch_id",
    "branch_name",
    "source",
    "review_date",
    "rating",
    "review_text",
    "language",
    "raw_source_file",
    "review_id_is_generated",
    "cleaned_text",
    "text_available",
    "text_length_chars",
    "text_word_count",
    "preprocessing_status",
]


def clean_review_text(value: Any) -> str | None:
    """Normalize review text without inventing text for missing values."""
    if value is None:
        return None
    text = str(value)
    text = unicodedata.normalize("NFKC", text)
    text = html.unescape(text)
    text = _TAG_PATTERN.sub(" ", text)
    text = _WHITESPACE_PATTERN.sub(" ", text).strip()
    text = _SPACE_BEFORE_PUNCTUATION_PATTERN.sub(r"\1", text)
    return text or None


def preprocess_records(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return copied records with derived text features added."""
    processed: list[dict[str, Any]] = []
    for record in records:
        processed_record = dict(record)
        original_text = record.get("review_text")
        cleaned_text = clean_review_text(original_text)
        processed_record.update(
            {
                "cleaned_text": cleaned_text,
                "text_available": cleaned_text is not None,
                "text_length_chars": len(cleaned_text) if cleaned_text else 0,
                "text_word_count": len(cleaned_text.split()) if cleaned_text else 0,
                "preprocessing_status": "available" if cleaned_text else "missing_text",
            }
        )
        processed.append(processed_record)
    return processed


def write_preprocessed_csv(records: list[dict[str, Any]], output_path: str | Path) -> None:
    """Write privacy-minimized preprocessed records and retain original text."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        output.write_text("\n", encoding="utf-8")
        return
    fieldnames = [field for field in ANALYTICAL_FIELDS if field in records[0]]
    with output.open("w", encoding="utf-8", newline="") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows({field: record.get(field) for field in fieldnames} for record in records)
