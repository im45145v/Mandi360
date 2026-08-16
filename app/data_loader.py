"""Read-only loaders for pre-computed results (no analytics logic here).

Every function reads an artifact already produced by src/pipeline.py and
returns a pandas DataFrame/dict for display. If an artifact is missing
(pipeline not yet run for that stage), an empty/None value is returned so
pages can show a clear "not available yet" message instead of crashing.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.config.settings import (
    ANOMALY_RESULTS_DIR,
    ASSOCIATION_RESULTS_DIR,
    CLUSTERING_RESULTS_DIR,
    CRM_RESULTS_DIR,
    FORECAST_RESULTS_DIR,
    INTERIM_DIR,
    NLP_RESULTS_DIR,
    RESULTS_TABLES_DIR,
)


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


@st.cache_data(show_spinner=False)
def load_dataset_summary() -> dict | None:
    return _read_json(RESULTS_TABLES_DIR / "dataset_summary.json")


@st.cache_data(show_spinner=False)
def load_branch_summary() -> pd.DataFrame:
    return _read_csv(RESULTS_TABLES_DIR / "branch_summary.csv")


@st.cache_data(show_spinner=False)
def load_monthly_summary() -> pd.DataFrame:
    return _read_csv(RESULTS_TABLES_DIR / "monthly_summary.csv")


@st.cache_data(show_spinner=False)
def load_manifest() -> dict | None:
    return _read_json(INTERIM_DIR / "dataset_manifest.json")


@st.cache_data(show_spinner=False)
def load_validation_report() -> dict | None:
    return _read_json(INTERIM_DIR / "validation_report.json")


@st.cache_data(show_spinner=False)
def load_nlp_reviews() -> pd.DataFrame:
    return _read_csv(NLP_RESULTS_DIR / "reviews_nlp_baseline.csv")


@st.cache_data(show_spinner=False)
def load_review_aspects() -> pd.DataFrame:
    return _read_csv(NLP_RESULTS_DIR / "review_aspects_baseline.csv")


@st.cache_data(show_spinner=False)
def load_topic_model() -> dict | None:
    return _read_json(NLP_RESULTS_DIR / "topic_model_nmf.json")


@st.cache_data(show_spinner=False)
def load_review_topics() -> pd.DataFrame:
    return _read_csv(NLP_RESULTS_DIR / "review_topics_nmf.csv")


@st.cache_data(show_spinner=False)
def load_cluster_model() -> dict | None:
    return _read_json(CLUSTERING_RESULTS_DIR / "cluster_model_kmeans.json")


@st.cache_data(show_spinner=False)
def load_association_rules() -> dict | None:
    return _read_json(ASSOCIATION_RESULTS_DIR / "association_rules.json")


@st.cache_data(show_spinner=False)
def load_anomalies() -> pd.DataFrame:
    return _read_csv(ANOMALY_RESULTS_DIR / "anomalies.csv")


@st.cache_data(show_spinner=False)
def load_forecasts() -> dict | None:
    return _read_json(FORECAST_RESULTS_DIR / "branch_forecasts.json")


@st.cache_data(show_spinner=False)
def load_crm_cases() -> pd.DataFrame:
    return _read_csv(CRM_RESULTS_DIR / "crm_cases.csv")
