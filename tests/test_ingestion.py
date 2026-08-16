import json

from src.ingestion.gmaps_json import (
    SourceSpec,
    ingest_gmaps_reviews,
    normalize_record,
    write_normalized_csv,
)
from src.preprocessing.validation import validate_normalized_reviews

FLAT_RECORD = {
    "reviewerId": "111111",
    "reviewerUrl": "https://www.google.com/maps/contrib/111111",
    "name": "Alice Reviewer",
    "text": "Great mandi, will come again.",
    "publishAt": "2 days ago",
    "publishedAtDate": "2026-08-10T12:00:00.000Z",
    "reviewId": "flat-review-1",
    "reviewUrl": "https://www.google.com/maps/reviews/flat-review-1",
    "stars": 5,
    "rating": None,
    "responseFromOwnerDate": "2026-08-11T09:00:00.000Z",
    "responseFromOwnerText": "Thank you!",
    "title": "Mandi @ 36 Arabian Kitchen",
    "language": "en",
}

FLAT_RECORD_MISSING_TEXT = {
    "reviewerId": "222222",
    "name": "Bob Reviewer",
    "text": None,
    "publishedAtDate": "2026-08-12T08:30:00.000Z",
    "reviewId": "flat-review-2",
    "stars": 3,
    "rating": None,
    "language": "en",
}

NESTED_RECORD = {
    "place": {"name": "MANDI @ 36 Arabian kitchen", "placeId": "abc123"},
    "author": {"id": "333333", "name": "Charlie Author"},
    "reviewId": "nested-review-1",
    "url": "https://www.google.com/maps/reviews/nested-review-1",
    "publishedAt": "2023-10-24T10:19:36.425Z",
    "text": "Loved the mutton mandi here.",
    "rating": 4,
    "ownerResponse": None,
    "language": "en",
}

NESTED_RECORD_NO_ID = {
    "place": {"name": "MANDI @ 36 Arabian kitchen"},
    "author": {"id": "444444", "name": "Dana Author"},
    "reviewId": "",
    "publishedAt": "2023-11-01T10:00:00.000Z",
    "text": "Decent food, average service.",
    "rating": 3,
}

DUPLICATE_OF_FLAT_RECORD = dict(FLAT_RECORD)


def _source(tmp_path, name, records, branch_id, branch_name):
    path = tmp_path / name
    path.write_text(json.dumps(records), encoding="utf-8")
    return SourceSpec(path=path, branch_id=branch_id, branch_name=branch_name)


def test_normalize_record_flat_schema():
    source = SourceSpec(path="unused.json", branch_id="banjara_hills", branch_name="Banjara Hills")
    normalized = normalize_record(FLAT_RECORD, source, "BanjaraHillsBranch.json")

    assert normalized["review_id"] == "flat-review-1"
    assert normalized["review_id_is_generated"] is False
    assert normalized["rating"] == 5.0
    assert normalized["review_text"] == "Great mandi, will come again."
    assert normalized["reviewer_id"] == "111111"
    assert normalized["owner_response_text"] == "Thank you!"
    assert normalized["review_date"] == "2026-08-10T12:00:00+00:00"
    assert normalized["branch_id"] == "banjara_hills"
    assert normalized["raw_source_file"] == "BanjaraHillsBranch.json"


def test_normalize_record_nested_schema():
    source = SourceSpec(path="unused.json", branch_id="jubilee_hills", branch_name="Jubilee Hills")
    normalized = normalize_record(NESTED_RECORD, source, "JubileeHillsBranch.json")

    assert normalized["review_id"] == "nested-review-1"
    assert normalized["rating"] == 4.0
    assert normalized["reviewer_id"] == "333333"
    assert normalized["reviewer_name"] == "Charlie Author"
    assert normalized["place_name_raw"] == "MANDI @ 36 Arabian kitchen"
    assert normalized["owner_response_text"] is None
    assert normalized["review_date"] == "2023-10-24T10:19:36.425000+00:00"


def test_normalize_record_missing_text_is_safe():
    source = SourceSpec(path="unused.json", branch_id="banjara_hills", branch_name="Banjara Hills")
    normalized = normalize_record(FLAT_RECORD_MISSING_TEXT, source, "BanjaraHillsBranch.json")

    assert normalized["review_text"] is None
    assert normalized["rating"] == 3.0


def test_normalize_record_generates_fallback_id_when_missing():
    source = SourceSpec(path="unused.json", branch_id="jubilee_hills", branch_name="Jubilee Hills")
    normalized = normalize_record(NESTED_RECORD_NO_ID, source, "JubileeHillsBranch.json")

    assert normalized["review_id"].startswith("generated-")
    assert normalized["review_id_is_generated"] is True


def test_ingest_gmaps_reviews_combines_multiple_sources(tmp_path):
    flat_source = _source(
        tmp_path,
        "BanjaraHillsBranch.json",
        [FLAT_RECORD, FLAT_RECORD_MISSING_TEXT],
        "banjara_hills",
        "Banjara Hills",
    )
    nested_source = _source(
        tmp_path,
        "JubileeHillsBranch.json",
        [NESTED_RECORD, NESTED_RECORD_NO_ID],
        "jubilee_hills",
        "Jubilee Hills",
    )

    records = ingest_gmaps_reviews([flat_source, nested_source])

    assert len(records) == 4
    branch_ids = {r["branch_id"] for r in records}
    assert branch_ids == {"banjara_hills", "jubilee_hills"}


def test_ingest_gmaps_reviews_does_not_modify_raw_file(tmp_path):
    source = _source(tmp_path, "BanjaraHillsBranch.json", [FLAT_RECORD], "banjara_hills", "Banjara Hills")
    original_bytes = source.path.read_bytes()

    ingest_gmaps_reviews([source])

    assert source.path.read_bytes() == original_bytes


def test_write_normalized_csv(tmp_path):
    source = SourceSpec(path="unused.json", branch_id="banjara_hills", branch_name="Banjara Hills")
    records = [normalize_record(FLAT_RECORD, source, "BanjaraHillsBranch.json")]
    output_path = tmp_path / "interim" / "reviews_normalized.csv"

    write_normalized_csv(records, output_path)

    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8")
    assert "flat-review-1" in content


def test_validate_normalized_reviews_detects_issues():
    source = SourceSpec(path="unused.json", branch_id="banjara_hills", branch_name="Banjara Hills")
    records = [
        normalize_record(FLAT_RECORD, source, "BanjaraHillsBranch.json"),
        normalize_record(FLAT_RECORD_MISSING_TEXT, source, "BanjaraHillsBranch.json"),
        normalize_record(DUPLICATE_OF_FLAT_RECORD, source, "BanjaraHillsBranch.json"),
    ]

    report = validate_normalized_reviews(records)

    assert report.total_records == 3
    assert report.missing_review_text == 1
    assert report.duplicate_review_id_count == 1
    assert "flat-review-1" in report.duplicate_review_id_samples
    assert report.records_by_branch == {"banjara_hills": 3}
    assert report.date_range_start == "2026-08-10T12:00:00+00:00"
    assert report.date_range_end == "2026-08-12T08:30:00+00:00"
    assert isinstance(report.warnings, list)
    assert isinstance(report.errors, list)
