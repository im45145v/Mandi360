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

from app.display import business_dataframe
from app.theme import CHART_SEQUENCE, apply_theme, banner, data_tag
from src.agents import tools
from src.config.settings import DEFAULT_SOURCES

apply_theme("Branch Intelligence")
banner("Branch CRM View", "A management view of one branch's customer experience and action priorities")

branch_options = {source.branch_name: source.branch_id for source in DEFAULT_SOURCES}
selected_name = st.selectbox("Select branch", list(branch_options.keys()))
branch_id = branch_options[selected_name]

summary = tools.get_branch_summary(branch_id)
if not summary:
    st.warning("Branch summary is not available yet. Refresh the latest review analysis first.")
    st.stop()

st.markdown(data_tag("real"), unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
col1.metric("Reviews", summary["review_count"])
col2.metric("Average Rating", summary["average_rating"])
col3.metric("Reviews with Text", summary["text_available_count"])

st.subheader("Rating Over Time")
st.markdown(data_tag("derived") + " Monthly observed ratings; empty months are left blank rather than estimated.", unsafe_allow_html=True)
trend = tools.get_sentiment_trend(branch_id)
trend_df = pd.DataFrame(trend)
if not trend_df.empty and "average_rating" in trend_df.columns:
    trend_df["average_rating"] = pd.to_numeric(trend_df["average_rating"], errors="coerce")
    trend_df = trend_df.dropna(subset=["average_rating"])
    fig = px.line(trend_df, x="month", y="average_rating", markers=True, title="Observed monthly average rating", labels={"month": "month", "average_rating": "average rating"})
    fig.update_yaxes(range=[1, 5], title="Average rating (1-5)")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No monthly rating history available for this branch.")

st.subheader("Experience Areas")
st.markdown(data_tag("derived"), unsafe_allow_html=True)
aspects = tools.get_aspect_sentiment(branch_id)
if aspects:
    df = pd.DataFrame(aspects)
    fig = px.bar(df, x="aspect", y="mention_count", color="aspect", color_discrete_sequence=CHART_SEQUENCE, labels={"aspect": "experience area", "mention_count": "mentions"})
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(
        business_dataframe(df, ["aspect", "mention_count", "average_sentiment_score"]),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No aspect mentions found for this branch.")

st.subheader("Looking Ahead")
st.markdown(data_tag("predicted"), unsafe_allow_html=True)
forecast = tools.get_forecast(branch_id)
if forecast:
    st.write(f"Management attention: **{forecast['risk_level'].upper()}** · Expected monthly direction: {forecast['trend_slope_per_month']}")
    st.dataframe(
        business_dataframe(pd.DataFrame(forecast["forecast"]), ["month", "predicted_average_rating", "lower_bound", "upper_bound"]),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("Not enough monthly history to forecast this branch yet.")

st.subheader("Early-Warning Months")
st.markdown(data_tag("derived"), unsafe_allow_html=True)
branch_anomalies = tools.get_anomalies(branch_id)
if branch_anomalies:
    st.dataframe(
        business_dataframe(pd.DataFrame(branch_anomalies), ["month", "alert_severity", "alert_reasons", "review_count", "average_rating", "negative_ratio"]),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No unusual months are flagged for this branch.")

st.subheader("CRM Action Priorities")
st.markdown(data_tag("derived") + " Evidence-ranked CRM tips for branch review; recommendations require manager validation.", unsafe_allow_html=True)
crm_cases = tools.get_crm_cases(branch_id=branch_id)
if crm_cases:
    st.dataframe(
        business_dataframe(pd.DataFrame(crm_cases), ["issue", "priority", "mention_count", "recommended_action", "suggested_owner", "review_cycle"]),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No evidence-ranked CRM actions for this branch.")

st.subheader("Search Customer Feedback")
query = st.text_input("Search customer comments", value="service")
if query:
    matches = tools.search_feedback(query, branch_id=branch_id, limit=20)
    st.markdown(data_tag("real") + f" {len(matches)} matching reviews shown (real text, max 20).", unsafe_allow_html=True)
    if matches:
        st.dataframe(
            business_dataframe(pd.DataFrame(matches), ["branch_name", "review_date", "rating", "review_text"]),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No matching reviews found.")
