from __future__ import annotations

from pathlib import Path
from typing import Iterable

from src.analytics.anomaly import build_monthly_branch_features, detect_anomalies, write_anomaly_artifacts
from src.analytics.association import mine_association_rules, write_association_artifacts
from src.analytics.clustering import fit_review_clusters, write_cluster_artifacts
from src.analytics.crm import build_crm_cases, write_crm_artifacts
from src.analytics.eda import write_eda_artifacts
from src.analytics.forecasting import forecast_branch_ratings, write_forecast_artifacts
from src.analytics.nlp import build_nlp_records, write_nlp_artifacts
from src.analytics.topics import fit_topic_model, write_topic_artifacts
from src.config.settings import (
    ANOMALY_RESULTS_DIR,
    ASSOCIATION_RESULTS_DIR,
    CLUSTERING_RESULTS_DIR,
    DEFAULT_SOURCES,
    FORECAST_RESULTS_DIR,
    CRM_RESULTS_DIR,
    INTERIM_DIR,
    NLP_RESULTS_DIR,
    RESULTS_TABLES_DIR,
)
from src.ingestion.gmaps_json import SourceSpec, ingest_gmaps_reviews, write_normalized_csv
from src.preprocessing.text import preprocess_records, write_preprocessed_csv
from src.preprocessing.validation import validate_normalized_reviews
from src.storage.manifest import build_dataset_manifest, save_manifest


def run_ingestion_pipeline(sources: Iterable[SourceSpec] | None = None) -> tuple[list[dict], dict]:
    """Run the data-foundation pipeline on one or more Google Maps exports.

    Writes the normalized CSV and validation report under data/interim without
    mutating the raw files in data/raw.
    """
    source_list = list(sources) if sources is not None else list(DEFAULT_SOURCES)
    records = ingest_gmaps_reviews(source_list)
    report = validate_normalized_reviews(records)

    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    normalized_output = INTERIM_DIR / "reviews_normalized.csv"
    write_normalized_csv(records, normalized_output)
    report.save(INTERIM_DIR / "validation_report.json")
    manifest = build_dataset_manifest(source_list, records, normalized_output)
    save_manifest(manifest, INTERIM_DIR / "dataset_manifest.json")
    processed_records = preprocess_records(records)
    write_preprocessed_csv(processed_records, INTERIM_DIR / "reviews_preprocessed.csv")
    write_eda_artifacts(processed_records, RESULTS_TABLES_DIR)
    nlp_records, aspect_rows = build_nlp_records(processed_records)
    write_nlp_artifacts(nlp_records, aspect_rows, NLP_RESULTS_DIR)
    crm_result = build_crm_cases(aspect_rows, [])
    try:
        topic_model = fit_topic_model(processed_records)
        write_topic_artifacts(topic_model, NLP_RESULTS_DIR)
    except ValueError:
        pass
    try:
        cluster_model = fit_review_clusters(processed_records)
        write_cluster_artifacts(cluster_model, CLUSTERING_RESULTS_DIR)
    except ValueError:
        pass
    try:
        association_result = mine_association_rules(nlp_records, aspect_rows)
        write_association_artifacts(association_result, ASSOCIATION_RESULTS_DIR)
    except ValueError:
        pass
    monthly_branch_features = build_monthly_branch_features(nlp_records)
    try:
        anomaly_result = detect_anomalies(monthly_branch_features)
        write_anomaly_artifacts(anomaly_result, ANOMALY_RESULTS_DIR)
        crm_result = build_crm_cases(aspect_rows, anomaly_result["rows"])
    except ValueError:
        pass
    write_crm_artifacts(crm_result, CRM_RESULTS_DIR)
    forecast_result = forecast_branch_ratings(monthly_branch_features)
    write_forecast_artifacts(forecast_result, FORECAST_RESULTS_DIR)
    return records, report.to_dict()


if __name__ == "__main__":
    run_ingestion_pipeline()
