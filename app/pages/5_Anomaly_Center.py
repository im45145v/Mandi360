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
from app.theme import CHART_SEQUENCE, apply_theme, banner, business_dataframe, data_tag

apply_theme("Early-Warning Center")
banner("Early-Warning Center", "Unusual branch-month changes in reviews, ratings, and customer mood")
st.markdown(
    data_tag("derived") + " This page translates anomaly detection into manager review points. "
    "Flags identify unusual combinations of review volume, rating, and customer mood; they are not confirmed incidents.",
    unsafe_allow_html=True,
)

anomalies = load_anomalies()
if anomalies.empty:
    st.warning("Early-warning results are not available yet. Refresh the latest review analysis first.")
    st.stop()

flagged = anomalies[anomalies["is_anomaly"].astype(str).str.lower() == "true"]
st.metric("Months Needing Attention", len(flagged))

fig = px.scatter(
    anomalies, x="month", y="average_rating", color="branch_id", size="review_count",
    symbol="is_anomaly", color_discrete_sequence=CHART_SEQUENCE,
    title="Monthly Average Rating (attention months marked)",
    labels={"month": "month", "average_rating": "average rating", "branch_id": "branch", "review_count": "reviews"},
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Early-Warning Months and Reasons")
display_columns = [
    column for column in [
        "branch_name", "branch_id", "month", "alert_severity", "alert_reasons",
        "review_count", "average_rating", "negative_ratio",
    ] if column in flagged.columns
]
st.dataframe(
    business_dataframe(flagged.sort_values(["alert_severity", "month"])[display_columns]),
    use_container_width=True,
    hide_index=True,
)
