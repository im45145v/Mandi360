"""Early-Warning Center — unusual branch-month combinations requiring review."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import plotly.express as px
import streamlit as st

from app.data_loader import load_anomalies
from app.theme import CHART_SEQUENCE, apply_theme, banner, data_tag

apply_theme("Early-Warning Center")
banner("Anomaly Center", "Unusual branch-month volume/rating/sentiment combinations")
st.markdown(
    data_tag("derived") + " Flags identify unusual combinations of review volume, rating, and "
    "sentiment. They require human review and are not confirmed incidents.",
    unsafe_allow_html=True,
)

anomalies = load_anomalies()
if anomalies.empty:
    st.warning("Anomaly results not available yet. Run `python -m src.pipeline`.")
    st.stop()

flagged = anomalies[anomalies["is_anomaly"].astype(str).str.lower() == "true"]
st.metric("Flagged branch-months", len(flagged))

fig = px.scatter(
    anomalies, x="month", y="average_rating", color="branch_id", size="review_count",
    symbol="is_anomaly", color_discrete_sequence=CHART_SEQUENCE,
    title="Monthly Average Rating (flagged anomalies marked)",
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Early-Warning Months and Reasons")
display_columns = [
    column for column in [
        "branch_name", "branch_id", "month", "alert_severity", "alert_reasons",
        "review_count", "average_rating", "negative_ratio", "anomaly_score",
    ] if column in flagged.columns
]
st.dataframe(flagged.sort_values(["alert_severity", "anomaly_score"])[display_columns], use_container_width=True)
