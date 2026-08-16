"""Centralized paths and source configuration for local pipeline runs."""
from __future__ import annotations

from pathlib import Path

from src.ingestion.gmaps_json import SourceSpec

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
RESULTS_TABLES_DIR = PROJECT_ROOT / "results" / "tables"
NLP_RESULTS_DIR = RESULTS_TABLES_DIR / "nlp"
CLUSTERING_RESULTS_DIR = RESULTS_TABLES_DIR / "clustering"
ASSOCIATION_RESULTS_DIR = RESULTS_TABLES_DIR / "association"
ANOMALY_RESULTS_DIR = RESULTS_TABLES_DIR / "anomaly"
FORECAST_RESULTS_DIR = RESULTS_TABLES_DIR / "predictive"
CRM_RESULTS_DIR = RESULTS_TABLES_DIR / "crm"

DEFAULT_SOURCES = [
    SourceSpec(
        path=RAW_DIR / "BanjaraHillsBranch.json",
        branch_id="banjara_hills",
        branch_name="Banjara Hills",
        brand_id="one_mandi",
    ),
    SourceSpec(
        path=RAW_DIR / "GachibowliBranch.json",
        branch_id="gachibowli",
        branch_name="Gachibowli",
        brand_id="one_mandi",
    ),
    SourceSpec(
        path=RAW_DIR / "JubileeHillsBranch.json",
        branch_id="jubilee_hills",
        branch_name="Jubilee Hills",
        brand_id="one_mandi",
    ),
]
