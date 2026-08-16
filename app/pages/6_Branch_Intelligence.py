"""Branch Intelligence — consolidated per-branch drill-down using the tool layer."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.express as px
import streamlit as st

from app.theme import CHART_SEQUENCE, apply_theme, banner, data_tag
from src.agents import tools
from src.config.settings import DEFAULT_SOURCES

apply_theme("Branch Intelligence")
banner("Branch Intelligence", "A management view of one branch's customer experience")

branch_options = {source.branch_name: source.branch_id for source in DEFAULT_SOURCES}
selected_name = st.selectbox("Select branch", list(branch_options.keys()))
branch_id = branch_options[selected_name]

summary = tools.get_branch_summary(branch_id)
if not summary:
    st.warning("Branch summary not available yet. Run `python -m src.pipeline`.")
    st.stop()

st.markdown(data_tag("real"), unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
col1.metric("Reviews", summary["review_count"])
col2.metric("Average Rating", summary["average_rating"])
col3.metric("Reviews with Text", summary["text_available_count"])

st.subheader("Rating Over Time")
st.markdown(data_tag("derived") + " Monthly observed ratings; empty months remain visible in the analytical artifact but have no invented rating.", unsafe_allow_html=True)
trend = tools.get_sentiment_trend(branch_id)
trend_df = pd.DataFrame(trend)
if not trend_df.empty and "average_rating" in trend_df.columns:
    trend_df["average_rating"] = pd.to_numeric(trend_df["average_rating"], errors="coerce")
    trend_df = trend_df.dropna(subset=["average_rating"])
    fig = px.line(trend_df, x="month", y="average_rating", markers=True, title="Observed monthly average rating")
    fig.update_yaxes(range=[1, 5], title="Average rating (1-5)")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No monthly rating history available for this branch.")

st.subheader("Experience Dimensions")
st.markdown(data_tag("derived"), unsafe_allow_html=True)
aspects = tools.get_aspect_sentiment(branch_id)
if aspects:
    df = pd.DataFrame(aspects)
    fig = px.bar(df, x="aspect", y="mention_count", color="aspect", color_discrete_sequence=CHART_SEQUENCE)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No aspect mentions found for this branch.")

st.subheader("Looking Ahead")
st.markdown(data_tag("predicted"), unsafe_allow_html=True)
forecast = tools.get_forecast(branch_id)
if forecast:
    st.write(f"Risk signal: **{forecast['risk_level'].upper()}** · Expected monthly direction: {forecast['trend_slope_per_month']}")
    st.dataframe(pd.DataFrame(forecast["forecast"]), use_container_width=True)
else:
    st.info("Not enough monthly history to forecast this branch yet.")

st.subheader("Early-Warning Months")
st.markdown(data_tag("derived"), unsafe_allow_html=True)
branch_anomalies = tools.get_anomalies(branch_id)
if branch_anomalies:
    st.dataframe(pd.DataFrame(branch_anomalies), use_container_width=True)
else:
    st.info("No anomalies flagged for this branch.")

st.subheader("Management Action Tips")
st.markdown(data_tag("derived") + " Evidence-ranked tips for branch review; recommendations require human validation.", unsafe_allow_html=True)
crm_cases = tools.get_crm_cases(branch_id=branch_id)
if crm_cases:
    st.dataframe(pd.DataFrame(crm_cases), use_container_width=True)
else:
    st.info("No evidence-ranked CRM cases for this branch.")

st.subheader("Search Customer Feedback")
query = st.text_input("Search cleaned review text", value="service")
if query:
    matches = tools.search_feedback(query, branch_id=branch_id, limit=20)
    st.markdown(data_tag("real") + f" {len(matches)} matching reviews shown (real text, max 20).", unsafe_allow_html=True)
    if matches:
        st.dataframe(pd.DataFrame(matches), use_container_width=True)
    else:
        st.info("No matching reviews found.")
