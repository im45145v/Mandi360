import json

from src.ingestion.gmaps_json import SourceSpec, normalize_record
from src.storage.manifest import build_dataset_manifest, sha256_file


def test_manifest_records_source_hashes_and_counts(tmp_path):
    raw_path = tmp_path / "branch.json"
    raw_path.write_text(json.dumps([{"reviewId": "review-1"}]), encoding="utf-8")
    source = SourceSpec(
        path=raw_path,
        branch_id="branch_a",
        branch_name="Branch A",
    )
    record = normalize_record(
        {"reviewId": "review-1", "publishedAtDate": "2026-01-01T00:00:00Z", "stars": 5},
        source,
        raw_path.name,
    )

    manifest = build_dataset_manifest([source], [record], tmp_path / "reviews.csv")

    assert manifest["normalized_output"]["record_count"] == 1
    assert manifest["records_by_branch"] == {"branch_a": 1}
    assert manifest["source_files"][0]["sha256"] == sha256_file(raw_path)
    assert manifest["source_files"][0]["size_bytes"] == raw_path.stat().st_size
