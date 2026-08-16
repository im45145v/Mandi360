"""Dataset lineage and reproducibility metadata."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from src.ingestion.gmaps_json import SourceSpec


def sha256_file(path: str | Path) -> str:
    """Return the SHA-256 digest of a file without loading it all into memory."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_dataset_manifest(
    sources: Iterable[SourceSpec],
    records: list[dict[str, Any]],
    normalized_output: str | Path,
) -> dict[str, Any]:
    """Build a JSON-serializable manifest for one ingestion run."""
    source_entries = []
    for source in sources:
        path = Path(source.path)
        source_entries.append(
            {
                "path": str(path),
                "file_name": path.name,
                "branch_id": source.branch_id,
                "branch_name": source.branch_name,
                "brand_id": source.brand_id,
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )

    output_path = Path(normalized_output)
    return {
        "manifest_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "data_status": "real_input_with_derived_normalization",
        "source_files": source_entries,
        "normalized_output": {
            "path": str(output_path),
            "record_count": len(records),
        },
        "records_by_branch": _count_by(records, "branch_id"),
        "records_by_source_file": _count_by(records, "raw_source_file"),
    }


def save_manifest(manifest: dict[str, Any], path: str | Path) -> None:
    """Persist a manifest as readable JSON."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _count_by(records: list[dict[str, Any]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        value = record.get(field)
        key = str(value) if value is not None else "<missing>"
        counts[key] = counts.get(key, 0) + 1
    return counts
