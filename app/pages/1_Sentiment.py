"""Sentiment view — baseline lexicon sentiment distribution and trend."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import plotly.express as px
import streamlit as st

from app.data_loader import load_anomalies, load_branch_summary, load_nlp_reviews
from app.theme import CHART_SEQUENCE, apply_theme, banner, data_tag
from app.visuals import show_wordcloud

apply_theme("Sentiment")
banner("Customer Sentiment", "How customers feel about the experience, by branch and time")
st.markdown(
    data_tag("derived") + " Sentiment is an initial language-based signal, not a validated "
    "customer-satisfaction measure. Use the review samples to verify the pattern.",
    unsafe_allow_html=True,
)

reviews = load_nlp_reviews()
if reviews.empty:
    st.warning("Run `python -m src.pipeline` first to generate NLP results.")
    st.stop()

branches = ["All"] + sorted(reviews["branch_id"].dropna().unique().tolist())
selected = st.selectbox("Branch", branches)
filtered = reviews if selected == "All" else reviews[reviews["branch_id"] == selected]

col1, col2 = st.columns(2)
with col1:
    dist = filtered["sentiment_label"].value_counts().reset_index()
    dist.columns = ["sentiment_label", "count"]
    fig = px.pie(
        dist, names="sentiment_label", values="count",
        color_discrete_sequence=CHART_SEQUENCE, title="Customer Feedback Distribution",
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    branch_summary = load_branch_summary()
    fig2 = px.bar(
        filtered.groupby("branch_id")["sentiment_score"].mean().reset_index(),
        x="branch_id", y="sentiment_score",
        color="branch_id", color_discrete_sequence=CHART_SEQUENCE,
        title="Average Customer Sentiment Signal by Branch",
    )
    fig2.update_layout(showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("What Customers Talk About")
    st.markdown(
        data_tag("real") + " Word size shows frequency in the selected review text. "
        "Use the examples below to understand the context behind the pattern.",
        unsafe_allow_html=True,
    )
    show_wordcloud(
        filtered["review_text"],
        "Language used in selected reviews",
        "YlOrBr",
    )

st.subheader("Monthly Sentiment Trend")
anomalies = load_anomalies()
if not anomalies.empty:
    trend = anomalies if selected == "All" else anomalies[anomalies["branch_id"] == selected]
    fig3 = px.line(
        trend, x="month", y="average_sentiment_score", color="branch_id",
        color_discrete_sequence=CHART_SEQUENCE, markers=True,
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("Monthly customer sentiment history is not available yet.")

st.subheader("Review Examples")
st.dataframe(
    filtered[["review_id", "branch_id", "rating", "sentiment_label", "sentiment_score", "review_text"]].head(200),
    use_container_width=True,
)
