"""Predictive Analytics view — branch rating forecasts and risk levels."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.data_loader import load_anomalies, load_forecasts
from app.theme import GOLD, MAROON, TEAL, apply_theme, banner, data_tag

apply_theme("Predictive Analytics")
banner("Looking Ahead", "Expected rating direction and branch risk signals")
st.markdown(
    data_tag("predicted") + " Forecasts extend historical patterns and are not certainties. "
    "Use them as an early-warning signal alongside current customer feedback.",
    unsafe_allow_html=True,
)

forecasts = load_forecasts()
if not forecasts:
    st.warning("Forecast results not available yet. Run `python -m src.pipeline`.")
    st.stop()

anomalies = load_anomalies()
risk_colors = {"stable": TEAL, "watch": GOLD, "elevated": MAROON}

for branch in forecasts["branches_forecasted"]:
    branch_id = branch["branch_id"]
    st.subheader(f"{branch_id.replace('_', ' ').title()} — risk signal: {branch['risk_level'].upper()}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Expected monthly direction", branch["trend_slope_per_month"])
    if branch["evaluation"]:
        col2.metric("Forecast error (typical)", branch["evaluation"]["mae"])
        col3.metric("Forecast error (larger misses)", branch["evaluation"]["rmse"])

    history = anomalies[anomalies["branch_id"] == branch_id].sort_values("month") if not anomalies.empty else pd.DataFrame()
    fig = go.Figure()
    if not history.empty:
        fig.add_trace(go.Scatter(x=history["month"], y=history["average_rating"], mode="lines+markers", name="Observed", line=dict(color=TEAL)))
    forecast_months = [row["month"] for row in branch["forecast"]]
    forecast_values = [row["predicted_average_rating"] for row in branch["forecast"]]
    fig.add_trace(go.Scatter(x=forecast_months, y=forecast_values, mode="lines+markers", name="Forecast", line=dict(color=risk_colors.get(branch["risk_level"], MAROON), dash="dash")))
    fig.add_trace(go.Scatter(
        x=forecast_months + forecast_months[::-1],
        y=[row["upper_bound"] for row in branch["forecast"]] + [row["lower_bound"] for row in branch["forecast"]][::-1],
        fill="toself", fillcolor="rgba(166,25,46,0.12)", line=dict(color="rgba(0,0,0,0)"),
        name="95% prediction interval",
    ))
    fig.update_layout(title="Observed rating history + forecast", plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)

if forecasts.get("branches_skipped_insufficient_history"):
    st.info(
        "Skipped (insufficient monthly history): "
        + ", ".join(row["branch_id"] for row in forecasts["branches_skipped_insufficient_history"])
    )
