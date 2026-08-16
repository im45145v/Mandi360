"""Executive Overview — Mandi360 Customer Experience Intelligence dashboard."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import plotly.express as px
import streamlit as st

from app.data_loader import load_anomalies, load_branch_summary, load_crm_cases, load_dataset_summary, load_monthly_summary, load_validation_report
from app.theme import CHART_SEQUENCE, apply_theme, banner, data_tag

apply_theme("Executive Overview")
banner(
    "Mandi @ 36 — Customer Experience Intelligence",
    "One Mandi restaurant brand, Hyderabad · Executive Overview",
)

summary = load_dataset_summary()
if summary is None:
    st.warning("Analysis results are not available yet. Run the data pipeline before opening the dashboard.")
    st.stop()

st.markdown(data_tag("real") + " Review volume, ratings, and dates below are real collected data.", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Reviews", f"{summary['record_count']:,}")
col2.metric("Branches", summary["branch_count"])
col3.metric("Average Rating", summary["average_rating"])
col4.metric("Reviews with Text", f"{summary['text_available_count']:,}")

st.caption(f"Date range: {summary['date_range_start']} → {summary['date_range_end']}")

anomalies = load_anomalies()
if not anomalies.empty:
    flagged = anomalies[anomalies["is_anomaly"].astype(str).str.lower() == "true"]
    alert_count = len(flagged)
    high_count = int((flagged.get("alert_severity", "low") == "high").sum()) if not flagged.empty else 0
    alert_col, high_col = st.columns(2)
    alert_col.metric("Active Alerts", alert_count, help="Derived model/rule outputs requiring human review.")
    high_col.metric("High-Severity Alerts", high_count)

st.subheader("Branch Comparison")
branch_df = load_branch_summary()
if not branch_df.empty:
    fig = px.bar(
        branch_df,
        x="branch_name",
        y="average_rating",
        color="branch_name",
        color_discrete_sequence=CHART_SEQUENCE,
        text="review_count",
        title="Average Customer Rating by Branch (bar label = review count)",
    )
    fig.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(branch_df, use_container_width=True)
else:
    st.info("Branch summary is not available yet.")

st.subheader("Rating Trend Over Time")
monthly_df = load_monthly_summary()
if not monthly_df.empty:
    fig2 = px.line(
        monthly_df.dropna(subset=["average_rating"]),
        x="month",
        y="average_rating",
        color="branch_name" if "branch_name" in monthly_df.columns else "branch_id",
        color_discrete_sequence=CHART_SEQUENCE,
        markers=True,
        title="Monthly Average Customer Rating by Branch (observed months)",
    )
    fig2.update_yaxes(range=[1, 5], title="Average rating (1-5)")
    fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Monthly rating history is not available yet.")

st.subheader("Priority Management Actions")
st.markdown(data_tag("derived") + " Evidence-ranked action tips from recurring customer issues and unusual branch patterns.", unsafe_allow_html=True)
crm_df = load_crm_cases()
if not crm_df.empty:
    columns = [column for column in ["branch_id", "issue", "priority", "mention_count", "average_sentiment_score", "recommended_action"] if column in crm_df.columns]
    st.dataframe(crm_df.head(8)[columns], use_container_width=True)
else:
    st.info("Priority actions are not available yet. Run the data pipeline to generate them.")

with st.expander("Data Quality / Validation Report"):
    report = load_validation_report()
    if report:
        st.json(report)
    else:
        st.info("Validation report not available yet.")

st.markdown("---")
st.caption(
    "Use the sidebar to explore customer sentiment, recurring issues, branch performance, "
    "forecasts, negative feedback, and the AI Analyst."
)
